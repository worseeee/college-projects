import tkinter as tk
from tkinter import ttk
import serial
import threading
import time
import queue
import json
import cv2
from PIL import Image, ImageTk
import paho.mqtt.client as mqtt

# 导入两大 AI 核心引擎
from vision_core import YoloVisionEngine
from llm_core import OllamaHealthExpert

# ================= 1. 数据结构 =================
class SensorData:
    def __init__(self, node_id, temp, hum, gas, light, pir, relay):
        self.node_id = node_id
        self.temp = temp
        self.hum = hum
        self.gas = gas
        self.light = light
        self.pir = pir
        self.relay = relay

# ================= 2. 串口感知引擎 =================
class SerialSensorManager:
    def __init__(self, data_queue, log_queue, port='COM3', baud=115200):
        self.port = port
        self.baud = baud
        self.ser = None
        self.running = False
        self.data_queue = data_queue
        self.log_queue = log_queue

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            self.running = True
            self.log_queue.put(f"[*] 成功连接到ZigBee ({self.port})")
            threading.Thread(target=self._read_loop, daemon=True).start()
            return True
        except Exception as e:
            self.log_queue.put(f"[!] 串口连接失败: {e}")
            return False

    def _read_loop(self):
        while self.running:
            if self.ser.in_waiting:
                raw_data = self.ser.readline()
                if len(raw_data) == 12:
                    try:
                        node_id = chr(raw_data[0])
                        temp = raw_data[1]
                        hum = raw_data[2]
                        gas = int(raw_data[3:6].decode('ascii'))
                        light = int(raw_data[6:9].decode('ascii'))
                        pir = int(chr(raw_data[9]))
                        relay = int(chr(raw_data[10]))
                        
                        data_obj = SensorData(node_id, temp, hum, gas, light, pir, relay)
                        self.data_queue.put(data_obj)
                    except:
                        pass 

    def send_command(self, node_id, state):
        if self.ser and self.ser.is_open:
            cmd_str = f"R:{node_id}:{state}"
            self.ser.write(cmd_str.encode('ascii'))
            self.log_queue.put(f"[边缘控制] 下发指令 -> {cmd_str}")

# ================= 3. OneNET MQTT 引擎 =================
class OneNetMqttClient:
    def __init__(self, log_queue, mqtt_log_queue):
        self.log_queue = log_queue
        self.mqtt_log_queue = mqtt_log_queue
        self.client = None
        self.connected = False
        self.product_id = ""
        self.device_name = ""

    def connect(self, product_id, device_name, token):
        self.product_id = product_id
        self.device_name = device_name
        self.client = mqtt.Client(client_id=self.device_name)
        self.client.username_pw_set(username=self.product_id, password=token)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        try:
            self.client.connect_async("mqtts.heclouds.com", 1883, 60)
            self.client.loop_start()
            self.log_queue.put("[云端] 尝试连接 OneNET...")
        except Exception as e:
            self.log_queue.put(f"[云端] 连接异常: {e}")

    def disconnect(self):
        if self.client:
            self.client.disconnect()
            self.client.loop_stop()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            self.log_queue.put("[云端] MQTT 成功连接！")
            self.mqtt_log_queue.put("=== 🔗 OneNET 云端链路已就绪 ===")

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False

    def post_property(self, data_obj, ai_status, llm_report=""):
        if not self.connected: return
        topic = f"$sys/{self.product_id}/{self.device_name}/thing/property/post"
        payload = {
            "id": str(int(time.time())), 
            "version": "1.0",
            "params": {
                "temperature": {"value": data_obj.temp},
                "humidity": {"value": data_obj.hum},
                "gas_concentration": {"value": data_obj.gas},
                "illuminance": {"value": data_obj.light},
                "pir_motion": {"value": True if data_obj.pir == 1 else False},
                "relay_control": {"value": True if data_obj.relay == 1 else False},
                "ai_fall_status": {"value": ai_status}
            }
        }
        # 如果大模型生成了报告或短信，附加到物模型中上报
        if llm_report:
            payload["params"]["llm_health_report"] = {"value": llm_report}
            
        json_str = json.dumps(payload)
        self.client.publish(topic, json_str, qos=0)
        self.mqtt_log_queue.put(f"UP ⬆ : {json_str}")

# ================= 4. Tkinter 综合网关界面 =================
class SmartGuardianUI:
    def __init__(self, root):
        self.root = root
        self.root.title("智守夕阳 (SmartGuardian) - 全栈智能网关")
        self.root.geometry("1000x750")
        
        # 队列组
        self.data_queue = queue.Queue()
        self.log_queue = queue.Queue()
        self.mqtt_log_queue = queue.Queue()
        self.vision_queue = queue.Queue()
        self.llm_queue = queue.Queue() # 【新增】大模型流式输出队列
        
        # 后台引擎
        self.sensor_mgr = SerialSensorManager(self.data_queue, self.log_queue, port='COM3')
        self.mqtt_mgr = OneNetMqttClient(self.log_queue, self.mqtt_log_queue)
        
        self.log_queue.put("[系统] 正在后台并发加载 YOLO 视觉与 Ollama 诊疗大脑...")
        # 注意：这里根据你截图里使用的模型名称，我改成了 'qwen3'，如果报错请改回你本地实际拥有的模型名
        self.llm_ai = OllamaHealthExpert(model_name='qwen3')
        self.vision_ai = YoloVisionEngine('yolov8n.pt') 
        
        self.is_vision_running = False 
        self.is_llm_running = False
        
        self.last_cloud_upload_time = 0 
        self.last_pir_state = 0
        self.current_ai_status = 0
        self.cached_latest_data = SensorData('1', 0, 0, 0, 0, 0, 0) # 缓存最新数据供LLM调用
        
        self.setup_ui()
        self.sensor_mgr.connect()
        self.root.after(100, self.process_queues)

    def setup_ui(self):
        self.status_frame = tk.Frame(self.root, bg="#333333", height=40)
        self.status_frame.pack(side=tk.TOP, fill=tk.X)
        self.status_label = tk.Label(self.status_frame, text="系统初始化中...", fg="white", bg="#333333", font=("微软雅黑", 10, "bold"))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # 依次添加各个功能页签
        self.tab_hardware = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_hardware, text=" 硬件感知与控制 ")
        self.init_hardware_tab()
        
        self.tab_vision = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_vision, text=" YOLO视觉与隐私 ")
        self.init_vision_tab()
        
        # 【新增】大模型智护诊疗页
        self.tab_llm = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_llm, text=" 大模型智护诊疗 ")
        self.init_llm_tab()

        self.tab_mqtt = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_mqtt, text=" MQTT云端透传 ")
        self.init_mqtt_tab()
        
        self.tab_log = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_log, text=" 系统全景日志 ")
        self.init_log_tab()

    def init_hardware_tab(self):
        data_frame = tk.LabelFrame(self.tab_hardware, text="节点 1 实时环境遥测", font=("微软雅黑", 10))
        data_frame.pack(fill=tk.X, padx=15, pady=15)
        self.var_temp = tk.StringVar(value="-- ℃")
        self.var_hum = tk.StringVar(value="-- %")
        self.var_gas = tk.StringVar(value="-- ppm")
        self.var_light = tk.StringVar(value="-- Lux")
        self.var_pir = tk.StringVar(value="--")
        self.var_relay = tk.StringVar(value="--")
        labels = [("温度:", self.var_temp), ("湿度:", self.var_hum), ("可燃气体:", self.var_gas), 
                  ("光照:", self.var_light), ("PIR红外:", self.var_pir), ("继电器状态:", self.var_relay)]
        for i, (text, var) in enumerate(labels):
            tk.Label(data_frame, text=text, font=("微软雅黑", 12)).grid(row=i//3, column=(i%3)*2, padx=15, pady=10, sticky="e")
            tk.Label(data_frame, textvariable=var, font=("微软雅黑", 12, "bold"), fg="#0052cc").grid(row=i//3, column=(i%3)*2+1, padx=5, pady=10, sticky="w")

        ctrl_frame = tk.LabelFrame(self.tab_hardware, text="网关控制模式", font=("微软雅黑", 10))
        ctrl_frame.pack(fill=tk.X, padx=15, pady=5)
        self.control_mode = tk.StringVar(value="AUTO")
        tk.Radiobutton(ctrl_frame, text="边缘自动模式 (AI托管)", variable=self.control_mode, value="AUTO", font=("微软雅黑", 10, "bold"), fg="#e67e22").pack(side=tk.LEFT, padx=10, pady=10)
        tk.Radiobutton(ctrl_frame, text="网关手动模式", variable=self.control_mode, value="MANUAL", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(ctrl_frame, text="强制开启干预", bg="#ff4d4d", fg="white", font=("微软雅黑", 10, "bold"), command=lambda: self.manual_control_trigger('1', '1')).pack(side=tk.LEFT, padx=10)
        tk.Button(ctrl_frame, text="强制关闭干预", bg="#4CAF50", fg="white", font=("微软雅黑", 10, "bold"), command=lambda: self.manual_control_trigger('1', '0')).pack(side=tk.LEFT, padx=10)

    def init_vision_tab(self):
        self.lbl_image = tk.Label(self.tab_vision, text="\n\n\n【隐私保护模式】\n摄像头默认休眠，异常时唤醒", bg="black", fg="#00ff00", font=("微软雅黑", 12), width=60, height=15)
        self.lbl_image.pack(pady=20)
        self.var_ai_status = tk.StringVar(value="AI 视觉状态: 待命 (休眠中)")
        tk.Label(self.tab_vision, textvariable=self.var_ai_status, font=("微软雅黑", 14, "bold"), fg="#e67e22").pack(pady=5)
        tk.Button(self.tab_vision, text="🔍 模拟 PIR 异常突变 (强制唤醒视觉)", bg="#0078D7", fg="white", font=("微软雅黑", 12, "bold"), command=self.trigger_vision_async).pack(pady=20)

    # ================= 【新增】大模型智护诊疗页 UI =================
    def init_llm_tab(self):
        # 左侧：RAG 本地病历区
        rag_frame = tk.LabelFrame(self.tab_llm, text="📄 RAG 本地病历库 (已脱敏)", font=("微软雅黑", 10))
        rag_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        rag_text = tk.Text(rag_frame, bg="#f4f4f4", font=("微软雅黑", 10), wrap="word")
        rag_text.insert(tk.END, self.llm_ai.patient_profile)
        rag_text.config(state='disabled')
        rag_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 右侧：流式诊断输出区
        diag_frame = tk.LabelFrame(self.tab_llm, text="🧠 边缘大模型健康研判 (Ollama)", font=("微软雅黑", 10))
        diag_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        btn_frame = tk.Frame(diag_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="生成今日综合健康报告", bg="#9b59b6", fg="white", font=("微软雅黑", 10, "bold"), 
                  command=self.trigger_llm_report_async).pack(side=tk.LEFT, padx=10)
                  
        self.llm_text = tk.Text(diag_frame, bg="#1e1e1e", fg="#00ffff", font=("Consolas", 11), wrap="word")
        self.llm_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.llm_text.insert(tk.END, "等待生成报告...\n")
        self.llm_text.config(state='disabled')

    def init_log_tab(self):
        self.log_text = tk.Text(self.tab_log, state='disabled', bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.log_text.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

    def init_mqtt_tab(self):
        auth_frame = tk.LabelFrame(self.tab_mqtt, text="OneNET 鉴权", font=("微软雅黑", 10))
        auth_frame.pack(fill=tk.X, padx=15, pady=10)
        tk.Label(auth_frame, text="Product ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_pid = tk.Entry(auth_frame, width=15); self.entry_pid.insert(0, "Fh9C41Ytt3"); self.entry_pid.grid(row=0, column=1)
        tk.Label(auth_frame, text="Device Name:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_dname = tk.Entry(auth_frame, width=15); self.entry_dname.insert(0, "Gateway_01"); self.entry_dname.grid(row=0, column=3)
        tk.Label(auth_frame, text="安全 Token:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_token = tk.Entry(auth_frame, width=40, show="*"); self.entry_token.grid(row=1, column=1, columnspan=3)
        tk.Button(auth_frame, text="🚀 一键直连云端", bg="#0078D7", fg="white", font=("微软雅黑", 10, "bold"), 
                  command=lambda: self.mqtt_mgr.connect(self.entry_pid.get(), self.entry_dname.get(), self.entry_token.get())).grid(row=0, column=4, rowspan=2, padx=10)
        json_frame = tk.LabelFrame(self.tab_mqtt, text="JSON 透传", font=("微软雅黑", 10))
        json_frame.pack(expand=True, fill=tk.BOTH, padx=15, pady=5)
        self.mqtt_text = tk.Text(json_frame, state='disabled', bg="#000080", fg="#ffff00", font=("Consolas", 10))
        self.mqtt_text.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

    def manual_control_trigger(self, node_id, state):
        if self.control_mode.get() == "MANUAL": self.sensor_mgr.send_command(node_id, state)
        else: self.log_queue.put("[提示] 处于自动模式，忽略手动指令。")

    def trigger_vision_async(self):
        if self.is_vision_running: return
        self.is_vision_running = True
        self.var_ai_status.set("AI 视觉状态: 正在张量推理...")
        def task():
            status, frame = self.vision_ai.wake_up_and_infer()
            self.vision_queue.put((status, frame))
        threading.Thread(target=task, daemon=True).start()

    # ================= 【核心】大模型异步流式调度 =================
    def trigger_llm_report_async(self):
        if self.is_llm_running:
            self.log_queue.put("[LLM] 报告正在生成中，请耐心等待...")
            return
        self.is_llm_running = True
        self.llm_queue.put("<CLEAR>") # 发送清空指令
        
        def task():
            # 捕获当前环境快照
            d = self.cached_latest_data
            generator = self.llm_ai.generate_diagnostic_report_stream(
                temp=d.temp, hum=d.hum, gas=d.gas, light=d.light, fall_status=self.current_ai_status)
            for chunk in generator:
                self.llm_queue.put(chunk) # 将生成的字逐个推入队列
            self.is_llm_running = False
            self.log_queue.put("[LLM] 今日综合健康研判报告生成完毕。")
            
        threading.Thread(target=task, daemon=True).start()

    def process_queues(self):
        zigbee_status = "已连接" if self.sensor_mgr.running else "未连接"
        cloud_status = "已连接" if self.mqtt_mgr.connected else "未连接"
        color = "green" if self.sensor_mgr.running else "red"
        self.update_status(f"ZigBee: {zigbee_status} | 云端: {cloud_status}", color)

        # 刷新各类文本日志
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')
            
        while not self.mqtt_log_queue.empty():
            msg = self.mqtt_log_queue.get()
            self.mqtt_text.config(state='normal')
            self.mqtt_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            self.mqtt_text.see(tk.END)
            self.mqtt_text.config(state='disabled')

        # 【新增】刷新 LLM 流式报告打字机效果
        while not self.llm_queue.empty():
            chunk = self.llm_queue.get()
            self.llm_text.config(state='normal')
            if chunk == "<CLEAR>":
                self.llm_text.delete(1.0, tk.END)
            else:
                self.llm_text.insert(tk.END, chunk)
                self.llm_text.see(tk.END)
            self.llm_text.config(state='disabled')
            
        # 接收视觉结果，并触发云边极危联动
        while not self.vision_queue.empty():
            status, frame = self.vision_queue.get()
            self.is_vision_running = False
            self.current_ai_status = status
            
            if status == 2:
                self.var_ai_status.set("!!! 极危: 视觉确认发生跌倒 !!!")
                if self.control_mode.get() == "AUTO":
                    self.sensor_mgr.send_command('1', '1') # 物理警报
                    
                # === 核心联动：视觉确诊跌倒 -> 瞬间拉起LLM生成急救短信 -> 打包上云 ===
                def emergency_sms_task():
                    self.log_queue.put("[系统] 正在生成大模型急救短信推向云端...")
                    sms = self.llm_ai.generate_urgent_sms(self.cached_latest_data.temp, self.cached_latest_data.gas, 2)
                    self.log_queue.put(f"[云端告警短信] {sms}")
                    if self.mqtt_mgr.connected:
                        self.mqtt_mgr.post_property(self.cached_latest_data, 2, llm_report=sms)
                threading.Thread(target=emergency_sms_task, daemon=True).start()
                
            elif status == 1:
                self.var_ai_status.set("AI 视觉状态: 目标安全 (活动中)")
            else:
                self.var_ai_status.set("AI 视觉状态: 未见异常目标")

            if frame is not None:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image).resize((480, 320), Image.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                self.lbl_image.imgtk = imgtk 
                self.lbl_image.configure(image=imgtk, text="")
            
        # 处理底层硬件数据与边缘控制防抖
        latest_data = None
        while not self.data_queue.empty():
            latest_data = self.data_queue.get()
            self.cached_latest_data = latest_data # 更新缓存
            
        if latest_data:
            if latest_data.node_id == '1':
                self.var_temp.set(f"{latest_data.temp} ℃")
                self.var_hum.set(f"{latest_data.hum} %")
                self.var_gas.set(f"{latest_data.gas:03d} ppm")
                self.var_light.set(f"{latest_data.light:03d} Lux")
                self.var_pir.set("活动" if latest_data.pir == 1 else "静止")
                self.var_relay.set("开启(干预中)" if latest_data.relay == 1 else "关闭(正常)")

            is_emergency = False
            if self.control_mode.get() == "AUTO":
                if latest_data.gas > 180:
                    is_emergency = True
                    if latest_data.relay == 0: self.sensor_mgr.send_command(latest_data.node_id, '1')
                elif latest_data.gas < 120:
                    if latest_data.relay == 1 and self.current_ai_status != 2: 
                        self.sensor_mgr.send_command(latest_data.node_id, '0')

                # PIR 异常触发视觉
                if self.last_pir_state == 1 and latest_data.pir == 0:
                    self.trigger_vision_async()
                    
            self.last_pir_state = latest_data.pir

            # 云端心跳上报
            if self.mqtt_mgr.connected:
                if time.time() - self.last_cloud_upload_time > 10 or is_emergency:
                    self.mqtt_mgr.post_property(latest_data, self.current_ai_status)
                    self.last_cloud_upload_time = time.time() 

        self.root.after(100, self.process_queues)

    def update_status(self, msg, color):
        self.status_label.config(text=msg, fg=color)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartGuardianUI(root)
    def on_closing():
        app.sensor_mgr.running = False
        app.mqtt_mgr.disconnect()
        if app.sensor_mgr.ser: app.sensor_mgr.ser.close()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()