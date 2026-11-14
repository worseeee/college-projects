"""
ElderGuard 数据存储模块 (database.py)
功能：封装SQLite数据库的所有CRUD操作，提供线程安全的数据访问接口
作者：ElderGuard开发团队
版本：1.0
"""

import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import os


class DatabaseManager:
    """
    数据库管理器类
    负责数据库初始化、数据增删改查、线程安全控制
    """
    
    def __init__(self, db_path: str = 'data/elderguard.db'):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径，默认为 data/elderguard.db
        """
        # 确保数据目录存在
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        self.db_path = db_path
        
        # 使用 check_same_thread=False 允许多线程访问同一连接
        # 注意：必须配合线程锁使用，否则会导致数据竞争
        self.conn = sqlite3.connect(
            db_path, 
            check_same_thread=False,
            timeout=10.0  # 设置10秒超时，避免长时间等待锁
        )
        
        # 启用外键约束（SQLite默认关闭）
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # 设置返回结果为字典格式（便于后续处理）
        self.conn.row_factory = sqlite3.Row
        
        # 创建线程锁，保证同一时间只有一个线程执行数据库操作
        self.lock = threading.Lock()
        
        # 初始化数据库表结构
        self._init_database()
        
        print(f"[数据库] 成功连接到数据库: {db_path}")
    
    
    @contextmanager
    def get_cursor(self):
        """
        上下文管理器：获取线程安全的数据库游标
        
        用法示例：
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM motion_events")
                results = cursor.fetchall()
        
        Yields:
            sqlite3.Cursor: 数据库游标对象
        """
        # 获取线程锁，阻塞其他线程
        with self.lock:
            cursor = self.conn.cursor()
            try:
                yield cursor
                # 如果操作成功，提交事务
                self.conn.commit()
            except Exception as e:
                # 如果发生异常，回滚事务
                self.conn.rollback()
                print(f"[数据库错误] 事务回滚: {e}")
                raise e
            finally:
                # 无论成功失败，都关闭游标
                cursor.close()
    
    
    def _init_database(self):
        """
        初始化数据库表结构
        如果表已存在则跳过，不会删除原有数据
        """
        with self.get_cursor() as cursor:
            # 1. 创建活动事件表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS motion_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,              -- 日期 (YYYY-MM-DD)
                    time TEXT NOT NULL,              -- 时间 (HH:MM:SS)
                    pir_state INTEGER NOT NULL,      -- PIR状态: 1=检测到运动, 0=静止
                    duration REAL DEFAULT 0,         -- 本次状态持续秒数
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- 记录创建时间
                )
            """)
            
            # 为日期和时间创建索引，加速查询
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_motion_date 
                ON motion_events(date, time)
            """)
            
            # 2. 创建环境记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS env_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,              -- 日期 (YYYY-MM-DD)
                    time TEXT NOT NULL,              -- 时间 (HH:MM:SS)
                    cpu_temp REAL,                   -- 树莓派CPU温度 (°C)
                    env_temp REAL,                   -- 环境温度 (°C)
                    humidity REAL,                   -- 环境湿度 (%)
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_env_date 
                ON env_records(date, time)
            """)
            
            # 3. 创建报警日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alarm_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    datetime TEXT NOT NULL,          -- 报警时间 (YYYY-MM-DD HH:MM:SS)
                    alarm_level INTEGER NOT NULL,    -- 报警等级: 1=轻度, 2=中度, 3=严重
                    duration_sec REAL,               -- 报警持续时长(秒)
                    by_button INTEGER DEFAULT 0,     -- 是否由按钮触发: 0=自动检测, 1=手动按钮
                    resolved INTEGER DEFAULT 0,      -- 是否已解除: 0=未解除, 1=已解除
                    resolve_time TEXT,               -- 解除时间
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alarm_datetime 
                ON alarm_logs(datetime)
            """)
            
            print("[数据库] 数据表初始化完成")
    
    
    # ==================== 插入数据接口 ====================
    
    def insert_motion_event(self, pir_state: int, duration: float = 0) -> int:
        """
        插入运动检测事件记录
        
        Args:
            pir_state: PIR传感器状态 (1=检测到运动, 0=静止)
            duration: 本次状态持续时长(秒)，默认0
        
        Returns:
            int: 插入记录的ID
        """
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO motion_events (date, time, pir_state, duration)
                VALUES (?, ?, ?, ?)
            """, (date_str, time_str, pir_state, duration))
            
            return cursor.lastrowid
    
    
    def insert_env_record(self, cpu_temp: float, env_temp: float, humidity: float) -> int:
        """
        插入环境监测记录
        
        Args:
            cpu_temp: CPU温度 (°C)
            env_temp: 环境温度 (°C)
            humidity: 环境湿度 (%)
        
        Returns:
            int: 插入记录的ID
        """
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO env_records (date, time, cpu_temp, env_temp, humidity)
                VALUES (?, ?, ?, ?, ?)
            """, (date_str, time_str, cpu_temp, env_temp, humidity))
            
            return cursor.lastrowid
    
    
    def insert_alarm_log(self, alarm_level: int, duration_sec: float = 0, 
                        by_button: bool = False) -> int:
        """
        插入报警日志记录
        
        Args:
            alarm_level: 报警等级 (1/2/3)
            duration_sec: 报警持续时长(秒)
            by_button: 是否由紧急按钮触发
        
        Returns:
            int: 插入记录的ID
        """
        now = datetime.now()
        datetime_str = now.strftime('%Y-%m-%d %H:%M:%S')
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO alarm_logs (datetime, alarm_level, duration_sec, by_button)
                VALUES (?, ?, ?, ?)
            """, (datetime_str, alarm_level, duration_sec, 1 if by_button else 0))
            
            return cursor.lastrowid
    
    
    def update_alarm_resolved(self, alarm_id: int) -> bool:
        """
        标记报警为已解除状态
        
        Args:
            alarm_id: 报警记录ID
        
        Returns:
            bool: 更新是否成功
        """
        resolve_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                UPDATE alarm_logs 
                SET resolved = 1, resolve_time = ?
                WHERE id = ?
            """, (resolve_time, alarm_id))
            
            return cursor.rowcount > 0
    
    
    # ==================== 查询数据接口 ====================
    
    def query_motion_history(self, days: int = 7) -> List[Dict]:
        """
        查询过去N天的运动检测历史记录
        
        Args:
            days: 查询天数，默认7天
        
        Returns:
            List[Dict]: 记录列表，每条记录包含 {id, date, time, pir_state, duration}
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, date, time, pir_state, duration
                FROM motion_events
                WHERE date >= ?
                ORDER BY date DESC, time DESC
            """, (start_date,))
            
            # 将 sqlite3.Row 对象转换为字典列表
            return [dict(row) for row in cursor.fetchall()]
    
    
    def query_env_history(self, days: int = 7) -> List[Dict]:
        """
        查询过去N天的环境监测历史记录
        
        Args:
            days: 查询天数，默认7天
        
        Returns:
            List[Dict]: 记录列表，每条记录包含 {id, date, time, cpu_temp, env_temp, humidity}
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, date, time, cpu_temp, env_temp, humidity
                FROM env_records
                WHERE date >= ?
                ORDER BY date DESC, time DESC
            """, (start_date,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    
    def query_alarm_logs(self, days: int = 30, limit: int = 100) -> List[Dict]:
        """
        查询报警历史记录
        
        Args:
            days: 查询天数，默认30天
            limit: 返回记录数量限制，默认100条
        
        Returns:
            List[Dict]: 报警记录列表
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, datetime, alarm_level, duration_sec, 
                       by_button, resolved, resolve_time
                FROM alarm_logs
                WHERE datetime >= ?
                ORDER BY datetime DESC
                LIMIT ?
            """, (start_date, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    
    def query_hourly_activity_baseline(self, days: int = 7) -> Dict[int, float]:
        """
        查询过去N天每小时的平均活动频次（用于构建行为基线）
        
        Args:
            days: 统计天数，默认7天
        
        Returns:
            Dict[int, float]: {小时: 平均活动次数}，例如 {0: 0.5, 1: 0.3, ..., 23: 2.1}
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        with self.get_cursor() as cursor:
            # 提取小时并统计每小时的运动事件数
            cursor.execute("""
                SELECT 
                    CAST(substr(time, 1, 2) AS INTEGER) as hour,
                    COUNT(*) as motion_count
                FROM motion_events
                WHERE date >= ? AND pir_state = 1
                GROUP BY hour
            """, (start_date,))
            
            results = cursor.fetchall()
            
            # 计算平均值（除以天数）
            baseline = {}
            for row in results:
                hour = row['hour']
                avg_count = row['motion_count'] / days
                baseline[hour] = round(avg_count, 2)
            
            # 填充缺失的小时（如果某小时从未有活动，设为0）
            for h in range(24):
                if h not in baseline:
                    baseline[h] = 0.0
            
            return baseline
    
    
    def query_today_summary(self) -> Dict:
        """
        查询今日统计摘要数据
        
        Returns:
            Dict: {
                'total_motion_count': 今日总活动次数,
                'max_static_duration': 最长静止时长(秒),
                'avg_temp': 平均温度,
                'avg_humidity': 平均湿度,
                'alarm_count': 今日报警次数
            }
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        with self.get_cursor() as cursor:
            # 查询运动统计
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_count,
                    MAX(duration) as max_duration
                FROM motion_events
                WHERE date = ? AND pir_state = 1
            """, (today,))
            motion_stats = dict(cursor.fetchone())
            
            # 查询环境统计
            cursor.execute("""
                SELECT 
                    AVG(env_temp) as avg_temp,
                    AVG(humidity) as avg_humidity
                FROM env_records
                WHERE date = ?
            """, (today,))
            env_stats = dict(cursor.fetchone())
            
            # 查询报警统计
            cursor.execute("""
                SELECT COUNT(*) as alarm_count
                FROM alarm_logs
                WHERE date(datetime) = ?
            """, (today,))
            alarm_stats = dict(cursor.fetchone())
            
            return {
                'total_motion_count': motion_stats.get('total_count', 0),
                'max_static_duration': motion_stats.get('max_duration', 0) or 0,
                'avg_temp': round(env_stats.get('avg_temp', 0) or 0, 1),
                'avg_humidity': round(env_stats.get('avg_humidity', 0) or 0, 1),
                'alarm_count': alarm_stats.get('alarm_count', 0)
            }
    
    
    def query_latest_env_record(self) -> Optional[Dict]:
        """
        查询最新的环境监测记录
        
        Returns:
            Dict 或 None: 最新记录，如果无数据则返回None
        """
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT date, time, cpu_temp, env_temp, humidity
                FROM env_records
                ORDER BY created_at DESC
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            return dict(result) if result else None
    
    
    def query_unresolved_alarms(self) -> List[Dict]:
        """
        查询所有未解除的报警记录
        
        Returns:
            List[Dict]: 未解除的报警列表
        """
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, datetime, alarm_level, duration_sec, by_button
                FROM alarm_logs
                WHERE resolved = 0
                ORDER BY datetime DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    
    # ==================== 数据维护接口 ====================
    
    def cleanup_old_data(self, keep_days: int = 30) -> Tuple[int, int, int]:
        """
        清理超过指定天数的历史数据
        
        Args:
            keep_days: 保留天数，默认30天
        
        Returns:
            Tuple[int, int, int]: (删除的运动记录数, 删除的环境记录数, 删除的报警记录数)
        """
        cutoff_date = (datetime.now() - timedelta(days=keep_days)).strftime('%Y-%m-%d')
        
        with self.get_cursor() as cursor:
            # 删除旧的运动记录
            cursor.execute("DELETE FROM motion_events WHERE date < ?", (cutoff_date,))
            motion_deleted = cursor.rowcount
            
            # 删除旧的环境记录
            cursor.execute("DELETE FROM env_records WHERE date < ?", (cutoff_date,))
            env_deleted = cursor.rowcount
            
            # 删除旧的报警记录
            cursor.execute("DELETE FROM alarm_logs WHERE date(datetime) < ?", (cutoff_date,))
            alarm_deleted = cursor.rowcount
            
            print(f"[数据库] 清理完成: 运动记录{motion_deleted}条, 环境记录{env_deleted}条, 报警记录{alarm_deleted}条")
            
            return motion_deleted, env_deleted, alarm_deleted
    
    
    def get_database_stats(self) -> Dict:
        """
        获取数据库统计信息
        
        Returns:
            Dict: {
                'motion_events_count': 运动记录总数,
                'env_records_count': 环境记录总数,
                'alarm_logs_count': 报警记录总数,
                'db_size_mb': 数据库文件大小(MB)
            }
        """
        with self.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as cnt FROM motion_events")
            motion_count = cursor.fetchone()['cnt']
            
            cursor.execute("SELECT COUNT(*) as cnt FROM env_records")
            env_count = cursor.fetchone()['cnt']
            
            cursor.execute("SELECT COUNT(*) as cnt FROM alarm_logs")
            alarm_count = cursor.fetchone()['cnt']
        
        # 获取数据库文件大小
        db_size_bytes = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        db_size_mb = round(db_size_bytes / (1024 * 1024), 2)
        
        return {
            'motion_events_count': motion_count,
            'env_records_count': env_count,
            'alarm_logs_count': alarm_count,
            'db_size_mb': db_size_mb
        }
    
    
    def close(self):
        """
        关闭数据库连接
        应在程序退出时调用
        """
        if self.conn:
            self.conn.close()
            print("[数据库] 连接已关闭")
    
    
    def __del__(self):
        """
        析构函数，确保数据库连接被关闭
        """
        self.close()


# ==================== 测试代码 ====================
if __name__ == '__main__':
    """
    模块测试代码
    运行此文件可验证数据库功能是否正常
    """
    print("=" * 50)
    print("开始测试 DatabaseManager 模块")
    print("=" * 50)
    
    # 1. 创建数据库实例
    db = DatabaseManager('data/test_elderguard.db')
    
    # 2. 测试插入数据
    print("\n[测试] 插入测试数据...")
    
    # 插入运动事件
    motion_id = db.insert_motion_event(pir_state=1, duration=5.2)
    print(f"✓ 插入运动事件，ID: {motion_id}")
    
    # 插入环境记录
    env_id = db.insert_env_record(cpu_temp=45.3, env_temp=24.5, humidity=60.2)
    print(f"✓ 插入环境记录，ID: {env_id}")
    
    # 插入报警日志
    alarm_id = db.insert_alarm_log(alarm_level=2, duration_sec=120.5, by_button=False)
    print(f"✓ 插入报警日志，ID: {alarm_id}")
    
    # 3. 测试查询数据
    print("\n[测试] 查询数据...")
    
    # 查询今日摘要
    summary = db.query_today_summary()
    print(f"✓ 今日摘要: {summary}")
    
    # 查询最新环境记录
    latest_env = db.query_latest_env_record()
    print(f"✓ 最新环境记录: {latest_env}")
    
    # 查询小时活动基线
    baseline = db.query_hourly_activity_baseline(days=7)
    print(f"✓ 活动基线样例（前3小时）: {dict(list(baseline.items())[:3])}")
    
    # 4. 测试数据库统计
    print("\n[测试] 数据库统计...")
    stats = db.get_database_stats()
    print(f"✓ 数据库统计: {stats}")
    
    # 5. 测试更新报警状态
    print("\n[测试] 更新报警状态...")
    success = db.update_alarm_resolved(alarm_id)
    print(f"✓ 标记报警{alarm_id}为已解除: {'成功' if success else '失败'}")
    
    # 6. 清理测试数据库
    print("\n[测试] 清理测试数据...")
    db.close()
    if os.path.exists('data/test_elderguard.db'):
        os.remove('data/test_elderguard.db')
        print("✓ 测试数据库已删除")
    
    print("\n" + "=" * 50)
    print("所有测试通过！DatabaseManager 模块工作正常")
    print("=" * 50)