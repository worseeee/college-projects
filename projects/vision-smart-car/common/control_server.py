# -*- coding: utf-8 -*-
"""Day2 遥控服务核心：Socket 收发、动作仲裁、避障与状态广播。"""

import select
import socket
import threading
import time

import RPi.GPIO as GPIO

from common import car_config as cfg
from common.gimbal import Gimbal
from common.motor import Car
from common import protocol as pro


class RemoteCarServer:
    """仅由 motion_loop 写电机 GPIO，急停和避障可中断巡检任务。"""

    def __init__(self, enable_avoid=False, enable_status=False):
        self.enable_avoid = bool(enable_avoid)
        self.enable_status = bool(enable_status)
        self.car = Car()
        self._gimbal = None
        self._gimbal_lock = threading.Lock()
        self._running = threading.Event()
        self._running.set()
        self._state_lock = threading.RLock()
        self._send_lock = threading.Lock()
        self._status_send_lock = threading.Lock()
        self._conn = None
        self._connected = threading.Event()
        self._manual = None
        self._macro = None
        self._macro_serial = 0
        self._avoid_request = threading.Event()
        self._avoid_active = threading.Event()
        self._stop_request = threading.Event()
        self._estop_request = threading.Event()
        self._sensor_state = (True, True)
        self._avoid_snapshot = (True, True)
        self._obstacle_reported = False
        self._avoid_done_for_obstacle = False
        self._avoid_status_hold_until = 0.0
        self._state = {
            "mode": "M1",
            "speed": 0,
            "obstacle": 0,
            "qr": "NONE",
            "score": 0,
            "photo": 0,
            "mission": "NONE",
            "progress": "0/0",
            "avoidance": "CLEAR",
        }
        if self.enable_avoid:
            GPIO.setup(cfg.SENSOR_L, GPIO.IN)
            GPIO.setup(cfg.SENSOR_R, GPIO.IN)

    def run(self):
        motion_thread = threading.Thread(target=self._motion_loop, name="motion", daemon=True)
        motion_thread.start()
        sensor_thread = None
        if self.enable_avoid:
            sensor_thread = threading.Thread(target=self._sensor_loop, name="infrared", daemon=True)
            sensor_thread.start()

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.settimeout(0.5)
            server.bind((cfg.CAR_HOST, cfg.CAR_PORT))
            server.listen(1)
            print(f"Day2 服务端监听 {cfg.CAR_HOST}:{cfg.CAR_PORT}")
            while self._running.is_set():
                try:
                    conn, address = server.accept()
                except socket.timeout:
                    continue
                print(f"PC 已连接：{address}；等待控制指令")
                self._serve_connection(conn)
                print("PC 连接已断开，小车已停车；等待重新连接")
        except KeyboardInterrupt:
            print("收到 Ctrl+C，正在关闭服务端")
        except OSError as exc:
            print(f"Socket 服务端启动或运行失败：{exc}")
        finally:
            self._running.clear()
            self._connected.clear()
            self._stop_request.set()
            self._close_connection()
            server.close()
            motion_thread.join(timeout=1.0)
            if sensor_thread is not None:
                sensor_thread.join(timeout=1.0)
            self.car.cleanup()

    def _serve_connection(self, conn):
        # select 负责读超时；保持发送阻塞模式，避免 50 ms 的读轮询超时
        # 意外终止状态发送线程。
        conn.setblocking(True)
        with self._state_lock:
            self._conn = conn
        self._connected.set()
        status_thread = None
        buffer = b""
        try:
            self._send_line(pro.encode_ack("CONNECTED"), conn)
            if self.enable_status:
                self._send_event(f"STAT 状态线程启动，周期 {cfg.STATUS_INTERVAL:g} 秒", conn)
                status_thread = threading.Thread(
                    target=self._status_loop, args=(conn,), name="status", daemon=True
                )
                status_thread.start()
            while self._running.is_set():
                readable, _, _ = select.select([conn], [], [], cfg.SOCKET_POLL_INTERVAL)
                if not readable:
                    continue
                chunk = conn.recv(1024)
                if not chunk:
                    break
                buffer += chunk
                while b"\n" in buffer:
                    raw, buffer = buffer.split(b"\n", 1)
                    line = raw.decode("utf-8", errors="replace").strip()
                    if line:
                        self._handle_line(line, conn)
        except (ConnectionError, OSError) as exc:
            print(f"Socket 收发结束：{exc}")
        finally:
            self._connected.clear()
            self._cancel_all(estop=False)
            if status_thread is not None:
                status_thread.join(timeout=0.3)
            with self._state_lock:
                if self._conn is conn:
                    self._conn = None
            try:
                conn.close()
            except OSError:
                pass

    def _handle_line(self, line, conn):
        try:
            command, args = pro.parse_command(line)
            if command == "PING":
                self._send_line(pro.encode_ack("PONG"), conn)
                return
            if command == "MOVE":
                direction, speed = args
                wheels = {
                    "F": (speed, speed),
                    "B": (-speed, -speed),
                    "L": (-speed, speed),
                    "R": (speed, -speed),
                }[direction]
                with self._state_lock:
                    self._manual = (wheels, speed)
                    self._macro = None
                    self._state.update(mode="M1", speed=speed, mission="NONE", progress="0/0")
                self._stop_request.clear()
                self._send_line(pro.encode_ack(f"MOVE {direction} {speed}"), conn)
            elif command == "STOP":
                self._cancel_all(estop=False)
                self._send_line(pro.encode_ack("STOPPED"), conn)
            elif command == "ESTOP":
                self._cancel_all(estop=True)
                self._send_line(pro.encode_ack("ESTOP"), conn)
            elif command == "GEAR":
                gear, speed = args
                with self._state_lock:
                    self._state["speed"] = speed
                    self._state["mode"] = "M1"
                    if self._manual is not None:
                        self._manual = (self._manual[0], speed)
                        old_wheels = self._manual[0]
                        signs = tuple(1 if value >= 0 else -1 for value in old_wheels)
                        self._manual = ((signs[0] * speed, signs[1] * speed), speed)
                    self._macro = None
                self._send_line(pro.encode_ack(f"GEAR {gear} {speed}"), conn)
            elif command == "TRAJ":
                if args == "CANCEL":
                    self._cancel_all(estop=False)
                    self._send_line(pro.encode_ack("MISSION CANCELLED"), conn)
                else:
                    self._start_mission(args)
                    self._send_line(pro.encode_ack(f"MISSION {args}"), conn)
            elif command == "GIMBAL":
                pan, tilt = args
                with self._state_lock:
                    if self._macro is not None:
                        self._macro = None
                        self._state.update(mode="M1", speed=0, mission="NONE", progress="0/0")
                        self._stop_request.set()
                self._set_gimbal(pan, tilt)
                self._send_line(pro.encode_ack(f"GIMBAL {pan} {tilt}"), conn)
        except Exception as exc:
            self._send_line(pro.encode_error(exc), conn)

    def _cancel_all(self, estop):
        with self._state_lock:
            self._manual = None
            self._macro = None
            self._state["speed"] = 0
            self._state["mission"] = "NONE"
            self._state["progress"] = "0/0"
            self._state["mode"] = "M4" if estop else "M1"
        self._stop_request.set()
        if estop:
            self._estop_request.set()
        else:
            self._estop_request.clear()

    def _start_mission(self, name):
        if name == "EIGHT":
            speed = cfg.FIGURE_EIGHT_SPEED
            arc = cfg.FIGURE_EIGHT_ARC_TIME
            steps = [
                ((int(speed * 0.2), speed), arc, cfg.PAN_LEFT),
                ((speed, int(speed * 0.2)), arc * 2 - 2.3, cfg.PAN_CENTER),
                ((int(speed * 0.2), speed), arc, cfg.PAN_RIGHT),
            ]
        elif name == "RECT":
            speed = cfg.RECT_SPEED
            steps = []
            for index in range(4):
                steps.append(((speed, speed), cfg.RECT_STRAIGHT_TIME, (cfg.PAN_LEFT, cfg.PAN_CENTER, cfg.PAN_RIGHT, cfg.PAN_CENTER)[index]))
                steps.append(((speed, -speed), cfg.RECT_TURN_TIME, cfg.PAN_CENTER))
        else:
            raise ValueError("不支持的巡检任务")
        with self._state_lock:
            self._macro_serial += 1
            self._macro = {
                "serial": self._macro_serial,
                "name": name,
                "steps": steps,
                "index": 0,
                "total": len(steps),
            }
            self._manual = None
            self._state.update(
                mode="M2", speed=speed, mission=name, progress=f"0/{len(steps)}"
            )
        self._stop_request.set()

    def _motion_loop(self):
        last_wheels = None
        while self._running.is_set():
            if self._estop_request.is_set():
                self.car.stop()
                last_wheels = (0, 0)
                self._estop_request.clear()
                time.sleep(0.01)
                continue
            if self._stop_request.is_set():
                self.car.stop()
                last_wheels = (0, 0)
                self._stop_request.clear()
            if self._avoid_request.is_set() and self.enable_avoid and self._connected.is_set():
                with self._state_lock:
                    manual_active = self._manual is not None and self._macro is None
                    macro_active = self._macro is not None
                    should_avoid = manual_active or macro_active
                    if manual_active:
                        # A manual drive request is one-shot: after avoiding, wait
                        # for a fresh key/button press instead of resuming into it.
                        self._manual = None
                        self._state.update(mode="M1", speed=0, mission="NONE", progress="0/0")
                self._avoid_request.clear()
                if should_avoid:
                    completed = self._perform_avoidance()
                    if completed:
                        if manual_active:
                            self._send_event("避障完成：小车已停车，等待新的遥控指令")
                        elif macro_active:
                            self._send_event("避障完成：恢复巡检任务")
                    last_wheels = (0, 0)
                    continue

            with self._state_lock:
                macro = self._macro
                manual = self._manual
            if macro is not None:
                last_wheels = self._run_macro_step(macro)
                continue
            if manual is not None:
                wheels, speed = manual
                if wheels != last_wheels:
                    self.car.set_wheels(*wheels)
                    last_wheels = wheels
                with self._state_lock:
                    self._state["speed"] = speed
                    if self._state["mode"] != "M4":
                        self._state["mode"] = "M1"
                time.sleep(0.01)
                continue
            if last_wheels != (0, 0):
                self.car.stop()
                last_wheels = (0, 0)
            time.sleep(0.01)
        self.car.stop()

    def _run_macro_step(self, macro):
        with self._state_lock:
            if self._macro is not macro:
                return (0, 0)
            index = macro["index"]
            if index >= macro["total"]:
                self._state["score"] += 1
                self._state.update(mode="M1", speed=0, mission="NONE", progress="0/0")
                self._macro = None
                self.car.stop()
                print(f"巡检任务 {macro['name']} 完成，得分 +1")
                return (0, 0)
            wheels, duration, pan = macro["steps"][index]
            self._state["progress"] = f"{index + 1}/{macro['total']}"
        if isinstance(pan, tuple):
            pan_angles = pan
        else:
            pan_angles = (pan,)
        for angle in pan_angles:
            if self._macro is not macro or self._estop_request.is_set():
                return (0, 0)
            try:
                self._set_gimbal(angle, cfg.TILT_LEVEL)
            except Exception as exc:
                print(f"云台扫描未执行：{exc}")
            if not self._interruptible_wait(0.18, macro):
                return (0, 0)
        end = time.monotonic() + duration
        self.car.set_wheels(*wheels)
        with self._state_lock:
            self._state["speed"] = max(abs(wheels[0]), abs(wheels[1]))
        while self._running.is_set() and time.monotonic() < end:
            if self._estop_request.is_set() or self._macro is not macro:
                self.car.stop()
                return (0, 0)
            if self._avoid_request.is_set() and self.enable_avoid and self._connected.is_set():
                self._avoid_request.clear()
                remaining = max(0.0, end - time.monotonic())
                self.car.stop()
                if not self._perform_avoidance():
                    return (0, 0)
                self._send_event("避障完成：恢复巡检任务")
                if self._macro is not macro or self._estop_request.is_set():
                    return (0, 0)
                end = time.monotonic() + remaining
                self.car.set_wheels(*wheels)
                with self._state_lock:
                    self._state["speed"] = max(abs(wheels[0]), abs(wheels[1]))
            time.sleep(0.02)
        self.car.stop()
        with self._state_lock:
            if self._macro is macro:
                macro["index"] += 1
                self._state["progress"] = f"{macro['index']}/{macro['total']}"
        return (0, 0)

    def _interruptible_wait(self, duration, macro=None):
        end = time.monotonic() + duration
        while self._running.is_set() and time.monotonic() < end:
            if (self._estop_request.is_set() or self._stop_request.is_set()
                    or (macro is not None and self._macro is not macro)):
                return False
            if (macro is not None and self.enable_avoid and self._connected.is_set()
                    and self._avoid_request.is_set()):
                self._avoid_request.clear()
                if not self._perform_avoidance():
                    return False
                self._send_event("避障完成：恢复巡检任务")
            time.sleep(0.02)
        return True

    def _perform_avoidance(self):
        self._avoid_active.set()
        left_clear, right_clear = self._avoid_snapshot
        with self._state_lock:
            self._state["obstacle"] = 1
            self._state["speed"] = 0
            self._state["avoidance"] = "STOPPING"
        self._publish_status()
        self._send_event("避障开始：先停车")
        self.car.stop()
        completed = False
        try:
            if not self._interruptible_wait(cfg.AVOID_STOP_TIME):
                return False
            if not left_clear and right_clear:
                if not self._avoid_action("后退", (-cfg.SPEED_DEFAULT, -cfg.SPEED_DEFAULT), cfg.AVOID_REVERSE_TIME):
                    return False
                if not self._interruptible_wait(cfg.AVOID_SETTLE_TIME):
                    return False
                if not self._avoid_action("右转", (cfg.SPEED_TURN, -cfg.SPEED_TURN), cfg.AVOID_TURN_TIME):
                    return False
            elif left_clear and not right_clear:
                if not self._avoid_action("后退", (-cfg.SPEED_DEFAULT, -cfg.SPEED_DEFAULT), cfg.AVOID_REVERSE_TIME):
                    return False
                if not self._interruptible_wait(cfg.AVOID_SETTLE_TIME):
                    return False
                if not self._avoid_action("左转", (-cfg.SPEED_TURN, cfg.SPEED_TURN), cfg.AVOID_TURN_TIME):
                    return False
            else:
                if not self._avoid_action("后退", (-cfg.SPEED_DEFAULT, -cfg.SPEED_DEFAULT), cfg.AVOID_BOTH_REVERSE_TIME):
                    return False
                if not self._interruptible_wait(cfg.AVOID_SETTLE_TIME):
                    return False
                if not self._avoid_action("左转", (-cfg.SPEED_TURN, cfg.SPEED_TURN), cfg.AVOID_BOTH_TURN_TIME):
                    return False
            if not self._interruptible_wait(cfg.AVOID_SETTLE_TIME):
                return False
            completed = True
        finally:
            self.car.stop()
            self._avoid_active.clear()
            with self._state_lock:
                self._state["speed"] = 0
                self._state["avoidance"] = "COMPLETE" if completed else "INTERRUPTED"
                self._avoid_status_hold_until = time.monotonic() + max(
                    1.0, 2.0 * cfg.STATUS_INTERVAL
                )
            self._publish_status()
        return completed

    def _avoid_action(self, label, wheels, duration):
        self._set_avoidance_state("REVERSING" if label == "后退" else "TURNING")
        self._send_event(f"避障动作：{label}（{duration:.2f} 秒）")
        return self._timed_wheels(wheels, duration)

    def _timed_wheels(self, wheels, duration):
        with self._state_lock:
            self._state["speed"] = max(abs(wheels[0]), abs(wheels[1]))
        self.car.set_wheels(*wheels)
        end = time.monotonic() + duration
        while self._running.is_set() and time.monotonic() < end:
            if self._estop_request.is_set() or self._stop_request.is_set():
                self.car.stop()
                return False
            time.sleep(0.02)
        return True

    def _sensor_loop(self):
        while self._running.is_set():
            try:
                left_raw = GPIO.input(cfg.SENSOR_L)
                right_raw = GPIO.input(cfg.SENSOR_R)
                if cfg.SENSOR_ACTIVE_LOW:
                    left_clear = left_raw == GPIO.HIGH
                    right_clear = right_raw == GPIO.HIGH
                else:
                    left_clear = left_raw == GPIO.LOW
                    right_clear = right_raw == GPIO.LOW
                self._sensor_state = (left_clear, right_clear)
                obstacle = not (left_clear and right_clear)
                with self._state_lock:
                    previous_obstacle = self._state["obstacle"]
                    previous_avoidance = self._state["avoidance"]
                    self._state["obstacle"] = int(obstacle)
                    if obstacle:
                        if previous_avoidance in ("CLEAR", "COMPLETE", "INTERRUPTED"):
                            self._state["avoidance"] = "DETECTED"
                    elif (not self._avoid_active.is_set() and not self._avoid_request.is_set()
                          and not self._avoid_done_for_obstacle
                          and time.monotonic() >= self._avoid_status_hold_until):
                        self._state["avoidance"] = "CLEAR"
                    status_changed = (
                        previous_obstacle != self._state["obstacle"]
                        or previous_avoidance != self._state["avoidance"]
                    )
                if status_changed:
                    self._publish_status()
                if not obstacle:
                    if self._obstacle_reported:
                        self._send_event("障碍解除：道路畅通")
                    self._obstacle_reported = False
                    self._avoid_done_for_obstacle = False
                else:
                    if not self._obstacle_reported:
                        self._obstacle_reported = True
                        if not left_clear and not right_clear:
                            side = "左右两侧"
                        elif not left_clear:
                            side = "左侧"
                        else:
                            side = "右侧"
                        self._send_event(f"检测到障碍：{side}")
                with self._state_lock:
                    should_avoid = self._manual is not None or self._macro is not None
                if (obstacle and should_avoid and self._connected.is_set()
                        and not self._avoid_active.is_set()
                        and not self._avoid_done_for_obstacle):
                    self._avoid_snapshot = (left_clear, right_clear)
                    self._avoid_done_for_obstacle = True
                    self._avoid_request.set()
            except Exception as exc:
                print(f"红外读取失败：{exc}")
            time.sleep(cfg.SENSOR_INTERVAL)

    def _status_loop(self, conn):
        while self._running.is_set() and self._connected.is_set():
            with self._state_lock:
                if self._conn is not conn:
                    return
            if not self._publish_status(conn):
                # 读线程会负责发现断线；状态循环保留运行，不因一次
                # 暂时的发送错误就永久停止。
                print("STAT 发送暂时失败；状态线程将在下一周期重试")
            time.sleep(cfg.STATUS_INTERVAL)

    def _publish_status(self, conn=None):
        if not self.enable_status or not self._connected.is_set():
            return False
        with self._status_send_lock:
            with self._state_lock:
                if conn is None:
                    conn = self._conn
                if conn is None or self._conn is not conn:
                    return False
                state = dict(self._state)
            # 让旧版 PC 也能在后退/转向期间继续看到障碍状态；新的 PC
            # 另外读取 avoidance 字段显示具体阶段。
            if state.get("avoidance") in ("STOPPING", "REVERSING", "TURNING"):
                state["obstacle"] = 1
            return self._send_line(pro.encode_status(**state), conn)

    def _set_avoidance_state(self, value):
        with self._state_lock:
            if self._state["avoidance"] == value:
                return
            self._state["avoidance"] = value
        self._publish_status()

    def _set_gimbal(self, pan, tilt):
        with self._gimbal_lock:
            if self._gimbal is None:
                self._gimbal = Gimbal()
                self._gimbal.center()
            self._gimbal.set_angles(pan, tilt)

    def _send_line(self, line, conn=None):
        if conn is None:
            with self._state_lock:
                conn = self._conn
        if conn is None:
            return False
        try:
            with self._send_lock:
                conn.sendall((str(line) + "\n").encode("utf-8"))
            return True
        except (ConnectionError, OSError):
            return False

    def _send_event(self, message, conn=None):
        print(message)
        return self._send_line(pro.encode_event(message), conn)

    def _close_connection(self):
        with self._state_lock:
            conn = self._conn
            self._conn = None
        if conn is not None:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                conn.close()
            except OSError:
                pass


def main(enable_avoid=False, enable_status=False):
    RemoteCarServer(enable_avoid=enable_avoid, enable_status=enable_status).run()
