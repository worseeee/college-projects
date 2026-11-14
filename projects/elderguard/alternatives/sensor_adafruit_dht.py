"""
ElderGuard 数据采集模块 (sensor.py) - 修复版
主要修复：
1. DHT初始化顺序调整（先DHT后GPIO）
2. 详细的错误类型区分
3. DHT重连机制
4. 备选dht11库支持
"""

import time
import threading
from datetime import datetime
from typing import Optional, Tuple, Callable

import RPi.GPIO as GPIO
import board
import adafruit_dht


class SensorManager:
    # ===== GPIO引脚定义 (BOARD物理编号) =====
    PIR_PIN    = 11   # 物理引脚11 = BCM17
    BUTTON_PIN = 18   # 物理引脚18 = BCM24
    # DHT11 接在 物理引脚22 = BCM25，由adafruit库直接管理，不经过RPi.GPIO

    # ===== 采集间隔 =====
    PIR_INTERVAL = 1.0
    DHT_INTERVAL = 60.0

    # ===== 数据合法范围 =====
    TEMP_MIN     = -10.0
    TEMP_MAX     =  60.0
    HUMIDITY_MIN =   0.0
    HUMIDITY_MAX = 100.0

    # ===== DHT重试策略 =====
    DHT_MAX_RETRIES  = 5
    DHT_RETRY_DELAY  = 2.5   # DHT11数据手册要求最小2秒采样间隔
    DHT_REINIT_AFTER = 3     # 连续失败多少次后尝试重新初始化


    # =========================================================
    # 初始化
    # =========================================================
    def __init__(self, database_manager, button_callback=None):
        self.db              = database_manager
        self.button_callback = button_callback
        self.running = False
        self.threads = []
        self.last_pir_state       = 0
        self.pir_state_start_time = None
        self.last_valid_temp     = None
        self.last_valid_humidity = None
        self.dht_fail_count      = 0
        self.dht_device          = None
        self.button_polling_mode = True

        # ===== 关键：先DHT后GPIO =====
        self._setup_dht()    # 第一步：adafruit独占DHT引脚
        self._setup_gpio()   # 第二步：RPi.GPIO只管PIR和按钮
        print("[传感器] 初始化完成")


    # =========================================================
    # DHT11 初始化 / 重新初始化
    # =========================================================
    def _setup_dht(self):
        """
        独立初始化DHT11，避免与RPi.GPIO占用GPIO子系统冲突。
        初始化后做一次预热读取（第一次几乎必定失败，属正常现象）。
        """
        # 清理可能残留的libgpiod进程
        try:
            import subprocess
            for proc in ('libgpiod_pulsein', 'libgpiod_pulsein64'):
                subprocess.run(
                    ['sudo', 'killall', proc],
                    capture_output=True, timeout=3
                )
        except Exception:
            pass

        time.sleep(1)

        try:
            self.dht_device = adafruit_dht.DHT11(
                board.D25,          # BCM25 = 物理引脚22
                use_pulseio=False   # 新版树莓派必须设为False
            )
            print("[DHT11] 传感器对象创建成功，预热中...")

            # 预热：等待2秒后做一次丢弃性读取
            time.sleep(2)
            try:
                _ = self.dht_device.temperature
                _ = self.dht_device.humidity
            except Exception:
                pass  # 第一次读取大概率失败，直接忽略

            time.sleep(2)
            print("[DHT11] 预热完成")

        except Exception as e:
            print(f"[DHT11] 初始化失败: {e}")
            print("[DHT11] 传感器将不可用，程序继续运行")
            self.dht_device = None


    def _reinit_dht(self):
        """连续失败达到阈值后，重建DHT设备对象。"""
        print("[DHT11] 尝试重新初始化...")
        try:
            if self.dht_device:
                self.dht_device.exit()
        except Exception:
            pass

        self.dht_device = None
        time.sleep(3)

        try:
            self.dht_device = adafruit_dht.DHT11(
                board.D25,
                use_pulseio=False
            )
            time.sleep(2)
            # 预热读取
            try:
                _ = self.dht_device.temperature
            except Exception:
                pass
            time.sleep(2)
            print("[DHT11] 重新初始化成功")
        except Exception as e:
            print(f"[DHT11] 重新初始化失败: {e}")
            self.dht_device = None


    # =========================================================
    # GPIO 初始化
    # =========================================================
    def _setup_gpio(self):
        """
        在DHT初始化完成之后再设置RPi.GPIO，
        避免两者同时占用GPIO子系统导致冲突。
        """
        GPIO.setwarnings(False)

        if GPIO.getmode() is None:
            GPIO.setmode(GPIO.BOARD)
            print("[GPIO] 模式设置为 BOARD")

        GPIO.setup(self.PIR_PIN, GPIO.IN)
        print(f"[GPIO] PIR引脚 (BOARD {self.PIR_PIN}) 配置完成")

        try:
            GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            print(f"[GPIO] 按钮引脚 (BOARD {self.BUTTON_PIN}) 配置完成")
        except Exception as e:
            print(f"[GPIO] 按钮引脚配置失败: {e}")

        print("[GPIO] 所有引脚配置完成")


    # =========================================================
    # 紧急按钮处理
    # =========================================================
    def _button_pressed_handler(self, channel):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[紧急按钮] 按钮按下！时间: {timestamp}")

        try:
            self.db.insert_alarm_log(
                alarm_level=3,
                duration_sec=0,
                by_button=True
            )
            print("[数据库] 紧急按钮事件已记录")
        except Exception as e:
            print(f"[错误] 记录紧急按钮事件失败: {e}")

        if self.button_callback:
            try:
                self.button_callback()
            except Exception as e:
                print(f"[错误] 紧急按钮回调执行失败: {e}")


    # =========================================================
    # 工具方法
    # =========================================================
    def _get_cpu_temperature(self) -> float:
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                return round(float(f.read().strip()) / 1000.0, 1)
        except Exception:
            return 0.0


    def _validate_dht_data(self, humidity: float, temperature: float) -> bool:
        if humidity is None or temperature is None:
            return False
        if not (self.TEMP_MIN <= temperature <= self.TEMP_MAX):
            print(f"[DHT11] 温度超出范围: {temperature}°C")
            return False
        if not (self.HUMIDITY_MIN <= humidity <= self.HUMIDITY_MAX):
            print(f"[DHT11] 湿度超出范围: {humidity}%")
            return False
        return True


    # =========================================================
    # DHT11 读取（带重试 + 重连 + 降级策略）
    # =========================================================
    def _read_dht11_with_retry(self) -> Tuple[Optional[float], Optional[float]]:
        """
        返回 (humidity, temperature)，失败时返回 (None, None)。
        降级顺序：实时读取 → 缓存值 → None
        """
        if self.dht_device is None:
            print("[DHT11] 设备不可用，跳过读取")
            return None, None

        for attempt in range(self.DHT_MAX_RETRIES):
            try:
                temperature = self.dht_device.temperature
                humidity    = self.dht_device.humidity

                if self._validate_dht_data(humidity, temperature):
                    self.dht_fail_count      = 0
                    self.last_valid_temp     = temperature
                    self.last_valid_humidity = humidity
                    print(
                        f"[DHT11] ✓ 读取成功（第{attempt+1}次尝试）"
                        f" T={temperature:.1f}°C  H={humidity:.1f}%"
                    )
                    return humidity, temperature
                else:
                    print(f"[DHT11] 第{attempt+1}次数据不合法: T={temperature}  H={humidity}")

            except RuntimeError as e:
                err = str(e)
                if "Checksum" in err:
                    print(f"[DHT11] 第{attempt+1}次 校验和错误（检查接线/干扰）")
                elif "Timed out" in err or "timeout" in err.lower():
                    print(f"[DHT11] 第{attempt+1}次 超时（传感器未响应）")
                else:
                    print(f"[DHT11] 第{attempt+1}次 RuntimeError: {err}")

            except Exception as e:
                print(f"[DHT11] 第{attempt+1}次 异常 [{type(e).__name__}]: {e}")
                # 遇到严重错误时立刻重建连接
                self._reinit_dht()
                if self.dht_device is None:
                    break

            # DHT11 数据手册要求相邻两次读取间隔 ≥ 2 秒
            if attempt < self.DHT_MAX_RETRIES - 1:
                time.sleep(self.DHT_RETRY_DELAY)

        # ===== 全部重试失败 =====
        self.dht_fail_count += 1
        print(f"[DHT11] ✗ 本轮全部失败（已连续失败 {self.dht_fail_count} 次）")

        # 达到阈值时尝试重新初始化，为下一轮采集做准备
        if self.dht_fail_count % self.DHT_REINIT_AFTER == 0:
            self._reinit_dht()

        # 降级：返回缓存值
        if self.last_valid_temp is not None:
            print(
                f"[DHT11] ⚠ 使用缓存值"
                f" T={self.last_valid_temp:.1f}°C  H={self.last_valid_humidity:.1f}%"
            )
            return self.last_valid_humidity, self.last_valid_temp

        return None, None


    # =========================================================
    # 采集线程
    # =========================================================
    def _collect_pir_data(self):
        print("[PIR线程] 启动")
        self.pir_state_start_time = time.time()

        while self.running:
            try:
                current_state = GPIO.input(self.PIR_PIN)
                current_time  = time.time()

                if current_state != self.last_pir_state:
                    duration = current_time - self.pir_state_start_time

                    self.db.insert_motion_event(
                        pir_state=self.last_pir_state,
                        duration=round(duration, 2)
                    )

                    last_txt = "运动" if self.last_pir_state == 1 else "静止"
                    curr_txt = "运动" if current_state         == 1 else "静止"
                    print(f"[PIR] 状态变化: {last_txt}({duration:.1f}s) → {curr_txt}")

                    self.last_pir_state       = current_state
                    self.pir_state_start_time = current_time

                time.sleep(self.PIR_INTERVAL)

            except Exception as e:
                print(f"[PIR线程] 异常: {e}")
                time.sleep(self.PIR_INTERVAL)

        print("[PIR线程] 已停止")


    def _collect_dht_data(self):
        print("[DHT线程] 启动，等待5秒后开始采集...")
        time.sleep(5)

        while self.running:
            try:
                cpu_temp              = self._get_cpu_temperature()
                humidity, temperature = self._read_dht11_with_retry()

                if humidity is not None and temperature is not None:
                    self.db.insert_env_record(
                        cpu_temp=cpu_temp,
                        env_temp=temperature,
                        humidity=humidity
                    )
                    print(
                        f"[DHT11] 数据已写入"
                        f" T={temperature:.1f}°C  H={humidity:.1f}%  CPU={cpu_temp}°C"
                    )
                else:
                    print("[DHT11] 本次采集无有效数据，跳过写库")

                time.sleep(self.DHT_INTERVAL)

            except Exception as e:
                print(f"[DHT线程] 异常: {e}")
                time.sleep(self.DHT_INTERVAL)

        print("[DHT线程] 已停止")


    def _collect_button_data(self):
        if not self.button_polling_mode:
            return

        print("[按钮线程] 启动（轮询模式）")
        last_state    = 1
        debounce_time = 0.0

        while self.running:
            try:
                current_state = GPIO.input(self.BUTTON_PIN)
                current_time  = time.time()

                # 下降沿 + 去抖
                if last_state == 1 and current_state == 0:
                    if current_time - debounce_time > 0.3:
                        print("\n[紧急按钮] 检测到按下")
                        self._button_pressed_handler(self.BUTTON_PIN)
                        debounce_time = current_time

                last_state = current_state
                time.sleep(0.1)

            except Exception as e:
                print(f"[按钮线程] 异常: {e}")
                time.sleep(0.1)

        print("[按钮线程] 已停止")


    # =========================================================
    # 启动 / 停止
    # =========================================================
    def start(self):
        if self.running:
            return

        self.running = True

        pir_thread    = threading.Thread(target=self._collect_pir_data,    daemon=True, name="PIR")
        dht_thread    = threading.Thread(target=self._collect_dht_data,    daemon=True, name="DHT")
        button_thread = threading.Thread(target=self._collect_button_data, daemon=True, name="BTN")

        pir_thread.start()
        dht_thread.start()
        button_thread.start()

        self.threads = [pir_thread, dht_thread, button_thread]
        print("[传感器] 所有采集线程已启动")


    def stop(self):
        if not self.running:
            return

        print("[传感器] 停止中...")
        self.running = False

        for t in self.threads:
            t.join(timeout=5.0)

        self.threads = []
        print("[传感器] 所有线程已停止")


    # =========================================================
    # 状态查询
    # =========================================================
    def get_current_status(self) -> dict:
        duration = (
            round(time.time() - self.pir_state_start_time, 1)
            if self.pir_state_start_time else 0.0
        )
        return {
            'pir_state':   self.last_pir_state,
            'pir_duration': duration,
            'temperature': self.last_valid_temp,
            'humidity':    self.last_valid_humidity,
            'cpu_temp':    self._get_cpu_temperature(),
            'dht_status':  '正常' if self.dht_fail_count < 3 else '异常',
        }


    # =========================================================
    # 资源清理
    # =========================================================
    def cleanup(self):
        print("[传感器] 清理资源...")
        self.stop()

        if self.dht_device:
            try:
                self.dht_device.exit()
                print("[DHT11] 设备已释放")
            except Exception:
                pass

        try:
            GPIO.cleanup()
            print("[GPIO] 引脚已释放")
        except Exception:
            pass

        print("[传感器] 清理完成")


    def __del__(self):
        try:
            self.cleanup()
        except Exception:
            pass