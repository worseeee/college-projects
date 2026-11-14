# -*- coding: utf-8 -*-
"""
Day1 教学示例：电机与底盘控制
============================================================
把 GPIO 初始化、左右轮差速、四方向运动和资源释放封装到 Car 类。
主程序不需要重复操作 AIN/BIN/PWM 引脚。
"""

import time

import RPi.GPIO as GPIO

from common import car_config as cfg


class Car:
    """L298N 双通道驱动的智能小车底盘。"""

    def __init__(self):
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
        GPIO.setup(cfg.BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.left_pwm = GPIO.PWM(cfg.PWMA, cfg.PWM_FREQ)
        self.right_pwm = GPIO.PWM(cfg.PWMB, cfg.PWM_FREQ)
        self.left_pwm.start(0)
        self.right_pwm.start(0)

        self.speed = cfg.SPEED_DEFAULT
        self._stop_motors()

    def set_wheels(self, left_speed, right_speed):
        """
        设置左右轮的速度和方向。

        正数前进，负数后退，0 停车；速度会被限制在 -100 到 100。
        """
        left_speed = max(-100, min(100, int(left_speed)))
        right_speed = max(-100, min(100, int(right_speed)))

        self.left_pwm.ChangeDutyCycle(abs(left_speed))
        GPIO.output(cfg.AIN1, left_speed > 0)
        GPIO.output(cfg.AIN2, left_speed < 0)

        self.right_pwm.ChangeDutyCycle(abs(right_speed))
        GPIO.output(cfg.BIN1, right_speed > 0)
        GPIO.output(cfg.BIN2, right_speed < 0)

    def _stop_motors(self):
        self.set_wheels(0, 0)

    def forward(self, speed=None, t_time=0.0):
        """左右轮同时正转。"""
        speed = self.speed if speed is None else speed
        self.speed = speed
        self.set_wheels(speed, speed)
        if t_time:
            time.sleep(t_time)

    def backward(self, speed=None, t_time=0.0):
        """左右轮同时反转。"""
        speed = self.speed if speed is None else speed
        self.set_wheels(-speed, -speed)
        if t_time:
            time.sleep(t_time)

    def turn_left(self, speed=None, t_time=0.0):
        """原地左转：左轮反转，右轮正转。"""
        speed = self.speed if speed is None else speed
        self.set_wheels(-speed, speed)
        if t_time:
            time.sleep(t_time)

    def turn_right(self, speed=None, t_time=0.0):
        """原地右转：左轮正转，右轮反转。"""
        speed = self.speed if speed is None else speed
        self.set_wheels(speed, -speed)
        if t_time:
            time.sleep(t_time)

    def stop(self, t_time=0.0):
        """停止电机，并可选地等待指定时间。"""
        self._stop_motors()
        if t_time:
            time.sleep(t_time)

    def set_gear(self, gear):
        """设置 0 到 5 档速度，返回对应 PWM 占空比。"""
        gear = int(gear)
        if not 0 <= gear <= 5:
            raise ValueError("gear 必须在 0 到 5 之间")
        speed = gear * 20
        self.speed = speed
        return speed

    def led(self, green=None, red=None):
        """控制状态灯；传入 None 表示保持当前状态。"""
        if green is not None:
            GPIO.output(cfg.LED_G, bool(green))
        if red is not None:
            GPIO.output(cfg.LED_R, bool(red))

    def wait_for_button(self):
        """绿灯待机，等待按键按下并松开；触发后红灯亮。"""
        print("请按下小车上的启动按键 ...")
        self.led(green=True, red=False)

        while GPIO.input(cfg.BTN_PIN) == GPIO.HIGH:
            time.sleep(0.01)

        time.sleep(0.01)
        while GPIO.input(cfg.BTN_PIN) == GPIO.LOW:
            time.sleep(0.01)

        self.led(green=False, red=True)
        print("按键已触发，开始运行。")
        time.sleep(0.3)

    def cleanup(self):
        """停车、关闭 PWM 并释放 GPIO。"""
        try:
            self._stop_motors()
            self.left_pwm.stop()
            self.right_pwm.stop()
        finally:
            GPIO.cleanup()
