"""
ElderGuard 数据报表生成模块 (report.py)
功能：生成包含环境趋势图、活动热力图、报警统计图的HTML报表
作者：ElderGuard开发团队
版本：1.0
"""

from pyecharts import options as opts
from pyecharts.charts import Line, HeatMap, Bar, Page, Grid
from pyecharts.globals import ThemeType
from datetime import datetime, timedelta
import os


class ReportGenerator:
    """
    健康报表生成器类
    负责从数据库读取数据并生成可视化HTML报表
    """
    
    # 报表配置
    REPORT_DAYS = 7                          # 报表统计天数
    OUTPUT_DIR = "output/reports"            # 报表输出目录
    THEME = ThemeType.LIGHT                  # 图表主题
    
    
    def __init__(self, database_manager):
        """
        初始化报表生成器
        
        Args:
            database_manager: 数据库管理器实例
        """
        self.db = database_manager
        
        # 确保输出目录存在
        if not os.path.exists(self.OUTPUT_DIR):
            os.makedirs(self.OUTPUT_DIR)
        
        print("[报表] 报表生成器初始化完成")
    
    
    def _generate_env_trend_chart(self) -> Line:
        """
        生成环境温湿度趋势图（近7天双轴折线图）
        
        Returns:
            Line: pyecharts折线图对象
        """
        print("[报表] 生成环境趋势图...")
        
        # 查询环境数据
        env_records = self.db.query_env_history(days=self.REPORT_DAYS)
        
        # 数据处理
        timestamps = []
        temperatures = []
        humidities = []
        
        for record in reversed(env_records):  # 反转为时间正序
            timestamp = f"{record['date']} {record['time']}"
            timestamps.append(timestamp)
            temperatures.append(record['env_temp'] if record['env_temp'] else None)
            humidities.append(record['humidity'] if record['humidity'] else None)
        
        # 创建折线图
        line = (
            Line(init_opts=opts.InitOpts(theme=self.THEME, width="1200px", height="400px"))
            .add_xaxis(xaxis_data=timestamps)
            .add_yaxis(
                series_name="温度(°C)",
                y_axis=temperatures,
                is_smooth=True,
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(width=2, color="#ff6b6b"),
                itemstyle_opts=opts.ItemStyleOpts(color="#ff6b6b")
            )
            .add_yaxis(
                series_name="湿度(%)",
                y_axis=humidities,
                is_smooth=True,
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(width=2, color="#4dabf7"),
                itemstyle_opts=opts.ItemStyleOpts(color="#4dabf7"),
                yaxis_index=1  # 使用第二Y轴
            )
            .extend_axis(
                yaxis=opts.AxisOpts(
                    name="湿度(%)",
                    type_="value",
                    min_=0,
                    max_=100,
                    position="right",
                    axislabel_opts=opts.LabelOpts(formatter="{value}%")
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="环境温湿度趋势（近7天）",
                    subtitle=f"数据时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                ),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                xaxis_opts=opts.XaxisOpts(
                    type_="category",
                    boundary_gap=False,
                    axislabel_opts=opts.LabelOpts(rotate=45, interval=len(timestamps)//10)
                ),
                yaxis_opts=opts.AxisOpts(
                    name="温度(°C)",
                    type_="value",
                    axislabel_opts=opts.LabelOpts(formatter="{value}°C")
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(range_start=0, range_end=100),
                    opts.DataZoomOpts(type_="inside")
                ],
                legend_opts=opts.LegendOpts(pos_top="5%")
            )
        )
        
        return line
    
    
    def _generate_activity_heatmap(self) -> HeatMap:
        """
        生成活动热力图（7天×24小时）
        
        Returns:
            HeatMap: pyecharts热力图对象
        """
        print("[报表] 生成活动热力图...")
        
        # 查询运动数据
        motion_events = self.db.query_motion_history(days=self.REPORT_DAYS)
        
        # 构建7天×24小时矩阵
        # 获取最近7天的日期列表
        end_date = datetime.now().date()
        date_list = [(end_date - timedelta(days=i)).strftime('%m-%d') for i in range(6, -1, -1)]
        
        # 初始化计数矩阵
        activity_matrix = {date: {hour: 0 for hour in range(24)} for date in date_list}
        
        # 统计每个时间段的活动次数
        for event in motion_events:
            if event['pir_state'] == 1:  # 只统计运动事件
                event_date = datetime.strptime(event['date'], '%Y-%m-%d').strftime('%m-%d')
                event_hour = int(event['time'].split(':')[0])
                
                if event_date in activity_matrix:
                    activity_matrix[event_date][event_hour] += 1
        
        # 转换为pyecharts需要的数据格式
        # [[小时, 日期, 活动次数], ...]
        heatmap_data = []
        for date in date_list:
            for hour in range(24):
                heatmap_data.append([hour, date, activity_matrix[date][hour]])
        
        # 创建热力图
        heatmap = (
            HeatMap(init_opts=opts.InitOpts(theme=self.THEME, width="1200px", height="500px"))
            .add_xaxis(xaxis_data=[f"{h:02d}:00" for h in range(24)])
            .add_yaxis(
                series_name="活动频次",
                yaxis_data=date_list,
                value=heatmap_data,
                label_opts=opts.LabelOpts(is_show=True, position="inside"),
                itemstyle_opts=opts.ItemStyleOpts(border_color="white", border_width=2)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="每日活动热力图（7天×24小时）",
                    subtitle="颜色深度代表活动频次，可快速识别作息规律"
                ),
                tooltip_opts=opts.TooltipOpts(
                    formatter="{b} {c}:00 活动{value}次"
                ),
                visualmap_opts=opts.VisualMapOpts(
                    min_=0,
                    max_=max([d[2] for d in heatmap_data]) if heatmap_data else 10,
                    is_calculable=True,
                    orient="horizontal",
                    pos_left="center",
                    pos_bottom="5%",
                    range_color=["#f0f9ff", "#0ea5e9", "#1e40af"]  # 蓝色渐变
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    splitarea_opts=opts.SplitAreaOpts(is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
                ),
                yaxis_opts=opts.AxisOpts(
                    type_="category",
                    splitarea_opts=opts.SplitAreaOpts(is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
                )
            )
        )
        
        return heatmap
    
    
    def _generate_alarm_bar_chart(self) -> Bar:
        """
        生成报警统计柱状图（按等级统计）
        
        Returns:
            Bar: pyecharts柱状图对象
        """
        print("[报表] 生成报警统计图...")
        
        # 查询报警记录
        alarm_logs = self.db.query_alarm_logs(days=30, limit=1000)
        
        # 按日期和等级统计
        from collections import defaultdict
        daily_stats = defaultdict(lambda: {1: 0, 2: 0, 3: 0})
        
        for log in alarm_logs:
            date = log['datetime'].split()[0]
            level = log['alarm_level']
            daily_stats[date][level] += 1
        
        # 获取最近30天日期列表
        date_list = [(datetime.now().date() - timedelta(days=i)).strftime('%Y-%m-%d') 
                     for i in range(29, -1, -1)]
        
        # 提取各等级数据
        level_1_data = [daily_stats[date][1] for date in date_list]
        level_2_data = [daily_stats[date][2] for date in date_list]
        level_3_data = [daily_stats[date][3] for date in date_list]
        
        # 创建柱状图
        bar = (
            Bar(init_opts=opts.InitOpts(theme=self.THEME, width="1200px", height="400px"))
            .add_xaxis(xaxis_data=[d[5:] for d in date_list])  # 只显示月-日
            .add_yaxis(
                series_name="一级报警",
                y_axis=level_1_data,
                stack="stack1",
                itemstyle_opts=opts.ItemStyleOpts(color="#ffc107")
            )
            .add_yaxis(
                series_name="二级报警",
                y_axis=level_2_data,
                stack="stack1",
                itemstyle_opts=opts.ItemStyleOpts(color="#fd7e14")
            )
            .add_yaxis(
                series_name="三级报警",
                y_axis=level_3_data,
                stack="stack1",
                itemstyle_opts=opts.ItemStyleOpts(color="#dc3545")
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="报警统计（近30天）",
                    subtitle="堆叠柱状图显示各等级报警分布"
                ),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=45, interval=2)
                ),
                yaxis_opts=opts.AxisOpts(
                    name="报警次数",
                    axislabel_opts=opts.LabelOpts(formatter="{value}次")
                ),
                legend_opts=opts.LegendOpts(pos_top="5%"),
                datazoom_opts=[opts.DataZoomOpts(range_start=70, range_end=100)]
            )
        )
        
        return bar
    
    
    def create_report(self) -> str:
        """
        生成完整的健康报表HTML文件
        
        Returns:
            str: 报表文件路径
        """
        print("\n" + "=" * 70)
        print("开始生成健康报表...")
        print("=" * 70)
        
        try:
            # 生成三个图表
            env_chart = self._generate_env_trend_chart()
            heatmap = self._generate_activity_heatmap()
            alarm_chart = self._generate_alarm_bar_chart()
            
            # 创建Page对象（多图表组合）
            page = Page(layout=Page.SimplePageLayout)
            page.add(
                env_chart,
                heatmap,
                alarm_chart
            )
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"health_report_{timestamp}.html"
            output_path = os.path.join(self.OUTPUT_DIR, filename)
            
            # 渲染HTML
            page.render(output_path)
            
            print(f"\n✓ 报表生成成功！")
            print(f"  文件路径: {output_path}")
            print(f"  包含图表: 环境趋势图、活动热力图、报警统计图")
            print("=" * 70 + "\n")
            
            return output_path
        
        except Exception as e:
            print(f"\n✗ 报表生成失败: {e}")
            raise


# ==================== 测试代码 ====================
if __name__ == '__main__':
    """
    模块测试代码
    """
    print("=" * 70)
    print("开始测试 ReportGenerator 模块")
    print("=" * 70)
    
    import sys
    sys.path.append('..')
    
    from core.database import DatabaseManager
    import random
    
    # 创建数据库并生成模拟数据
    db = DatabaseManager('data/test_report.db')
    
    print("\n[测试] 生成模拟数据...")
    
    # 生成7天的环境数据
    base_time = datetime.now() - timedelta(days=7)
    for day in range(7):
        for hour in range(24):
            for minute in range(0, 60, 30):  # 每小时2条记录
                event_time = base_time + timedelta(days=day, hours=hour, minutes=minute)
                db.conn.execute(
                    "INSERT INTO env_records (date, time, cpu_temp, env_temp, humidity) VALUES (?, ?, ?, ?, ?)",
                    (event_time.strftime('%Y-%m-%d'),
                     event_time.strftime('%H:%M:%S'),
                     random.uniform(40, 60),
                     random.uniform(20, 30),
                     random.uniform(40, 70))
                )
    
    # 生成7天的活动数据
    for day in range(7):
        for hour in range(24):
            # 模拟活动模式：夜间少，白天多
            if 22 <= hour or hour < 6:
                event_count = random.randint(0, 2)
            else:
                event_count = random.randint(3, 15)
            
            for _ in range(event_count):
                event_time = base_time + timedelta(days=day, hours=hour, minutes=random.randint(0, 59))
                db.conn.execute(
                    "INSERT INTO motion_events (date, time, pir_state, duration) VALUES (?, ?, ?, ?)",
                    (event_time.strftime('%Y-%m-%d'),
                     event_time.strftime('%H:%M:%S'),
                     1,
                     random.uniform(5, 30))
                )
    
    # 生成30天的报警记录
    for day in range(30):
        alarm_count = random.randint(0, 5)
        for _ in range(alarm_count):
            alarm_time = base_time + timedelta(days=day, hours=random.randint(0, 23))
            db.insert_alarm_log(
                alarm_level=random.randint(1, 3),
                duration_sec=random.uniform(60, 600),
                by_button=False
            )
    
    db.conn.commit()
    print("✓ 模拟数据生成完成")
    
    # 创建报表生成器
    report_gen = ReportGenerator(db)
    
    # 生成报表
    output_file = report_gen.create_report()
    
    print(f"\n[测试] 请在浏览器中打开: {output_file}")
    
    # 清理
    db.close()
    
    import os
    if os.path.exists('data/test_report.db'):
        os.remove('data/test_report.db')
    
    print("\n测试完成！")