import tkinter as tk
from tkinter import messagebox, ttk
import time
import os

# 定义日志文件和数据文件路径
DATA_FILE = "devices.txt"
LOG_FILE = "operation_log.txt"

def get_current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S')

def log_operation(action, content):
    current_time = get_current_time()
    log_entry = f"[{current_time}] {action}: {content}\n"
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"日志记录失败: {e}")

class Device:
    def __init__(self, dev_id, name, model, status="在库", borrower="无"):
        self.dev_id = dev_id      # 设备编号
        self.name = name          # 设备名称 (如: Raspberry Pi 4B)
        self.model = model        # 型号/规格
        self.status = status      # 状态：在库/已借出
        self.borrower = borrower  # 借用人姓名

    def __str__(self):
        return f"{self.dev_id},{self.name},{self.model},{self.status},{self.borrower}"

class DeviceManager:
    def __init__(self):
        self.devices = []
        self.load_data()

    def load_data(self):
        """从txt文件中加载设备数据"""
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 5:
                        self.devices.append(Device(*parts))
        except Exception as e:
            messagebox.showerror("错误", f"数据加载失败: {e}")

    def save_data(self):
        """将当前设备列表覆盖写入txt文件"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                for dev in self.devices:
                    f.write(str(dev) + '\n')
        except Exception as e:
            messagebox.showerror("错误", f"数据保存失败: {e}")

    def add_device(self, dev_id, name, model):
        """添加新设备"""
        for dev in self.devices:
            if dev.dev_id == dev_id:
                return False, "设备ID已存在"
        
        new_dev = Device(dev_id, name, model)
        self.devices.append(new_dev)
        self.save_data()
        # 记录带时间戳的日志 [cite: 1053]
        log_operation("入库", f"新增设备 {name} (ID: {dev_id})")
        return True, "添加成功"

    def borrow_device(self, dev_id, student_name):
        """借出设备"""
        for dev in self.devices:
            if dev.dev_id == dev_id:
                if dev.status == "已借出":
                    return False, f"设备已被 {dev.borrower} 借出"
                
                dev.status = "已借出"
                dev.borrower = student_name
                self.save_data()
                log_operation("借出", f"{student_name} 借走了 {dev.name} (ID: {dev_id})")
                return True, "借阅成功"
        return False, "未找到该设备ID"

    def return_device(self, dev_id):
        """归还设备"""
        for dev in self.devices:
            if dev.dev_id == dev_id:
                if dev.status == "在库":
                    return False, "该设备已在库中，无需归还"
                
                old_borrower = dev.borrower
                dev.status = "在库"
                dev.borrower = "无"
                self.save_data()
                log_operation("归还", f"{old_borrower} 归还了 {dev.name} (ID: {dev_id})")
                return True, "归还成功"
        return False, "未找到该设备ID"

class App:
    def __init__(self, root):
        self.manager = DeviceManager()
        self.root = root
        self.root.title("物联网工程实验室设备管理系统 - 刘胜炜 0000000000")
        self.root.geometry("900x600")
        self.root['bg'] = '#f0f0f0'  # 设置背景色

        # === 顶部标题区域 ===
        title_label = tk.Label(root, text="智能实验室设备借还系统", font=("黑体", 20, "bold"), bg='#f0f0f0', fg='#333')
        title_label.pack(pady=10)

        # === 中间主要操作区域 ===
        main_frame = tk.Frame(root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # --- 左侧：控制面板 ---
        control_frame = tk.LabelFrame(main_frame, text="设备操作", font=("Arial", 12), bg='#f0f0f0')
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10, ipadx=10)

        # 输入控件变量
        self.v_id = tk.StringVar()
        self.v_name = tk.StringVar()
        self.v_model = tk.StringVar()
        self.v_student = tk.StringVar()

        # 布局输入框 (Grid布局)
        tk.Label(control_frame, text="设备编号:", bg='#f0f0f0').grid(row=0, column=0, pady=5, sticky=tk.E)
        tk.Entry(control_frame, textvariable=self.v_id).grid(row=0, column=1, pady=5)

        tk.Label(control_frame, text="设备名称:", bg='#f0f0f0').grid(row=1, column=0, pady=5, sticky=tk.E)
        tk.Entry(control_frame, textvariable=self.v_name).grid(row=1, column=1, pady=5)

        tk.Label(control_frame, text="设备型号:", bg='#f0f0f0').grid(row=2, column=0, pady=5, sticky=tk.E)
        tk.Entry(control_frame, textvariable=self.v_model).grid(row=2, column=1, pady=5)

        tk.Label(control_frame, text="借用人姓名:", bg='#f0f0f0', fg='blue').grid(row=3, column=0, pady=5, sticky=tk.E)
        tk.Entry(control_frame, textvariable=self.v_student).grid(row=3, column=1, pady=5)

        # 按钮区域
        btn_frame = tk.Frame(control_frame, bg='#f0f0f0')
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)

        tk.Button(btn_frame, text="设备入库", command=self.action_add, bg='#e1f5fe', width=12).pack(pady=5)
        tk.Button(btn_frame, text="借出设备", command=self.action_borrow, bg='#fff9c4', width=12).pack(pady=5)
        tk.Button(btn_frame, text="归还设备", command=self.action_return, bg='#c8e6c9', width=12).pack(pady=5)
        tk.Button(btn_frame, text="刷新列表", command=self.refresh_list, width=12).pack(pady=5)

        # --- 右侧：数据展示 (Treeview) ---
        tree_frame = tk.LabelFrame(main_frame, text="设备清单", font=("Arial", 12), bg='#f0f0f0')
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("id", "name", "model", "status", "borrower")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # 设置表头
        self.tree.heading("id", text="编号")
        self.tree.heading("name", text="名称")
        self.tree.heading("model", text="型号")
        self.tree.heading("status", text="状态")
        self.tree.heading("borrower", text="当前持有人")
        
        # 设置列宽
        self.tree.column("id", width=80)
        self.tree.column("name", width=150)
        self.tree.column("status", width=80)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 底部状态栏 - 显示时间
        self.time_label = tk.Label(root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.time_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_time()
        
        # 初始化列表
        self.refresh_list()

    def update_time(self):
        """实时更新底部时间显示"""
        current_time = time.strftime('当前系统时间: %Y-%m-%d %H:%M:%S')
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def refresh_list(self):
        """刷新右侧列表显示"""
        # 清空现有显示
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 重新读取数据
        for dev in self.manager.devices:
            self.tree.insert("", tk.END, values=(dev.dev_id, dev.name, dev.model, dev.status, dev.borrower))

    def action_add(self):
        """处理添加按钮事件"""
        dev_id = self.v_id.get()
        name = self.v_name.get()
        model = self.v_model.get()
        if not dev_id or not name:
            messagebox.showwarning("提示", "编号和名称为必填项！")
            return
        success, msg = self.manager.add_device(dev_id, name, model)
        if success:
            messagebox.showinfo("成功", msg)
            self.refresh_list()
            self.v_id.set('')
            self.v_name.set('')
            self.v_model.set('')
        else:
            messagebox.showerror("错误", msg)

    def action_borrow(self):
        """处理借出按钮事件"""
        dev_id = self.v_id.get()
        student = self.v_student.get()
        if not dev_id or not student:
            messagebox.showwarning("提示", "借出时必须填写设备编号和借用人姓名！")
            return
        success, msg = self.manager.borrow_device(dev_id, student)
        if success:
            messagebox.showinfo("成功", msg)
            self.refresh_list()
        else:
            messagebox.showerror("失败", msg)

    def action_return(self):
        """处理归还按钮事件"""
        dev_id = self.v_id.get()
        if not dev_id:
            messagebox.showwarning("提示", "归还时必须填写设备编号！")
            return
        success, msg = self.manager.return_device(dev_id)
        if success:
            messagebox.showinfo("成功", msg)
            self.refresh_list()
        else:
            messagebox.showerror("失败", msg)

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
