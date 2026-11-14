# -*- coding: utf-8 -*-
"""Day2 PC 端 Tkinter 遥控器：鼠标/键盘控制、轨迹、云台和状态显示。"""

import queue
import os
import socket
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import car_config as cfg
from common import protocol as pro


class NetworkClient:
    """在后台线程循环收发，避免 Socket 操作阻塞 Tk 主循环。"""

    def __init__(self, events):
        self.events = events
        self.outgoing = queue.Queue()
        self._stop = threading.Event()
        self._close_after_flush = threading.Event()
        self._thread = None
        self.connected = False

    def connect(self, host, port):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._close_after_flush.clear()
        self._thread = threading.Thread(
            target=self._network_loop, args=(host, int(port)), daemon=True
        )
        self._thread.start()

    def send(self, line):
        if self.connected:
            self.outgoing.put(str(line))

    def send_estop(self):
        if not self.connected:
            return
        while True:
            try:
                self.outgoing.get_nowait()
            except queue.Empty:
                break
        self.outgoing.put(pro.encode_estop())

    def disconnect(self, after_flush=False):
        if after_flush:
            self._close_after_flush.set()
        else:
            self._stop.set()

    def _network_loop(self, host, port):
        sock = None
        buffer = b""
        try:
            sock = socket.create_connection((host, port), timeout=3.0)
            sock.settimeout(0.05)
            self.connected = True
            self.events.put(("connected", f"已连接 {host}:{port}"))
            while not self._stop.is_set():
                while True:
                    try:
                        line = self.outgoing.get_nowait()
                    except queue.Empty:
                        break
                    sock.sendall((line + "\n").encode("utf-8"))
                if self._close_after_flush.is_set() and self.outgoing.empty():
                    break
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    buffer += chunk
                    while b"\n" in buffer:
                        raw, buffer = buffer.split(b"\n", 1)
                        line = raw.decode("utf-8", errors="replace").strip()
                        if not line:
                            continue
                        if line.startswith("STAT|"):
                            try:
                                self.events.put(("status", pro.decode_status(line)))
                            except ValueError as exc:
                                self.events.put(("message", f"状态解析错误：{exc}"))
                        elif line.startswith("EVENT|"):
                            try:
                                self.events.put(("event", pro.decode_event(line)))
                            except ValueError as exc:
                                self.events.put(("message", f"事件解析错误：{exc}"))
                        else:
                            self.events.put(("message", line))
                except socket.timeout:
                    pass
            if self._close_after_flush.is_set():
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
        except (OSError, ValueError) as exc:
            self.events.put(("error", str(exc)))
        finally:
            self.connected = False
            if sock is not None:
                try:
                    sock.close()
                except OSError:
                    pass
            self.events.put(("disconnected", "连接已关闭"))


class RemoteConsole:
    COLORS = {
        "background": "#f3f6fb",
        "panel": "#ffffff",
        "ink": "#1d2b3a",
        "muted": "#68788a",
        "blue": "#2b67b1",
        "blue_pressed": "#17487f",
        "red": "#c54444",
        "red_pressed": "#8f2727",
        "green": "#2d8a62",
        "border": "#d7e0ea",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("SmartCar Day2 远程巡检控制台")
        self.root.geometry("1050x760")
        self.root.minsize(920, 680)
        self.root.configure(bg=self.COLORS["background"])
        self.events = queue.Queue()
        self.network = NetworkClient(self.events)
        self._drive_owner = None
        self._drive_direction = None
        self._held_drive_keys = set()
        self._blocked_drive_keys = set()
        self._closing = False
        self._gear_selected = False
        self._last_gear = None
        self.speed = cfg.SPEED_DEFAULT
        self._visual_buttons = {}
        self._connected_at = None
        self._last_status_at = None
        self._status_timeout_reported = False

        self.host_var = tk.StringVar(value=cfg.PC_DEFAULT_HOST)
        self.port_var = tk.StringVar(value=str(cfg.CAR_PORT))
        self.connection_var = tk.StringVar(value="未连接")
        self.speed_var = tk.DoubleVar(value=cfg.SPEED_DEFAULT)
        self.speed_text_var = tk.StringVar(value="默认速度 45%")
        self.status_vars = {
            "mode": tk.StringVar(value="等待状态"),
            "speed": tk.StringVar(value="--"),
            "obstacle": tk.StringVar(value="--"),
            "score": tk.StringVar(value="--"),
            "qr": tk.StringVar(value="--"),
            "photo": tk.StringVar(value="--"),
            "mission": tk.StringVar(value="--"),
            "progress": tk.StringVar(value="--"),
        }
        self.status_heartbeat_var = tk.StringVar(value="未连接，尚未收到 STAT")
        self.pan_var = tk.IntVar(value=cfg.PAN_CENTER)
        self.tilt_var = tk.IntVar(value=cfg.TILT_LEVEL)
        self._build_ui()
        self._bind_keys()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<FocusOut>", self._focus_out)
        self.root.after(80, self._poll_events)

    def _build_ui(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=self.COLORS["background"])
        style.configure("Panel.TFrame", background=self.COLORS["panel"])
        style.configure("Title.TLabel", background=self.COLORS["background"],
                        foreground=self.COLORS["ink"], font=("Microsoft YaHei UI", 18, "bold"))
        style.configure("Sub.TLabel", background=self.COLORS["background"],
                        foreground=self.COLORS["muted"], font=("Microsoft YaHei UI", 9))
        style.configure("PanelTitle.TLabel", background=self.COLORS["panel"],
                        foreground=self.COLORS["ink"], font=("Microsoft YaHei UI", 12, "bold"))
        style.configure("Value.TLabel", background=self.COLORS["panel"],
                        foreground=self.COLORS["blue"], font=("Microsoft YaHei UI", 11, "bold"))
        style.configure("TButton", font=("Microsoft YaHei UI", 10), padding=(10, 7))

        header = ttk.Frame(self.root, padding=(20, 16, 20, 8))
        header.pack(fill="x")
        ttk.Label(header, text="SmartCar Day2 远程巡检控制台", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="方向键按住行驶，松开停车；鼠标方向键与键盘控制同步。状态由小车端定时回传。",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        connection = ttk.Frame(self.root, padding=(20, 6, 20, 14))
        connection.pack(fill="x")
        ttk.Label(connection, text="小车 IP").pack(side="left")
        ttk.Entry(connection, textvariable=self.host_var, width=18).pack(side="left", padx=(6, 14))
        ttk.Label(connection, text="端口").pack(side="left")
        ttk.Entry(connection, textvariable=self.port_var, width=7).pack(side="left", padx=(6, 14))
        self.connect_button = ttk.Button(connection, text="连接小车", command=self._toggle_connection)
        self.connect_button.pack(side="left")
        ttk.Label(connection, textvariable=self.connection_var, foreground=self.COLORS["muted"]).pack(
            side="left", padx=14
        )

        body = ttk.Frame(self.root, padding=(20, 0, 20, 18))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        control = ttk.Frame(body, style="Panel.TFrame", padding=16)
        control.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        telemetry = ttk.Frame(body, style="Panel.TFrame", padding=16)
        telemetry.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self._build_control_panel(control)
        self._build_telemetry_panel(telemetry)

        footer = ttk.Frame(self.root, padding=(20, 0, 20, 12))
        footer.pack(fill="x")
        ttk.Label(
            footer,
            text="运行小车端 08_L3_threaded_server.py 以启用避障与状态回传；ESC 急停并退出。",
            style="Sub.TLabel",
        ).pack(anchor="w")

    def _build_control_panel(self, parent):
        ttk.Label(parent, text="远程控制器", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(parent, text="按住方向键移动，松开即停车", background=self.COLORS["panel"],
                  foreground=self.COLORS["muted"]).pack(anchor="w", pady=(2, 7))

        pad = tk.Frame(parent, bg=self.COLORS["panel"])
        pad.pack(pady=5)
        positions = {
            "W": (0, 1, "▲\nW"),
            "A": (1, 0, "◀\nA"),
            "F": (1, 1, "■\nF 停止"),
            "D": (1, 2, "▶\nD"),
            "S": (2, 1, "▼\nS"),
        }
        for key, (row, col, label) in positions.items():
            color = self.COLORS["red"] if key == "F" else self.COLORS["blue"]
            button = tk.Button(
                pad, text=label, width=9, height=3, relief="raised", bd=2,
                bg=color, fg="white", activebackground=self.COLORS["blue_pressed"],
                activeforeground="white", font=("Microsoft YaHei UI", 10, "bold"),
                takefocus=False,
            )
            button.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            if key == "F":
                button.bind("<ButtonRelease-1>", lambda event: self._stop())
            else:
                button.bind("<ButtonPress-1>", lambda event, d=key: self._press_drive(d, ("mouse", d)))
                button.bind("<ButtonRelease-1>", lambda event, d=key: self._release_drive(("mouse", d)))
                self._visual_buttons[key] = (button, color)

        ttk.Button(parent, text="X  急停（保持连接）", command=self._estop).pack(fill="x", pady=(4, 2))

        ttk.Label(parent, text="五档速度", style="PanelTitle.TLabel").pack(anchor="w", pady=(13, 0))
        scale = ttk.Scale(parent, from_=20, to=100, variable=self.speed_var,
                          orient="horizontal", command=self._on_scale)
        scale.pack(fill="x", pady=(6, 0))
        scale.bind("<ButtonPress-1>", self._activate_gear_slider, add="+")
        scale.bind("<KeyPress>", self._activate_gear_slider, add="+")
        tick_row = ttk.Frame(parent, style="Panel.TFrame")
        tick_row.pack(fill="x")
        for index, value in enumerate((20, 40, 60, 80, 100)):
            tick_row.columnconfigure(index, weight=1)
            ttk.Label(tick_row, text=f"{value}%", background=self.COLORS["panel"],
                      foreground=self.COLORS["muted"]).grid(row=0, column=index)
        ttk.Label(parent, textvariable=self.speed_text_var, background=self.COLORS["panel"],
                  foreground=self.COLORS["blue"]).pack(anchor="e", pady=(2, 0))

        ttk.Label(parent, text="巡检任务", style="PanelTitle.TLabel").pack(anchor="w", pady=(12, 4))
        mission_row = ttk.Frame(parent, style="Panel.TFrame")
        mission_row.pack(fill="x")
        ttk.Button(mission_row, text="启动 8 字", command=lambda: self._send(pro.encode_trajectory("EIGHT"))).pack(
            side="left", expand=True, fill="x", padx=(0, 4)
        )
        ttk.Button(mission_row, text="启动矩形", command=lambda: self._send(pro.encode_trajectory("RECT"))).pack(
            side="left", expand=True, fill="x", padx=4
        )
        ttk.Button(mission_row, text="取消任务", command=lambda: self._send(pro.encode_trajectory("CANCEL"))).pack(
            side="left", expand=True, fill="x", padx=(4, 0)
        )

        ttk.Label(parent, text="云台角度", style="PanelTitle.TLabel").pack(anchor="w", pady=(12, 4))
        angles = ttk.Frame(parent, style="Panel.TFrame")
        angles.pack(fill="x")
        ttk.Label(angles, text="水平").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(angles, from_=30, to=300, increment=1, width=6, textvariable=self.pan_var).grid(
            row=0, column=1, padx=(4, 10)
        )
        ttk.Label(angles, text="俯仰").grid(row=0, column=2, sticky="w")
        ttk.Spinbox(angles, from_=30, to=300, increment=1, width=6, textvariable=self.tilt_var).grid(
            row=0, column=3, padx=(4, 10)
        )
        ttk.Button(angles, text="应用角度", command=self._apply_gimbal).grid(row=0, column=4)
        preset_row = ttk.Frame(parent, style="Panel.TFrame")
        preset_row.pack(fill="x", pady=(5, 0))
        for label, pan, tilt in (
            ("左摆", cfg.PAN_LEFT, cfg.TILT_LEVEL),
            ("居中", cfg.PAN_CENTER, cfg.TILT_LEVEL),
            ("右摆", cfg.PAN_RIGHT, cfg.TILT_LEVEL),
            ("低头", cfg.PAN_CENTER, cfg.TILT_DOWN),
            ("平视", cfg.PAN_CENTER, cfg.TILT_LEVEL),
            ("抬头", cfg.PAN_CENTER, cfg.TILT_UP),
        ):
            ttk.Button(preset_row, text=label, command=lambda p=pan, t=tilt: self._preset_gimbal(p, t)).pack(
                side="left", expand=True, fill="x", padx=2
            )

    def _build_telemetry_panel(self, parent):
        ttk.Label(parent, text="实时状态", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(parent, textvariable=self.status_heartbeat_var, background=self.COLORS["panel"],
                  foreground=self.COLORS["muted"]).pack(anchor="w", pady=(2, 12))
        rows = (
            ("运行模式", "mode"),
            ("当前速度", "speed"),
            ("避障状态", "obstacle"),
            ("巡检得分", "score"),
            ("二维码", "qr"),
            ("拍照数量", "photo"),
            ("任务", "mission"),
            ("进度", "progress"),
        )
        table = ttk.Frame(parent, style="Panel.TFrame")
        table.pack(fill="x")
        table.columnconfigure(1, weight=1)
        for row, (label, key) in enumerate(rows):
            ttk.Label(table, text=label, background=self.COLORS["panel"],
                      foreground=self.COLORS["muted"]).grid(row=row, column=0, sticky="w", pady=7)
            ttk.Label(table, textvariable=self.status_vars[key], style="Value.TLabel").grid(
                row=row, column=1, sticky="e", pady=7
            )
            if row < len(rows) - 1:
                tk.Frame(table, height=1, bg=self.COLORS["border"]).grid(
                    row=row, column=0, columnspan=2, sticky="ew", pady=(0, 2)
                )
        ttk.Label(parent, text="通信记录", style="PanelTitle.TLabel").pack(anchor="w", pady=(18, 6))
        self.log = tk.Text(parent, height=10, wrap="word", state="disabled",
                           bg="#f7f9fc", fg=self.COLORS["ink"], relief="flat",
                           font=("Consolas", 9))
        self.log.pack(fill="both", expand=True)
        ttk.Label(parent, text="M1 遥控  ·  M2 巡检  ·  M4 急停",
                  background=self.COLORS["panel"], foreground=self.COLORS["muted"]).pack(
                      anchor="w", pady=(8, 0)
                  )

    def _bind_keys(self):
        self.root.bind_all("<KeyPress>", self._key_press)
        self.root.bind_all("<KeyRelease>", self._key_release)
        self.root.bind_all("<ButtonRelease-1>", self._global_mouse_release, add="+")

    def _global_mouse_release(self, _event):
        # Release may land on another widget after the pointer leaves the
        # direction pad; still send STOP for the held mouse command.
        if self._drive_owner and self._drive_owner[0] == "mouse":
            self._release_drive(self._drive_owner)

    def _key_press(self, event):
        key = event.keysym.lower()
        if key == "escape":
            self._send_estop()
            self._release_all_visuals()
            self.network.disconnect(after_flush=True)
            self.root.after(180, self._destroy)
            return "break"
        if self._entry_has_focus():
            return None
        if key == "q":
            self._on_close()
            return "break"
        if key == "x":
            self._estop()
            return "break"
        if key == "f":
            self._stop()
            return "break"
        if key in ("w", "a", "s", "d"):
            if key in self._held_drive_keys:
                return "break"
            self._held_drive_keys.add(key)
            if key in self._blocked_drive_keys:
                return "break"
            direction = key.upper()
            self._press_drive(direction, ("key", direction))
            return "break"
        return None

    def _key_release(self, event):
        key = event.keysym.lower()
        if key in ("w", "a", "s", "d"):
            self._held_drive_keys.discard(key)
            self._blocked_drive_keys.discard(key)
            direction = key.upper()
            self._release_drive(("key", direction))
            return "break"
        return None

    def _entry_has_focus(self):
        widget = self.root.focus_get()
        if widget is None:
            return False
        return isinstance(widget, (tk.Entry, ttk.Entry, ttk.Spinbox, tk.Spinbox))

    def _press_drive(self, direction, owner):
        if not self.network.connected:
            return
        if self._drive_owner == owner and self._drive_direction == direction:
            return
        if self._drive_direction:
            self._set_button_visual(self._drive_direction, False)
        self._drive_owner = owner
        self._drive_direction = direction
        self._set_button_visual(direction, True)
        self.speed = int(round(float(self.speed_var.get())))
        wire_direction = {"W": "F", "S": "B", "A": "L", "D": "R"}[direction]
        self._send(pro.encode_move(wire_direction, self.speed))

    def _release_drive(self, owner):
        if self._drive_owner == owner:
            self._stop()

    def _set_button_visual(self, direction, pressed):
        item = self._visual_buttons.get(direction)
        if not item:
            return
        button, normal_color = item
        if pressed:
            button.configure(bg=self.COLORS["blue_pressed"], relief="sunken")
        else:
            button.configure(bg=normal_color, relief="raised")

    def _release_all_visuals(self):
        self._blocked_drive_keys.update(self._held_drive_keys)
        for direction in tuple(self._visual_buttons):
            self._set_button_visual(direction, False)
        self._drive_owner = None
        self._drive_direction = None

    def _stop(self):
        self._send(pro.encode_stop())
        self._release_all_visuals()

    def _estop(self):
        self._send_estop()
        self._release_all_visuals()
        self.connection_var.set("急停已发送")

    def _send_estop(self):
        if self.network.connected:
            self.network.send_estop()
            self._append_log(f"> {pro.encode_estop()}  [优先级急停]")

    def _activate_gear_slider(self, _event):
        self._gear_selected = True

    def _on_scale(self, raw_value):
        if not self._gear_selected:
            return
        value = float(raw_value)
        levels = (20, 40, 60, 80, 100)
        speed = min(levels, key=lambda item: abs(item - value))
        gear = levels.index(speed) + 1
        self.speed = speed
        self.speed_text_var.set(f"第 {gear} 档  ·  {speed}%")
        if self.speed_var.get() != speed:
            self.speed_var.set(speed)
        if gear != self._last_gear:
            self._last_gear = gear
            self._send(pro.encode_gear(gear))

    def _toggle_connection(self):
        if self.network.connected:
            self.network.disconnect()
            return
        try:
            port = int(self.port_var.get())
            if not 1 <= port <= 65535:
                raise ValueError("端口范围应为 1 到 65535")
        except ValueError as exc:
            messagebox.showerror("连接设置错误", str(exc), parent=self.root)
            return
        self.connect_button.configure(state="disabled")
        self.connection_var.set("正在连接…")
        self.status_heartbeat_var.set("正在连接，尚未收到 STAT…")
        self.network.connect(self.host_var.get().strip(), port)

    def _send(self, line):
        if self.network.connected:
            self.network.send(line)
            self._append_log(f"> {line}")

    def _apply_gimbal(self):
        self._preset_gimbal(self.pan_var.get(), self.tilt_var.get())

    def _preset_gimbal(self, pan, tilt):
        pan, tilt = int(pan), int(tilt)
        if not 0 <= pan <= 300 or not 0 <= tilt <= 300:
            messagebox.showerror("角度超出范围", "水平与俯仰角度均须为 0°–300°。", parent=self.root)
            return
        self.pan_var.set(pan)
        self.tilt_var.set(tilt)
        try:
            self._send(pro.encode_gimbal(pan, tilt))
        except ValueError as exc:
            messagebox.showerror("云台角度错误", str(exc), parent=self.root)

    def _poll_events(self):
        while True:
            try:
                event, payload = self.events.get_nowait()
            except queue.Empty:
                break
            if event == "connected":
                self.connect_button.configure(text="断开连接", state="normal")
                self.connection_var.set(payload)
                self._connected_at = time.monotonic()
                self._last_status_at = None
                self._status_timeout_reported = False
                self.status_heartbeat_var.set("已连接，等待小车 STAT 状态…")
            elif event == "disconnected":
                self.connect_button.configure(text="连接小车", state="normal")
                if not self._closing:
                    self.connection_var.set(payload)
                    self._release_all_visuals()
                    self.status_heartbeat_var.set("连接已断开，STAT 已停止")
            elif event == "error":
                self.connect_button.configure(text="连接小车", state="normal")
                self.connection_var.set("连接失败")
                self.status_heartbeat_var.set("连接失败，未收到 STAT")
                self._append_log(f"! {payload}")
            elif event == "status":
                self._show_status(payload)
                self._last_status_at = time.monotonic()
                self._status_timeout_reported = False
                self.status_heartbeat_var.set(f"STAT 已更新 {time.strftime('%H:%M:%S')}")
            elif event == "event":
                if payload == "避障完成：小车已停车，等待新的遥控指令":
                    self._release_all_visuals()
                self._append_log(f"< 小车状态：{payload}")
            elif event == "message":
                self._append_log(f"< {payload}")
        self._check_status_freshness()
        if not self._closing:
            self.root.after(80, self._poll_events)

    def _check_status_freshness(self):
        if not self.network.connected:
            return
        reference = self._last_status_at or self._connected_at
        if reference is None or time.monotonic() - reference <= max(3.0, cfg.STATUS_INTERVAL * 2.5):
            return
        if self._last_status_at is None:
            self.status_heartbeat_var.set("未收到 STAT：请检查服务端是否启用状态线程")
            message = "已连接但未收到 STAT；请确认树莓派运行 08_L3_threaded_server.py"
        else:
            self.status_heartbeat_var.set("STAT 回传超时，正在等待恢复…")
            message = "STAT 回传超过两个周期未更新"
        if not self._status_timeout_reported:
            self._append_log(f"! {message}")
            self._status_timeout_reported = True

    def _show_status(self, state):
        mode_names = {"M1": "M1 遥控", "M2": "M2 巡检", "M3": "M3 追踪", "M4": "M4 急停"}
        avoidance_names = {
            "CLEAR": "道路畅通",
            "DETECTED": "检测到障碍",
            "STOPPING": "避障中：停车",
            "REVERSING": "避障中：后退",
            "TURNING": "避障中：转向",
            "COMPLETE": "避障完成",
            "INTERRUPTED": "避障被中断",
        }
        self.status_vars["mode"].set(mode_names.get(state.get("mode"), state.get("mode", "--")))
        self.status_vars["speed"].set(f"{state.get('speed', '--')}%")
        avoidance = state.get("avoidance")
        if avoidance in avoidance_names:
            obstacle_text = avoidance_names[avoidance]
        else:
            obstacle_text = "检测到障碍" if state.get("obstacle") else "道路畅通"
        self.status_vars["obstacle"].set(obstacle_text)
        self.status_vars["score"].set(str(state.get("score", "--")))
        self.status_vars["qr"].set(str(state.get("qr", "--")))
        self.status_vars["photo"].set(str(state.get("photo", "--")))
        self.status_vars["mission"].set(str(state.get("mission", "NONE")))
        self.status_vars["progress"].set(str(state.get("progress", "0/0")))

    def _append_log(self, message):
        self.log.configure(state="normal")
        self.log.insert("end", f"{time.strftime('%H:%M:%S')}  {message}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _focus_out(self, _event):
        self.root.after(40, self._stop_if_focus_left)

    def _stop_if_focus_left(self):
        if self._closing:
            return
        try:
            if not self.root.winfo_viewable():
                self._stop()
                return
            focused = self.root.focus_get()
            if focused is not None and focused.winfo_toplevel() == self.root:
                return
            if self._drive_owner and self._drive_owner[0] == "mouse":
                pointer = self.root.winfo_containing(
                    self.root.winfo_pointerx(), self.root.winfo_pointery()
                )
                if pointer is not None and pointer.winfo_toplevel() == self.root:
                    return
            self._stop()
        except tk.TclError:
            self._stop()

    def _on_close(self):
        self._closing = True
        self._release_all_visuals()
        self.network.disconnect(after_flush=False)
        self.root.after(120, self._destroy)

    def _destroy(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass


def main():
    root = tk.Tk()
    RemoteConsole(root)
    root.mainloop()


if __name__ == "__main__":
    main()
