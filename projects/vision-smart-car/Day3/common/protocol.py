# -*- coding: utf-8 -*-
"""Day2 PC/小车共用的 UTF-8、换行分帧控制协议。"""

import re

_MOVE_RE = re.compile(r"^([FBLR])(\d{1,3})M$")
GEAR_SPEEDS = (0, 20, 40, 60, 80, 100)


def encode_move(direction, speed):
    direction = str(direction).strip().upper()
    speed = int(speed)
    if direction not in ("F", "B", "L", "R"):
        raise ValueError("direction 必须为 F/B/L/R")
    if not 0 <= speed <= 100:
        raise ValueError("speed 必须在 0 到 100 之间")
    return f"{direction}{speed}M"


def decode_move(line):
    """解析移动命令；返回 (方向, 速度)，F 单字母表示普通停车。"""
    value = str(line).strip().upper()
    if value in ("F", "STOP"):
        return "STOP", 0
    if value == "X":
        return "ESTOP", 0
    match = _MOVE_RE.fullmatch(value)
    if not match:
        raise ValueError(f"无效移动指令: {value}")
    direction, speed = match.groups()
    speed = int(speed)
    if speed > 100:
        raise ValueError("speed 必须在 0 到 100 之间")
    return direction, speed


def encode_stop():
    return "F"


def encode_estop():
    return "X"


def encode_gear(gear):
    gear = int(gear)
    if not 1 <= gear <= 5:
        raise ValueError("gear 必须在 1 到 5 之间")
    return f"GEAR|{gear}"


def decode_gear(line):
    fields = str(line).strip().upper().split("|")
    if len(fields) != 2 or fields[0] != "GEAR":
        raise ValueError("无效档位指令")
    gear = int(fields[1])
    if not 1 <= gear <= 5:
        raise ValueError("gear 必须在 1 到 5 之间")
    return gear, GEAR_SPEEDS[gear]


def encode_trajectory(name):
    name = str(name).strip().upper()
    if name not in ("EIGHT", "RECT", "CANCEL"):
        raise ValueError("轨迹名称必须为 EIGHT/RECT/CANCEL")
    return f"TRAJ|{name}"


def encode_gimbal(pan, tilt):
    pan, tilt = int(pan), int(tilt)
    if not 30 <= pan <= 150 or not 30 <= tilt <= 150:
        raise ValueError("云台角度必须在 30 到 150 度之间")
    return f"GIMBAL|{pan}|{tilt}"


def encode_ping():
    return "PING"


def parse_command(line):
    """将一条命令解析为 (类型, 参数)；协议错误由调用方回传 ERR。"""
    value = str(line).strip().upper()
    if not value:
        raise ValueError("空指令")
    if value == "PING":
        return "PING", None
    if value.startswith("GEAR|"):
        return "GEAR", decode_gear(value)
    if value.startswith("TRAJ|"):
        parts = value.split("|")
        if len(parts) != 2 or parts[1] not in ("EIGHT", "RECT", "CANCEL"):
            raise ValueError("无效轨迹指令")
        return "TRAJ", parts[1]
    if value.startswith("GIMBAL|"):
        parts = value.split("|")
        if len(parts) != 3:
            raise ValueError("云台指令格式为 GIMBAL|pan|tilt")
        pan, tilt = int(parts[1]), int(parts[2])
        if not 30 <= pan <= 150 or not 30 <= tilt <= 150:
            raise ValueError("云台角度必须在 30 到 150 度之间")
        return "GIMBAL", (pan, tilt)
    direction, speed = decode_move(value)
    if direction == "STOP":
        return "STOP", None
    if direction == "ESTOP":
        return "ESTOP", None
    return "MOVE", (direction, speed)


def encode_status(
    mode="M1",
    speed=0,
    obstacle=0,
    qr="NONE",
    score=0,
    photo=0,
    mission="NONE",
    progress="0/0",
    avoidance="CLEAR",
):
    """将状态字段编码为一行；调用方负责追加换行符。"""
    safe_qr = str(qr).replace("|", "/").replace("\n", " ")
    safe_mission = str(mission).replace("|", "/").replace("\n", " ")
    safe_avoidance = str(avoidance).replace("|", "/").replace("\n", " ")
    return (
        f"STAT|mode={mode}|speed={int(speed)}|obstacle={int(bool(obstacle))}"
        f"|qr={safe_qr}|score={int(score)}|photo={int(photo)}"
        f"|mission={safe_mission}|progress={progress}|avoidance={safe_avoidance}"
    )


def decode_status(line):
    value = str(line).strip()
    if not value.startswith("STAT|"):
        raise ValueError("状态行必须以 STAT| 开头")
    state = {}
    for field in value.split("|")[1:]:
        if "=" not in field:
            continue
        key, item = field.split("=", 1)
        state[key] = item
    for key in ("speed", "obstacle", "score", "photo"):
        if key in state:
            state[key] = int(state[key])
    return state


def encode_ack(message="OK"):
    safe = str(message).replace("|", "/").replace("\n", " ")
    return f"ACK|{safe}"


def encode_error(message):
    safe = str(message).replace("|", "/").replace("\n", " ")
    return f"ERR|{safe}"


def encode_event(message):
    """编码供 PC 通信记录显示的服务端事件。"""
    safe = str(message).replace("|", "/").replace("\r", " ").replace("\n", " ")
    return f"EVENT|{safe}"


def decode_event(line):
    value = str(line).strip()
    if not value.startswith("EVENT|"):
        raise ValueError("事件行必须以 EVENT| 开头")
    return value.split("|", 1)[1]
