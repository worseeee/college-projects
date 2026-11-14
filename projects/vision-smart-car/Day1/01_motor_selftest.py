# -*- coding: utf-8 -*-
"""Day1 四方向自测，逐项按键启动，便于检查方向和标签。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import car_config as cfg
from common.motor import Car


def main():
    car = Car()
    actions = [
        ("前进", car.forward),
        ("后退", car.backward),
        ("左转", car.turn_left),
        ("右转", car.turn_right),
    ]
    try:
        for label, action in actions:
            print(f"即将测试：{label}。确认车轮悬空后按启动键。")
            car.wait_for_button()
            action(cfg.SPEED_TURN if "转" in label else cfg.SPEED_DEFAULT, 1.0)
            car.stop(0.5)
        print("四方向测试完成")
    except KeyboardInterrupt:
        print("用户中断，正在停车")
    finally:
        car.stop()
        car.cleanup()


if __name__ == "__main__":
    main()
