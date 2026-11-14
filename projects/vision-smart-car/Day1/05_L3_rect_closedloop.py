# -*- coding: utf-8 -*-
"""矩形闭环：四条直线与四次原地转向；按实车校准时长。"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.motor import Car

SPEED = 45
STRAIGHT_TIME = 5.5   # 每条边持续时间，需按场地/车速校准
TURN_TIME = 2.165      # 原地约 90 度转向时长，需实车校准


def main():
    car = Car()
    try:
        car.wait_for_button()
        for side in range(4):
            print(f"矩形边 {side + 1}/4：直行")
            car.forward(SPEED, STRAIGHT_TIME)
            car.stop(0.4)
            print("原地右转")
            car.turn_right(SPEED, TURN_TIME)
            car.stop(0.5)
        print("矩形闭环程序完成；请测量终点与起点误差并调整时长")
    except KeyboardInterrupt:
        print("用户中断，正在停车")
    finally:
        car.stop()
        car.cleanup()


if __name__ == "__main__":
    main()
