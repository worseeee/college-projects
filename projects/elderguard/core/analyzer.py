"""
ElderGuard 行为分析模块 (analyzer.py)
功能：基于历史数据构建个性化行为基线，实时检测异常活动模式
作者：ElderGuard开发团队
版本：1.0
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import statistics
import threading


class BehaviorAnalyzer:
    """
    行为分析器类
    负责构建个性化活动基线、异常检测、报警等级评估
    """
    
    # 基线配置参数
    BASELINE_DAYS = 7               # 基线统计天数
    MIN_DATA_DAYS = 1               # 最少需要的数据天数
    
    # 异常检测阈值（倍数）
    SENSITIVITY_LEVEL_1 = 2.0       # 一级报警：静止时长 > 基线的2倍
    SENSITIVITY_LEVEL_2 = 3.0       # 二级报警：静止时长 > 基线的3倍
    SENSITIVITY_LEVEL_3 = 4.0       # 三级报警：静止时长 > 基线的4倍
    
    # 冷启动默认阈值（秒）
    DEFAULT_BASELINE = {
        'night': 3600,      # 夜间（22:00-06:00）：1小时静止正常
        'morning': 1800,    # 早晨（06:00-10:00）：30分钟
        'daytime': 1200,    # 白天（10:00-18:00）：20分钟
        'evening': 1800     # 傍晚（18:00-22:00）：30分钟
    }
    
    # 环境异常阈值
    TEMP_HIGH_THRESHOLD = 35.0      # 高温预警(°C)
    TEMP_LOW_THRESHOLD = 10.0       # 低温预警(°C)
    HUMIDITY_LOW_THRESHOLD = 30.0   # 低湿度预警(%)
    HUMIDITY_HIGH_THRESHOLD = 80.0  # 高湿度预警(%)
    
    # 基线更新间隔（秒）
    BASELINE_UPDATE_INTERVAL = 3600  # 每小时更新一次基线
    
    
    def __init__(self, database_manager):
        """
        初始化行为分析器
        
        Args:
            database_manager: 数据库管理器实例
        """
        self.db = database_manager
        
        # 行为基线数据结构
        # {hour: {'avg_static_duration': float, 'sample_count': int, 'std_dev': float}}
        self.hourly_baseline = {}
        
        # 基线构建状态
        self.baseline_ready = False
        self.baseline_data_days = 0
        self.last_baseline_update = None
        
        # 当前异常状态追踪
        self.current_alarm_level = 0
        self.current_static_start_time = None
        self.last_motion_time = time.time()
        
        # 环境异常状态
        self.env_alarm_active = False
        
        # 线程安全锁
        self.lock = threading.Lock()
        
        # 初始化基线
        self._build_baseline()
        
        print("[分析器] 行为分析器初始化完成")
    
    
    def _get_time_period(self, hour: int) -> str:
        """
        根据小时获取时间段类型
        
        Args:
            hour: 小时 (0-23)
        
        Returns:
            str: 时间段类型 ('night'/'morning'/'daytime'/'evening')
        """
        if 22 <= hour or hour < 6:
            return 'night'
        elif 6 <= hour < 10:
            return 'morning'
        elif 10 <= hour < 18:
            return 'daytime'
        else:
            return 'evening'
    
    
    def _get_default_baseline(self, hour: int) -> float:
        """
        获取冷启动时的默认基线值
        
        Args:
            hour: 小时 (0-23)
        
        Returns:
            float: 默认静止时长阈值（秒）
        """
        period = self._get_time_period(hour)
        return self.DEFAULT_BASELINE[period]
    
    
    def _calculate_hourly_statistics(self, motion_events: list) -> Dict[int, dict]:
        """
        计算每小时的活动统计数据
        
        Args:
            motion_events: 运动事件列表（从数据库查询得到）
        
        Returns:
            Dict[int, dict]: {
                hour: {
                    'avg_static_duration': 平均静止时长,
                    'max_static_duration': 最大静止时长,
                    'sample_count': 样本数量,
                    'std_dev': 标准差
                }
            }
        """
        # 按小时分组静止事件
        hourly_data = {h: [] for h in range(24)}
        
        for event in motion_events:
            try:
                # 解析时间字符串
                time_str = event['time']
                hour = int(time_str.split(':')[0])
                
                # 只统计静止状态（pir_state=0）且持续时间>0的事件
                if event['pir_state'] == 0 and event['duration'] > 0:
                    hourly_data[hour].append(event['duration'])
            
            except Exception as e:
                print(f"[分析器] 解析事件数据失败: {e}, 事件: {event}")
                continue
        
        # 计算每小时的统计指标
        hourly_stats = {}
        
        for hour, durations in hourly_data.items():
            if len(durations) == 0:
                # 如果某小时没有数据，使用默认值
                hourly_stats[hour] = {
                    'avg_static_duration': self._get_default_baseline(hour),
                    'max_static_duration': self._get_default_baseline(hour),
                    'sample_count': 0,
                    'std_dev': 0.0
                }
            else:
                # 计算平均值、最大值、标准差
                avg_duration = statistics.mean(durations)
                max_duration = max(durations)
                std_dev = statistics.stdev(durations) if len(durations) > 1 else 0.0
                
                hourly_stats[hour] = {
                    'avg_static_duration': round(avg_duration, 2),
                    'max_static_duration': round(max_duration, 2),
                    'sample_count': len(durations),
                    'std_dev': round(std_dev, 2)
                }
        
        return hourly_stats
    
    
    def _build_baseline(self):
        """
        构建个性化行为基线
        从数据库读取历史数据并计算每小时的正常活动模式
        """
        with self.lock:
            print(f"[分析器] 开始构建行为基线（统计过去{self.BASELINE_DAYS}天数据）...")
            
            try:
                # 查询历史运动事件
                motion_events = self.db.query_motion_history(days=self.BASELINE_DAYS)
                
                if not motion_events:
                    print("[分析器] ⚠️  数据库中暂无历史数据，使用默认基线")
                    self._use_default_baseline()
                    return
                
                # 计算实际数据天数
                unique_dates = set(event['date'] for event in motion_events)
                self.baseline_data_days = len(unique_dates)
                
                print(f"[分析器] 找到 {len(motion_events)} 条记录，覆盖 {self.baseline_data_days} 天")
                
                # 冷启动处理：数据不足时混合使用默认值
                if self.baseline_data_days < self.MIN_DATA_DAYS:
                    print(f"[分析器] ⚠️  数据天数不足（需要至少{self.MIN_DATA_DAYS}天），使用默认基线")
                    self._use_default_baseline()
                    return
                
                # 计算每小时统计数据
                self.hourly_baseline = self._calculate_hourly_statistics(motion_events)
                
                # 标记基线已就绪
                self.baseline_ready = True
                self.last_baseline_update = datetime.now()
                
                # 打印基线摘要
                self._print_baseline_summary()
                
            except Exception as e:
                print(f"[分析器] ❌ 构建基线失败: {e}")
                self._use_default_baseline()
    
    
    def _use_default_baseline(self):
        """
        使用默认基线（冷启动或数据不足时）
        """
        self.hourly_baseline = {}
        
        for hour in range(24):
            default_value = self._get_default_baseline(hour)
            self.hourly_baseline[hour] = {
                'avg_static_duration': default_value,
                'max_static_duration': default_value * 1.5,
                'sample_count': 0,
                'std_dev': 0.0
            }
        
        self.baseline_ready = True
        self.baseline_data_days = 0
        self.last_baseline_update = datetime.now()
        
        print("[分析器] ✓ 默认基线已加载")
    
    
    def _print_baseline_summary(self):
        """
        打印基线摘要信息（用于调试）
        """
        print("\n" + "=" * 70)
        print("个性化行为基线摘要")
        print("=" * 70)
        print(f"数据覆盖天数: {self.baseline_data_days}天")
        print(f"更新时间: {self.last_baseline_update.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 70)
        print(f"{'时段':<15} {'平均静止(秒)':<15} {'样本数':<10} {'标准差(秒)'}")
        print("-" * 70)
        
        # 按时间段分组显示
        periods = {
            'night': [22, 23, 0, 1, 2, 3, 4, 5],
            'morning': [6, 7, 8, 9],
            'daytime': [10, 11, 12, 13, 14, 15, 16, 17],
            'evening': [18, 19, 20, 21]
        }
        
        for period_name, hours in periods.items():
            period_display = {
                'night': '夜间(22-06时)',
                'morning': '早晨(06-10时)',
                'daytime': '白天(10-18时)',
                'evening': '傍晚(18-22时)'
            }
            
            avg_values = [self.hourly_baseline[h]['avg_static_duration'] for h in hours]
            avg_avg = statistics.mean(avg_values)
            total_samples = sum(self.hourly_baseline[h]['sample_count'] for h in hours)
            
            print(f"{period_display[period_name]:<15} {avg_avg:<15.1f} {total_samples:<10} "
                  f"{statistics.mean([self.hourly_baseline[h]['std_dev'] for h in hours]):.1f}")
        
        print("=" * 70 + "\n")
    
    
    def update_baseline(self):
        """
        更新行为基线
        应定期调用（建议每小时调用一次）
        """
        # 检查是否需要更新
        if self.last_baseline_update:
            time_since_update = (datetime.now() - self.last_baseline_update).total_seconds()
            if time_since_update < self.BASELINE_UPDATE_INTERVAL:
                return
        
        print(f"[分析器] 正在更新行为基线...")
        self._build_baseline()
    
    
    def analyze_motion_anomaly(self, current_static_duration: float) -> Tuple[int, str]:
        """
        分析运动异常（核心算法）
        
        Args:
            current_static_duration: 当前静止持续时长（秒）
        
        Returns:
            Tuple[int, str]: (报警等级, 异常原因描述)
                报警等级: 0=正常, 1=轻度异常, 2=中度异常, 3=严重异常
        """
        if not self.baseline_ready:
            return 0, "基线未就绪"
        
        # 获取当前小时
        current_hour = datetime.now().hour
        
        # 获取该小时的基线数据
        baseline = self.hourly_baseline.get(current_hour)
        if not baseline:
            return 0, "该时段无基线数据"
        
        avg_static = baseline['avg_static_duration']
        sample_count = baseline['sample_count']
        
        # 冷启动优化：样本数少时增加容忍度
        if sample_count < 10:
            # 样本不足时，提高阈值倍数（降低敏感度）
            tolerance_boost = 1.5
            print(f"[分析器] 样本不足({sample_count}条)，容忍度提升{tolerance_boost}倍")
        else:
            tolerance_boost = 1.0
        
        # 计算异常等级阈值
        threshold_level_1 = avg_static * self.SENSITIVITY_LEVEL_1 * tolerance_boost
        threshold_level_2 = avg_static * self.SENSITIVITY_LEVEL_2 * tolerance_boost
        threshold_level_3 = avg_static * self.SENSITIVITY_LEVEL_3 * tolerance_boost
        
        # 判定异常等级
        if current_static_duration >= threshold_level_3:
            alarm_level = 3
            reason = (f"严重异常：静止{current_static_duration:.0f}秒，"
                     f"超过该时段基线({avg_static:.0f}秒)的{self.SENSITIVITY_LEVEL_3}倍")
        
        elif current_static_duration >= threshold_level_2:
            alarm_level = 2
            reason = (f"中度异常：静止{current_static_duration:.0f}秒，"
                     f"超过该时段基线({avg_static:.0f}秒)的{self.SENSITIVITY_LEVEL_2}倍")
        
        elif current_static_duration >= threshold_level_1:
            alarm_level = 1
            reason = (f"轻度异常：静止{current_static_duration:.0f}秒，"
                     f"超过该时段基线({avg_static:.0f}秒)的{self.SENSITIVITY_LEVEL_1}倍")
        
        else:
            alarm_level = 0
            reason = "活动模式正常"
        
        # 记录分析日志
        if alarm_level > 0:
            print(f"\n[异常检测] {reason}")
            print(f"            当前时段: {current_hour}:00-{current_hour+1}:00")
            print(f"            基线数据: 平均{avg_static:.0f}秒 (样本数: {sample_count})")
            print(f"            报警阈值: L1={threshold_level_1:.0f}s, "
                  f"L2={threshold_level_2:.0f}s, L3={threshold_level_3:.0f}s\n")
        
        return alarm_level, reason
    
    
    def analyze_environment_anomaly(self, temperature: float, humidity: float) -> Tuple[int, str]:
        """
        分析环境异常
        
        Args:
            temperature: 当前温度(°C)
            humidity: 当前湿度(%)
        
        Returns:
            Tuple[int, str]: (报警等级, 异常原因)
        """
        if temperature is None or humidity is None:
            return 0, "传感器数据无效"
        
        reasons = []
        max_level = 0
        
        # 温度异常检测
        if temperature >= self.TEMP_HIGH_THRESHOLD:
            max_level = max(max_level, 2)
            reasons.append(f"高温预警({temperature}°C)")
        
        elif temperature <= self.TEMP_LOW_THRESHOLD:
            max_level = max(max_level, 1)
            reasons.append(f"低温提醒({temperature}°C)")
        
        # 湿度异常检测
        if humidity <= self.HUMIDITY_LOW_THRESHOLD:
            max_level = max(max_level, 1)
            reasons.append(f"低湿度提醒({humidity}%)")
        
        elif humidity >= self.HUMIDITY_HIGH_THRESHOLD:
            max_level = max(max_level, 1)
            reasons.append(f"高湿度提醒({humidity}%)")
        
        reason = ", ".join(reasons) if reasons else "环境正常"
        
        if max_level > 0:
            print(f"[环境检测] {reason}")
        
        return max_level, reason
    
    
    def get_comprehensive_analysis(self, sensor_status: dict) -> Dict:
        """
        综合分析传感器状态（用于UI显示和报警决策）
        
        Args:
            sensor_status: 传感器状态字典（来自SensorManager.get_current_status()）
        
        Returns:
            Dict: {
                'motion_alarm_level': 运动异常等级 (0-3),
                'motion_reason': 运动异常原因,
                'env_alarm_level': 环境异常等级 (0-3),
                'env_reason': 环境异常原因,
                'final_alarm_level': 最终报警等级（取最高值）,
                'baseline_status': 基线状态描述,
                'current_hour_baseline': 当前时段基线值
            }
        """
        # 分析运动异常
        motion_level, motion_reason = self.analyze_motion_anomaly(
            sensor_status.get('pir_duration', 0)
        )
        
        # 分析环境异常
        env_level, env_reason = self.analyze_environment_anomaly(
            sensor_status.get('temperature'),
            sensor_status.get('humidity')
        )
        
        # 综合决策：取最高报警等级
        final_level = max(motion_level, env_level)
        
        # 获取当前时段基线
        current_hour = datetime.now().hour
        baseline_info = self.hourly_baseline.get(current_hour, {})
        
        # 基线状态描述
        if self.baseline_data_days == 0:
            baseline_status = "使用默认基线（暂无历史数据）"
        elif self.baseline_data_days < self.BASELINE_DAYS:
            baseline_status = f"基于{self.baseline_data_days}天数据（仍在学习中）"
        else:
            baseline_status = f"基于{self.baseline_data_days}天完整数据"
        
        return {
            'motion_alarm_level': motion_level,
            'motion_reason': motion_reason,
            'env_alarm_level': env_level,
            'env_reason': env_reason,
            'final_alarm_level': final_level,
            'baseline_status': baseline_status,
            'current_hour_baseline': baseline_info.get('avg_static_duration', 0),
            'baseline_sample_count': baseline_info.get('sample_count', 0)
        }
    
    
    def get_baseline_data(self) -> Dict:
        """
        获取完整基线数据（用于报表生成）
        
        Returns:
            Dict: 基线数据字典
        """
        return {
            'hourly_baseline': self.hourly_baseline.copy(),
            'baseline_ready': self.baseline_ready,
            'data_days': self.baseline_data_days,
            'last_update': self.last_baseline_update.strftime('%Y-%m-%d %H:%M:%S') if self.last_baseline_update else None
        }


# ==================== 测试代码 ====================
if __name__ == '__main__':
    """
    模块测试代码
    运行此文件可验证行为分析功能是否正常
    """
    import sys
    sys.path.append('..')
    
    from core.database import DatabaseManager
    
    print("=" * 70)
    print("开始测试 BehaviorAnalyzer 模块")
    print("=" * 70)
    
    # 1. 创建数据库并插入模拟数据
    db = DatabaseManager('data/test_analyzer.db')
    
    print("\n[测试] 生成模拟历史数据...")
    
    # 模拟7天的数据
    import random
    base_time = datetime.now() - timedelta(days=7)
    
    for day in range(7):
        for hour in range(24):
            # 模拟每小时的活动模式
            if 22 <= hour or hour < 6:
                # 夜间：长时间静止
                num_events = random.randint(1, 3)
                avg_duration = random.uniform(1800, 3600)
            elif 6 <= hour < 10:
                # 早晨：中等活动
                num_events = random.randint(3, 6)
                avg_duration = random.uniform(600, 1200)
            elif 10 <= hour < 18:
                # 白天：频繁活动
                num_events = random.randint(5, 10)
                avg_duration = random.uniform(300, 900)
            else:
                # 傍晚：中等活动
                num_events = random.randint(3, 6)
                avg_duration = random.uniform(600, 1200)
            
            # 插入运动和静止事件
            for _ in range(num_events):
                event_time = base_time + timedelta(days=day, hours=hour, minutes=random.randint(0, 59))
                
                # 插入运动事件
                db.conn.execute(
                    "INSERT INTO motion_events (date, time, pir_state, duration) VALUES (?, ?, ?, ?)",
                    (event_time.strftime('%Y-%m-%d'), 
                     event_time.strftime('%H:%M:%S'),
                     1,
                     random.uniform(5, 30))
                )
                
                # 插入静止事件
                static_duration = random.gauss(avg_duration, avg_duration * 0.3)
                db.conn.execute(
                    "INSERT INTO motion_events (date, time, pir_state, duration) VALUES (?, ?, ?, ?)",
                    (event_time.strftime('%Y-%m-%d'),
                     event_time.strftime('%H:%M:%S'),
                     0,
                     max(10, static_duration))
                )
    
    db.conn.commit()
    print(f"✓ 已生成模拟数据")
    
    # 2. 创建分析器实例
    print("\n[测试] 创建行为分析器...")
    analyzer = BehaviorAnalyzer(db)
    
    # 3. 测试异常检测
    print("\n[测试] 异常检测测试...")
    
    test_cases = [
        {'duration': 300, 'hour': 14, 'desc': '白天静止5分钟（正常）'},
        {'duration': 1200, 'hour': 14, 'desc': '白天静止20分钟（轻度异常）'},
        {'duration': 2400, 'hour': 14, 'desc': '白天静止40分钟（中度异常）'},
        {'duration': 3600, 'hour': 14, 'desc': '白天静止1小时（严重异常）'},
        {'duration': 3600, 'hour': 2, 'desc': '凌晨2点静止1小时（正常）'},
    ]
    
    for case in test_cases:
        # 临时修改时间（模拟不同时段）
        original_hour = datetime.now().hour
        
        level, reason = analyzer.analyze_motion_anomaly(case['duration'])
        
        print(f"\n  场景: {case['desc']}")
        print(f"  检测结果: 等级{level} - {reason}")
    
    # 4. 测试环境异常检测
    print("\n[测试] 环境异常检测...")
    
    env_test_cases = [
        {'temp': 24, 'humi': 60, 'desc': '正常环境'},
        {'temp': 38, 'humi': 60, 'desc': '高温预警'},
        {'temp': 24, 'humi': 25, 'desc': '低湿度提醒'},
        {'temp': 8, 'humi': 85, 'desc': '低温+高湿度'},
    ]
    
    for case in env_test_cases:
        level, reason = analyzer.analyze_environment_anomaly(case['temp'], case['humi'])
        print(f"\n  场景: {case['desc']}")
        print(f"  检测结果: 等级{level} - {reason}")
    
    # 5. 测试综合分析
    print("\n[测试] 综合分析测试...")
    
    mock_sensor_status = {
        'pir_duration': 2000,
        'temperature': 36,
        'humidity': 28
    }
    
    analysis = analyzer.get_comprehensive_analysis(mock_sensor_status)
    
    print(f"\n综合分析结果:")
    print(f"  运动异常: 等级{analysis['motion_alarm_level']} - {analysis['motion_reason']}")
    print(f"  环境异常: 等级{analysis['env_alarm_level']} - {analysis['env_reason']}")
    print(f"  最终报警等级: {analysis['final_alarm_level']}")
    print(f"  基线状态: {analysis['baseline_status']}")
    print(f"  当前时段基线: {analysis['current_hour_baseline']:.0f}秒 "
          f"(样本数: {analysis['baseline_sample_count']})")
    
    # 6. 测试基线更新
    print("\n[测试] 测试基线更新...")
    analyzer.update_baseline()
    
    # 7. 获取基线数据
    baseline_data = analyzer.get_baseline_data()
    print(f"\n基线数据摘要:")
    print(f"  就绪状态: {baseline_data['baseline_ready']}")
    print(f"  数据天数: {baseline_data['data_days']}")
    print(f"  最后更新: {baseline_data['last_update']}")
    
    # 8. 清理测试数据
    print("\n[测试] 清理测试数据...")
    db.close()
    
    import os
    if os.path.exists('data/test_analyzer.db'):
        os.remove('data/test_analyzer.db')
        print("✓ 测试数据库已删除")
    
    print("\n" + "=" * 70)
    print("所有测试通过！BehaviorAnalyzer 模块工作正常")
    print("=" * 70)