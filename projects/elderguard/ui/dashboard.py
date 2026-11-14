"""
ElderGuard 实时监控界面模块 (dashboard.py)
功能：提供Tkinter可视化界面，实时显示传感器状态、报警等级、历史记录
作者：ElderGuard开发团队
版本：1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
from typing import Optional


class DashboardUI:
    """
    实时监控仪表盘类
    负责显示传感器数据、报警状态、历史记录
    """
    
    # 界面配置
    WINDOW_TITLE = "ElderGuard 独居老人监护系统"
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 600
    
    # 刷新间隔（毫秒）
    REFRESH_INTERVAL = 1000  # 1秒刷新一次
    
    # 状态灯颜色
    COLOR_NORMAL = "#28a745"    # 绿色
    COLOR_LEVEL_1 = "#ffc107"   # 黄色
    COLOR_LEVEL_2 = "#fd7e14"   # 橙色
    COLOR_LEVEL_3 = "#dc3545"   # 红色
    COLOR_OFF = "#6c757d"       # 灰色（未激活）
    
    
    def __init__(self, sensor_manager, analyzer, alarm_controller, database_manager, report_generator):
        """
        初始化仪表盘
        
        Args:
            sensor_manager: 传感器管理器实例
            analyzer: 行为分析器实例
            alarm_controller: 报警控制器实例
            database_manager: 数据库管理器实例
            report_generator: 报表生成器实例
        """
        self.sensor = sensor_manager
        self.analyzer = analyzer
        self.alarm = alarm_controller
        self.db = database_manager
        self.report = report_generator
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 创建界面组件
        self._create_widgets()
        
        # 启动定时刷新
        self._schedule_refresh()
        
        print("[界面] Tkinter界面初始化完成")
    
    
    def _create_widgets(self):
        """
        创建所有界面组件
        """
        # 主标题栏
        self._create_header()
        
        # 主容器（使用Grid布局）
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧：实时传感器数据面板
        self._create_sensor_panel(main_frame)
        
        # 中间：报警状态指示灯
        self._create_alarm_panel(main_frame)
        
        # 右侧：历史报警记录
        self._create_history_panel(main_frame)
        
        # 底部：控制按钮栏
        self._create_control_panel()
    
    
    def _create_header(self):
        """
        创建顶部标题栏
        """
        header_frame = tk.Frame(self.root, bg="#343a40", height=60)
        header_frame.pack(fill=tk.X)
        
        # 主标题
        title_label = tk.Label(
            header_frame,
            text="🏠 ElderGuard 监护系统",
            font=("Arial", 20, "bold"),
            bg="#343a40",
            fg="white"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # 系统状态指示
        self.status_label = tk.Label(
            header_frame,
            text="● 系统运行中",
            font=("Arial", 12),
            bg="#343a40",
            fg="#28a745"
        )
        self.status_label.pack(side=tk.RIGHT, padx=20)
        
        # 当前时间
        self.time_label = tk.Label(
            header_frame,
            text="",
            font=("Arial", 12),
            bg="#343a40",
            fg="white"
        )
        self.time_label.pack(side=tk.RIGHT, padx=20)
    
    
    def _create_sensor_panel(self, parent):
        """
        创建左侧传感器数据面板
        """
        panel = tk.LabelFrame(
            parent,
            text="📊 实时传感器数据",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # PIR运动检测
        pir_frame = tk.Frame(panel)
        pir_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(pir_frame, text="运动状态:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.pir_status_label = tk.Label(
            pir_frame,
            text="静止",
            font=("Arial", 11, "bold"),
            fg=self.COLOR_OFF
        )
        self.pir_status_label.pack(side=tk.LEFT, padx=10)
        
        self.pir_duration_label = tk.Label(
            pir_frame,
            text="(0秒)",
            font=("Arial", 10),
            fg="gray"
        )
        self.pir_duration_label.pack(side=tk.LEFT)
        
        # 分隔线
        tk.Frame(panel, height=2, bg="#dee2e6").pack(fill=tk.X, pady=10)
        
        # 环境温度
        temp_frame = tk.Frame(panel)
        temp_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(temp_frame, text="环境温度:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.temp_label = tk.Label(
            temp_frame,
            text="--°C",
            font=("Arial", 14, "bold"),
            fg="#ff6b6b"
        )
        self.temp_label.pack(side=tk.LEFT, padx=10)
        
        # 环境湿度
        humidity_frame = tk.Frame(panel)
        humidity_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(humidity_frame, text="环境湿度:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.humidity_label = tk.Label(
            humidity_frame,
            text="--%",
            font=("Arial", 14, "bold"),
            fg="#4dabf7"
        )
        self.humidity_label.pack(side=tk.LEFT, padx=10)
        
        # CPU温度
        cpu_temp_frame = tk.Frame(panel)
        cpu_temp_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(cpu_temp_frame, text="CPU温度:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.cpu_temp_label = tk.Label(
            cpu_temp_frame,
            text="--°C",
            font=("Arial", 11),
            fg="gray"
        )
        self.cpu_temp_label.pack(side=tk.LEFT, padx=10)
        
        # 分隔线
        tk.Frame(panel, height=2, bg="#dee2e6").pack(fill=tk.X, pady=10)
        
        # 今日统计摘要
        tk.Label(
            panel,
            text="📅 今日统计",
            font=("Arial", 11, "bold")
        ).pack(anchor=tk.W, pady=5)
        
        self.today_motion_label = tk.Label(
            panel,
            text="活动次数: --",
            font=("Arial", 10)
        )
        self.today_motion_label.pack(anchor=tk.W, pady=2)
        
        self.today_max_static_label = tk.Label(
            panel,
            text="最长静止: --",
            font=("Arial", 10)
        )
        self.today_max_static_label.pack(anchor=tk.W, pady=2)
        
        self.today_alarm_label = tk.Label(
            panel,
            text="报警次数: --",
            font=("Arial", 10)
        )
        self.today_alarm_label.pack(anchor=tk.W, pady=2)
        
        # 基线状态
        tk.Frame(panel, height=2, bg="#dee2e6").pack(fill=tk.X, pady=10)
        
        tk.Label(
            panel,
            text="🧠 行为基线",
            font=("Arial", 11, "bold")
        ).pack(anchor=tk.W, pady=5)
        
        self.baseline_status_label = tk.Label(
            panel,
            text="加载中...",
            font=("Arial", 9),
            fg="gray",
            wraplength=250,
            justify=tk.LEFT
        )
        self.baseline_status_label.pack(anchor=tk.W, pady=2)
    
    
    def _create_alarm_panel(self, parent):
        """
        创建中间报警状态指示灯面板
        """
        panel = tk.LabelFrame(
            parent,
            text="🚨 报警状态",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Canvas绘制三个状态灯
        canvas_height = 400
        self.alarm_canvas = tk.Canvas(
            panel,
            width=280,
            height=canvas_height,
            bg="white",
            highlightthickness=0
        )
        self.alarm_canvas.pack()
        
        # 绘制三个圆形指示灯
        light_radius = 40
        light_spacing = 120
        start_y = 80
        
        # 存储灯的Canvas对象ID
        self.alarm_lights = []
        self.alarm_labels = []
        
        alarm_configs = [
            {"level": 1, "text": "一级报警", "color": self.COLOR_LEVEL_1},
            {"level": 2, "text": "二级报警", "color": self.COLOR_LEVEL_2},
            {"level": 3, "text": "三级报警", "color": self.COLOR_LEVEL_3}
        ]
        
        for i, config in enumerate(alarm_configs):
            y = start_y + i * light_spacing
            
            # 绘制圆形（初始为灰色/未激活状态）
            light_id = self.alarm_canvas.create_oval(
                140 - light_radius,
                y - light_radius,
                140 + light_radius,
                y + light_radius,
                fill=self.COLOR_OFF,
                outline="#dee2e6",
                width=3
            )
            self.alarm_lights.append(light_id)
            
            # 绘制文本标签
            label_id = self.alarm_canvas.create_text(
                140,
                y + light_radius + 25,
                text=config['text'],
                font=("Arial", 12, "bold"),
                fill="gray"
            )
            self.alarm_labels.append(label_id)
            
            # 绘制等级描述
            desc_text = {
                1: "LED闪烁提醒",
                2: "蜂鸣器间歇",
                3: "持续报警+通知"
            }[config['level']]
            
            self.alarm_canvas.create_text(
                140,
                y + light_radius + 45,
                text=desc_text,
                font=("Arial", 9),
                fill="gray"
            )
        
        # 当前报警原因显示
        self.alarm_reason_text = tk.Text(
            panel,
            height=4,
            width=35,
            font=("Arial", 9),
            bg="#f8f9fa",
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.alarm_reason_text.pack(pady=10)
        self.alarm_reason_text.insert(1.0, "暂无报警")
        self.alarm_reason_text.config(state=tk.DISABLED)
    
    
    def _create_history_panel(self, parent):
        """
        创建右侧历史记录面板
        """
        panel = tk.LabelFrame(
            parent,
            text="📋 历史报警记录（最近10条）",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        panel.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        # 创建Treeview表格
        columns = ("时间", "等级", "持续", "状态")
        self.history_tree = ttk.Treeview(
            panel,
            columns=columns,
            show="headings",
            height=20
        )
        
        # 设置列标题
        self.history_tree.heading("时间", text="时间")
        self.history_tree.heading("等级", text="等级")
        self.history_tree.heading("持续", text="持续时长")
        self.history_tree.heading("状态", text="状态")
        
        # 设置列宽
        self.history_tree.column("时间", width=140, anchor=tk.CENTER)
        self.history_tree.column("等级", width=60, anchor=tk.CENTER)
        self.history_tree.column("持续", width=80, anchor=tk.CENTER)
        self.history_tree.column("状态", width=60, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            panel,
            orient=tk.VERTICAL,
            command=self.history_tree.yview
        )
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置Grid权重
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(2, weight=1)
        parent.rowconfigure(0, weight=1)
    
    
    def _create_control_panel(self):
        """
        创建底部控制按钮栏
        """
        panel = tk.Frame(self.root, bg="#f8f9fa", height=60)
        panel.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 生成报表按钮
        report_btn = tk.Button(
            panel,
            text="📊 生成健康报表",
            font=("Arial", 11, "bold"),
            bg="#007bff",
            fg="white",
            activebackground="#0056b3",
            activeforeground="white",
            relief=tk.RAISED,
            command=self._generate_report
        )
        report_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 刷新基线按钮
        baseline_btn = tk.Button(
            panel,
            text="🔄 更新行为基线",
            font=("Arial", 11),
            bg="#6c757d",
            fg="white",
            activebackground="#5a6268",
            activeforeground="white",
            relief=tk.RAISED,
            command=self._update_baseline
        )
        baseline_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 测试报警按钮（调试用）
        test_btn = tk.Button(
            panel,
            text="🔔 测试三级报警",
            font=("Arial", 11),
            bg="#dc3545",
            fg="white",
            activebackground="#c82333",
            activeforeground="white",
            relief=tk.RAISED,
            command=self._test_alarm
        )
        test_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 退出按钮
        exit_btn = tk.Button(
            panel,
            text="❌ 退出系统",
            font=("Arial", 11),
            bg="#6c757d",
            fg="white",
            activebackground="#5a6268",
            activeforeground="white",
            relief=tk.RAISED,
            command=self._on_closing
        )
        exit_btn.pack(side=tk.RIGHT, padx=10, pady=10)
    
    
    def _update_display(self):
        """
        更新所有显示数据（核心刷新函数）
        """
        try:
            # 1. 更新顶部时间
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.time_label.config(text=current_time)
            
            # 2. 更新传感器数据
            sensor_status = self.sensor.get_current_status()
            
            # PIR状态
            pir_state = sensor_status['pir_state']
            pir_duration = sensor_status['pir_duration']
            
            if pir_state == 1:
                self.pir_status_label.config(text="运动中", fg=self.COLOR_NORMAL)
            else:
                self.pir_status_label.config(text="静止", fg=self.COLOR_OFF)
            
            self.pir_duration_label.config(text=f"({pir_duration:.0f}秒)")
            
            # 温湿度
            temp = sensor_status['temperature']
            humidity = sensor_status['humidity']
            
            if temp is not None:
                self.temp_label.config(text=f"{temp:.1f}°C")
            else:
                self.temp_label.config(text="--°C")
            
            if humidity is not None:
                self.humidity_label.config(text=f"{humidity:.1f}%")
            else:
                self.humidity_label.config(text="--%")
            
            # CPU温度
            cpu_temp = sensor_status['cpu_temp']
            self.cpu_temp_label.config(text=f"{cpu_temp:.1f}°C")
            
            # 3. 更新今日统计
            today_summary = self.db.query_today_summary()
            
            self.today_motion_label.config(
                text=f"活动次数: {today_summary['total_motion_count']}"
            )
            self.today_max_static_label.config(
                text=f"最长静止: {today_summary['max_static_duration']:.0f}秒"
            )
            self.today_alarm_label.config(
                text=f"报警次数: {today_summary['alarm_count']}"
            )
            
            # 4. 更新基线状态
            baseline_data = self.analyzer.get_baseline_data()
            self.baseline_status_label.config(
                text=f"{baseline_data['data_days']}天历史数据\n"
                     f"更新时间: {baseline_data['last_update'] or '未更新'}"
            )
            
            # 5. 更新报警状态指示灯
            alarm_status = self.alarm.get_status()
            current_level = alarm_status['level']
            alarm_reason = alarm_status['reason']
            
            # 重置所有灯为灰色
            for light_id in self.alarm_lights:
                self.alarm_canvas.itemconfig(light_id, fill=self.COLOR_OFF)
            
            # 点亮对应等级的灯
            if current_level == 1:
                self.alarm_canvas.itemconfig(self.alarm_lights[0], fill=self.COLOR_LEVEL_1)
            elif current_level == 2:
                self.alarm_canvas.itemconfig(self.alarm_lights[1], fill=self.COLOR_LEVEL_2)
            elif current_level == 3:
                self.alarm_canvas.itemconfig(self.alarm_lights[2], fill=self.COLOR_LEVEL_3)
            
            # 更新报警原因文本
            self.alarm_reason_text.config(state=tk.NORMAL)
            self.alarm_reason_text.delete(1.0, tk.END)
            if current_level > 0:
                self.alarm_reason_text.insert(1.0, f"当前报警原因:\n{alarm_reason}")
            else:
                self.alarm_reason_text.insert(1.0, "系统正常运行，暂无报警")
            self.alarm_reason_text.config(state=tk.DISABLED)
            
            # 6. 更新历史记录表格
            self._update_history_table()
            
        except Exception as e:
            print(f"[界面] 更新显示数据异常: {e}")
    
    
    def _update_history_table(self):
        """
        更新历史报警记录表格
        """
        # 清空现有记录
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # 查询最新10条记录
        alarm_logs = self.db.query_alarm_logs(days=7, limit=10)
        
        for log in alarm_logs:
            # 格式化时间
            time_str = log['datetime'].split()[1][:5]  # 只显示时:分
            date_str = log['datetime'].split()[0][5:]  # 只显示月-日
            display_time = f"{date_str} {time_str}"
            
            # 等级文本
            level_text = {1: "一级", 2: "二级", 3: "三级"}.get(log['alarm_level'], "未知")
            
            # 持续时长
            duration = log['duration_sec']
            if duration >= 3600:
                duration_text = f"{duration/3600:.1f}小时"
            elif duration >= 60:
                duration_text = f"{duration/60:.0f}分钟"
            else:
                duration_text = f"{duration:.0f}秒"
            
            # 状态
            status_text = "已解除" if log['resolved'] else "进行中"
            
            # 插入记录
            self.history_tree.insert(
                "",
                tk.END,
                values=(display_time, level_text, duration_text, status_text)
            )
    
    
    def _schedule_refresh(self):
        """
        使用root.after()实现非阻塞定时刷新
        """
        self._update_display()
        # 递归调用，实现持续刷新
        self.root.after(self.REFRESH_INTERVAL, self._schedule_refresh)
    
    
    def _generate_report(self):
        """
        生成健康报表按钮回调
        """
        try:
            messagebox.showinfo("提示", "正在生成报表，请稍候...")
            
            # 在子线程中生成报表（避免阻塞UI）
            def generate():
                try:
                    output_path = self.report.create_report()
                    self.root.after(0, lambda: messagebox.showinfo(
                        "成功",
                        f"报表生成完成！\n保存路径:\n{output_path}"
                    ))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror(
                        "错误",
                        f"报表生成失败:\n{str(e)}"
                    ))
            
            threading.Thread(target=generate, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("错误", f"操作失败: {e}")
    
    
    def _update_baseline(self):
        """
        更新行为基线按钮回调
        """
        try:
            self.analyzer.update_baseline()
            messagebox.showinfo("成功", "行为基线已更新！")
        except Exception as e:
            messagebox.showerror("错误", f"更新基线失败: {e}")
    
    
    def _test_alarm(self):
        """
        测试报警按钮回调
        """
        try:
            self.alarm.set_alarm_level(3, "测试：手动触发三级报警")
            messagebox.showwarning("测试", "已触发三级报警测试！\n请观察LED和蜂鸣器。")
        except Exception as e:
            messagebox.showerror("错误", f"测试失败: {e}")
    
    
    def _on_closing(self):
        """
        窗口关闭事件处理
        """
        if messagebox.askokcancel("退出", "确定要退出监护系统吗？"):
            print("[界面] 用户请求退出系统")
            self.root.quit()
            self.root.destroy()
    
    
    def run(self):
        """
        启动Tkinter主循环（阻塞）
        """
        print("[界面] 启动Tkinter主窗口...")
        self.root.mainloop()


# ==================== 测试代码 ====================
if __name__ == '__main__':
    """
    独立测试代码（不依赖真实硬件）
    """
    print("=" * 70)
    print("开始测试 DashboardUI 模块（模拟模式）")
    print("=" * 70)
    
    import sys
    sys.path.append('..')
    
    from core.database import DatabaseManager
    
    # 创建模拟对象
    class MockSensor:
        def get_current_status(self):
            import random
            return {
                'pir_state': random.choice([0, 1]),
                'pir_duration': random.uniform(0, 300),
                'temperature': random.uniform(20, 30),
                'humidity': random.uniform(40, 70),
                'cpu_temp': random.uniform(40, 60)
            }
    
    class MockAnalyzer:
        def get_baseline_data(self):
            return {
                'data_days': 7,
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        def update_baseline(self):
            print("[模拟] 更新基线")
    
    class MockAlarm:
        def __init__(self):
            self.level = 0
        
        def get_status(self):
            return {
                'level': self.level,
                'reason': "模拟报警原因",
                'duration': 120
            }
        
        def set_alarm_level(self, level, reason):
            self.level = level
            print(f"[模拟] 设置报警等级: {level}, 原因: {reason}")
    
    class MockReport:
        def create_report(self):
            import time
            time.sleep(2)  # 模拟生成时间
            return "output/reports/test_report.html"
    
    # 创建数据库并插入测试数据
    db = DatabaseManager('data/test_dashboard.db')
    
    # 插入模拟报警记录
    for i in range(10):
        db.insert_alarm_log(
            alarm_level=i % 3 + 1,
            duration_sec=(i + 1) * 60,
            by_button=False
        )
        if i % 2 == 0:
            db.update_alarm_resolved(i + 1)
    
    # 创建界面
    dashboard = DashboardUI(
        sensor_manager=MockSensor(),
        analyzer=MockAnalyzer(),
        alarm_controller=MockAlarm(),
        database_manager=db,
        report_generator=MockReport()
    )
    
    # 启动界面
    dashboard.run()
    
    # 清理
    db.close()
    import os
    if os.path.exists('data/test_dashboard.db'):
        os.remove('data/test_dashboard.db')
    
    print("\n测试完成！")