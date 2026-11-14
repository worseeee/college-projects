import serial
import threading
import time

# 定义数据结构：用于封装解析后的传感器数据
class SensorData:
    def __init__(self, node_id, temp, hum, gas, light, pir, relay):
        self.node_id = node_id
        self.temp = temp
        self.hum = hum
        self.gas = gas
        self.light = light
        self.pir = pir
        self.relay = relay

    def __str__(self):
        return (f"[节点 {self.node_id}] "
                f"温湿度:{self.temp}℃ {self.hum}% | "
                f"气体:{self.gas:03d} 光照:{self.light:03d} | "
                f"PIR:{self.pir} 继电器:{self.relay}")

# 核心类：串口传感器管理器
class SerialSensorManager:
    def __init__(self, port='COM3', baud=115200):
        self.port = port
        self.baud = baud
        self.ser = None
        self.running = False

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            self.running = True
            print(f">>> 边缘网关：成功连接到ZigBee协调器 ({self.port})")
            # 开启独立的后台守护线程，专门负责读取串口，避免阻塞主程序
            threading.Thread(target=self._read_loop, daemon=True).start()
        except Exception as e:
            print(f"!!! 串口连接失败: {e}")

    def _read_loop(self):
        """异步读取并解析 12 字节异构协议帧"""
        while self.running:
            if self.ser.in_waiting:
                # 读到 \n (0x0A) 为止
                raw_data = self.ser.readline()
                
                # 严格的长度校验：必须等于 12 字节
                if len(raw_data) == 12:
                    try:
                        # === 严格对应方案 3.2 的拆包逻辑 ===
                        node_id = chr(raw_data[0])              # Byte 0: ASCII
                        temp = raw_data[1]                      # Byte 1: uint8 (直接取整数值)
                        hum = raw_data[2]                       # Byte 2: uint8 (直接取整数值)
                        
                        # Byte 3~5 (气体), Byte 6~8 (光照), 解码为 ASCII 字符串后转 int
                        gas = int(raw_data[3:6].decode('ascii'))
                        light = int(raw_data[6:9].decode('ascii'))
                        
                        # Byte 9 (PIR), Byte 10 (继电器)
                        pir = int(chr(raw_data[9]))
                        relay = int(chr(raw_data[10]))
                        
                        # 组装为对象
                        data_obj = SensorData(node_id, temp, hum, gas, light, pir, relay)
                        print(f"[数据入库] {data_obj}")
                        
                        # TODO: 这里未来会加入触发 YOLO 和 Ollama 的逻辑
                        
                    except Exception as e:
                        print(f"[解析异常] 遇到脏数据 {raw_data.hex()} -> {e}")
                else:
                    # 过滤掉单片机启动时的乱码或长度不对的残缺帧
                    pass 

    def send_command(self, node_id, state):
        """下发继电器控制指令，格式如 'R:1:1' """
        if self.ser and self.ser.is_open:
            cmd_str = f"R:{node_id}:{state}"
            self.ser.write(cmd_str.encode('ascii'))
            print(f"[下发干预] 指令已发送 -> {cmd_str}")

# ================= 单元测试运行入口 =================
if __name__ == "__main__":
    # 注意：运行前请确保关闭“串口调试助手”，否则会提示串口被占用
    # 根据你的截图，串口是 COM3
    mgr = SerialSensorManager(port='COM3')
    mgr.connect()
    
    try:
        while True:
            # 在主线程中模拟云端或按键的控制：每隔 5 秒反转一次继电器
            time.sleep(5)
            print("\n--- 模拟自动下发控制指令 ---")
            mgr.send_command(node_id=1, state=1)  # 开
            time.sleep(5)
            mgr.send_command(node_id=1, state=0)  # 关
            
    except KeyboardInterrupt:
        print("\n>>> 收到退出指令，正在关闭网关...")
        mgr.running = False
        if mgr.ser:
            mgr.ser.close()