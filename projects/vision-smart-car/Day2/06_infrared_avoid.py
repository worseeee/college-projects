
# -*- coding: utf-8 -*-
"""Day2 L1：双红外传感器避障。"""

import argparse
import os
import sys
import time

import RPi.GPIO as GPIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import car_config as cfg
from common.motor import Car


# 连续采样参数
SAMPLE_COUNT = 3
SAMPLE_INTERVAL = 0.01

# 避障动作时间
SINGLE_TURN_TIME = 0.6
BACKWARD_TIME = 1
ESCAPE_TURN_TIME = 0.45


def configure_sensors():
    GPIO.setup(cfg.SENSOR_L, GPIO.IN)
    GPIO.setup(cfg.SENSOR_R, GPIO.IN)


def read_sensors():
    """返回左右是否畅通：True 为畅通，False 为检测到障碍。"""
    left_raw = GPIO.input(cfg.SENSOR_L)
    right_raw = GPIO.input(cfg.SENSOR_R)

    if cfg.SENSOR_ACTIVE_LOW:
        return left_raw == GPIO.HIGH, right_raw == GPIO.HIGH

    return left_raw == GPIO.LOW, right_raw == GPIO.LOW


def read_stable_sensors():
    """连续采样，以多数结果确定传感器状态。"""
    readings = []

    for _ in range(SAMPLE_COUNT):
        readings.append(read_sensors())
        time.sleep(SAMPLE_INTERVAL)

    left_clear = sum(r[0] for r in readings) > SAMPLE_COUNT // 2
    right_clear = sum(r[1] for r in readings) > SAMPLE_COUNT // 2

    return left_clear, right_clear


def avoid_once(car):
    """严格按照任务书的四种传感器状态执行动作。"""
    left_clear, right_clear = read_stable_sensors()

    if left_clear and right_clear:
        # 两侧畅通：前进
        car.forward(cfg.SPEED_DEFAULT)

    elif not left_clear and right_clear:
        # 仅左侧有障碍：向右短暂转向
        print("左侧有障碍，向右转")
        car.turn_right(cfg.SPEED_TURN, SINGLE_TURN_TIME)

    elif left_clear and not right_clear:
        # 仅右侧有障碍：向左短暂转向
        print("右侧有障碍，向左转")
        car.turn_left(cfg.SPEED_TURN, SINGLE_TURN_TIME)

    else:
        # 左右两侧均有障碍：停车、后退、左转
        print("左右两侧均有障碍，后退并左转")
        car.stop(0.2)
        car.backward(cfg.SPEED_DEFAULT, BACKWARD_TIME)
        car.stop(0.1)
        car.turn_left(cfg.SPEED_TURN, ESCAPE_TURN_TIME)
        car.stop(0.1)

    return left_clear, right_clear


def main():
    parser = argparse.ArgumentParser(description="Day2 红外避障")
    parser.add_argument(
        "--sensor-test",
        action="store_true",
        help="只读取传感器，不启动电机",
    )
    args = parser.parse_args()

    car = Car()

    try:
        configure_sensors()

        if args.sensor_test:
            print("传感器测试：无遮挡应显示 clear，有障碍应显示 blocked。")

            while True:
                left_clear, right_clear = read_stable_sensors()
                print(
                    f"L={'clear' if left_clear else 'blocked'}  "
                    f"R={'clear' if right_clear else 'blocked'}"
                )
                time.sleep(0.2)

        print("按小车启动键开始避障；Ctrl+C 停车退出。")
        car.wait_for_button()

        previous = None

        while True:
            left_clear, right_clear = avoid_once(car)
            current = (left_clear, right_clear)

            if current != previous:
                print(
                    f"L={'clear' if left_clear else 'blocked'}  "
                    f"R={'clear' if right_clear else 'blocked'}"
                )
                previous = current

            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\n收到 Ctrl+C，正在停车。")

    finally:
        car.stop()
        car.cleanup()


if __name__ == "__main__":
    main()
