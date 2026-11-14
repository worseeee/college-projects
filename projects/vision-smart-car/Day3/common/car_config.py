# -*- coding: utf-8 -*-
"""
Day1 教学示例：车辆配置
============================================================
这里只放会随着硬件或调试变化的数据。配置模块不初始化 GPIO。
"""

# ==================== 电机引脚（BCM 编号） ====================
PWMA = 18   # 左电机 PWM
AIN1 = 22   # 左电机方向 1
AIN2 = 27   # 左电机方向 2
PWMB = 23   # 右电机 PWM
BIN1 = 25   # 右电机方向 1
BIN2 = 24   # 右电机方向 2

# ==================== 交互引脚 ====================
BTN_PIN = 19   # 启动按键，按下为低电平
LED_G = 5      # 绿灯：等待按键
LED_R = 6      # 红灯：正在运行

# ==================== 电机参数 ====================
PWM_FREQ = 100          # 电机 PWM 频率，单位 Hz
SPEED_DEFAULT = 45      # 默认直行速度，范围 0~100
SPEED_TURN = 55         # 默认转向速度，范围 0~100

# ==================== Day2 红外传感器（BCM 编号） ====================
SENSOR_L = 12           # 左红外数字输出
SENSOR_R = 16           # 右红外数字输出
SENSOR_ACTIVE_LOW = True  # 常见模块遮挡时输出低电平；实测相反时设为 False

# ==================== Day2 Socket 通信 ====================
CAR_HOST = "0.0.0.0"
CAR_PORT = 8888
PC_DEFAULT_HOST = "192.168.137.100"
STATUS_INTERVAL = 1.5
SENSOR_INTERVAL = 0.03
SOCKET_POLL_INTERVAL = 0.05

# 避障动作时长（秒）：现场完成方向测试后可按车速微调。
AVOID_STOP_TIME = 0.20
AVOID_REVERSE_TIME = 0.35
AVOID_TURN_TIME = 0.65
AVOID_BOTH_REVERSE_TIME = 0.55
AVOID_BOTH_TURN_TIME = 0.80
AVOID_SETTLE_TIME = 0.15

# ==================== Day1 / Day2 运动参数 ====================
GEAR_SPEEDS = (0, 20, 40, 60, 80, 100)  # 0 档停车，1~5 档
FIGURE_EIGHT_SPEED = 60
FIGURE_EIGHT_ARC_TIME = 7.8
RECT_SPEED = 45
RECT_STRAIGHT_TIME = 5.5
RECT_TURN_TIME = 2.165

# ==================== PCA9685 云台 ====================
PCA9685_ADDRESS = 0x40
SERVO_FREQ = 50
TILT_CHANNEL = 9
PAN_CHANNEL = 10
SERVO_MIN_US = 1000
SERVO_MAX_US = 2000
SERVO_MIN_ANGLE = 30
SERVO_MAX_ANGLE = 150
TILT_DOWN = 70
TILT_LEVEL = 90
TILT_UP = 110
PAN_LEFT = 45
PAN_CENTER = 90
PAN_RIGHT = 135

