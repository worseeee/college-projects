import tkinter as tk
from tkinter import Canvas, Label, Button, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import torch
import time
from pathlib import Path
from ultralytics import YOLO

# 加载YOLO模型（这里使用nano版本，您可以根据需要更改）
model1 = YOLO("yolov8n.pt")
model2 = YOLO("yolov8n-seg.pt")

class PersonTracker:
    def __init__(self):
        self.next_id = 0
        self.tracked_persons = {}
        self.max_disappeared = 30
        self.max_distance = 100
        
    def update(self, detections):
        if len(detections) == 0:
            # 如果没有检测到人，增加所有跟踪对象的消失计数
            for person_id in list(self.tracked_persons.keys()):
                self.tracked_persons[person_id]['disappeared'] += 1
                if self.tracked_persons[person_id]['disappeared'] > self.max_disappeared:
                    del self.tracked_persons[person_id]
            return {}
        
        # 如果当前没有跟踪的人，直接注册所有检测到的人
        if len(self.tracked_persons) == 0:
            for detection in detections:
                self.register(detection)
        else:
            # 计算当前检测到的人与已跟踪的人之间的距离
            person_ids = list(self.tracked_persons.keys())
            person_centroids = [self.tracked_persons[person_id]['centroid'] for person_id in person_ids]
            
            # 计算距离矩阵
            D = np.linalg.norm(np.array(person_centroids)[:, np.newaxis] - np.array(detections), axis=2)
            
            # 找到最小距离的匹配
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_row_idxs = set()
            used_col_idxs = set()
            
            for (row, col) in zip(rows, cols):
                if row in used_row_idxs or col in used_col_idxs:
                    continue
                    
                if D[row, col] > self.max_distance:
                    continue
                    
                person_id = person_ids[row]
                self.tracked_persons[person_id]['centroid'] = detections[col]
                self.tracked_persons[person_id]['disappeared'] = 0
                
                used_row_idxs.add(row)
                used_col_idxs.add(col)
            
            # 处理未匹配的检测和跟踪对象
            unused_row_idxs = set(range(0, D.shape[0])).difference(used_row_idxs)
            unused_col_idxs = set(range(0, D.shape[1])).difference(used_col_idxs)
            
            if D.shape[0] >= D.shape[1]:
                for row in unused_row_idxs:
                    person_id = person_ids[row]
                    self.tracked_persons[person_id]['disappeared'] += 1
                    if self.tracked_persons[person_id]['disappeared'] > self.max_disappeared:
                        del self.tracked_persons[person_id]
            else:
                for col in unused_col_idxs:
                    self.register(detections[col])
        
        return self.tracked_persons
    
    def register(self, centroid):
        self.tracked_persons[self.next_id] = {
            'centroid': centroid,
            'disappeared': 0
        }
        self.next_id += 1

class MyWindow:
    def __init__(self, root):
        self.root = root
        root.title("Camera with People Counter")
        root.geometry("960x700")

        self.create_buttons()
        self.create_image_displays()
        self.create_info_label()
        self.camera = cv2.VideoCapture(0)  # 打开相机
        self.left_photo = tk.PhotoImage()
        self.right_photo = tk.PhotoImage()
        self.snapshot_count = 0  # 用于递增文件名编号
        
        # 人流量检测相关变量
        self.person_tracker = PersonTracker()
        self.counting_line_y = 240  # 计数线位置（图像中心）
        self.people_count_in = 0    # 进入人数
        self.people_count_out = 0   # 离开人数
        self.current_people = 0     # 当前区域内人数
        self.person_positions = {}  # 记录每个人的历史位置
        self.is_capturing = False   # 控制视频流状态
        
        # 视频文件相关变量
        self.video_capture = None   # 视频文件捕获对象
        self.video_file_path = None # 当前视频文件路径
        self.is_video_mode = False  # 是否为视频文件模式
        self.video_frame_count = 0  # 视频总帧数
        self.current_frame = 0      # 当前帧数

    def create_buttons(self):
        # 创建一个框架，用于水平居中排列按钮
        button_frame = tk.Frame(self.root)
        button_frame.pack(side="top")

        # 第一行按钮
        first_row = tk.Frame(button_frame)
        first_row.pack(side="top", pady=5)
        
        # 创建启动摄像头按钮
        self.capture_button = tk.Button(first_row, text="启动摄像头", width=12, height=2, command=self.start_capture)
        self.capture_button.pack(side="left", padx=5)

        # 创建停止按钮
        self.stop_button = tk.Button(first_row, text="停止", width=10, height=2, command=self.stop_capture)
        self.stop_button.pack(side="left", padx=5)

        # 创建拍摄按钮
        self.start_button = tk.Button(first_row, text="拍摄", width=10, height=2, command=self.take_snapshot)
        self.start_button.pack(side="left", padx=5)
        
        # 创建重置计数按钮
        self.reset_button = tk.Button(first_row, text="重置计数", width=10, height=2, command=self.reset_count)
        self.reset_button.pack(side="left", padx=5)

        # 第二行按钮
        second_row = tk.Frame(button_frame)
        second_row.pack(side="top", pady=5)
        
        # 创建选择视频文件按钮
        self.select_video_button = tk.Button(second_row, text="选择视频文件", width=12, height=2, command=self.select_video_file)
        self.select_video_button.pack(side="left", padx=5)
        
        # 创建播放视频按钮
        self.play_video_button = tk.Button(second_row, text="播放视频", width=10, height=2, command=self.play_video, state="disabled")
        self.play_video_button.pack(side="left", padx=5)
        
        # 创建暂停视频按钮
        self.pause_video_button = tk.Button(second_row, text="暂停视频", width=10, height=2, command=self.pause_video, state="disabled")
        self.pause_video_button.pack(side="left", padx=5)

    def create_image_displays(self):
        # 创建一个框架，用于容纳两个Canvas并在水平方向上居中排列
        image_frame = tk.Frame(self.root)
        image_frame.pack(side="top", pady=20)  # 添加垂直间距以使其垂直居中

        # 创建左侧Canvas并设置背景颜色为白色
        self.left_canvas = Canvas(image_frame, width=320, height=240, bg="white")
        self.left_canvas.pack(side="left", padx=20)

        # 创建右侧Canvas并设置背景颜色为白色
        self.right_canvas = Canvas(image_frame, width=320, height=240, bg="white")
        self.right_canvas.pack(side="left", padx=10)

    def create_info_label(self):
        # 创建一个Label用于显示交互信息，设置背景颜色为白色，放置在底部并铺满整个宽度
        self.info_label = Label(self.root, text="人流量检测系统 - 点击启动摄像头或选择视频文件开始检测", font=("Arial", 12), bg="white", height=10)
        self.info_label.pack(side="bottom", fill="x")

    def select_video_file(self):
        """选择视频文件"""
        file_types = [
            ('视频文件', '*.mp4 *.avi *.mov *.mkv *.wmv *.flv'),
            ('MP4文件', '*.mp4'),
            ('AVI文件', '*.avi'),
            ('所有文件', '*.*')
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=file_types
        )
        
        if file_path:
            self.video_file_path = file_path
            self.load_video_file()

    def load_video_file(self):
        """加载视频文件"""
        try:
            # 释放之前的视频捕获对象
            if self.video_capture:
                self.video_capture.release()
            
            # 创建新的视频捕获对象
            self.video_capture = cv2.VideoCapture(self.video_file_path)
            
            if not self.video_capture.isOpened():
                messagebox.showerror("错误", "无法打开视频文件")
                return
            
            # 获取视频信息
            self.video_frame_count = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            duration = self.video_frame_count / fps if fps > 0 else 0
            
            # 重置相关变量
            self.current_frame = 0
            self.is_video_mode = True
            self.reset_count()
            
            # 更新按钮状态
            self.play_video_button.config(state="normal")
            self.capture_button.config(state="disabled")
            
            # 显示视频信息
            filename = Path(self.video_file_path).name
            info_text = f"已加载视频: {filename} | 总帧数: {self.video_frame_count} | 时长: {duration:.1f}秒"
            self.info_label.config(text=info_text)
            
        except Exception as e:
            messagebox.showerror("错误", f"加载视频文件失败: {str(e)}")

    def play_video(self):
        """播放视频"""
        if not self.video_capture or not self.video_capture.isOpened():
            messagebox.showerror("错误", "没有加载视频文件")
            return
        
        self.is_capturing = True
        self.is_video_mode = True
        self.play_video_button.config(state="disabled")
        self.pause_video_button.config(state="normal")
        self.stop_button.config(state="normal")
        self.update_video_frame()

    def pause_video(self):
        """暂停视频"""
        self.is_capturing = False
        self.play_video_button.config(state="normal")
        self.pause_video_button.config(state="disabled")

    def update_video_frame(self):
        """更新视频帧"""
        if not self.is_capturing or not self.is_video_mode:
            return
        
        if not self.video_capture or not self.video_capture.isOpened():
            return
        
        ret, frame = self.video_capture.read()
        if not ret:
            # 视频播放完毕
            self.stop_capture()
            messagebox.showinfo("完成", "视频播放完毕")
            return
        
        self.current_frame += 1
        
        start_time = time.time()
        
        # 检测人员
        people_centroids = self.detect_people(frame)
        
        # 更新跟踪
        tracked_persons = self.person_tracker.update(people_centroids)
        
        # 更新人流量计数
        self.update_people_count(tracked_persons)
        
        # 处理左侧显示（原始检测结果）
        results1 = model1(frame)
        annotated_frame1 = results1[0].plot()
        
        # 处理右侧显示（人流量检测结果）
        annotated_frame2 = frame.copy()
        annotated_frame2 = self.draw_annotations(annotated_frame2, tracked_persons)
        
        elapsed = time.time() - start_time
        fps = 1/elapsed if elapsed > 0 else 0
        
        # 添加FPS和进度信息
        progress = (self.current_frame / self.video_frame_count) * 100 if self.video_frame_count > 0 else 0
        cv2.putText(annotated_frame1, f"FPS: {fps:.1f}", (frame.shape[1] - 150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(annotated_frame2, f"FPS: {fps:.1f}", (frame.shape[1] - 150, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(annotated_frame2, f"Progress: {progress:.1f}%", (frame.shape[1] - 150, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # 转换图像格式并显示
        image1 = Image.fromarray(cv2.cvtColor(annotated_frame1, cv2.COLOR_BGR2RGB))
        image2 = Image.fromarray(cv2.cvtColor(annotated_frame2, cv2.COLOR_BGR2RGB))
        
        # 调整图像大小
        resized1 = image1.resize((320, 240), Image.LANCZOS)
        resized2 = image2.resize((320, 240), Image.LANCZOS)

        self.left_photo_resized = ImageTk.PhotoImage(image=resized1)
        self.right_photo_resized = ImageTk.PhotoImage(image=resized2)

        # 在Canvas上显示图像
        self.left_canvas.delete("all")
        self.right_canvas.delete("all")
        self.left_canvas.create_image(0, 0, anchor="nw", image=self.left_photo_resized)
        self.right_canvas.create_image(0, 0, anchor="nw", image=self.right_photo_resized)
        
        # 更新信息标签
        filename = Path(self.video_file_path).name if self.video_file_path else ""
        info_text = f"视频: {filename} | 进度: {self.current_frame}/{self.video_frame_count} ({progress:.1f}%) | 进入: {self.people_count_in} | 离开: {self.people_count_out} | 当前: {self.current_people} | FPS: {fps:.1f}"
        self.info_label.config(text=info_text)

        # 继续更新（视频播放速度控制）
        if self.is_capturing and self.is_video_mode:
            self.root.after(33, self.update_video_frame)  # 约30fps

    def detect_people(self, frame):
        """检测画面中的人员"""
        results = model1(frame, classes=[0])  # 只检测人（class 0）
        people_centroids = []
        
        if results[0].boxes is not None:
            for box in results[0].boxes:
                if box.conf > 0.5:  # 置信度阈值
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    centroid_x = int((x1 + x2) / 2)
                    centroid_y = int((y1 + y2) / 2)
                    people_centroids.append([centroid_x, centroid_y])
        
        return people_centroids

    def update_people_count(self, tracked_persons):
        """更新人流量计数"""
        for person_id, person_data in tracked_persons.items():
            centroid = person_data['centroid']
            
            # 如果是新检测到的人，初始化其位置历史
            if person_id not in self.person_positions:
                self.person_positions[person_id] = [centroid[1]]  # 只记录y坐标
            else:
                # 添加新位置
                self.person_positions[person_id].append(centroid[1])
                
                # 只保留最近的几个位置
                if len(self.person_positions[person_id]) > 5:
                    self.person_positions[person_id] = self.person_positions[person_id][-5:]
                
                # 检查是否穿过计数线
                positions = self.person_positions[person_id]
                if len(positions) >= 2:
                    # 检查从上到下穿过计数线（进入）
                    if (positions[-2] < self.counting_line_y and 
                        positions[-1] >= self.counting_line_y):
                        self.people_count_in += 1
                        self.current_people += 1
                    
                    # 检查从下到上穿过计数线（离开）
                    elif (positions[-2] > self.counting_line_y and 
                          positions[-1] <= self.counting_line_y):
                        self.people_count_out += 1
                        self.current_people = max(0, self.current_people - 1)
        
        # 清理已消失的人的位置记录
        current_person_ids = set(tracked_persons.keys())
        self.person_positions = {pid: pos for pid, pos in self.person_positions.items() 
                               if pid in current_person_ids}

    def draw_annotations(self, frame, tracked_persons):
        """在画面上绘制检测框、计数线和统计信息"""
        # 绘制计数线
        cv2.line(frame, (0, self.counting_line_y), (frame.shape[1], self.counting_line_y), (0, 255, 255), 2)
        cv2.putText(frame, "Counting Line", (10, self.counting_line_y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # 绘制检测到的人员
        for person_id, person_data in tracked_persons.items():
            centroid = person_data['centroid']
            cv2.circle(frame, tuple(centroid), 5, (0, 255, 0), -1)
            cv2.putText(frame, f"ID: {person_id}", (centroid[0] - 20, centroid[1] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 绘制统计信息
        cv2.putText(frame, f"In: {self.people_count_in}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"Out: {self.people_count_out}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(frame, f"Current: {self.current_people}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        
        return frame

    def start_capture(self):
        """启动摄像头视频捕获和人流量检测"""
        self.is_capturing = True
        self.is_video_mode = False
        self.capture_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.play_video_button.config(state="disabled")
        self.update_frame()

    def stop_capture(self):
        """停止视频捕获"""
        self.is_capturing = False
        self.capture_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.pause_video_button.config(state="disabled")
        
        if self.is_video_mode and self.video_capture:
            self.play_video_button.config(state="normal")
        else:
            self.play_video_button.config(state="disabled")

    def reset_count(self):
        """重置人流量计数"""
        self.people_count_in = 0
        self.people_count_out = 0
        self.current_people = 0
        self.person_positions = {}
        self.person_tracker = PersonTracker()
        self.info_label.config(text="计数已重置")

    def update_frame(self):
        """更新摄像头视频帧"""
        if not self.is_capturing or self.is_video_mode:
            return
            
        ret, frame = self.camera.read()
        if not ret:
            print("无法读取帧")
            return

        start_time = time.time()
        
        # 检测人员
        people_centroids = self.detect_people(frame)
        
        # 更新跟踪
        tracked_persons = self.person_tracker.update(people_centroids)
        
        # 更新人流量计数
        self.update_people_count(tracked_persons)
        
        # 处理左侧显示（原始检测结果）
        results1 = model1(frame)
        annotated_frame1 = results1[0].plot()
        
        # 处理右侧显示（人流量检测结果）
        annotated_frame2 = frame.copy()
        annotated_frame2 = self.draw_annotations(annotated_frame2, tracked_persons)
        
        elapsed = time.time() - start_time
        fps = 1/elapsed if elapsed > 0 else 0
        
        # 添加FPS信息
        cv2.putText(annotated_frame1, f"FPS: {fps:.1f}", (frame.shape[1] - 150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(annotated_frame2, f"FPS: {fps:.1f}", (frame.shape[1] - 150, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # 转换图像格式并显示
        image1 = Image.fromarray(cv2.cvtColor(annotated_frame1, cv2.COLOR_BGR2RGB))
        image2 = Image.fromarray(cv2.cvtColor(annotated_frame2, cv2.COLOR_BGR2RGB))
        
        # 调整图像大小
        resized1 = image1.resize((320, 240), Image.LANCZOS)
        resized2 = image2.resize((320, 240), Image.LANCZOS)

        self.left_photo_resized = ImageTk.PhotoImage(image=resized1)
        self.right_photo_resized = ImageTk.PhotoImage(image=resized2)

        # 在Canvas上显示图像
        self.left_canvas.delete("all")
        self.right_canvas.delete("all")
        self.left_canvas.create_image(0, 0, anchor="nw", image=self.left_photo_resized)
        self.right_canvas.create_image(0, 0, anchor="nw", image=self.right_photo_resized)
        
        # 更新信息标签
        info_text = f"摄像头模式 | 进入: {self.people_count_in} | 离开: {self.people_count_out} | 当前: {self.current_people} | FPS: {fps:.1f}"
        self.info_label.config(text=info_text)

        # 继续更新
        if self.is_capturing and not self.is_video_mode:
            self.root.after(50, self.update_frame)  # 50ms后继续更新

    def take_snapshot(self):
        """拍摄快照"""
        if self.is_video_mode and self.video_capture:
            ret, frame = self.video_capture.read()
            if ret:
                # 重新设置视频位置
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        else:
            ret, frame = self.camera.read()
            
        if not ret:
            return
            
        # 获取当前检测结果
        people_centroids = self.detect_people(frame)
        tracked_persons = self.person_tracker.update(people_centroids)
        
        # 生成带注释的图像
        annotated_frame = self.draw_annotations(frame.copy(), tracked_persons)
        
        # 保存图像
        self.snapshot_count += 1
        mode_prefix = "video" if self.is_video_mode else "camera"
        filename = f"{mode_prefix}_people_count_snapshot_{self.snapshot_count}.png"
        cv2.imwrite(filename, annotated_frame)
        
        # 更新信息
        self.info_label.config(text=f"快照已保存: {filename}")

    def __del__(self):
        """释放资源"""
        if hasattr(self, 'camera'):
            self.camera.release()
        if hasattr(self, 'video_capture') and self.video_capture:
            self.video_capture.release()

def main():
    root = tk.Tk()
    my_window = MyWindow(root)
    
    def on_closing():
        my_window.is_capturing = False
        if hasattr(my_window, 'camera'):
            my_window.camera.release()
        if hasattr(my_window, 'video_capture') and my_window.video_capture:
            my_window.video_capture.release()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()