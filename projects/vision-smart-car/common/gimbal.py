# -*- coding: utf-8 -*-
"""PCA9685 双轴云台控制。硬件库仅在树莓派上使用。"""

from common import car_config as cfg


class Gimbal:
    def __init__(self):
        try:
            import Adafruit_PCA9685
        except ImportError as exc:
            raise RuntimeError("缺少 Adafruit_PCA9685，请在树莓派安装云台驱动") from exc
        self.pwm = Adafruit_PCA9685.PCA9685(address=cfg.PCA9685_ADDRESS)
        self.pwm.set_pwm_freq(cfg.SERVO_FREQ)

    @staticmethod
    def angle_to_count(angle):
        angle = max(cfg.SERVO_MIN_ANGLE, min(cfg.SERVO_MAX_ANGLE, int(angle)))
        pulse_us = cfg.SERVO_MIN_US + angle / 180.0 * (
            cfg.SERVO_MAX_US - cfg.SERVO_MIN_US
        )
        return int(pulse_us / 20000.0 * 4096)

    def set_angle(self, channel, angle):
        angle = int(angle)
        if not cfg.SERVO_MIN_ANGLE <= angle <= cfg.SERVO_MAX_ANGLE:
            raise ValueError("云台角度必须在 0 到 300 度之间")
        self.pwm.set_pwm(channel, 0, self.angle_to_count(angle))

    def set_angles(self, pan, tilt):
        self.set_angle(cfg.PAN_CHANNEL, pan)
        self.set_angle(cfg.TILT_CHANNEL, tilt)

    def center(self):
        self.set_angles(cfg.PAN_CENTER, cfg.TILT_LEVEL)

    def scan_pan(self, tilt=None):
        tilt = cfg.TILT_LEVEL if tilt is None else int(tilt)
        for angle in (cfg.PAN_LEFT, cfg.PAN_CENTER, cfg.PAN_RIGHT):
            self.set_angles(angle, tilt)
