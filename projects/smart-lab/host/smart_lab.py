import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import serial
import serial.tools.list_ports
import threading
import time
import sqlite3
from datetime import datetime
import queue
import os

try:
    import winsound
    AUDIO_BACKEND = 'winsound'
except ImportError:
    try:
        import pygame
        pygame.mixer.init()
        AUDIO_BACKEND = 'pygame'
    except ImportError:
        AUDIO_BACKEND = None
        print("警告: 未安装音频库，报警铃声功能不可用")

class AlarmSound:
    def __init__(self):
        self.alarm_file = None
        self.is_playing = False
        self.stop_flag = False
        self.play_thread = None
    
    def set_alarm_file(self, filepath):
        if os.path.exists(filepath):
            self.alarm_file = filepath
            return True
        return False
    
    def play_alarm(self, loop=True):
        if self.is_playing:
            return
        
        self.stop_flag = False
        self.is_playing = True
        
        self.play_thread = threading.Thread(target=self._play_loop, args=(loop,), daemon=True)
        self.play_thread.start()
    
    def _play_loop(self, loop):
        while not self.stop_flag:
            try:
                if AUDIO_BACKEND == 'winsound':
                    if self.alarm_file and os.path.exists(self.alarm_file):
                        winsound.PlaySound(self.alarm_file, winsound.SND_FILENAME)
                    else:
                        winsound.Beep(1000, 500)
                        time.sleep(0.3)
                        winsound.Beep(1500, 500)
                        time.sleep(0.3)
                elif AUDIO_BACKEND == 'pygame':
                    if self.alarm_file and os.path.exists(self.alarm_file):
                        pygame.mixer.music.load(self.alarm_file)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy() and not self.stop_flag:
                            time.sleep(0.1)
                    else:
                        time.sleep(1)
                else:
                    print('\a')
                    time.sleep(1)
            except Exception as e:
                print(f"播放音频错误: {e}")
                time.sleep(1)
            
            if not loop:
                break
            time.sleep(0.5)
        
        self.is_playing = False
    
    def stop_alarm(self):
        self.stop_flag = True
        if AUDIO_BACKEND == 'winsound':
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except:
                pass
        elif AUDIO_BACKEND == 'pygame':
            try:
                pygame.mixer.music.stop()
            except:
                pass

class SerialManager:
    FRAME_HEADER = 0xAA
    FRAME_TAIL = 0x55
    FRAME_SIZE = 11  
    
    CMD_HEARTBEAT = 0x01
    CMD_PIR_DETECTED = 0x02
    CMD_BORROW_REQUEST = 0x03
    CMD_RETURN_REQUEST = 0x04
    CMD_OPEN_LOCK = 0x10
    CMD_CLOSE_LOCK = 0x11
    CMD_STATUS_QUERY = 0x20
    CMD_TEMP_HUMIDITY = 0x30
    CMD_SMOKE_ALARM = 0x40
    CMD_SMOKE_CLEAR = 0x41
    CMD_SMOKE_DATA = 0x42
    
    def __init__(self):
        self.serial_port = None
        self.is_running = False
        self.rx_thread = None
        self.data_queue = queue.Queue()
    
    def connect(self, port, baudrate=115200):
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=0.5
            )
            self.is_running = True
            self.rx_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.rx_thread.start()
            return True, "串口连接成功"
        except Exception as e:
            return False, f"串口连接失败: {str(e)}"
    
    def disconnect(self):
        self.is_running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
    
    def _receive_loop(self):
        buffer = bytearray()
        
        while self.is_running:
            try:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    buffer.extend(data)
                    
                    while len(buffer) >= self.FRAME_SIZE:
                        if buffer[0] != self.FRAME_HEADER:
                            buffer.pop(0)
                            continue
                        
                        if len(buffer) < self.FRAME_SIZE:
                            break
                        
                        frame = bytes(buffer[:self.FRAME_SIZE])
                        buffer = buffer[self.FRAME_SIZE:]
                        
                        self._parse_frame(frame)
                        
                time.sleep(0.01)
            except Exception as e:
                print(f"接收错误: {e}")
    
    def _parse_frame(self, frame):
        
        if frame[10] != self.FRAME_TAIL:
            print(f"帧尾错误: {frame.hex()}")
            return False
        
        checksum = sum(frame[:9]) & 0xFF
        if checksum != frame[9]:
            print(f"校验和错误: 计算={checksum:02X}, 收到={frame[9]:02X}")
            return False
    
        smoke_value = (frame[7] << 8) | frame[8]
        
        data = {
            'node_id': frame[2],
            'cmd': frame[3],
            'status': frame[4],
            'temperature': frame[5],
            'humidity': frame[6],
            'smoke_value': smoke_value,
            'timestamp': time.time(),
            'raw': frame.hex().upper()
        }
        
        self.data_queue.put(data)
        return True
    
    def get_data(self):
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None
    
    def send_command(self, node_id, cmd, status=0, temp=0, humi=0, smoke_h=0, smoke_l=0):
    
        frame = bytearray(self.FRAME_SIZE)
        frame[0] = self.FRAME_HEADER
        frame[1] = 7  
        frame[2] = node_id
        frame[3] = cmd
        frame[4] = status
        frame[5] = temp
        frame[6] = humi
        frame[7] = smoke_h
        frame[8] = smoke_l
        frame[9] = sum(frame[:9]) & 0xFF  # 校验和
        frame[10] = self.FRAME_TAIL
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(frame)
            print(f"发送: {frame.hex().upper()}")
            return True
        return False
    
    @staticmethod
    def list_ports():
        return [port.device for port in serial.tools.list_ports.comports()]

class DatabaseManager:
    def __init__(self, db_file='smart_lab.db'):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self.lock = threading.Lock()
        self.init_database()
    
    def init_database(self):

        if os.path.exists(self.db_file):
            try:
                os.remove(self.db_file)
                print(f"已删除旧数据库: {self.db_file}")
            except:
                pass
        
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                device_id INTEGER PRIMARY KEY,
                device_name TEXT NOT NULL,
                device_model TEXT,
                cabinet_id INTEGER,
                status TEXT DEFAULT '在库',
                current_borrower TEXT,
                last_borrow_time TEXT,
                last_return_time TEXT,
                borrow_count INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS borrow_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cabinet_id INTEGER,
                device_id INTEGER,
                borrower_name TEXT,
                student_id TEXT,
                borrow_time TEXT,
                return_time TEXT,
                duration INTEGER,
                status TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cabinet_status (
                cabinet_id INTEGER PRIMARY KEY,
                node_id INTEGER,
                online_status TEXT DEFAULT '离线',
                current_status TEXT DEFAULT 'IDLE',
                temperature REAL DEFAULT 0,
                humidity REAL DEFAULT 0,
                smoke_value INTEGER DEFAULT 0,
                last_heartbeat TEXT,
                pir_trigger_count INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alarm_records (
                alarm_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cabinet_id INTEGER,
                alarm_type TEXT,
                alarm_value INTEGER,
                alarm_time TEXT,
                clear_time TEXT,
                status TEXT
            )
        ''')
        
        self.conn.commit()
        print("数据库初始化完成")
    
    def update_cabinet_status(self, cabinet_id, **kwargs):
        with self.lock:
            try:
                self.cursor.execute('SELECT * FROM cabinet_status WHERE cabinet_id = ?', (cabinet_id,))
                if not self.cursor.fetchone():
                    self.cursor.execute('''
                        INSERT INTO cabinet_status (cabinet_id, node_id, online_status, smoke_value)
                        VALUES (?, ?, '在线', 0)
                    ''', (cabinet_id, cabinet_id))
                
                if kwargs:
                    fields = []
                    values = []
                    for key, value in kwargs.items():
                        fields.append(f"{key} = ?")
                        values.append(value)
                    
                    values.append(cabinet_id)
                    query = f"UPDATE cabinet_status SET {', '.join(fields)} WHERE cabinet_id = ?"
                    self.cursor.execute(query, values)
                
                self.conn.commit()
            except Exception as e:
                print(f"数据库更新错误: {e}")
    
    def record_alarm(self, cabinet_id, alarm_type, alarm_value):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self.lock:
            self.cursor.execute('''
                INSERT INTO alarm_records (cabinet_id, alarm_type, alarm_value, alarm_time, status)
                VALUES (?, ?, ?, ?, '报警中')
            ''', (cabinet_id, alarm_type, alarm_value, now))
            self.conn.commit()
            return self.cursor.lastrowid
    
    def clear_alarm(self, cabinet_id):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self.lock:
            self.cursor.execute('''
                UPDATE alarm_records SET clear_time = ?, status = '已解除'
                WHERE cabinet_id = ? AND status = '报警中'
            ''', (now, cabinet_id))
            self.conn.commit()
    
    def get_cabinet_list(self):
        with self.lock:
            self.cursor.execute('SELECT * FROM cabinet_status')
            return self.cursor.fetchall()
    
    def get_borrow_records(self, limit=100):
        with self.lock:
            self.cursor.execute('''
                SELECT * FROM borrow_records 
                ORDER BY borrow_time DESC LIMIT ?
            ''', (limit,))
            return self.cursor.fetchall()
    
    def record_borrow(self, cabinet_id, device_id, borrower, student_id):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self.lock:
            self.cursor.execute('''
                INSERT INTO borrow_records 
                (cabinet_id, device_id, borrower_name, student_id, borrow_time, status)
                VALUES (?, ?, ?, ?, ?, '借出中')
            ''', (cabinet_id, device_id, borrower, student_id, now))
            self.conn.commit()
            return self.cursor.lastrowid
    
    def record_return(self, record_id):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self.lock:
            self.cursor.execute('''
                SELECT device_id, borrow_time FROM borrow_records WHERE record_id = ?
            ''', (record_id,))
            result = self.cursor.fetchone()
            
            if result:
                device_id, borrow_time = result
                borrow_dt = datetime.strptime(borrow_time, '%Y-%m-%d %H:%M:%S')
                return_dt = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                duration = int((return_dt - borrow_dt).total_seconds() / 60)
                
                self.cursor.execute('''
                    UPDATE borrow_records 
                    SET return_time = ?, duration = ?, status = '已归还'
                    WHERE record_id = ?
                ''', (now, duration, record_id))
                self.conn.commit()
                return True
        return False
    
    def add_device(self, device_name, device_model, cabinet_id):
        try:
            with self.lock:
                self.cursor.execute('''
                    INSERT INTO devices (device_name, device_model, cabinet_id, status)
                    VALUES (?, ?, ?, '在库')
                ''', (device_name, device_model, cabinet_id))
                self.conn.commit()
            return True, "设备添加成功"
        except Exception as e:
            return False, f"添加失败: {str(e)}"

class AlarmDialog(tk.Toplevel):
    def __init__(self, parent, node_id, smoke_value, on_close=None):
        super().__init__(parent)
        
        self.on_close = on_close
        self.flash_state = True
        self.is_cleared = False  
        self.node_id = node_id   
        
        self.title("🚨 紧急警报 🚨")
        self.geometry("500x350")
        self.configure(bg='red')
        
        self.transient(parent)
        self.grab_set()
        self.attributes('-topmost', True)
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 350) // 2
        self.geometry(f"+{x}+{y}")
        
        self.create_content(node_id, smoke_value)
        self.flash()
        
        self.protocol("WM_DELETE_WINDOW", self.close_dialog)
    
    def create_content(self, node_id, smoke_value):
        self.icon_label = tk.Label(self, text="🔥", font=('Arial', 80), bg='red', fg='yellow')
        self.icon_label.pack(pady=10)
        
        self.title_label = tk.Label(self, text="⚠️ 烟雾报警 ⚠️", 
                                    font=('黑体', 28, 'bold'), bg='red', fg='white')
        self.title_label.pack(pady=10)
        
        info_text = f"设备柜 {node_id} 检测到烟雾！\n烟雾浓度: {smoke_value}"
        self.info_label = tk.Label(self, text=info_text,
                                   font=('黑体', 18), bg='red', fg='white')
        self.info_label.pack(pady=10)
        
        self.time_label = tk.Label(self, 
                                   text=f"报警时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                   font=('Arial', 14), bg='red', fg='white')
        self.time_label.pack(pady=5)
        
        self.countdown_label = tk.Label(self, text="", font=('Arial', 12), bg='red', fg='white')
        self.countdown_label.pack(pady=5)
        
        self.btn_frame = tk.Frame(self, bg='red')
        self.btn_frame.pack(pady=20)
        
        self.ack_btn = tk.Button(self.btn_frame, text="确认报警", 
                                 font=('黑体', 16, 'bold'),
                                 bg='yellow', fg='red',
                                 width=15, height=2,
                                 command=self.close_dialog)
        self.ack_btn.pack()
    
    def show_alarm_cleared(self, smoke_value):

        if not self.winfo_exists():
            return
            
        self.is_cleared = True
        
        self.configure(bg='#2E7D32')  
        self.title("✅ 警报解除 ✅")
        
        self.icon_label.configure(text="✅", bg='#2E7D32', fg='white')
        
        self.title_label.configure(text="✅ 警报已解除 ✅", bg='#2E7D32', fg='white')
        
        self.info_label.configure(
            text=f"设备柜 {self.node_id} 烟雾已恢复正常\n当前浓度: {smoke_value}",
            bg='#2E7D32', fg='white'
        )
        
        self.time_label.configure(
            text=f"解除时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            bg='#2E7D32', fg='white'
        )
        
        self.countdown_label.configure(bg='#2E7D32', fg='yellow')
        
        self.btn_frame.configure(bg='#2E7D32')
        self.ack_btn.configure(text="关闭窗口", bg='white', fg='#2E7D32')
        
        self.start_countdown(5)
    
    def start_countdown(self, seconds):

        if not self.winfo_exists():
            return
            
        if seconds > 0:
            self.countdown_label.configure(text=f"窗口将在 {seconds} 秒后自动关闭")
            self.after(1000, lambda: self.start_countdown(seconds - 1))
        else:
            self.close_dialog()
    
    def flash(self):
        if not self.winfo_exists():
            return
        
        if self.is_cleared:
            return
            
        if self.flash_state:
            self.configure(bg='red')
            self.icon_label.configure(bg='red')
            self.title_label.configure(bg='red')
            self.info_label.configure(bg='red')
            self.time_label.configure(bg='red')
            self.countdown_label.configure(bg='red')
            self.btn_frame.configure(bg='red')
        else:
            self.configure(bg='orange')
            self.icon_label.configure(bg='orange')
            self.title_label.configure(bg='orange')
            self.info_label.configure(bg='orange')
            self.time_label.configure(bg='orange')
            self.countdown_label.configure(bg='orange')
            self.btn_frame.configure(bg='orange')
        
        self.flash_state = not self.flash_state
        self.after(300, self.flash)
    
    def close_dialog(self):
        if self.on_close:
            self.on_close(self.node_id)  
        self.destroy()
        
class SmartLabGUI:
    
    SMOKE_ALARM_THRESHOLD = 1200  
    SMOKE_CLEAR_THRESHOLD = 1000  
    
    def __init__(self, root):
        self.root = root
        self.root.title("智能实验室设备借还管理系统")
        self.root.geometry("1400x900")
        
        self.db_manager = DatabaseManager()
        self.serial_manager = SerialManager()
        self.alarm_sound = AlarmSound()
        
        self.cabinet_status = {}
        self.active_alarms = {}
        self.alarm_dialogs = {}  
        
        self.create_widgets()
        self.poll_serial_data()
        self.update_timer()
    
    def create_widgets(self):
        
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        system_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="系统", menu=system_menu)
        system_menu.add_command(label="连接串口", command=self.connect_serial)
        system_menu.add_command(label="断开串口", command=self.disconnect_serial)
        system_menu.add_separator()
        system_menu.add_command(label="设置报警铃声", command=self.set_alarm_sound)
        system_menu.add_command(label="测试报警", command=self.test_alarm)
        system_menu.add_separator()
        system_menu.add_command(label="退出", command=self.root.quit)
        
        device_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设备管理", menu=device_menu)
        device_menu.add_command(label="添加设备", command=self.add_device_dialog)
        device_menu.add_command(label="设备列表", command=self.show_device_list)
        
        
        main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_frame = ttk.Frame(main_frame)
        main_frame.add(left_frame, weight=1)
        
        right_frame = ttk.Frame(main_frame)
        main_frame.add(right_frame, weight=2)
        
    
        cabinet_label = ttk.LabelFrame(left_frame, text="设备柜实时状态", padding=10)
        cabinet_label.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.cabinet_tree = ttk.Treeview(cabinet_label, 
                                         columns=('id', 'status', 'temp', 'humi', 'smoke', 'online'),
                                         show='headings', height=15)
        self.cabinet_tree.heading('id', text='柜号')
        self.cabinet_tree.heading('status', text='状态')
        self.cabinet_tree.heading('temp', text='温度℃')
        self.cabinet_tree.heading('humi', text='湿度%')
        self.cabinet_tree.heading('smoke', text='烟雾值')
        self.cabinet_tree.heading('online', text='在线')
        
        self.cabinet_tree.column('id', width=50, anchor='center')
        self.cabinet_tree.column('status', width=70)
        self.cabinet_tree.column('temp', width=60, anchor='center')
        self.cabinet_tree.column('humi', width=60, anchor='center')
        self.cabinet_tree.column('smoke', width=70, anchor='center')
        self.cabinet_tree.column('online', width=50, anchor='center')
        
        scrollbar = ttk.Scrollbar(cabinet_label, orient=tk.VERTICAL, 
                                  command=self.cabinet_tree.yview)
        self.cabinet_tree.configure(yscroll=scrollbar.set)
        
        self.cabinet_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="开锁", command=self.open_lock).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关锁", command=self.close_lock).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="查询", command=self.query_status).pack(side=tk.LEFT, padx=5)
        
        self.alarm_frame = ttk.LabelFrame(left_frame, text="报警状态", padding=10)
        self.alarm_frame.pack(fill=tk.X, pady=5)
        
        self.alarm_label = tk.Label(self.alarm_frame, text="✅ 系统正常", 
                                    font=('黑体', 14), fg='green')
        self.alarm_label.pack()
        
        self.stop_alarm_btn = ttk.Button(self.alarm_frame, text="停止报警音", 
                                         command=self.stop_alarm, state='disabled')
        self.stop_alarm_btn.pack(pady=5)
        
        operation_frame = ttk.LabelFrame(right_frame, text="借还操作", padding=10)
        operation_frame.pack(fill=tk.X, pady=5)
        
        form_frame = ttk.Frame(operation_frame)
        form_frame.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="设备柜号:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_cabinet_id = ttk.Entry(form_frame, width=15)
        self.entry_cabinet_id.grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="学号:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.entry_student_id = ttk.Entry(form_frame, width=15)
        self.entry_student_id.grid(row=0, column=3, padx=5)
        
        ttk.Label(form_frame, text="姓名:").grid(row=0, column=4, sticky=tk.W, pady=5)
        self.entry_name = ttk.Entry(form_frame, width=15)
        self.entry_name.grid(row=0, column=5, padx=5)
        
        ttk.Button(form_frame, text="确认借出", command=self.handle_borrow, 
                  width=12).grid(row=0, column=6, padx=10)
        ttk.Button(form_frame, text="确认归还", command=self.handle_return,
                  width=12).grid(row=0, column=7, padx=5)
        
        record_frame = ttk.LabelFrame(right_frame, text="最近借还记录", padding=10)
        record_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.record_tree = ttk.Treeview(record_frame,
                                        columns=('id', 'cabinet', 'name', 'student', 
                                                'borrow', 'return', 'status'),
                                        show='headings', height=8)
        
        for col, text, width in [('id', 'ID', 50), ('cabinet', '柜号', 50),
                                  ('name', '姓名', 80), ('student', '学号', 100),
                                  ('borrow', '借出时间', 140), ('return', '归还时间', 140),
                                  ('status', '状态', 70)]:
            self.record_tree.heading(col, text=text)
            self.record_tree.column(col, width=width, anchor='center')
        
        record_scroll = ttk.Scrollbar(record_frame, orient=tk.VERTICAL,
                                      command=self.record_tree.yview)
        self.record_tree.configure(yscroll=record_scroll.set)
        
        self.record_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        record_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        log_frame = ttk.LabelFrame(right_frame, text="系统日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, 
                                                   state='disabled', wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_text.tag_configure('ALARM', foreground='red', font=('黑体', 10, 'bold'))
        self.log_text.tag_configure('WARN', foreground='orange')
        self.log_text.tag_configure('SUCCESS', foreground='green')
        self.log_text.tag_configure('INFO', foreground='black')
        
        self.status_bar = ttk.Label(self.root, text="系统就绪 | 串口: 未连接", 
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.refresh_cabinet_list()
        self.refresh_record_list()
    
    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, log_entry, level)
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        
        print(log_entry.strip())
    
    def poll_serial_data(self):
        while True:
            data = self.serial_manager.get_data()
            if data is None:
                break
            self.process_serial_data(data)
        
        self.root.after(50, self.poll_serial_data)
    
    def process_serial_data(self, data):
        node_id = data['node_id']
        cmd = data['cmd']
        smoke_value = data.get('smoke_value', 0)
        
        self.cabinet_status[node_id] = data
        
        self.log(f"收到: {data['raw']} (节点:{node_id}, cmd:0x{cmd:02X}, 烟雾:{smoke_value})")
        
        self.db_manager.update_cabinet_status(
            node_id, 
            online_status='在线',
            temperature=data['temperature'],
            humidity=data['humidity'],
            smoke_value=smoke_value,
            last_heartbeat=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        if cmd == SerialManager.CMD_HEARTBEAT:
            self.log(f"设备柜 {node_id} 心跳 (烟雾:{smoke_value})")
        
        elif cmd == SerialManager.CMD_PIR_DETECTED:
            self.log(f"⚠️ 设备柜 {node_id} 检测到人体活动!", 'WARN')
            self.show_pir_dialog(node_id)
        
        elif cmd == SerialManager.CMD_TEMP_HUMIDITY:
            temp = data['temperature']
            humi = data['humidity']
            self.log(f"设备柜 {node_id} 温度:{temp}℃ 湿度:{humi}% 烟雾:{smoke_value}")
        
        elif cmd == SerialManager.CMD_SMOKE_DATA:
            self.log(f"设备柜 {node_id} 烟雾浓度: {smoke_value}")
    
            if smoke_value > self.SMOKE_ALARM_THRESHOLD and node_id not in self.active_alarms:
                self.log(f"🔥 烟雾超标！浓度 {smoke_value} > 阈值 {self.SMOKE_ALARM_THRESHOLD}", 'ALARM')
                self.handle_smoke_alarm(node_id, smoke_value)
            elif smoke_value < self.SMOKE_CLEAR_THRESHOLD and node_id in self.active_alarms:
                self.handle_smoke_clear(node_id)
        
        elif cmd == SerialManager.CMD_SMOKE_ALARM:
            self.log(f"🔥🔥🔥 设备柜 {node_id} 烟雾报警！浓度: {smoke_value}", 'ALARM')
            self.handle_smoke_alarm(node_id, smoke_value)
        
        elif cmd == SerialManager.CMD_SMOKE_CLEAR:
            self.log(f"✅ 设备柜 {node_id} 烟雾报警解除，浓度: {smoke_value}", 'SUCCESS')
            self.handle_smoke_clear(node_id)
        
        elif cmd == SerialManager.CMD_BORROW_REQUEST:
            self.log(f"设备柜 {node_id} 借出确认", 'SUCCESS')
        
        elif cmd == SerialManager.CMD_RETURN_REQUEST:
            self.log(f"设备柜 {node_id} 归还确认", 'SUCCESS')
        
        self.refresh_cabinet_list()
    
    def handle_smoke_alarm(self, node_id, smoke_value):
        if node_id in self.active_alarms:
            return  
        
        self.active_alarms[node_id] = {
            'time': datetime.now(),
            'value': smoke_value
        }
        
        self.db_manager.record_alarm(node_id, 'SMOKE', smoke_value)
        
        self.alarm_label.config(text=f"🔥 设备柜 {node_id} 烟雾报警！浓度:{smoke_value}", fg='red')
        self.stop_alarm_btn.config(state='normal')
        
        self.alarm_sound.play_alarm(loop=True)
        
        dialog = AlarmDialog(self.root, node_id, smoke_value, 
                            on_close=self.on_alarm_dialog_closed)
        self.alarm_dialogs[node_id] = dialog
    
    def handle_smoke_clear(self, node_id):

        smoke_value = 0
        if node_id in self.cabinet_status:
            smoke_value = self.cabinet_status[node_id].get('smoke_value', 0)
        
        if node_id in self.alarm_dialogs:
            try:
                dialog = self.alarm_dialogs[node_id]
                if dialog.winfo_exists():
                    dialog.show_alarm_cleared(smoke_value)
                    self.log(f"设备柜 {node_id} 警报解除弹窗已更新，5秒后自动关闭", 'SUCCESS')
            except Exception as e:
                print(f"更新弹窗错误: {e}")
        
        if node_id in self.active_alarms:
            del self.active_alarms[node_id]
        
        self.db_manager.clear_alarm(node_id)
        
        if not self.active_alarms:
            self.alarm_label.config(text="✅ 系统正常", fg='green')
            self.stop_alarm_btn.config(state='disabled')
            self.alarm_sound.stop_alarm()
            
    def on_alarm_dialog_closed(self, node_id):
        if node_id in self.alarm_dialogs:
            del self.alarm_dialogs[node_id]
        self.log(f"设备柜 {node_id} 的报警弹窗已关闭")
        
    def on_alarm_acknowledged(self):
        pass
    
    def stop_alarm(self):
        self.alarm_sound.stop_alarm()
        self.log("报警音已停止", 'INFO')
    
    def set_alarm_sound(self):
        filepath = filedialog.askopenfilename(
            title="选择报警音文件",
            filetypes=[("WAV文件", "*.wav"), ("MP3文件", "*.mp3"), ("所有文件", "*.*")]
        )
        if filepath:
            if self.alarm_sound.set_alarm_file(filepath):
                self.log(f"报警音已设置: {filepath}", 'SUCCESS')
                messagebox.showinfo("成功", f"报警音已设置为:\n{filepath}")
    
    def test_alarm(self):
        self.log("测试报警触发", 'ALARM')
        self.handle_smoke_alarm(99, 9999)
    
    def show_pir_dialog(self, node_id):
        try:
            self.root.bell()
        except:
            pass
        
        result = messagebox.askyesno(
            "🚨 检测到活动", 
            f"设备柜 {node_id} 检测到人体活动！\n\n是否开锁?",
            icon='warning'
        )
        
        if result:
            self.serial_manager.send_command(node_id, SerialManager.CMD_OPEN_LOCK)
            self.log(f"发送开锁命令到设备柜 {node_id}")
    
    def connect_serial(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("选择串口")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="选择串口:").pack(pady=10)
        
        ports = SerialManager.list_ports()
        port_combo = ttk.Combobox(dialog, values=ports, state='readonly', width=25)
        port_combo.pack(pady=5)
        if ports:
            port_combo.current(0)
        
        def do_connect():
            port = port_combo.get()
            if port:
                success, msg = self.serial_manager.connect(port)
                if success:
                    self.log(msg, 'SUCCESS')
                    self.status_bar.config(text=f"系统运行 | 串口: {port}")
                    dialog.destroy()
                else:
                    messagebox.showerror("错误", msg)
        
        ttk.Button(dialog, text="连接", command=do_connect).pack(pady=10)
    
    def disconnect_serial(self):
        self.serial_manager.disconnect()
        self.log("串口已断开")
        self.status_bar.config(text="系统就绪 | 串口: 未连接")
    
    def open_lock(self):
        selected = self.cabinet_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择设备柜")
            return
        
        item = self.cabinet_tree.item(selected[0])
        cabinet_id = int(item['values'][0])
        
        if self.serial_manager.send_command(cabinet_id, SerialManager.CMD_OPEN_LOCK):
            self.log(f"发送开锁命令到设备柜 {cabinet_id}")
        else:
            messagebox.showerror("错误", "串口未连接")
    
    def close_lock(self):
        selected = self.cabinet_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择设备柜")
            return
        
        item = self.cabinet_tree.item(selected[0])
        cabinet_id = int(item['values'][0])
        
        if self.serial_manager.send_command(cabinet_id, SerialManager.CMD_CLOSE_LOCK):
            self.log(f"发送关锁命令到设备柜 {cabinet_id}")
        else:
            messagebox.showerror("错误", "串口未连接")
    
    def query_status(self):
        if self.serial_manager.send_command(0xFF, SerialManager.CMD_STATUS_QUERY):
            self.log("查询所有设备柜状态")
        else:
            messagebox.showerror("错误", "串口未连接")
    
    def handle_borrow(self):
        cabinet_id = self.entry_cabinet_id.get()
        student_id = self.entry_student_id.get()
        name = self.entry_name.get()
        
        if not all([cabinet_id, student_id, name]):
            messagebox.showwarning("提示", "请填写完整信息")
            return
        
        try:
            cabinet_id = int(cabinet_id)
            self.serial_manager.send_command(cabinet_id, SerialManager.CMD_OPEN_LOCK)
            self.db_manager.record_borrow(cabinet_id, cabinet_id, name, student_id)
            
            self.log(f"{name}({student_id}) 借出设备柜 {cabinet_id}", 'SUCCESS')
            messagebox.showinfo("成功", "借出登记成功,设备柜已开锁")
            
            self.entry_cabinet_id.delete(0, tk.END)
            self.entry_student_id.delete(0, tk.END)
            self.entry_name.delete(0, tk.END)
            
            self.refresh_record_list()
        except ValueError:
            messagebox.showerror("错误", "柜号必须为数字")
    
    def handle_return(self):
        cabinet_id = self.entry_cabinet_id.get()
        
        if not cabinet_id:
            messagebox.showwarning("提示", "请填写设备柜号")
            return
        
        try:
            cabinet_id = int(cabinet_id)
            
            self.db_manager.cursor.execute('''
                SELECT record_id FROM borrow_records 
                WHERE cabinet_id = ? AND status = '借出中'
                ORDER BY borrow_time DESC LIMIT 1
            ''', (cabinet_id,))
            result = self.db_manager.cursor.fetchone()
            
            if result:
                record_id = result[0]
                self.serial_manager.send_command(cabinet_id, SerialManager.CMD_CLOSE_LOCK)
                self.db_manager.record_return(record_id)
                
                self.log(f"设备柜 {cabinet_id} 归还成功", 'SUCCESS')
                messagebox.showinfo("成功", "归还登记成功,设备柜已关锁")
                
                self.entry_cabinet_id.delete(0, tk.END)
                self.refresh_record_list()
            else:
                messagebox.showwarning("提示", "该设备柜没有未归还记录")
        except ValueError:
            messagebox.showerror("错误", "柜号必须为数字")
    
    def refresh_cabinet_list(self):
        existing_items = {}
        for item_id in self.cabinet_tree.get_children():
            item = self.cabinet_tree.item(item_id)
            if item['values']:  
                node_id = item['values'][0]
                existing_items[node_id] = item_id
        
        for node_id, data in self.cabinet_status.items():
            status = '报警' if node_id in self.active_alarms else 'IDLE'
            temp = data.get('temperature', '-')
            humi = data.get('humidity', '-')
            smoke = data.get('smoke_value', '-')
            online = '在线' if time.time() - data['timestamp'] < 30 else '离线'
            
            values = (node_id, status, temp, humi, smoke, online)
            
            if node_id in existing_items:
                item_id = existing_items[node_id]
                self.cabinet_tree.item(item_id, values=values)
                
                if node_id in self.active_alarms:
                    self.cabinet_tree.item(item_id, tags=('alarm',))
                else:
                    self.cabinet_tree.item(item_id, tags=())
                
                del existing_items[node_id]
            else:
                item_id = self.cabinet_tree.insert('', tk.END, values=values)
                if node_id in self.active_alarms:
                    self.cabinet_tree.item(item_id, tags=('alarm',))
        
        self.cabinet_tree.tag_configure('alarm', background='red', foreground='white')
    
    def refresh_record_list(self):
        for item in self.record_tree.get_children():
            self.record_tree.delete(item)
        
        records = self.db_manager.get_borrow_records(50)
        for rec in records:
            self.record_tree.insert('', tk.END, values=(
                rec[0], rec[1], rec[3], rec[4], rec[5], rec[6] or '-', rec[8]
            ))
    
    def add_device_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("添加设备")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        
        ttk.Label(dialog, text="设备名称:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="设备型号:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        model_entry = ttk.Entry(dialog, width=30)
        model_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="设备柜号:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        cabinet_entry = ttk.Entry(dialog, width=30)
        cabinet_entry.grid(row=2, column=1, padx=10, pady=10)
        
        def do_add():
            name = name_entry.get()
            model = model_entry.get()
            cabinet = cabinet_entry.get()
            
            if name and cabinet:
                try:
                    success, msg = self.db_manager.add_device(name, model, int(cabinet))
                    if success:
                        messagebox.showinfo("成功", msg)
                        dialog.destroy()
                    else:
                        messagebox.showerror("错误", msg)
                except ValueError:
                    messagebox.showerror("错误", "柜号必须为数字")
        
        ttk.Button(dialog, text="确定", command=do_add).grid(row=3, column=0, columnspan=2, pady=20)
    
    def show_device_list(self):
        list_window = tk.Toplevel(self.root)
        list_window.title("设备列表")
        list_window.geometry("800x600")
        
        tree = ttk.Treeview(list_window, 
                           columns=('id', 'name', 'model', 'cabinet', 'status', 'borrower', 'count'),
                           show='headings')
        
        for col, text in [('id', '设备ID'), ('name', '设备名称'), ('model', '型号'),
                          ('cabinet', '柜号'), ('status', '状态'), ('borrower', '当前借用人'),
                          ('count', '借用次数')]:
            tree.heading(col, text=text)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.db_manager.cursor.execute('SELECT * FROM devices')
        devices = self.db_manager.cursor.fetchall()
        
        for dev in devices:
            tree.insert('', tk.END, values=(
                dev[0], dev[1], dev[2], dev[3], dev[4], dev[5] or '-', dev[8]
            ))
    
    def update_timer(self):
        current_time = time.time()
        for node_id, data in list(self.cabinet_status.items()):
            if current_time - data['timestamp'] > 30:
                self.log(f"设备柜 {node_id} 离线", 'WARN')
        
        self.refresh_cabinet_list()
        self.root.after(5000, self.update_timer)


def main():
    root = tk.Tk()
    app = SmartLabGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
