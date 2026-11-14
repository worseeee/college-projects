"""
ElderGuard 报警控制模块 (alarm.py)
功能：实现三级分级报警的硬件控制、状态机管理、远程通知
作者：ElderGuard开发团队
版本：1.0 - 修复版
"""

import RPi.GPIO as GPIO
import threading
import time
import requests
from datetime import datetime
from typing import Optional, Callable
from enum import IntEnum


class AlarmLevel(IntEnum):
    """报警等级枚举"""
    NORMAL = 0      # 正常状态
    LEVEL_1 = 1     # 轻度异常：LED闪烁
    LEVEL_2 = 2     # 中度异常：蜂鸣器间歇
    LEVEL_3 = 3     # 严重异常：蜂鸣器持续 + 远程通知


class AlarmController:
    """
    报警控制器类
    负责三级分级报警的硬件控制、状态机管理、远程通知
    """
    
    # GPIO引脚定义（BOARD物理编码）
    LED_PIN = 16        # 状态指示LED
    BUZZER_PIN = 32     # 蜂鸣器
    
    # LED PWM配置
    LED_PWM_FREQUENCY = 1000
    LED_BLINK_FREQUENCY = 1.0
    LED_DUTY_CYCLE = 50
    
    # 蜂鸣器PWM配置
    BUZZER_FREQUENCY_LOW = 2000
    BUZZER_FREQUENCY_HIGH = 3000
    BUZZER_DUTY_CYCLE = 50
    
    # 蜂鸣器间歇配置（Level 2）
    BUZZER_BEEP_ON_TIME = 0.2
    BUZZER_BEEP_OFF_TIME = 0.3
    
    # 远程通知配置
    WEBHOOK_TIMEOUT = 5
    WEBHOOK_RETRY = 2
    
    # 报警升级配置
    AUTO_ESCALATE_INTERVAL = 300
    
    
    def __init__(self, database_manager, webhook_url: Optional[str] = None,
                 dingtalk_secret: Optional[str] = None,
                 status_callback: Optional[Callable] = None):
        """
        初始化报警控制器
        
        Args:
            database_manager: 数据库管理器实例
            webhook_url: 钉钉Webhook地址
            dingtalk_secret: 钉钉加签密钥（可选）
            status_callback: 状态变更回调函数
        """
        # ===== 关键修复：立即初始化所有属性 =====
        self.db = database_manager
        self.dingtalk_webhook = webhook_url
        self.dingtalk_secret = dingtalk_secret
        self.status_callback = status_callback
        
        # 当前报警状态（必须在最开始初始化）
        self.current_level = AlarmLevel.NORMAL
        self.current_reason = ""
        self.level_start_time = None
        self.current_alarm_id = None
        
        # PWM对象（先设置为None，避免cleanup时出错）
        self.led_pwm = None
        self.buzzer_pwm = None
        
        # 线程控制
        self.running = False
        self.alarm_thread = None
        self.lock = threading.Lock()
        
        # 报警历史追踪
        self.last_notification_time = None
        self.notification_cooldown = 300
        # ==========================================
        
        # 初始化GPIO（放在所有属性初始化之后）
        try:
            self._setup_gpio()
        except Exception as e:
            print(f"[警告] 报警器GPIO初始化失败: {e}")
            print("[系统] 报警器将在软件模拟模式下运行")
        
        print("[报警器] 报警控制器初始化完成")
    
    
    def _setup_gpio(self):
        """
        初始化GPIO引脚配置
        注意：不再调用GPIO.setmode()，由SensorManager统一设置
        """
        # ===== 修改：检查模式但不强制重设 =====
        try:
            current_mode = GPIO.getmode()
            if current_mode is None:
                GPIO.setmode(GPIO.BOARD)
                print("[GPIO] 报警器设置模式为BOARD")
            elif current_mode != GPIO.BOARD:
                print(f"[GPIO] 警告：当前模式={current_mode}，期望BOARD")
            # 如果已经是BOARD模式，什么都不做
        except Exception as e:
            print(f"[警告] GPIO模式检查异常: {e}")

        GPIO.setwarnings(False)

        # 其余不变...
        try:
            GPIO.setup(self.LED_PIN, GPIO.OUT)
            GPIO.output(self.LED_PIN, GPIO.LOW)
            self.led_pwm = GPIO.PWM(self.LED_PIN, self.LED_PWM_FREQUENCY)
            self.led_pwm.start(0)
            print(f"[GPIO] LED引脚已配置 (Pin{self.LED_PIN})")
        except Exception as e:
            print(f"[警告] LED初始化失败: {e}")

        try:
            GPIO.setup(self.BUZZER_PIN, GPIO.OUT)
            GPIO.output(self.BUZZER_PIN, GPIO.LOW)
            self.buzzer_pwm = GPIO.PWM(self.BUZZER_PIN, self.BUZZER_FREQUENCY_LOW)
            self.buzzer_pwm.start(0)
            print(f"[GPIO] 蜂鸣器引脚已配置 (Pin{self.BUZZER_PIN})")
        except Exception as e:
            print(f"[警告] 蜂鸣器初始化失败: {e}")
    
    
    def _led_blink_thread(self):
        """LED闪烁线程（Level 1报警）"""
        print("[LED] 启动闪烁模式（1Hz）")
        
        if not self.led_pwm:
            print("[LED] PWM未初始化，跳过")
            return
        
        blink_period = 1.0 / self.LED_BLINK_FREQUENCY
        half_period = blink_period / 2
        
        while self.running and self.current_level == AlarmLevel.LEVEL_1:
            try:
                self.led_pwm.ChangeDutyCycle(self.LED_DUTY_CYCLE)
                time.sleep(half_period)
                self.led_pwm.ChangeDutyCycle(0)
                time.sleep(half_period)
            except:
                break
        
        if self.led_pwm:
            self.led_pwm.ChangeDutyCycle(0)
        print("[LED] 闪烁模式已停止")
    
    
    def _buzzer_beep_thread(self):
        """蜂鸣器间歇鸣叫线程（Level 2报警）"""
        print("[蜂鸣器] 启动间歇模式（500ms周期）")
        
        if not self.buzzer_pwm:
            print("[蜂鸣器] PWM未初始化，跳过")
            return
        
        while self.running and self.current_level == AlarmLevel.LEVEL_2:
            try:
                self.buzzer_pwm.ChangeFrequency(self.BUZZER_FREQUENCY_LOW)
                self.buzzer_pwm.ChangeDutyCycle(self.BUZZER_DUTY_CYCLE)
                time.sleep(self.BUZZER_BEEP_ON_TIME)
                
                self.buzzer_pwm.ChangeDutyCycle(0)
                time.sleep(self.BUZZER_BEEP_OFF_TIME)
            except:
                break
        
        if self.buzzer_pwm:
            self.buzzer_pwm.ChangeDutyCycle(0)
        print("[蜂鸣器] 间歇模式已停止")
    
    
    def _buzzer_continuous_thread(self):
        """蜂鸣器持续鸣叫线程（Level 3报警）"""
        print("[蜂鸣器] 启动持续模式（高音调）")
        
        if not self.buzzer_pwm:
            print("[蜂鸣器] PWM未初始化，跳过")
            return
        
        tone_switch_interval = 0.5
        high_tone = True
        
        while self.running and self.current_level == AlarmLevel.LEVEL_3:
            try:
                if high_tone:
                    self.buzzer_pwm.ChangeFrequency(self.BUZZER_FREQUENCY_HIGH)
                else:
                    self.buzzer_pwm.ChangeFrequency(self.BUZZER_FREQUENCY_LOW)
                
                self.buzzer_pwm.ChangeDutyCycle(self.BUZZER_DUTY_CYCLE)
                
                high_tone = not high_tone
                time.sleep(tone_switch_interval)
            except:
                break
        
        if self.buzzer_pwm:
            self.buzzer_pwm.ChangeDutyCycle(0)
        print("[蜂鸣器] 持续模式已停止")
    
    
    def _send_notification(self, level: int, reason: str) -> bool:
        """
        发送钉钉机器人通知
        
        Args:
            level: 报警等级
            reason: 报警原因
        
        Returns:
            bool: 发送是否成功
        """
        dingtalk_webhook = self.dingtalk_webhook
        dingtalk_secret = self.dingtalk_secret
        
        if not dingtalk_webhook:
            print("[通知] 未配置钉钉Webhook地址，跳过远程通知")
            return False
        
        # 检查通知冷却时间
        if self.last_notification_time:
            time_since_last = time.time() - self.last_notification_time
            if time_since_last < self.notification_cooldown:
                print(f"[通知] 距离上次通知仅{time_since_last:.0f}秒，跳过")
                return False
        
        # 构建通知消息
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        level_text = {
            1: "⚠️ 轻度异常",
            2: "🔶 中度异常",
            3: "🚨 严重异常"
        }.get(level, "未知等级")
        
        message = {
            "msgtype": "text",
            "text": {
                "content": f"【ElderGuard报警通知】\n\n"
                          f"等级: {level_text}\n"
                          f"原因: {reason}\n"
                          f"时间: {timestamp}\n\n"
                          f"请及时查看老人状态！"
            }
        }
        
        # 如果使用加签，生成签名
        url = dingtalk_webhook
        if dingtalk_secret:
            import hmac
            import hashlib
            import base64
            from urllib.parse import quote_plus
            
            timestamp_ms = str(round(time.time() * 1000))
            secret_enc = dingtalk_secret.encode('utf-8')
            string_to_sign = f'{timestamp_ms}\n{dingtalk_secret}'
            string_to_sign_enc = string_to_sign.encode('utf-8')
            hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
            sign = quote_plus(base64.b64encode(hmac_code))
            url = f"{dingtalk_webhook}&timestamp={timestamp_ms}&sign={sign}"
        
        # 重试发送
        for attempt in range(1, self.WEBHOOK_RETRY + 1):
            try:
                print(f"[通知] 发送钉钉通知（尝试 {attempt}/{self.WEBHOOK_RETRY}）...")
                
                response = requests.post(
                    url,
                    json=message,
                    timeout=self.WEBHOOK_TIMEOUT,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('errcode') == 0:
                        print(f"[通知] ✓ 钉钉通知发送成功")
                        self.last_notification_time = time.time()
                        return True
                    else:
                        print(f"[通知] ✗ 发送失败: {result.get('errmsg')}")
                        if result.get('errcode') == 310000:
                            print(f"[提示] 消息可能缺少安全关键词")
                            break
                else:
                    print(f"[通知] ✗ HTTP错误: {response.status_code}")
            
            except requests.Timeout:
                print(f"[通知] ✗ 请求超时")
            except Exception as e:
                print(f"[通知] ✗ 异常: {e}")
            
            if attempt < self.WEBHOOK_RETRY:
                time.sleep(1)
        
        print(f"[通知] ✗ 钉钉通知发送失败")
        return False
    
    
    def _stop_all_alarms(self):
        """停止所有报警输出"""
        if self.led_pwm:
            try:
                self.led_pwm.ChangeDutyCycle(0)
            except:
                pass
        
        if self.buzzer_pwm:
            try:
                self.buzzer_pwm.ChangeDutyCycle(0)
            except:
                pass
        
        if self.alarm_thread and self.alarm_thread.is_alive():
            self.alarm_thread.join(timeout=2.0)
    
    
    def set_alarm_level(self, level: int, reason: str = "", by_button: bool = False) -> bool:
        """
        设置报警等级（核心接口）
        
        Args:
            level: 报警等级 (0-3)
            reason: 报警原因描述
            by_button: 是否由紧急按钮触发
        
        Returns:
            bool: 设置是否成功
        """
        with self.lock:
            # 参数校验
            if not (0 <= level <= 3):
                print(f"[报警器] ✗ 无效的报警等级: {level}")
                return False
            
            new_level = AlarmLevel(level)
            
            # 检查是否需要状态变更
            if new_level == self.current_level and reason == self.current_reason:
                return True
            
            # 记录状态变更日志
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n{'='*60}")
            print(f"[报警器] 状态变更: Level {self.current_level} → Level {new_level}")
            print(f"         原因: {reason if reason else '无'}")
            print(f"         时间: {timestamp}")
            print(f"         触发方式: {'紧急按钮' if by_button else '自动检测'}")
            print(f"{'='*60}\n")
            
            # 如果存在旧的报警记录，先解除
            if self.current_alarm_id and self.current_level != AlarmLevel.NORMAL:
                self._resolve_current_alarm()
            
            # 停止旧的报警输出
            if self.current_level != AlarmLevel.NORMAL:
                self.running = False
                self._stop_all_alarms()
            
            # 更新状态
            self.current_level = new_level
            self.current_reason = reason
            self.level_start_time = time.time()
            
            # 写入新的报警记录到数据库
            if new_level != AlarmLevel.NORMAL:
                try:
                    self.current_alarm_id = self.db.insert_alarm_log(
                        alarm_level=int(new_level),
                        duration_sec=0,
                        by_button=by_button
                    )
                except Exception as e:
                    print(f"[报警器] ✗ 写入数据库失败: {e}")
            
            # 启动对应等级的报警
            if new_level == AlarmLevel.NORMAL:
                print("[报警器] 恢复正常状态")
                self._stop_all_alarms()
            
            elif new_level == AlarmLevel.LEVEL_1:
                print("[报警器] 启动一级报警：LED闪烁")
                self.running = True
                self.alarm_thread = threading.Thread(
                    target=self._led_blink_thread,
                    name="LED_Blink",
                    daemon=True
                )
                self.alarm_thread.start()
            
            elif new_level == AlarmLevel.LEVEL_2:
                print("[报警器] 启动二级报警：蜂鸣器间歇")
                self.running = True
                self.alarm_thread = threading.Thread(
                    target=self._buzzer_beep_thread,
                    name="Buzzer_Beep",
                    daemon=True
                )
                self.alarm_thread.start()
            
            elif new_level == AlarmLevel.LEVEL_3:
                print("[报警器] 启动三级报警：蜂鸣器持续 + 远程通知")
                self.running = True
                
                self.alarm_thread = threading.Thread(
                    target=self._buzzer_continuous_thread,
                    name="Buzzer_Continuous",
                    daemon=True
                )
                self.alarm_thread.start()
                
                # 异步发送远程通知
                notification_thread = threading.Thread(
                    target=self._send_notification,
                    args=(int(new_level), reason),
                    daemon=True
                )
                notification_thread.start()
            
            # 调用状态变更回调函数
            if self.status_callback:
                try:
                    self.status_callback(int(new_level), reason)
                except Exception as e:
                    print(f"[报警器] ✗ 回调函数执行失败: {e}")
            
            return True
    
    
    def _resolve_current_alarm(self):
        """解除当前报警（更新数据库记录）"""
        if not self.current_alarm_id:
            return
        
        try:
            duration = time.time() - self.level_start_time if self.level_start_time else 0
            
            self.db.update_alarm_resolved(self.current_alarm_id)
            
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    "UPDATE alarm_logs SET duration_sec = ? WHERE id = ?",
                    (round(duration, 2), self.current_alarm_id)
                )
            
            print(f"[数据库] 报警记录已解除（ID: {self.current_alarm_id}, 持续{duration:.0f}秒）")
            self.current_alarm_id = None
            
        except Exception as e:
            print(f"[报警器] ✗ 解除报警记录失败: {e}")
    
    
    def escalate_if_needed(self):
        """自动升级报警等级"""
        if self.current_level == AlarmLevel.NORMAL or not self.level_start_time:
            return
        
        duration = time.time() - self.level_start_time
        
        if duration >= self.AUTO_ESCALATE_INTERVAL and self.current_level < AlarmLevel.LEVEL_3:
            new_level = self.current_level + 1
            print(f"[报警器] ⬆️ 自动升级：Level {self.current_level} → Level {new_level} "
                  f"（持续{duration/60:.1f}分钟）")
            
            escalate_reason = f"{self.current_reason}（持续{duration/60:.0f}分钟未缓解）"
            self.set_alarm_level(int(new_level), escalate_reason)
    
    
    def get_status(self) -> dict:
        """获取当前报警状态"""
        duration = time.time() - self.level_start_time if self.level_start_time else 0
        
        return {
            'level': int(self.current_level),
            'reason': self.current_reason,
            'duration': round(duration, 1),
            'alarm_id': self.current_alarm_id
        }
    
    
    def cleanup(self):
        """清理资源"""
        print("[报警器] 清理报警控制器...")
        
        # 解除当前报警
        if hasattr(self, 'current_level') and self.current_level != AlarmLevel.NORMAL:
            self._resolve_current_alarm()
        
        # 停止所有输出
        if hasattr(self, 'running'):
            self.running = False
        self._stop_all_alarms()
        
        # 停止PWM
        if hasattr(self, 'led_pwm') and self.led_pwm:
            try:
                self.led_pwm.stop()
            except:
                pass
        
        if hasattr(self, 'buzzer_pwm') and self.buzzer_pwm:
            try:
                self.buzzer_pwm.stop()
            except:
                pass
        
        # 重置GPIO引脚
        try:
            if hasattr(self, 'LED_PIN'):
                GPIO.output(self.LED_PIN, GPIO.LOW)
            if hasattr(self, 'BUZZER_PIN'):
                GPIO.output(self.BUZZER_PIN, GPIO.LOW)
        except:
            pass
        
        print("[报警器] 清理完成")
    
    
    def __del__(self):
        """析构函数"""
        try:
            self.cleanup()
        except:
            pass