-- ElderGuard 数据库初始化脚本
-- 如果手动创建数据库时使用

-- 活动事件表
CREATE TABLE IF NOT EXISTS motion_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,              -- 日期 (YYYY-MM-DD)
    time TEXT NOT NULL,              -- 时间 (HH:MM:SS)
    pir_state INTEGER NOT NULL,      -- PIR状态: 1=检测到运动, 0=静止
    duration REAL DEFAULT 0,         -- 本次状态持续秒数
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_motion_date ON motion_events(date, time);

-- 环境记录表
CREATE TABLE IF NOT EXISTS env_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    cpu_temp REAL,
    env_temp REAL,
    humidity REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_env_date ON env_records(date, time);

-- 报警日志表
CREATE TABLE IF NOT EXISTS alarm_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime TEXT NOT NULL,
    alarm_level INTEGER NOT NULL,
    duration_sec REAL,
    by_button INTEGER DEFAULT 0,
    resolved INTEGER DEFAULT 0,
    resolve_time TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alarm_datetime ON alarm_logs(datetime);