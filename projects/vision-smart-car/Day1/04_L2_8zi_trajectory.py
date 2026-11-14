# -*- coding: utf-8 -*-
"""低速 8 字轨迹；先在空旷平地调节 ARC_TIME 和 TURN_TIME。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.motor import Car

SPEED = 60
ARC_TIME =  7.8      # 每段弧线持续时间，依车型/地面调整

def drive_arc(car, left_speed, right_speed, duration):
    car.set_wheels(left_speed, right_speed)
    import time
    time.sleep(duration)

def main():
    car = Car()
    try:
        car.wait_for_button()
        drive_arc(car, int(SPEED * 0.2), SPEED, ARC_TIME)
        drive_arc(car, SPEED, int(SPEED * 0.2), ARC_TIME * 2 - 2.3)
        drive_arc(car, int(SPEED * 0.2), SPEED, ARC_TIME)
        print("8 字轨迹程序完成")
    except KeyboardInterrupt:
        print("用户中断，正在停车")
    finally:
        car.stop()
        car.cleanup()


if __name__ == "__main__":
    main()
