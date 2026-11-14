import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial
import serial.tools.list_ports
import threading
import queue
import json
import time
import datetime
import requests
import paho.mqtt.client as mqtt

class SerialUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("物联网应用系统综合设计 - 智能控制台")
        self.root.geometry("1000x680")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 串口对象与多线程控制
        self.serial_port = None
        self.is_reading = False
        self.data_queue = queue.Queue()
        
        # 缓存解析后的最新传感器数据及状态
        self.current_sensor_data = {
            "node_id": 1, "temperature": 0, "humidity": 0,
            "light": 0, "pir": 0, "mq2": 0, "relay_status": 0
        }

        # OneNET 平台配置参数
        self.product_id_http = "J7936UtYPR"  
        self.device_name_http = "http_device_1" 
        self.product_id_mqtt = "3j3CNnOX2C"
        self.device_name_mqtt = "mqtt_device_1"
        self.device_token_http = 'REPLACE_WITH_YOUR_VALUE' 
        self.app_auth = "REPLACE_WITH_ONENET_TOKEN" 
        self.device_token_mqtt = 'REPLACE_WITH_YOUR_VALUE'

        self.init_vars()
        self.setup_ui()
        self.scan_ports()
        
        # --- MQTT 客户端初始化 ---
        self.mqtt_client = mqtt.Client(client_id=self.device_name_mqtt)
        self.mqtt_client.username_pw_set(username=self.product_id_mqtt, password=self.device_token_mqtt)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.is_mqtt_connected = False

        # 启动主线程的队列定时轮询 (每100ms)
        self.root.after(100, self.process_queue)
        
        # 【新增】启动 MQTT 自动上报循环 (每5000ms = 5秒)
        self.root.after(5000, self.auto_mqtt_report)

    def init_vars(self):
        self.port_var = tk.StringVar()
        self.baud_var = tk.StringVar(value="115200")
        self.status_var = tk.StringVar(value="状态: 未连接")
        
        self.temp_var = tk.StringVar(value="-- ℃")
        self.hum_var = tk.StringVar(value="-- %")
        self.light_var = tk.StringVar(value="-- lx")
        self.pir_var = tk.StringVar(value="未知")
        self.mq2_var = tk.StringVar(value="-- (原始值)")
        self.relay_var = tk.StringVar(value="关闭 (OFF)")

    def setup_ui(self):
        status_frame = ttk.Frame(self.root, padding=5)
        status_frame.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(status_frame, textvariable=self.status_var, font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT)

        work_frame = ttk.Frame(self.root, padding=10)
        work_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 1. 串口配置区
        serial_frame = ttk.LabelFrame(work_frame, text="串口配置", padding=10)
        serial_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        ttk.Label(serial_frame, text="串口号:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.port_combo = ttk.Combobox(serial_frame, textvariable=self.port_var, width=12, state="readonly")
        self.port_combo.grid(row=0, column=1, pady=5)
        ttk.Button(serial_frame, text="刷新", command=self.scan_ports, width=6).grid(row=0, column=2, padx=5)

        ttk.Label(serial_frame, text="波特率:").grid(row=1, column=0, sticky=tk.W, pady=5)
        baud_combo = ttk.Combobox(serial_frame, textvariable=self.baud_var, width=12, state="readonly")
        baud_combo['values'] = ("9600", "38400", "57600", "115200")
        baud_combo.grid(row=1, column=1, pady=5)

        self.btn_open = ttk.Button(serial_frame, text="打开串口", command=self.open_serial)
        self.btn_open.grid(row=2, column=0, columnspan=3, pady=15, sticky=tk.EW)
        self.btn_close = ttk.Button(serial_frame, text="关闭串口", command=self.close_serial, state=tk.DISABLED)
        self.btn_close.grid(row=3, column=0, columnspan=3, pady=5, sticky=tk.EW)

        # 2. 传感器数据显示区
        sensor_frame = ttk.LabelFrame(work_frame, text="本地数据监测", padding=10)
        sensor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.create_sensor_label(sensor_frame, "温度 (T):", self.temp_var, 0)
        self.create_sensor_label(sensor_frame, "湿度 (H):", self.hum_var, 1)
        self.create_sensor_label(sensor_frame, "光照 (L):", self.light_var, 2)
        self.create_sensor_label(sensor_frame, "红外 (P):", self.pir_var, 3)
        self.create_sensor_label(sensor_frame, "烟雾 (M):", self.mq2_var, 4)

        # 3. 控制策略与云平台区
        cloud_frame = ttk.LabelFrame(work_frame, text="控制策略与云平台", padding=10)
        cloud_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        ctrl_sub_frame = ttk.LabelFrame(cloud_frame, text="多维阈值管理与联动", padding=8)
        ctrl_sub_frame.pack(fill=tk.X, pady=5)

        ttk.Label(ctrl_sub_frame, text="模式:").grid(row=0, column=0, sticky=tk.E, pady=4)
        self.mode_combo = ttk.Combobox(ctrl_sub_frame, values=["手动模式", "自动模式"], width=10, state="readonly")
        self.mode_combo.current(0)
        self.mode_combo.bind("<<ComboboxSelected>>", lambda e: self.sync_data_to_cloud())
        self.mode_combo.grid(row=0, column=1, columnspan=3, sticky=tk.W, pady=4)

        ttk.Label(ctrl_sub_frame, text="温度(下限-上限):").grid(row=1, column=0, sticky=tk.E, pady=4)
        self.temp_dn_entry = ttk.Entry(ctrl_sub_frame, width=5); self.temp_dn_entry.insert(0, "15"); self.temp_dn_entry.grid(row=1, column=1, padx=2)
        self.temp_up_entry = ttk.Entry(ctrl_sub_frame, width=5); self.temp_up_entry.insert(0, "35"); self.temp_up_entry.grid(row=1, column=2, padx=2)

        ttk.Label(ctrl_sub_frame, text="湿度(下限-上限):").grid(row=2, column=0, sticky=tk.E, pady=4)
        self.hum_dn_entry = ttk.Entry(ctrl_sub_frame, width=5); self.hum_dn_entry.insert(0, "30"); self.hum_dn_entry.grid(row=2, column=1, padx=2)
        self.hum_up_entry = ttk.Entry(ctrl_sub_frame, width=5); self.hum_up_entry.insert(0, "70"); self.hum_up_entry.grid(row=2, column=2, padx=2)

        ttk.Label(ctrl_sub_frame, text="光照/烟雾(上限):").grid(row=3, column=0, sticky=tk.E, pady=4)
        self.light_up_entry = ttk.Entry(ctrl_sub_frame, width=5); self.light_up_entry.insert(0, "800"); self.light_up_entry.grid(row=3, column=1, padx=2)
        self.mq2_up_entry = ttk.Entry(ctrl_sub_frame, width=5); self.mq2_up_entry.insert(0, "150"); self.mq2_up_entry.grid(row=3, column=2, padx=2)

        ttk.Label(ctrl_sub_frame, text="继电器状态:").grid(row=4, column=0, sticky=tk.E, pady=6)
        ttk.Label(ctrl_sub_frame, textvariable=self.relay_var, font=("微软雅黑", 10, "bold"), foreground="#cc0000").grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=6)

        btn_frame = ttk.Frame(ctrl_sub_frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=4)
        ttk.Button(btn_frame, text="手动开启", command=lambda: self.manual_relay_control(1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="手动关闭", command=lambda: self.manual_relay_control(0)).pack(side=tk.LEFT, padx=5)

        # 协议控制区
        mqtt_btn_frame = ttk.Frame(cloud_frame)
        mqtt_btn_frame.pack(fill=tk.X, pady=5)
        self.btn_mqtt_conn = ttk.Button(mqtt_btn_frame, text="MQTT 连接云端", command=self.mqtt_connect)
        self.btn_mqtt_conn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        # 将原来手动上报按钮的名字改一下，以区分自动上报
        ttk.Button(mqtt_btn_frame, text="手动触发上报", command=self.mqtt_post_property).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        http_btn_frame = ttk.Frame(cloud_frame)
        http_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(http_btn_frame, text="HTTP 上报(POST)", command=self.http_post_data).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(http_btn_frame, text="HTTP 查询(GET)", command=self.http_get_data).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # 底部：日志区
        log_frame = ttk.LabelFrame(self.root, text="系统与接收日志", padding=10)
        log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, font=("Consolas", 10), bg="#f4f4f4")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Button(log_frame, text="清空\n日志", command=lambda: self.log_text.delete(1.0, tk.END)).pack(side=tk.RIGHT, fill=tk.Y, padx=5)

    def create_sensor_label(self, parent, text, var, row):
        ttk.Label(parent, text=text, font=("微软雅黑", 12)).grid(row=row, column=0, sticky=tk.E, pady=10, padx=10)
        ttk.Label(parent, textvariable=var, font=("微软雅黑", 12, "bold"), foreground="#0052cc").grid(row=row, column=1, sticky=tk.W, pady=10)

    # ================== 本地与串口控制逻辑 ==================
    def scan_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combo['values'] = [port.device for port in ports]
        if self.port_combo['values']: self.port_combo.current(0)

    def open_serial(self):
        port = self.port_var.get(); baud = self.baud_var.get()
        if not port: return
        try:
            self.serial_port = serial.Serial(port, int(baud), timeout=1)
            self.is_reading = True
            self.status_var.set(f"状态: 已连接 {port} @ {baud}")
            self.btn_open.config(state=tk.DISABLED)
            self.btn_close.config(state=tk.NORMAL)
            threading.Thread(target=self.serial_read_thread, daemon=True).start()
            self.log_sys(f"成功打开串口 {port}")
        except Exception as e: messagebox.showerror("错误", f"无法打开串口 {port}")

    def close_serial(self):
        self.is_reading = False
        time.sleep(0.1)
        if self.serial_port and self.serial_port.is_open: self.serial_port.close()
        self.status_var.set("状态: 未连接")
        self.btn_open.config(state=tk.NORMAL)
        self.btn_close.config(state=tk.DISABLED)

    def serial_read_thread(self):
        while self.is_reading and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    raw_data = self.serial_port.readline()
                    try:
                        decoded = raw_data.decode('utf-8').strip()
                        if decoded: self.data_queue.put(decoded)
                    except: pass
            except:
                self.data_queue.put("ERROR:DISCONNECTED")
                break
            time.sleep(0.01)

    def process_queue(self):
        try:
            while not self.data_queue.empty():
                msg = self.data_queue.get_nowait()
                if msg == "ERROR:DISCONNECTED":
                    self.close_serial(); continue
                self.log_rx(msg)
                self.parse_data(msg)
        except queue.Empty: pass
        finally:
            self.root.after(100, self.process_queue)

    def parse_data(self, raw_str):
        if len(raw_str) != 12: return
        try:
            self.current_sensor_data["node_id"] = int(raw_str[0])
            self.current_sensor_data["temperature"] = int(raw_str[1:3])
            self.current_sensor_data["humidity"] = int(raw_str[3:5])
            self.current_sensor_data["mq2"] = int(raw_str[5:8])
            self.current_sensor_data["light"] = int(raw_str[8:11])
            self.current_sensor_data["pir"] = int(raw_str[11])
            
            self.temp_var.set(f'{self.current_sensor_data["temperature"]} ℃')
            self.hum_var.set(f'{self.current_sensor_data["humidity"]} %')
            self.mq2_var.set(f'{self.current_sensor_data["mq2"]} (0-255)')
            self.light_var.set(f'{self.current_sensor_data["light"]} lx')
            self.pir_var.set("有人" if self.current_sensor_data["pir"] == 1 else "无人")
            
            # --- 自动模式越界检测与事件触发 ---
            if self.mode_combo.get() == "自动模式":
                try:
                    t_dn = int(self.temp_dn_entry.get()); t_up = int(self.temp_up_entry.get())
                    h_dn = int(self.hum_dn_entry.get()); h_up = int(self.hum_up_entry.get())
                    l_up = int(self.light_up_entry.get()); m_up = int(self.mq2_up_entry.get())
                    
                    is_alert = (self.current_sensor_data["temperature"] < t_dn or self.current_sensor_data["temperature"] > t_up or 
                                self.current_sensor_data["humidity"] < h_dn or self.current_sensor_data["humidity"] > h_up or 
                                self.current_sensor_data["light"] > l_up or self.current_sensor_data["mq2"] > m_up)
                    
                    if is_alert:
                        if self.current_sensor_data["relay_status"] == 0:
                            self.log_sys("[自动控制] 检测到传感器越界，报警开启！")
                            self.execute_relay_control(1)
                            # 触发云端事件上报 (Event Post)
                            self.mqtt_post_event("Env_Alert", "环境参数越界告警！")
                    else:
                        if self.current_sensor_data["relay_status"] == 1:
                            self.log_sys("[自动控制] 数据恢复正常，报警解除。")
                            self.execute_relay_control(0)
                except ValueError: pass
        except ValueError: pass

    def manual_relay_control(self, status):
        if self.mode_combo.get() == "自动模式":
            messagebox.showwarning("提示", "当前处于[自动模式]，请先切换回[手动模式]！")
            return
        self.execute_relay_control(status)

    def execute_relay_control(self, status):
        """核心：改变本地状态并下发单片机"""
        self.current_sensor_data["relay_status"] = status
        self.relay_var.set("开启 (ON)" if status == 1 else "关闭 (OFF)")
        
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(f"R:{status}\n".encode('utf-8'))
                self.log_sys(f"已向下位机下发继电器指令: R:{status}")
            except Exception as e: self.log_sys(f"串口下发失败: {e}")
            
        self.sync_data_to_cloud()

    def sync_data_to_cloud(self):
        """优先使用 MQTT 上报，如未连接则退回 HTTP"""
        if self.is_mqtt_connected:
            self.mqtt_post_property()
        else:
            self.http_post_data()

    # ================== MQTT 核心双向协议实现 ==================
    def mqtt_connect(self):
        if not self.is_mqtt_connected:
            self.log_sys("正在连接 OneNET MQTT 服务器...")
            try:
                self.mqtt_client.connect("mqtts.heclouds.com", 1883, 60)
                self.mqtt_client.loop_start()
            except Exception as e: self.log_sys(f"MQTT 连接失败: {e}")
        else:
            self.mqtt_client.loop_stop(); self.mqtt_client.disconnect()

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.is_mqtt_connected = True
            self.log_sys("✅ MQTT 连接成功！")
            self.btn_mqtt_conn.config(text=" MQTT 断开连接")
            
            # --- 核心：连接成功后，立刻订阅各类 Topic ---
            topic_set = f"$sys/{self.product_id_mqtt}/{self.device_name_mqtt}/thing/property/set"
            self.mqtt_client.subscribe(topic_set)
            self.log_sys(f"已订阅云端下发控制通道: {topic_set}")

            topic_event_reply = f"$sys/{self.product_id_mqtt}/{self.device_name_mqtt}/thing/event/post/reply"
            self.mqtt_client.subscribe(topic_event_reply)

            topic_prop_reply = f"$sys/{self.product_id_mqtt}/{self.device_name_mqtt}/thing/property/post/reply"
            self.mqtt_client.subscribe(topic_prop_reply)
        else:
            self.log_sys(f"❌ MQTT 连接被拒绝，错误码: {rc}")

    def on_mqtt_disconnect(self, client, userdata, rc):
        self.is_mqtt_connected = False
        self.log_sys("⚠️ MQTT 已断开连接。")
        self.btn_mqtt_conn.config(text="MQTT 连接云端")

    def on_mqtt_message(self, client, userdata, msg):
        """接收云端主动下发的指令 (Property Set) 及各项回复"""
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            if "event/post/reply" in msg.topic:
                if payload.get("code") == 200:
                    self.log_sys("✅ 云端确认：事件上报格式完全正确，已被成功接收！")
                else:
                    self.log_sys(f"❌ 云端拒收事件！原因: {payload.get('msg')} (错误码:{payload.get('code')})")
                return 
            
            if "property/post/reply" in msg.topic:
                # 自动上报的频率很高，这里屏蔽 200 成功的日志，防止刷屏。只在出错时提醒。
                if payload.get("code") != 200:
                    self.log_sys(f"❌ 云端拒收属性！原因: {payload.get('msg')} (错误码:{payload.get('code')})")
                return
            
            self.log_sys(f"⬇️ 收到云端指令: {payload}")
            
            # 检查云端是否想控制继电器 (relay_status)
            if "params" in payload and "relay_status" in payload["params"]:
                target_status = int(payload["params"]["relay_status"])
                
                # 涉及 UI 更新，必须委托给主线程执行，防止跨线程崩溃
                self.root.after(0, self._handle_cloud_command, target_status, payload.get("id"))
                
        except Exception as e:
            self.log_sys(f"云端指令解析失败: {e}")

    def _handle_cloud_command(self, target_status, msg_id):
        """在主 UI 线程中执行云端指令并回复"""
        if self.mode_combo.get() == "自动模式":
            self.log_sys("被拒绝：云端尝试下发控制，但设备处于本地[自动模式]保护中！")
            self._reply_to_cloud(msg_id, 400, "Device in Auto Mode")
            return
            
        self.log_sys(f"执行云端下发指令 -> 继电器状态改为: {target_status}")
        self.execute_relay_control(target_status) 
        
        # 必须回复确认消息，否则云端会显示“下发超时”
        self._reply_to_cloud(msg_id, 200, "success")

    def _reply_to_cloud(self, msg_id, code, msg):
        """向云端发送 Property Set Reply 确认报文"""
        reply_topic = f"$sys/{self.product_id_mqtt}/{self.device_name_mqtt}/thing/property/set_reply"
        reply_payload = {"id": msg_id, "code": code, "msg": msg}
        self.mqtt_client.publish(reply_topic, json.dumps(reply_payload))
        self.log_sys("⬆️ 已向云端发送指令执行确认 (Reply)。")

    # 【新增】非阻塞定时自动上报功能
    def auto_mqtt_report(self):
        """每隔5秒自动触发一次 MQTT 属性上报"""
        if self.is_mqtt_connected:
            self.mqtt_post_property(is_auto=True)
            
        # 再次装填定时器，实现死循环
        self.root.after(5000, self.auto_mqtt_report)

    def mqtt_post_property(self, is_auto=False):
        """MQTT 协议：属性上报"""
        if not self.is_mqtt_connected: return
        topic = f"$sys/{self.product_id_mqtt}/{self.device_name_mqtt}/thing/property/post"
        payload = self._build_standard_payload()
        self.mqtt_client.publish(topic, json.dumps(payload), qos=1)
        
        # 如果是手动点击按钮，打印日志；如果是自动循环，静默发送防止刷屏
        if not is_auto:
            self.log_sys("⬆️ MQTT 属性已手动上报。")

    def mqtt_post_event(self, event_name, desc):
        """MQTT 协议：事件上报 (Event Post)"""
        if not self.is_mqtt_connected: return
        topic = f"$sys/{self.product_id_mqtt}/{self.device_name_mqtt}/thing/event/post"
        
        payload = {
            "id": str(int(time.time())),
            "version": "1.0",
            # 【重要修复】：此处必须是 events，绝不能是 params
            "events": {
                event_name: {
                    "value": { "description": desc, "temperature": self.current_sensor_data["temperature"], "humidity": self.current_sensor_data["humidity"], "light": self.current_sensor_data["light"], "mq2": self.current_sensor_data["mq2"] },
                    "time": int(time.time() * 1000) 
                }
            }
        }
        
        try:
            json_str = json.dumps(payload)
            self.mqtt_client.publish(topic, json_str, qos=1)
            self.log_sys(f"🚨 已向云端上报紧急事件: {event_name}")
        except Exception as e:
            self.log_sys(f"事件上报打包失败: {e}")

    def _build_standard_payload(self):
        return {
            "id": str(int(time.time())), "version": "1.0",
            "params": {
                "node_id": {"value": int(self.current_sensor_data.get("node_id", 0))},
                "temperature": {"value": int(self.current_sensor_data.get("temperature", 0))},
                "humidity": {"value": int(self.current_sensor_data.get("humidity", 0))},
                "light": {"value": int(self.current_sensor_data.get("light", 0))},
                "pir": {"value": int(self.current_sensor_data.get("pir", 0))},
                "mq2": {"value": int(self.current_sensor_data.get("mq2", 0))},
                "relay_status": {"value": int(self.current_sensor_data.get("relay_status", 0))},
                "control_mode": {"value": 1 if self.mode_combo.get() == "自动模式" else 0}
            }
        }

    # ================== HTTP 兼容回退逻辑 ==================
    def http_post_data(self):
        topic = f"$sys/{self.product_id_http}/{self.device_name_http}/thing/property/post"
        url = f"https://open.iot.10086.cn/fuse/http/device/thing/property/post?topic={topic}&protocol=http"
        headers = {"Content-Type": "application/json", "token": self.device_token_http}
        threading.Thread(target=lambda: requests.post(url, headers=headers, json=self._build_standard_payload()), daemon=True).start()

    def http_get_data(self):
        url = f"https://iot-api.heclouds.com/thingmodel/query-device-property?product_id={self.product_id_http}&device_name={self.device_name_http}"
        headers = {"Content-Type": "application/json", "authorization": self.app_auth}
        threading.Thread(target=lambda: self.log_sys(f"\n{json.dumps(requests.get(url, headers=headers).json(), indent=2)}"), daemon=True).start()

    def log_sys(self, msg):
        self.log_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [SYS] {msg}\n")
        self.log_text.see(tk.END)

    def log_rx(self, msg):
        self.log_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [RX] {msg}\n")
        self.log_text.see(tk.END)

    def on_closing(self):
        if self.is_reading: self.close_serial()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    ttk.Style().theme_use('clam') 
    app = SerialUIApp(root)
    root.mainloop()