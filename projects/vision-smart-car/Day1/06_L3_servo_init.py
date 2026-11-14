
# -*- coding: utf-8 -*-
"""Day1 任务 I：云台初始化"""

import time
import Adafruit_PCA9685


# PCA9685 配置
pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(50)

# 舵机通道
TILT_CHANNEL = 9       # 上下俯仰舵机
PAN_CHANNEL = 10       # 左右水平舵机

# 舵机脉宽范围（微秒），需根据实际舵机确认
SERVO_MIN_US = 1000
SERVO_MAX_US = 2000
PWM_PERIOD_US = 20000

# 三个俯仰姿态的初始角度
TILT_DOWN = 150
TILT_LEVEL = 210
TILT_UP = 270

# 水平初始角度
PAN_LEFT = 45
PAN_CENTER = 90
PAN_RIGHT = 135

def angle_to_count(angle):
    """将 0°~180°角度转换为 PCA9685 计数值。"""
    pulse_us = SERVO_MIN_US + angle / 180.0 * (
        SERVO_MAX_US - SERVO_MIN_US
    )
    return int(pulse_us / PWM_PERIOD_US * 4096)


def set_servo(channel, angle):
    """控制指定通道的舵机转到目标角度。"""
    count = angle_to_count(angle)
    pwm.set_pwm(channel, 0, count)


def main():
    try:
        # 云台水平居中，俯仰回到平视参考位置
        set_servo(PAN_CHANNEL, PAN_CENTER)
        set_servo(TILT_CHANNEL, TILT_LEVEL)
        time.sleep(1)

        # 低头
        print("云台：低头")
        set_servo(TILT_CHANNEL, TILT_DOWN)
        time.sleep(1)

        # 平视
        print("云台：平视")
        set_servo(TILT_CHANNEL, TILT_LEVEL)
        time.sleep(1)

        # 抬头
        print("云台：抬头")
        set_servo(TILT_CHANNEL, TILT_UP)
        time.sleep(1)

        # 最后回到平视，水平居中
        set_servo(TILT_CHANNEL, TILT_LEVEL)
        set_servo(PAN_CHANNEL, PAN_CENTER)
        time.sleep(1)

        #向左摆头
        print("云台：左摆")
        set_servo(PAN_CHANNEL, PAN_LEFT)
        time.sleep(1)

        #向右摆头
        print("云台：右摆")
        set_servo(PAN_CHANNEL, PAN_RIGHT)
        time.sleep(1)

        print("云台初始化完成")

    except KeyboardInterrupt:
        print("\n用户中断云台初始化")


if __name__ == "__main__":
    main()
