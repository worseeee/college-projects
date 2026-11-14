# -*- coding: utf-8 -*-
"""
Day1 基础运动试用（面向对象版）
============================================================
运行目录：示例代码/
    python3 Day1/基础运动试用/basic_motion_oop.py

本文件只负责主流程。引脚和参数位于 common/car_config.py，
Car 类位于 common/motor.py，主程序通过对象方法表达动作意图。

运行后绿灯等待按键，按键后红灯亮，小车依次演示：
前进 -> 停车 -> 后退 -> 停车 -> 左转 -> 停车 -> 右转 -> 停车。
按 Ctrl+C 可随时停止，程序会停车并释放 GPIO。
"""

import os
import sys


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
from common.motor import Car


def run_motion_demo(car):
    """执行一轮基础运动，只通过 Car 对象的方法控制小车。"""
    print("前进")
    car.forward(cfg.SPEED_DEFAULT, 1.2)
    car.stop(0.4)

    print("后退")
    car.backward(cfg.SPEED_DEFAULT, 1.2)
    car.stop(0.4)

    print("左转")
    car.turn_left(cfg.SPEED_TURN, 0.8)
    car.stop(0.4)

    print("右转")
    car.turn_right(cfg.SPEED_TURN, 0.8)
    car.stop(0.4)

    print("停车")
    car.led(green=True, red=False)
    print("本轮演示完成，可以再次按下启动按键。")


def main():
    print("=" * 56)
    print(" 基础运动试用（面向对象版）")
    print("=" * 56)

    car = Car()
    try:
        while True:
            car.wait_for_button()
            run_motion_demo(car)
    except KeyboardInterrupt:
        print("\n收到 Ctrl+C，准备停车 ...")
    finally:
        car.cleanup()
        print("已停车并释放 GPIO。")


if __name__ == "__main__":
    main()
