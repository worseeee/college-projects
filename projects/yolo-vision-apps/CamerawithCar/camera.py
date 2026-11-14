import tkinter as tk
from tkinter import Canvas, Label, messagebox, filedialog, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import time
from pathlib import Path
from ultralytics import YOLO

# 加载YOLO模型
model1 = YOLO("yolov8n.pt")

class VehicleTracker:
    def __init__(self):
        self.next_id = 0
        self.tracked_vehicles = {}
        self.max_disappeared = 30
        self.max_distance = 100
        
    def update(self, detections):
        if len(detections) == 0:
            for vehicle_id in list(self.tracked_vehicles.keys()):
                self.tracked_vehicles[vehicle_id]['disappeared'] += 1
                if self.tracked_vehicles[vehicle_id]['disappeared'] > self.max_disappeared:
                    del self.tracked_vehicles[vehicle_id]
            return {}
        
        if len(self.tracked_vehicles) == 0:
            for detection in detections:
                self.register(detection)
        else:
            vehicle_ids = list(self.tracked_vehicles.keys())
            vehicle_centroids = [self.tracked_vehicles[vehicle_id]['centroid'] for vehicle_id in vehicle_ids]
            
            D = np.linalg.norm(np.array(vehicle_centroids)[:, np.newaxis] - np.array(detections), axis=2)
            
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_row_idxs = set()
            used_col_idxs = set()
            
            for (row, col) in zip(rows, cols):
                if row in used_row_idxs or col in used_col_idxs:
                    continue
                if D[row, col] > self.max_distance:
                    continue
                    
                vehicle_id = vehicle_ids[row]
                self.tracked_vehicles[vehicle_id]['centroid'] = detections[col]
                self.tracked_vehicles[vehicle_id]['disappeared'] = 0
                
                used_row_idxs.add(row)
                used_col_idxs.add(col)
            
            unused_row_idxs = set(range(0, D.shape[0])).difference(used_row_idxs)
            unused_col_idxs = set(range(0, D.shape[1])).difference(used_col_idxs)
            
            if D.shape[0] >= D.shape[1]:
                for row in unused_row_idxs:
                    vehicle_id = vehicle_ids[row]
                    self.tracked_vehicles[vehicle_id]['disappeared'] += 1
                    if self.tracked_vehicles[vehicle_id]['disappeared'] > self.max_disappeared:
                        del self.tracked_vehicles[vehicle_id]
            else:
                for col in unused_col_idxs:
                    self.register(detections[col])
        
        return self.tracked_vehicles
    
    def register(self, centroid):
        self.tracked_vehicles[self.next_id] = {
            'centroid': centroid,
            'disappeared': 0
        }
        self.next_id += 1

class MyWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("智能车流量双向检测系统 (Auto-Lane Detection)")
        self.root.geometry("1100x700")  # 扩大窗口以容纳控制面板
        self.root.configure(bg="#f0f0f0")

        self.camera = cv2.VideoCapture(0)
        self.photo = tk.PhotoImage()
        self.snapshot_count = 0
        
        # 车流量检测与轨迹状态
        self.vehicle_tracker = VehicleTracker()
        self.vehicle_count_in = 0    
        self.vehicle_count_out = 0   
        self.current_vehicles = 0    
        self.vehicle_positions = {}  
        self.is_capturing = False   
        
        self.video_capture = None   
        self.video_file_path = None 
        self.is_video_mode = False  
        self.video_frame_count = 0  
        self.current_frame = 0      
        self.last_processed_frame = None # 用于截图和重识别

        self.build_ui()

    def build_ui(self):
        """构建全新的带控制面板的 UI 布局"""
        # 顶部标题
        title_label = tk.Label(self.root, text="YOLO 智能车流量双向检测系统", font=("微软雅黑", 16, "bold"), bg="#f0f0f0", fg="#333")
        title_label.pack(pady=10)

        # 主体框架 (左右分栏)
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20)

        # 左侧：视频显示区
        video_frame = tk.Frame(main_frame, bg="black", width=640, height=480)
        video_frame.pack(side="left", padx=10, pady=10)
        video_frame.pack_propagate(False) # 锁定大小
        self.canvas = Canvas(video_frame, width=640, height=480, bg="black", highlightthickness=0)
        self.canvas.pack()

        # 底部：状态信息条
        self.info_label = tk.Label(self.root, text="系统准备就绪 - 请选择视频文件或启动摄像头", font=("微软雅黑", 10), bg="#ddd", height=2)
        self.info_label.pack(side="bottom", fill="x")

        # 右侧：控制台面板
        control_frame = tk.Frame(main_frame, bg="#f0f0f0", width=350)
        control_frame.pack(side="right", fill="y", padx=10, pady=10)

        # 1. 媒体控制区
        media_group = tk.LabelFrame(control_frame, text="媒体控制", font=("微软雅黑", 10, "bold"), bg="#f0f0f0", padx=10, pady=10)
        media_group.pack(fill="x", pady=5)
        
        btn_opts = {"width": 12, "font": ("微软雅黑", 9)}
        tk.Button(media_group, text="选择视频文件", command=self.select_video_file, bg="#4CAF50", fg="white", **btn_opts).grid(row=0, column=0, padx=5, pady=5)
        self.play_video_button = tk.Button(media_group, text="播放视频", command=self.play_video, state="disabled", **btn_opts)
        self.play_video_button.grid(row=0, column=1, padx=5, pady=5)
        self.pause_video_button = tk.Button(media_group, text="暂停视频", command=self.pause_video, state="disabled", **btn_opts)
        self.pause_video_button.grid(row=1, column=0, padx=5, pady=5)
        self.capture_button = tk.Button(media_group, text="启动摄像头", command=self.start_capture, **btn_opts)
        self.capture_button.grid(row=1, column=1, padx=5, pady=5)
        
        # 2. 算法控制区 (核心修改点)
        algo_group = tk.LabelFrame(control_frame, text="车道线与计数线配置", font=("微软雅黑", 10, "bold"), bg="#f0f0f0", padx=10, pady=10)
        algo_group.pack(fill="x", pady=5)

        tk.Button(algo_group, text="🎯 自动识别画面分隔线", command=self.trigger_auto_detect, bg="#2196F3", fg="white", font=("微软雅黑", 10)).pack(fill="x", pady=5)

        # 分隔线控制滑块
        tk.Label(algo_group, text="分隔线顶部位置 (X轴 %):", bg="#f0f0f0", font=("微软雅黑", 9)).pack(anchor="w")
        self.div_top_slider = tk.Scale(algo_group, from_=0, to=100, orient="horizontal", length=300, bg="#f0f0f0", highlightthickness=0)
        self.div_top_slider.set(50)
        self.div_top_slider.pack()

        tk.Label(algo_group, text="分隔线底部位置 (X轴 %):", bg="#f0f0f0", font=("微软雅黑", 9)).pack(anchor="w")
        self.div_bottom_slider = tk.Scale(algo_group, from_=0, to=100, orient="horizontal", length=300, bg="#f0f0f0", highlightthickness=0)
        self.div_bottom_slider.set(50)
        self.div_bottom_slider.pack()

        # 计数线高度控制滑块
        tk.Label(algo_group, text="左侧驶入车道 计数线高度 (Y轴 %):", bg="#f0f0f0", font=("微软雅黑", 9)).pack(anchor="w")
        self.left_line_slider = tk.Scale(algo_group, from_=10, to=90, orient="horizontal", length=300, bg="#f0f0f0", highlightthickness=0)
        self.left_line_slider.set(70) # 默认偏下
        self.left_line_slider.pack()

        tk.Label(algo_group, text="右侧驶出车道 计数线高度 (Y轴 %):", bg="#f0f0f0", font=("微软雅黑", 9)).pack(anchor="w")
        self.right_line_slider = tk.Scale(algo_group, from_=10, to=90, orient="horizontal", length=300, bg="#f0f0f0", highlightthickness=0)
        self.right_line_slider.set(70)
        self.right_line_slider.pack()

        # 3. 统计控制区
        stat_group = tk.Frame(control_frame, bg="#f0f0f0")
        stat_group.pack(fill="x", pady=15)
        tk.Button(stat_group, text="拍摄快照", command=self.take_snapshot, bg="#ff9800", fg="white", font=("微软雅黑", 10), width=12).pack(side="left", padx=10)
        tk.Button(stat_group, text="重置统计", command=self.reset_count, bg="#f44336", fg="white", font=("微软雅黑", 10), width=12).pack(side="right", padx=10)

    def trigger_auto_detect(self):
        """触发自动识别车道分隔线算法"""
        if self.last_processed_frame is None:
            messagebox.showwarning("警告", "请先加载视频或启动摄像头！")
            return
        self.auto_detect_divider(self.last_processed_frame)

    def auto_detect_divider(self, frame):
        """核心算法：使用 Canny 边缘检测和霍夫变换自动识别路面双黄线/白实线"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        h, w = edges.shape
        
        # 建立掩膜(Mask)，只保留画面中央 40% 的区域，过滤掉路边建筑和树木的干扰
        mask = np.zeros_like(edges)
        points = np.array([
            [int(w * 0.3), 0],
            [int(w * 0.7), 0],
            [int(w * 0.7), h],
            [int(w * 0.3), h]
        ])
        cv2.fillPoly(mask, [points], 255)
        masked_edges = cv2.bitwise_and(edges, mask)
        
        # 霍夫直线检测
        lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, threshold=50, minLineLength=h//4, maxLineGap=50)
        
        if lines is not None:
            valid_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if y2 == y1: continue
                # 过滤掉过于水平的线，只保留倾斜度较大的纵向分隔线
                slope = (x2 - x1) / (y2 - y1)
                if abs(slope) < 1.5: 
                    valid_lines.append((x1, y1, x2, y2))
            
            if valid_lines:
                # 对所有有效纵向线求平均，拟合出一条贯穿屏幕的中心分隔线
                avg_x1 = np.mean([l[0] for l in valid_lines])
                avg_y1 = np.mean([l[1] for l in valid_lines])
                avg_x2 = np.mean([l[2] for l in valid_lines])
                avg_y2 = np.mean([l[3] for l in valid_lines])
                
                slope = (avg_x2 - avg_x1) / (avg_y2 - avg_y1 + 1e-6)
                top_x = avg_x1 + slope * (0 - avg_y1)
                bottom_x = avg_x1 + slope * (h - avg_y1)
                
                # 限制在屏幕宽度内
                top_x = max(0, min(w, top_x))
                bottom_x = max(0, min(w, bottom_x))
                
                # 自动设置滑块参数
                self.div_top_slider.set(top_x / w * 100)
                self.div_bottom_slider.set(bottom_x / w * 100)
                messagebox.showinfo("成功", "算法已成功捕获车道分隔斜线！您仍可通过滑块微调。")
                return
                
        messagebox.showwarning("提示", "未能在当前画面识别出清晰的车道线，系统已使用默认中线，请手动拖动滑块对齐！")

    def select_video_file(self):
        file_types = [('视频文件', '*.mp4 *.avi *.mov *.mkv *.wmv *.flv'), ('所有文件', '*.*')]
        file_path = filedialog.askopenfilename(title="选择视频文件", filetypes=file_types)
        if file_path:
            self.video_file_path = file_path
            self.load_video_file()

    def load_video_file(self):
        try:
            if self.video_capture:
                self.video_capture.release()
            self.video_capture = cv2.VideoCapture(self.video_file_path)
            
            if not self.video_capture.isOpened():
                messagebox.showerror("错误", "无法打开视频文件")
                return
            
            # 读取第一帧用于自动识别线
            ret, frame = self.video_capture.read()
            if ret:
                self.last_processed_frame = frame.copy()
                self.auto_detect_divider(frame) # 加载时自动识别
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0) # 倒带
            
            self.video_frame_count = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            
            self.current_frame = 0
            self.is_video_mode = True
            self.reset_count()
            
            self.play_video_button.config(state="normal")
            self.capture_button.config(state="disabled")
            
            filename = Path(self.video_file_path).name
            self.info_label.config(text=f"已加载视频: {filename} | 准备播放")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载视频失败: {str(e)}")

    def play_video(self):
        self.is_capturing = True
        self.is_video_mode = True
        self.play_video_button.config(state="disabled")
        self.pause_video_button.config(state="normal")
        self.update_video_frame()

    def pause_video(self):
        self.is_capturing = False
        self.play_video_button.config(state="normal")
        self.pause_video_button.config(state="disabled")

    def detect_vehicles(self, frame):
        """检测画面中的车辆：car, motorcycle, bus, truck"""
        results = model1(frame, classes=[2, 3, 5, 7]) 
        vehicle_centroids = []
        if results[0].boxes is not None:
            for box in results[0].boxes:
                if box.conf > 0.4:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    vehicle_centroids.append([int((x1 + x2) / 2), int((y1 + y2) / 2)])
        return vehicle_centroids

    def get_divider_x(self, y_coord, frame_height, frame_width):
        """基于斜线方程，计算在特定 Y 坐标处的分隔线 X 坐标"""
        top_x = (self.div_top_slider.get() / 100.0) * frame_width
        bottom_x = (self.div_bottom_slider.get() / 100.0) * frame_width
        return int(top_x + (y_coord / frame_height) * (bottom_x - top_x))

    def update_vehicle_count(self, tracked_vehicles, frame_width, frame_height):
        """核心逻辑：基于倾斜分隔线的双车道独立检测"""
        left_line_y = int(frame_height * (self.left_line_slider.get() / 100.0))
        right_line_y = int(frame_height * (self.right_line_slider.get() / 100.0))
        
        self.current_vehicles = len(tracked_vehicles)

        for vehicle_id, vehicle_data in tracked_vehicles.items():
            c_x, c_y = vehicle_data['centroid']
            
            if vehicle_id not in self.vehicle_positions:
                self.vehicle_positions[vehicle_id] = [c_y] 
            else:
                self.vehicle_positions[vehicle_id].append(c_y)
                if len(self.vehicle_positions[vehicle_id]) > 5:
                    self.vehicle_positions[vehicle_id] = self.vehicle_positions[vehicle_id][-5:]
                
                positions = self.vehicle_positions[vehicle_id]
                if len(positions) >= 2:
                    # 动态计算车辆当前Y坐标对应的斜线X界限
                    div_x = self.get_divider_x(c_y, frame_height, frame_width)
                    
                    if c_x < div_x:  
                        # 左侧车道逻辑 (驶入 IN - 从上往下越线)
                        if positions[-2] < left_line_y and positions[-1] >= left_line_y:
                            self.vehicle_count_in += 1
                    else:  
                        # 右侧车道逻辑 (驶出 OUT - 从下往上越线)
                        if positions[-2] > right_line_y and positions[-1] <= right_line_y:
                            self.vehicle_count_out += 1
        
        current_vehicle_ids = set(tracked_vehicles.keys())
        self.vehicle_positions = {vid: pos for vid, pos in self.vehicle_positions.items() if vid in current_vehicle_ids}

    def draw_all_annotations(self, frame, tracked_vehicles):
        """在画面上动态绘制倾斜的分割线和吸附的计数线"""
        frame_height, frame_width = frame.shape[:2]
        
        top_x = int((self.div_top_slider.get() / 100.0) * frame_width)
        bottom_x = int((self.div_bottom_slider.get() / 100.0) * frame_width)
        left_line_y = int((self.left_line_slider.get() / 100.0) * frame_height)
        right_line_y = int((self.right_line_slider.get() / 100.0) * frame_height)
        
        # 计算计数线与斜线交点的X坐标
        cross_left_x = self.get_divider_x(left_line_y, frame_height, frame_width)
        cross_right_x = self.get_divider_x(right_line_y, frame_height, frame_width)

        results = model1(frame, classes=[2, 3, 5, 7])
        annotated_frame = results[0].plot()
        
        # 1. 绘制倾斜的车道中线分割线 (白色实线)
        cv2.line(annotated_frame, (top_x, 0), (bottom_x, frame_height), (255, 255, 255), 3)
        
        # 2. 绘制左侧进车道计数线 (绿色，起点x=0 到 交点x)
        cv2.line(annotated_frame, (0, left_line_y), (cross_left_x, left_line_y), (0, 255, 0), 4)
        cv2.putText(annotated_frame, "IN", (10, left_line_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    
        # 3. 绘制右侧出车道计数线 (红色，起点交点x 到 终点x=width)
        cv2.line(annotated_frame, (cross_right_x, right_line_y), (frame_width, right_line_y), (0, 0, 255), 4)
        cv2.putText(annotated_frame, "OUT", (cross_right_x + 10, right_line_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # 绘制跟踪点、轨迹及ID
        for vehicle_id, vehicle_data in tracked_vehicles.items():
            centroid = vehicle_data['centroid']
            cv2.circle(annotated_frame, tuple(centroid), 8, (255, 0, 255), -1) 
            cv2.circle(annotated_frame, tuple(centroid), 12, (255, 0, 255), 2)  
            cv2.putText(annotated_frame, f"ID:{vehicle_id}", (centroid[0] - 25, centroid[1] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
            
            if vehicle_id in self.vehicle_positions and len(self.vehicle_positions[vehicle_id]) > 1:
                positions = self.vehicle_positions[vehicle_id]
                for i in range(1, len(positions)):
                    pt1 = (centroid[0], positions[i-1])
                    pt2 = (centroid[0], positions[i])
                    cv2.line(annotated_frame, pt1, pt2, (255, 0, 255), 2)
        
        # 绘制左上角统计面板
        cv2.rectangle(annotated_frame, (10, 10), (320, 140), (0, 0, 0), -1) 
        cv2.rectangle(annotated_frame, (10, 10), (320, 140), (255, 255, 255), 2)
        cv2.putText(annotated_frame, f"Traffic Flow Dashboard", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(annotated_frame, f"Left Lane (IN) : {self.vehicle_count_in}", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(annotated_frame, f"Right Lane(OUT): {self.vehicle_count_out}", (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(annotated_frame, f"Active Vehicles: {self.current_vehicles}", (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        return annotated_frame

    def update_video_frame(self):
        if not self.is_capturing or not self.is_video_mode: return
        if not self.video_capture or not self.video_capture.isOpened(): return
        
        ret, frame = self.video_capture.read()
        if not ret:
            self.stop_capture()
            messagebox.showinfo("完成", "视频播放完毕")
            return
        
        self.current_frame += 1
        self.last_processed_frame = frame.copy()
        start_time = time.time()
        frame_height, frame_width = frame.shape[:2]
        
        vehicle_centroids = self.detect_vehicles(frame)
        tracked_vehicles = self.vehicle_tracker.update(vehicle_centroids)
        self.update_vehicle_count(tracked_vehicles, frame_width, frame_height)
        annotated_frame = self.draw_all_annotations(frame, tracked_vehicles)
        
        fps = 1/(time.time() - start_time) if (time.time() - start_time) > 0 else 0
        progress = (self.current_frame / self.video_frame_count) * 100 if self.video_frame_count > 0 else 0
        
        image = Image.fromarray(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
        resized = image.resize((640, 480), Image.LANCZOS)
        self.photo_resized = ImageTk.PhotoImage(image=resized)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo_resized)
        
        filename = Path(self.video_file_path).name if self.video_file_path else ""
        self.info_label.config(text=f"状态: 播放中 | 视频: {filename} | 进度: {progress:.1f}% | FPS: {fps:.1f}")

        if self.is_capturing and self.is_video_mode:
            self.root.after(33, self.update_video_frame)

    def start_capture(self):
        self.is_capturing = True
        self.is_video_mode = False
        self.capture_button.config(state="disabled")
        self.play_video_button.config(state="disabled")
        
        ret, frame = self.camera.read()
        if ret: 
            self.last_processed_frame = frame.copy()
            self.auto_detect_divider(frame) # 启动摄像头时也自动识别一次
            
        self.update_frame()

    def stop_capture(self):
        self.is_capturing = False
        self.capture_button.config(state="normal")
        self.pause_video_button.config(state="disabled")
        if self.is_video_mode and self.video_capture:
            self.play_video_button.config(state="normal")
        else:
            self.play_video_button.config(state="disabled")

    def reset_count(self):
        self.vehicle_count_in = 0
        self.vehicle_count_out = 0
        self.current_vehicles = 0
        self.vehicle_positions = {}
        self.vehicle_tracker = VehicleTracker()
        messagebox.showinfo("提示", "计数已重置！")

    def update_frame(self):
        if not self.is_capturing or self.is_video_mode: return
        ret, frame = self.camera.read()
        if not ret: return

        self.last_processed_frame = frame.copy()
        start_time = time.time()
        frame_height, frame_width = frame.shape[:2]
        
        vehicle_centroids = self.detect_vehicles(frame)
        tracked_vehicles = self.vehicle_tracker.update(vehicle_centroids)
        self.update_vehicle_count(tracked_vehicles, frame_width, frame_height)
        annotated_frame = self.draw_all_annotations(frame, tracked_vehicles)
        
        fps = 1/(time.time() - start_time) if (time.time() - start_time) > 0 else 0

        image = Image.fromarray(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
        resized = image.resize((640, 480), Image.LANCZOS)
        self.photo_resized = ImageTk.PhotoImage(image=resized)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo_resized)
        
        self.info_label.config(text=f"状态: 摄像头实时监测中 | FPS: {fps:.1f}")

        if self.is_capturing and not self.is_video_mode:
            self.root.after(30, self.update_frame)

    def take_snapshot(self):
        if self.last_processed_frame is None: return
        
        frame = self.last_processed_frame.copy()
        vehicle_centroids = self.detect_vehicles(frame)
        tracked_vehicles = self.vehicle_tracker.update(vehicle_centroids)
        annotated_frame = self.draw_all_annotations(frame, tracked_vehicles)
        
        self.snapshot_count += 1
        mode_prefix = "video" if self.is_video_mode else "camera"
        filename = f"{mode_prefix}_slanted_lane_count_{self.snapshot_count}.png"
        cv2.imwrite(filename, annotated_frame)
        messagebox.showinfo("成功", f"快照已保存至程序目录: {filename}")

    def __del__(self):
        if hasattr(self, 'camera'): self.camera.release()
        if hasattr(self, 'video_capture') and self.video_capture: self.video_capture.release()

def main():
    root = tk.Tk()
    my_window = MyWindow(root)
    def on_closing():
        my_window.is_capturing = False
        if hasattr(my_window, 'camera'): my_window.camera.release()
        if hasattr(my_window, 'video_capture') and my_window.video_capture: my_window.video_capture.release()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()