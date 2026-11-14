# -*- coding: utf-8 -*-
"""
Day1 基础运动试用（面向过程版）
============================================================
运行目录：示例代码/
    python3 Day1/基础运动试用/basic_motion_procedural.py

引脚和常用参数统一从 common/car_config.py 读取，本文件只保留
过程式流程：初始化硬件 -> 等待按键 -> 按顺序调用运动函数。

运行后绿灯等待按键，按键后红灯亮，小车依次演示：
前进 -> 停车 -> 后退 -> 停车 -> 左转 -> 停车 -> 右转 -> 停车。
按 Ctrl+C 可随时停止，程序会停车并释放 GPIO。
"""

import os
import sys
import time

import RPi.GPIO as GPIO


# 让脚本从任何目录运行时都能找到上一级的 common 包。
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    ),
)

from common import car_config as cfg


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(
    [
        cfg.AIN1,
        cfg.AIN2,
        cfg.PWMA,
        cfg.BIN1,
        cfg.BIN2,
        cfg.PWMB,
        cfg.LED_G,
        cfg.LED_R,
    ],
    GPIO.OUT,
)
GPIO.setup(
    cfg.BTN_PIN,
    GPIO.IN,
    pull_up_down=GPIO.PUD_UP,
)

left_pwm = GPIO.PWM(cfg.PWMA, cfg.PWM_FREQ)
right_pwm = GPIO.PWM(cfg.PWMB, cfg.PWM_FREQ)
left_pwm.start(0)
right_pwm.start(0)


def set_wheel(pwm, in1, in2, speed):
    """设置一个轮子的方向和速度：正数前进，负数后退，0 停车。"""
    speed = max(-100, min(100, int(speed)))
    pwm.ChangeDutyCycle(abs(speed))
    GPIO.output(in1, speed > 0)
    GPIO.output(in2, speed < 0)


def set_left_wheel(speed):
    set_wheel(left_pwm, cfg.AIN1, cfg.AIN2, speed)


def set_right_wheel(speed):
    set_wheel(right_pwm, cfg.BIN1, cfg.BIN2, speed)


def stop_motors():
    set_left_wheel(0)
    set_right_wheel(0)


def forward(speed, duration):
    set_left_wheel(speed)
    set_right_wheel(speed)
    time.sleep(duration)


def backward(speed, duration):
    set_left_wheel(-speed)
    set_right_wheel(-speed)
    time.sleep(duration)


def turn_left(speed, duration):
    # 与 common/motor.py 的 Car.turn_left 一致：左轮反转、右轮正转。
    set_left_wheel(-speed)
    set_right_wheel(speed)
    time.sleep(duration)


def turn_right(speed, duration):
    # 与 common/motor.py 的 Car.turn_right 一致：左轮正转、右轮反转。
    set_left_wheel(speed)
    set_right_wheel(-speed)
    time.sleep(duration)


def wait_for_button():
    """绿灯待机，等待按键按下并松开；随后红灯亮表示程序运行。"""
    print("请按下小车上的启动按键 ...")
    GPIO.output(cfg.LED_G, True)
    GPIO.output(cfg.LED_R, False)

    while GPIO.input(cfg.BTN_PIN) == GPIO.HIGH:
        time.sleep(0.01)

    time.sleep(0.01)          # 消抖，和 common/motor.py 的等待逻辑保持一致
    while GPIO.input(cfg.BTN_PIN) == GPIO.LOW:
        time.sleep(0.01)

    GPIO.output(cfg.LED_G, False)
    GPIO.output(cfg.LED_R, True)
    print("启动成功，小车开始基础运动演示。")
    time.sleep(0.3)


def run_motion_demo():
    """执行一轮基础运动，动作之间留出短暂停车时间。"""
    print("前进")
    forward(cfg.SPEED_DEFAULT, 1.2)
    stop_motors()
    time.sleep(0.4)

    print("后退")
    backward(cfg.SPEED_DEFAULT, 1.2)
    stop_motors()
    time.sleep(0.4)

    print("左转")
    turn_left(cfg.SPEED_TURN, 0.8)
    stop_motors()
    time.sleep(0.4)

    print("右转")
    turn_right(cfg.SPEED_TURN, 0.8)
    stop_motors()
    time.sleep(0.4)

    print("停车")
    GPIO.output(cfg.LED_R, False)
    GPIO.output(cfg.LED_G, True)
    print("本轮演示完成，可以再次按下启动按键。")


def cleanup():
    """停车、关闭 PWM、熄灭指示灯并释放 GPIO。"""
    stop_motors()
    left_pwm.stop()
    right_pwm.stop()
    GPIO.output(cfg.LED_G, False)
    GPIO.output(cfg.LED_R, False)
    GPIO.cleanup()


def main():
    print("=" * 56)
    print(" 基础运动试用（面向过程版）")
    print("=" * 56)
    try:
        while True:
            wait_for_button()
            run_motion_demo()
    except KeyboardInterrupt:
        print("\n收到 Ctrl+C，准备停车 ...")
    finally:
        cleanup()
        print("已停车并释放 GPIO。")


if __name__ == "__main__":
    main()
