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
import cv2  
from PIL import Image, ImageTk  
import os
from ultralytics import YOLO

class SerialUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("物联网应用系统综合设计 - 智能视觉与控制网关")
        self.root.geometry("1150x850") 
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # ================= 硬件与网络参数 =================
        self.serial_port = None
        self.is_reading = False
        self.data_queue = queue.Queue()
        # 【修改点】加入了 person_count 用于 AI 数据上云
        self.current_sensor_data = {
            "node_id": 1, "temperature": 0, "humidity": 0,
            "light": 0, "pir": 0, "mq2": 0, "relay_status": 0,
            "person_count": 0 
        }

        self.product_id_http = "J7936UtYPR"  
        self.device_name_http = "http_device_1" 
        self.product_id_mqtt = "3j3CNnOX2C"
        self.device_name_mqtt = "mqtt_device_1"
        self.device_token_http = 'REPLACE_WITH_YOUR_VALUE' 
        self.app_auth = "REPLACE_WITH_ONENET_TOKEN" 
        self.device_token_mqtt = 'REPLACE_WITH_YOUR_VALUE'

        # ================= 视觉与 AI 模型参数 =================
        self.cap = None                 
        self.is_camera_running = False  
        self.photo_count = 0            
        self.last_frame = None          
        self.photo = None               
        
        self.ai_mode = tk.StringVar(value="None")       
        self.img_res = tk.StringVar(value="640x480")    
        
        try:
            print("正在加载 YOLO 模型...")
            self.model_det = YOLO("yolov8n.pt")      
            self.model_seg = YOLO("yolov8n-seg.pt")  
            print("YOLO 模型加载成功！")
        except Exception as e:
            print(f"模型加载失败: {e}")

        # ================= 初始化 =================
        self.init_vars()
        self.setup_ui()
        self.scan_ports()
        
        self.mqtt_client = mqtt.Client(client_id=self.device_name_mqtt)
        self.mqtt_client.username_pw_set(username=self.product_id_mqtt, password=self.device_token_mqtt)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.is_mqtt_connected = False

        self.root.after(100, self.process_queue)
        self.root.after(5000, self.auto_mqtt_report) # 启动5秒自动上报

    def init_vars(self):
        self.port_var = tk.StringVar()
        self.baud_var = tk.StringVar(value="115200")
        self.status_var = tk.StringVar(value="状态: 串口未连接 | MQTT未连接")
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
        work_frame.pack(side=tk.TOP, fill=tk.X)

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
        self.mode_combo.grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=4)

        ttk.Label(ctrl_sub_frame, text="温度(下限-上限):").grid(row=1, column=0, sticky=tk.E, pady=4)
        self.temp_dn_entry = ttk.Entry(ctrl_sub_frame, width=5); self.temp_dn_entry.insert(0, "15"); self.temp_dn_entry.grid(row=1, column=1, padx=2)
        self.temp_up_entry = ttk.Entry(ctrl_sub_frame, width=5); self.temp_up_entry.insert(0, "35"); self.temp_up_entry.grid(row=1, column=2, padx=2)

        ttk.Label(ctrl_sub_frame, text="湿度(下限-上限):").grid(row=2, column=0, sticky=tk.E, pady=4)
        self.hum_dn_entry = ttk.Entry(ctrl_sub_frame, width=5); self.hum_dn_entry.insert(0, "30"); self.hum_dn_entry.grid(row=2, column=1, padx=2)
        self.hum_up_entry = ttk.Entry(ctrl_sub_frame, width=5); self.hum_up_entry.insert(0, "70"); self.hum_up_entry.grid(row=2, column=2, padx=2)

        ttk.Label(ctrl_sub_frame, text="光照/烟雾(上限):").grid(row=3, column=0, sticky=tk.E, pady=4)
        self.light_up_entry = ttk.Entry(ctrl_sub_frame, width=5); self.light_up_entry.insert(0, "800"); self.light_up_entry.grid(row=3, column=1, padx=2)
        self.mq2_up_entry = ttk.Entry(ctrl_sub_frame, width=5); self.mq2_up_entry.insert(0, "150"); self.mq2_up_entry.grid(row=3, column=2, padx=2)

        relay_frame = ttk.Frame(ctrl_sub_frame)
        relay_frame.grid(row=4, column=0, columnspan=3, pady=6)
        ttk.Label(relay_frame, text="继电器状态: ").pack(side=tk.LEFT)
        ttk.Label(relay_frame, textvariable=self.relay_var, font=("微软雅黑", 10, "bold"), foreground="#cc0000").pack(side=tk.LEFT)

        btn_frame = ttk.Frame(ctrl_sub_frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=4)
        ttk.Button(btn_frame, text="手动开启", command=lambda: self.manual_relay_control(1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="手动关闭", command=lambda: self.manual_relay_control(0)).pack(side=tk.LEFT, padx=5)

        protocol_frame1 = ttk.Frame(cloud_frame)
        protocol_frame1.pack(fill=tk.X, pady=2)
        self.btn_mqtt_conn = ttk.Button(protocol_frame1, text="MQTT 连接云端", command=self.mqtt_connect)
        self.btn_mqtt_conn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(protocol_frame1, text="手动触发上报", command=self.mqtt_post_property).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        protocol_frame2 = ttk.Frame(cloud_frame)
        protocol_frame2.pack(fill=tk.X, pady=2)
        ttk.Button(protocol_frame2, text="HTTP 上报(POST)", command=self.http_post_data).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(protocol_frame2, text="HTTP 查询(GET)", command=self.http_get_data).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # ================= 视觉与 AI 控制区 =================
        vision_frame = ttk.LabelFrame(self.root, text="YOLOv8 视觉监控与 AI 识别区", padding=10)
        vision_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        self.canvas = tk.Canvas(vision_frame, width=640, height=480, bg="black")
        self.canvas.pack(side=tk.LEFT, padx=10, pady=5)
        
        cam_ctrl_frame = ttk.Frame(vision_frame)
        cam_ctrl_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.btn_start_cam = tk.Button(cam_ctrl_frame, text="▶ 启动摄像头", bg="#4CAF50", fg="white", font=("微软雅黑", 10), command=self.start_camera)
        self.btn_start_cam.pack(fill=tk.X, pady=5)
        self.btn_stop_cam = tk.Button(cam_ctrl_frame, text="⏹ 关闭摄像头", bg="#f44336", fg="white", font=("微软雅黑", 10), command=self.stop_camera, state=tk.DISABLED)
        self.btn_stop_cam.pack(fill=tk.X, pady=5)
        self.btn_capture = tk.Button(cam_ctrl_frame, text="📸 抓拍保存图片", bg="#2196F3", fg="white", font=("微软雅黑", 10), command=self.capture_photo, state=tk.DISABLED)
        self.btn_capture.pack(fill=tk.X, pady=5)

        ttk.Separator(cam_ctrl_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Label(cam_ctrl_frame, text="选择 AI 模式:", font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, pady=2)
        tk.Radiobutton(cam_ctrl_frame, text="原图预览 (关闭AI)", variable=self.ai_mode, value="None").pack(anchor=tk.W)
        tk.Radiobutton(cam_ctrl_frame, text="人流量检测 (yolov8n)", variable=self.ai_mode, value="Detect").pack(anchor=tk.W)
        tk.Radiobutton(cam_ctrl_frame, text="人流量分割 (yolov8n-seg)", variable=self.ai_mode, value="Segment").pack(anchor=tk.W)
        
        ttk.Label(cam_ctrl_frame, text="输入分辨率:", font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, pady=(10,2))
        res_combo = ttk.Combobox(cam_ctrl_frame, textvariable=self.img_res, values=["320x240", "640x480", "1280x720"], state="readonly")
        res_combo.pack(fill=tk.X)

        # 底部：日志区
        log_frame = ttk.LabelFrame(self.root, text="系统与接收日志", padding=10)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=5, font=("Consolas", 10), bg="#f4f4f4")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Button(log_frame, text="清空\n日志", command=lambda: self.log_text.delete(1.0, tk.END)).pack(side=tk.RIGHT, fill=tk.Y, padx=5)

    def create_sensor_label(self, parent, text, var, row):
        ttk.Label(parent, text=text, font=("微软雅黑", 12)).grid(row=row, column=0, sticky=tk.E, pady=10, padx=10)
        ttk.Label(parent, textvariable=var, font=("微软雅黑", 12, "bold"), foreground="#0052cc").grid(row=row, column=1, sticky=tk.W, pady=10)

    # ================== 摄像头与 YOLOv8 逻辑 ==================
    def start_camera(self):
        if not self.is_camera_running:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("硬件错误", "无法打开摄像头！")
                return
            self.is_camera_running = True
            self.btn_start_cam.config(state=tk.DISABLED)
            self.btn_stop_cam.config(state=tk.NORMAL)
            self.btn_capture.config(state=tk.NORMAL)
            self.log_sys("成功启动摄像头预览！")
            self.update_camera_frame()

    def stop_camera(self):
        self.is_camera_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.canvas.delete("all")
        self.btn_start_cam.config(state=tk.NORMAL)
        self.btn_stop_cam.config(state=tk.DISABLED)
        self.btn_capture.config(state=tk.DISABLED)
        self.current_sensor_data["person_count"] = 0 # 关掉摄像头重置人数
        self.log_sys("已关闭摄像头。")

    def capture_photo(self):
        if not self.is_camera_running or self.last_frame is None: return
        self.photo_count += 1
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"capture_{timestamp}_{self.photo_count}.jpg"
        cv2.imwrite(filename, self.last_frame)
        self.log_sys(f"📸 抓拍成功！图片已保存为: {filename}")

    def update_camera_frame(self):
        """核心：视频流读取 + YOLO 推理 + 提取人数用于上云"""
        if not self.is_camera_running: return

        ret, frame = self.cap.read()
        if ret:
            start_time = time.time()
            mode = self.ai_mode.get()
            target_w, target_h = map(int, self.img_res.get().split('x'))
            inference_time = 0.0
            person_count = 0 # 初始化当前帧人数

            if mode == "None":
                annotated_frame = frame.copy()
            else:
                model = self.model_det if mode == "Detect" else self.model_seg
                # 【修改点】：限制 classes=[0] 只识别“人”
                results = model(frame, imgsz=target_w, classes=[0], verbose=False)
                annotated_frame = results[0].plot()
                inference_time = results[0].speed['inference']
                
                # 【修改点】：提取当前画面中检测到的人数，并更新到传感器字典中，供 MQTT 读取
                if results[0].boxes is not None:
                    person_count = len(results[0].boxes)
            
            # 更新全局变量，MQTT 定时上报会读取这个值
            self.current_sensor_data["person_count"] = person_count

            total_time = time.time() - start_time
            fps = 1.0 / total_time if total_time > 0 else 0

            # 叠加 OSD 信息
            cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"Inf Time: {inference_time:.1f} ms", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"Persons: {person_count}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            self.last_frame = annotated_frame.copy()
            
            cv2_im = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            cv2_im = cv2.resize(cv2_im, (640, 480))
            pil_im = Image.fromarray(cv2_im)
            self.photo = ImageTk.PhotoImage(image=pil_im)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            
        self.root.after(30, self.update_camera_frame)

    # ================== 通信与控制逻辑 ==================
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
            self.btn_open.config(state=tk.DISABLED)
            self.btn_close.config(state=tk.NORMAL)
            threading.Thread(target=self.serial_read_thread, daemon=True).start()
            self.status_var.set(f"状态: 已连接串口 {port} | MQTT未连接")
            self.log_sys(f"成功打开串口 {port}")
        except Exception as e: messagebox.showerror("错误", f"无法打开串口 {port}")

    def close_serial(self):
        self.is_reading = False
        time.sleep(0.1)
        if self.serial_port and self.serial_port.is_open: self.serial_port.close()
        self.btn_open.config(state=tk.NORMAL)
        self.btn_close.config(state=tk.DISABLED)
        self.status_var.set("状态: 串口已断开")

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
                self.parse_data(msg)
        except queue.Empty: pass
        finally:
            self.root.after(100, self.process_queue)

    def parse_data(self, raw_str):
        if len(raw_str) != 12: return
        try:
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
        except ValueError: pass

    def manual_relay_control(self, status):
        self.current_sensor_data["relay_status"] = status
        self.relay_var.set("开启 (ON)" if status == 1 else "关闭 (OFF)")

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
            self.log_sys("✅ MQTT 连接成功！AI 数据已打通上云通道。")
            self.btn_mqtt_conn.config(text=" MQTT 断开连接")
            self.status_var.set(self.status_var.get().replace("MQTT未连接", "MQTT已在线"))
            
            # 订阅回复通道，用于检测属性上报是否成功
            topic_prop_reply = f"$sys/{self.product_id_mqtt}/{self.device_name_mqtt}/thing/property/post/reply"
            self.mqtt_client.subscribe(topic_prop_reply)
        else:
            self.log_sys(f"❌ MQTT 连接被拒绝，错误码: {rc}")

    def on_mqtt_disconnect(self, client, userdata, rc):
        self.is_mqtt_connected = False
        self.log_sys("⚠️ MQTT 已断开连接。")
        self.btn_mqtt_conn.config(text="MQTT 连接云端")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            if "property/post/reply" in msg.topic:
                if payload.get("code") != 200:
                    self.log_sys(f"❌ 云端拒收属性！原因: {payload.get('msg')} (错误码:{payload.get('code')})")
        except: pass

    def auto_mqtt_report(self):
        """【修改点】：每5秒自动将包含人流量数据的 Payload 上报"""
        if self.is_mqtt_connected:
            self.mqtt_post_property(is_auto=True)
        self.root.after(5000, self.auto_mqtt_report)

    def _build_standard_payload(self):
        """【修改点】：加入 person_count (当前人流量)"""
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
                "control_mode": {"value": 1 if self.mode_combo.get() == "自动模式" else 0},
                "person_count": {"value": int(self.current_sensor_data.get("person_count", 0))} # AI 上云核心！
            }
        }

    def mqtt_post_property(self, is_auto=False):
        if not self.is_mqtt_connected: return
        topic = f"$sys/{self.product_id_mqtt}/{self.device_name_mqtt}/thing/property/post"
        payload = self._build_standard_payload()
        self.mqtt_client.publish(topic, json.dumps(payload), qos=1)
        if not is_auto: 
            self.log_sys(f"⬆️ MQTT 属性已手动上报。当前人数：{self.current_sensor_data['person_count']}")

    def http_post_data(self):
        pass
    def http_get_data(self):
        pass

    def log_sys(self, msg):
        self.log_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [SYS] {msg}\n")
        self.log_text.see(tk.END)

    def on_closing(self):
        self.stop_camera()
        if self.is_reading: self.close_serial()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    ttk.Style().theme_use('clam') 
    app = SerialUIApp(root)
    root.mainloop()