# -*- coding: utf-8 -*-
"""Day1 五档速度演示：0 档停车，1-5 档分别为 20%-100%。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.motor import Car


def main():
    car = Car()
    try:
        for gear in range(6):
            speed = car.set_gear(gear)
            print(f"第 {gear} 档，占空比 {speed}%")
            if gear == 0:
                car.stop(1.0)
            else:
                car.forward(t_time=1.5)
                car.stop(0.5)
        print("五档变速测试完成")
    except KeyboardInterrupt:
        print("用户中断，正在停车")
    finally:
        car.stop()
        car.cleanup()


if __name__ == "__main__":
    main()
