# -*- coding: utf-8 -*-
"""按键启动后依次演示四方向；Ctrl+C 时立即停车并释放 GPIO。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import car_config as cfg
from common.motor import Car


def main():
    car = Car()
    try:
        while True:
            car.wait_for_button()
            for label, action, speed, duration in (
                ("前进", car.forward, cfg.SPEED_DEFAULT, 1.2),
                ("后退", car.backward, cfg.SPEED_DEFAULT, 1.2),
                ("左转", car.turn_left, cfg.SPEED_TURN, 0.8),
                ("右转", car.turn_right, cfg.SPEED_TURN, 0.8),
            ):
                print(label)
                action(speed, duration)
                car.stop(0.4)
            car.led(green=True, red=False)
            print("一轮完成，可再次按键启动")
    except KeyboardInterrupt:
        print("收到 Ctrl+C，正在安全停车")
    finally:
        car.stop()
        car.led(green=False, red=False)
        car.cleanup()


if __name__ == "__main__":
    main()
