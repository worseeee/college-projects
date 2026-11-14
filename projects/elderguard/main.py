#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ElderGuard 系统主入口 (main.py)
功能：整合所有模块，启动完整的监护系统
作者：ElderGuard开发团队
版本：1.0 - 稳定版
"""

import signal
import sys
import time
import threading
from datetime import datetime
import traceback

# 强制刷新标准输出
import functools
print = functools.partial(print, flush=True)

# 导入核心模块
from core.database import DatabaseManager
from core.sensor import SensorManager
from core.analyzer import BehaviorAnalyzer
from core.alarm import AlarmController

# 导入UI模块
from ui.dashboard import DashboardUI
from ui.report import ReportGenerator


class ElderGuardSystem:
    """
    ElderGuard 系统主控制器
    负责整合所有模块并协调运行
    """
    
    # 系统配置
    ANALYSIS_INTERVAL = 60          # 分析间隔（秒）
    BASELINE_UPDATE_INTERVAL = 3600 # 基线更新间隔（秒）
    
    # 钉钉机器人配置（可选）
    DINGTALK_WEBHOOK = None  # 填入您的Webhook地址
    DINGTALK_SECRET = ""     # 如果使用加签，填入secret
    
    
    def __init__(self):
        """
        初始化系统
        """
        print("\n" + "=" * 70)
        print("ElderGuard 独居老人监护系统 v1.0")
        print("=" * 70)
        print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70 + "\n")
        
        # 模块实例
        self.db = None
        self.sensor = None
        self.analyzer = None
        self.alarm = None
        self.dashboard = None
        self.report = None
        
        # 线程控制
        self.running = False
        self.analysis_thread = None
        self.baseline_thread = None
        
        # 注册信号处理器
        self._register_signal_handlers()
        
        # 初始化所有模块
        self._initialize_modules()
    
    
    def _register_signal_handlers(self):
        """
        注册系统信号处理器（捕获Ctrl+C等退出信号）
        """
        def signal_handler(signum, frame):
            print(f"\n\n[系统] 接收到退出信号 ({signum})，正在安全退出...")
            self.shutdown()
            sys.exit(0)
        
        # 捕获常见退出信号
        signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # kill命令
        
        print("[系统] 信号处理器已注册")
    
    
    def _initialize_modules(self):
        try:
            print("\n[初始化] 开始初始化系统模块...\n")

            # 1. 数据库
            print("[1/6] 初始化数据库管理器...")
            self.db = DatabaseManager('data/elderguard.db')
            print("      ✅ 数据库连接成功\n")

            # 2. 报表生成器
            print("[2/6] 初始化报表生成器...")
            self.report = ReportGenerator(self.db)
            print("      ✅ 报表生成器就绪\n")

            # 3. 行为分析器
            print("[3/6] 初始化行为分析器...")
            self.analyzer = BehaviorAnalyzer(self.db)
            print("      ✅ 行为分析器就绪\n")

            # ===== 关键修改：传感器必须在报警控制器之前初始化 =====

            # 4. 传感器管理器（DHT11必须在任何GPIO.setmode之前初始化）
            print("[4/6] 初始化传感器管理器...")
            self.sensor = SensorManager(
                database_manager=self.db,
                button_callback=self._emergency_button_callback
            )
            print("      ✅ 传感器管理器就绪\n")

            # 5. 报警控制器（在传感器之后初始化，因为它会调用GPIO.setmode）
            print("[5/6] 初始化报警控制器...")
            self.alarm = AlarmController(
                database_manager=self.db,
                webhook_url=self.DINGTALK_WEBHOOK,
                dingtalk_secret=self.DINGTALK_SECRET,
                status_callback=self._alarm_status_callback
            )
            print("      ✅ 报警控制器就绪\n")

            # 6. Tkinter界面
            print("[6/6] 初始化可视化界面...")
            try:
                self.dashboard = DashboardUI(
                    sensor_manager=self.sensor,
                    analyzer=self.analyzer,
                    alarm_controller=self.alarm,
                    database_manager=self.db,
                    report_generator=self.report
                )
                print("      ✅ 界面初始化完成\n")
            except Exception as ui_error:
                print(f"      ⚠️ 界面初始化失败: {ui_error}")
                print("      系统将在无界面模式下运行\n")
                self.dashboard = None

            print("=" * 70)
            print("所有模块初始化成功！")
            print("=" * 70 + "\n")

        except Exception as e:
            print(f"\n[错误] 模块初始化失败: {e}")
            traceback.print_exc()
            self.shutdown()
            sys.exit(1)
    
    
    def _emergency_button_callback(self):
        """
        紧急按钮回调函数
        当物理按钮被按下时触发
        """
        print("\n" + "!" * 70)
        print("!!! 紧急按钮被按下 !!!")
        print("!" * 70 + "\n")
        
        # 直接触发三级报警
        self.alarm.set_alarm_level(
            level=3,
            reason="紧急求助按钮被按下",
            by_button=True
        )
    
    
    def _alarm_status_callback(self, level, reason):
        """
        报警状态变更回调函数
        通知其他模块报警状态已改变
        
        Args:
            level: 报警等级
            reason: 报警原因
        """
        print(f"[回调] 报警状态变更: Level {level} - {reason}")
    
    
    def _analysis_loop(self):
        """
        分析循环线程
        定期执行行为分析并更新报警状态
        """
        print(f"[分析线程] 启动，分析间隔: {self.ANALYSIS_INTERVAL}秒")
        
        while self.running:
            try:
                # 1. 获取当前传感器状态
                sensor_status = self.sensor.get_current_status()
                
                # 2. 执行综合分析
                analysis = self.analyzer.get_comprehensive_analysis(sensor_status)
                
                # 3. 根据分析结果更新报警等级
                final_level = analysis['final_alarm_level']
                
                if final_level > 0:
                    # 存在异常，设置对应等级报警
                    reason = analysis['motion_reason']
                    if analysis['env_alarm_level'] > 0:
                        reason += f"; {analysis['env_reason']}"
                    
                    self.alarm.set_alarm_level(final_level, reason)
                else:
                    # 正常状态，解除报警
                    self.alarm.set_alarm_level(0, "活动模式正常")
                
                # 4. 检查是否需要自动升级报警
                self.alarm.escalate_if_needed()
                
                # 5. 打印分析摘要（调试用）
                if final_level > 0:
                    print(f"\n[分析摘要] {datetime.now().strftime('%H:%M:%S')}")
                    print(f"  运动异常: Level {analysis['motion_alarm_level']} - {analysis['motion_reason']}")
                    print(f"  环境异常: Level {analysis['env_alarm_level']} - {analysis['env_reason']}")
                    print(f"  最终等级: Level {final_level}")
                    print(f"  当前基线: {analysis['current_hour_baseline']:.0f}秒 "
                          f"(样本数: {analysis['baseline_sample_count']})\n")
                
                # 等待下次分析
                time.sleep(self.ANALYSIS_INTERVAL)
                
            except Exception as e:
                print(f"[分析线程] 异常: {e}")
                traceback.print_exc()
                time.sleep(self.ANALYSIS_INTERVAL)
        
        print("[分析线程] 已停止")
    
    
    def _baseline_update_loop(self):
        """
        基线更新循环线程
        定期更新行为基线
        """
        print(f"[基线线程] 启动，更新间隔: {self.BASELINE_UPDATE_INTERVAL}秒")
        
        while self.running:
            try:
                time.sleep(self.BASELINE_UPDATE_INTERVAL)
                
                if not self.running:
                    break
                
                print(f"\n[基线更新] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.analyzer.update_baseline()
                
            except Exception as e:
                print(f"[基线线程] 异常: {e}")
                traceback.print_exc()
        
        print("[基线线程] 已停止")
    
    
    def start(self):
        """
        启动系统
        """
        try:
            print("\n" + "=" * 70)
            print("正在启动系统...")
            print("=" * 70 + "\n")
            
            # 1. 启动传感器采集
            print("[启动] 启动传感器采集线程...")
            self.sensor.start()
            print("       ✓ 传感器采集已启动\n")
            
            # 2. 启动分析循环线程
            print("[启动] 启动行为分析线程...")
            self.running = True
            self.analysis_thread = threading.Thread(
                target=self._analysis_loop,
                name="Analysis_Loop",
                daemon=True
            )
            self.analysis_thread.start()
            print("       ✓ 分析线程已启动\n")
            
            # 3. 启动基线更新线程
            print("[启动] 启动基线更新线程...")
            self.baseline_thread = threading.Thread(
                target=self._baseline_update_loop,
                name="Baseline_Update",
                daemon=True
            )
            self.baseline_thread.start()
            print("       ✓ 基线更新线程已启动\n")
            
            # 4. 显示系统状态
            print("=" * 70)
            print("系统启动成功！")
            print("=" * 70)
            print("\n系统运行中，当前状态:")
            print(f"  • 传感器采集: 运行中")
            print(f"  • 行为分析: 每{self.ANALYSIS_INTERVAL}秒执行一次")
            print(f"  • 基线更新: 每{self.BASELINE_UPDATE_INTERVAL//60}分钟执行一次")
            print(f"  • 远程通知: {'已配置' if self.DINGTALK_WEBHOOK else '未配置'}")
            print(f"  • 可视化界面: {'已启用' if self.dashboard else '已禁用（无显示环境）'}")
            print("\n按Ctrl+C可安全退出系统")
            print("=" * 70 + "\n")
            
            # 5. 启动Tkinter主循环（阻塞）或后台运行
            if self.dashboard:
                print("[启动] 启动可视化界面...\n")
                self.dashboard.run()
            else:
                print("[启动] 无界面模式，系统在后台运行...")
                print("传感器数据将持续采集并存入数据库\n")
                
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n\n[系统] 接收到Ctrl+C，正在退出...")
            
        except Exception as e:
            print(f"\n[错误] 系统启动失败: {e}")
            traceback.print_exc()
            self.shutdown()
            sys.exit(1)
    
    
    def shutdown(self):
        """
        安全关闭系统
        """
        print("\n\n" + "=" * 70)
        print("正在安全关闭系统...")
        print("=" * 70 + "\n")
        
        try:
            # 1. 停止所有线程
            print("[关闭] 停止后台线程...")
            self.running = False
            
            if self.analysis_thread and self.analysis_thread.is_alive():
                self.analysis_thread.join(timeout=3.0)
            
            if self.baseline_thread and self.baseline_thread.is_alive():
                self.baseline_thread.join(timeout=3.0)
            
            print("       ✓ 后台线程已停止\n")
            
            # 2. 停止传感器采集
            if self.sensor:
                print("[关闭] 停止传感器采集...")
                self.sensor.cleanup()
                print("       ✓ 传感器已清理\n")
            
            # 3. 关闭报警控制器
            if self.alarm:
                print("[关闭] 关闭报警控制器...")
                self.alarm.cleanup()
                print("       ✓ 报警器已清理\n")
            
            # 4. 关闭数据库连接
            if self.db:
                print("[关闭] 关闭数据库连接...")
                self.db.close()
                print("       ✓ 数据库已关闭\n")
            
            print("=" * 70)
            print("系统已安全退出")
            print("=" * 70 + "\n")
            
        except Exception as e:
            print(f"[警告] 关闭过程中出现异常: {e}")
            traceback.print_exc()


def main():
    """
    主函数
    """
    # 创建系统实例
    system = ElderGuardSystem()
    
    try:
        # 启动系统
        system.start()
        
    except KeyboardInterrupt:
        print("\n\n[系统] 接收到Ctrl+C，正在退出...")
        
    except Exception as e:
        print(f"\n[致命错误] 系统运行异常: {e}")
        traceback.print_exc()
        
    finally:
        # 确保系统被正确关闭
        system.shutdown()


if __name__ == '__main__':
    main()