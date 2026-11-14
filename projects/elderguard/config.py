"""
ElderGuard 系统配置文件 (config.py)
功能：集中管理所有可配置参数
"""

# ==================== 数据库配置 ====================
DATABASE_PATH = 'data/elderguard.db'
DATA_RETENTION_DAYS = 30  # 数据保留天数


# ==================== GPIO引脚配置 ====================
# 使用BOARD物理编码
GPIO_PIR_PIN = 11         # PIR人体红外传感器
GPIO_DHT_PIN = 22         # DHT11温湿度传感器
GPIO_BUTTON_PIN = 18      # 紧急求助按钮
GPIO_LED_PIN = 16         # 状态指示LED
GPIO_BUZZER_PIN = 32      # 蜂鸣器


# ==================== 传感器采集配置 ====================
PIR_SAMPLE_INTERVAL = 1.0       # PIR采集间隔（秒）
DHT_SAMPLE_INTERVAL = 30.0      # DHT11采集间隔（秒）
DHT_MAX_RETRIES = 5             # DHT11最大重试次数
DHT_RETRY_DELAY = 2.0           # DHT11重试间隔（秒）

# DHT11数据合法性范围
TEMP_MIN = 0.0
TEMP_MAX = 50.0
HUMIDITY_MIN = 20.0
HUMIDITY_MAX = 95.0


# ==================== 行为分析配置 ====================
BASELINE_DAYS = 7               # 基线统计天数
MIN_DATA_DAYS = 1               # 最少需要的数据天数

# 异常检测阈值倍数
SENSITIVITY_LEVEL_1 = 2.0       # 一级报警阈值
SENSITIVITY_LEVEL_2 = 3.0       # 二级报警阈值
SENSITIVITY_LEVEL_3 = 4.0       # 三级报警阈值

# 冷启动默认基线（秒）
DEFAULT_BASELINE = {
    'night': 3600,      # 夜间（22:00-06:00）
    'morning': 1800,    # 早晨（06:00-10:00）
    'daytime': 1200,    # 白天（10:00-18:00）
    'evening': 1800     # 傍晚（18:00-22:00）
}

# 环境异常阈值
TEMP_HIGH_THRESHOLD = 35.0      # 高温预警(°C)
TEMP_LOW_THRESHOLD = 10.0       # 低温预警(°C)
HUMIDITY_LOW_THRESHOLD = 30.0   # 低湿度预警(%)
HUMIDITY_HIGH_THRESHOLD = 80.0  # 高湿度预警(%)


# ==================== 报警控制配置 ====================
# LED PWM配置
LED_PWM_FREQUENCY = 1000        # PWM频率（Hz）
LED_BLINK_FREQUENCY = 1.0       # 闪烁频率（Hz）
LED_DUTY_CYCLE = 50             # 占空比（%）

# 蜂鸣器PWM配置
BUZZER_FREQUENCY_LOW = 2000     # 低音调（Hz）
BUZZER_FREQUENCY_HIGH = 3000    # 高音调（Hz）
BUZZER_DUTY_CYCLE = 50          # 占空比（%）

# 蜂鸣器间歇配置
BUZZER_BEEP_ON_TIME = 0.2       # 鸣叫持续时间（秒）
BUZZER_BEEP_OFF_TIME = 0.3      # 静默持续时间（秒）

# 报警升级配置
AUTO_ESCALATE_INTERVAL = 300    # 自动升级间隔（秒）

# 远程通知配置
WEBHOOK_URL = None              # Webhook地址（企业微信/飞书）
WEBHOOK_TIMEOUT = 5             # 请求超时时间（秒）
WEBHOOK_RETRY = 2               # 重试次数
NOTIFICATION_COOLDOWN = 300     # 通知冷却时间（秒）


# ==================== 系统运行配置 ====================
ANALYSIS_INTERVAL = 60          # 行为分析间隔（秒）
BASELINE_UPDATE_INTERVAL = 3600 # 基线更新间隔（秒）


# ==================== UI配置 ====================
WINDOW_TITLE = "ElderGuard 独居老人监护系统"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
REFRESH_INTERVAL = 1000         # UI刷新间隔（毫秒）


# ==================== 报表配置 ====================
REPORT_DAYS = 7                 # 报表统计天数
OUTPUT_DIR = "output/reports"   # 报表输出目录