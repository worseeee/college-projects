# -*- coding: utf-8 -*-
"""Day1 最小运动验证：前进 2 秒后停车。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.motor import Car


def main():
    car = Car()
    try:
        print("前进 2 秒")
        car.forward(50, 2)
        car.stop()
        print("最小运动验证完成")
    except KeyboardInterrupt:
        print("用户中断，正在停车")
    finally:
        car.stop()
        car.cleanup()


if __name__ == "__main__":
    main()
