import tkinter as tk
from tkinter import Canvas, Label, Button
import cv2
import numpy as np
from PIL import Image, ImageTk

class MyWindow:
    def __init__(self, root):
        self.root = root
        root.title("Camera")
        root.geometry("960x640")

        self.create_buttons()
        self.create_image_displays()
        self.create_info_label()
        self.camera = cv2.VideoCapture(0)  # 打开相机
        self.left_photo = tk.PhotoImage()
        self.right_photo = tk.PhotoImage()
        self.snapshot_count = 0  # 用于递增文件名编号

    def create_buttons(self):
        # 创建一个框架，用于水平居中排列按钮
        button_frame = tk.Frame(self.root)
        button_frame.pack(side="top")

        # 创建拍摄按钮，绑定事件处理函数
        self.capture_button = tk.Button(button_frame, text="启动", width=10, height=2, command=self.start_capture)
        self.capture_button.pack(side="left", padx=10, pady=20)

        # 创建拍摄按钮
        self.start_button = tk.Button(button_frame, text="拍摄", width=10, height=2, command=self.take_snapshot)
        self.start_button.pack(side="left", padx=10)

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
        self.info_label = Label(self.root, text="This is 信息", font=("Arial", 12), bg="white", height=10)
        self.info_label.pack(side="bottom", fill="x")

    def start_capture(self):
        while True:
            ret, frame = self.camera.read()

            if not ret:
                print("无法读取帧")
                break

            # 使用PIL库将图像数据从OpenCV格式转换为Tkinter PhotoImage格式
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.left_photo = ImageTk.PhotoImage(image=image)

            # 调整图像大小为Canvas的大小（320x240）
            resized = image.resize((320, 240), Image.LANCZOS)

            self.left_photo_resized = ImageTk.PhotoImage(image=resized)
            self.right_photo_resized = ImageTk.PhotoImage(image=resized)

            # 在Canvas上显示调整大小后的左半边和右半边图像
            self.left_canvas.create_image(0, 0, anchor="nw", image=self.left_photo_resized)
            self.right_canvas.create_image(0, 0, anchor="nw", image=self.right_photo_resized)

            self.root.update()  # 更新Tkinter窗口

    def take_snapshot(self):
        # 获取当前的左半边和右半边图像
        left_image = Image.fromarray(cv2.cvtColor(self.camera.read()[1], cv2.COLOR_BGR2RGB))
        right_image = Image.fromarray(cv2.cvtColor(self.camera.read()[1], cv2.COLOR_BGR2RGB))

        # 递增文件名编号
        self.snapshot_count += 1

        # 保存左半边和右半边图像为PNG文件
        left_filename = f"left{self.snapshot_count}.png"
        right_filename = f"right{self.snapshot_count}.png"

        left_image.save(left_filename, "png")
        right_image.save(right_filename, "png")

        # 更新信息标签
        self.info_label.config(text=f"Left: {left_filename}, Right: {right_filename}均已保存！！")

def main():
    root = tk.Tk()
    my_window = MyWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()

