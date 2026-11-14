import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re

class StudentRegistrationSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("学生信息注册界面 - 刘胜炜 0000000000")
        self.root.geometry("500x650")
        self.root.resizable(False, False)
        
        self.root.configure(bg="#f0f0f0")
        
        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.main_frame.pack(padx=20, pady=20)
        
        self.create_logo()
        
        title_label = tk.Label(self.main_frame, text="注册详细信息", 
                              font=("黑体", 18, "bold"), bg="#f0f0f0")
        title_label.grid(row=1, column=0, columnspan=3, pady=15)
        
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.confirm_pwd_var = tk.StringVar()
        self.gender_var = tk.StringVar(value="男")
        self.contact_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.class_var = tk.StringVar()
        self.major_var = tk.StringVar()
        self.id_number_var = tk.StringVar()
        self.college_var = tk.StringVar()
        
        self.create_input_fields()
        
        self.create_buttons()
        
        watermark = tk.Label(root, text="刘胜炜-0000000000", 
                           fg="gray", font=("Arial", 8), bg="#f0f0f0")
        watermark.pack(side=tk.BOTTOM, pady=5)
    
    def create_logo(self):
        canvas = tk.Canvas(self.main_frame, width=80, height=80, 
                          bg="#f0f0f0", highlightthickness=0)
        canvas.grid(row=0, column=0, columnspan=3, pady=10)
        
        canvas.create_oval(10, 10, 70, 70, fill="#1e3a8a", outline="#1e3a8a", width=2)

        canvas.create_arc(25, 25, 55, 55, start=45, extent=90, 
                         fill="white", outline="white", width=2)
        canvas.create_arc(25, 25, 55, 55, start=225, extent=90, 
                         fill="white", outline="white", width=2)
        
        canvas.create_line(30, 40, 50, 30, fill="white", width=2)
        canvas.create_line(30, 40, 50, 50, fill="white", width=2)
    
    def create_input_fields(self):
        fields = [
            ("用户名:", self.username_var, 2, "entry"),
            ("密码:", self.password_var, 3, "password"),
            ("确认密码:", self.confirm_pwd_var, 4, "password"),
            ("性别:", self.gender_var, 5, "radio"),
            ("联系方式:", self.contact_var, 6, "entry"),
            ("学号:", self.grade_var, 7, "entry"),
            ("班级:", self.class_var, 8, "entry"),
            ("专业:", self.major_var, 9, "entry"),
            ("身份证号码:", self.id_number_var, 10, "entry"),
            ("所在学院:", self.college_var, 11, "combobox"),
        ]
        
        for label_text, var, row, field_type in fields:
            label = tk.Label(self.main_frame, text=label_text, 
                           font=("Arial", 10), bg="#f0f0f0", anchor="e")
            label.grid(row=row, column=0, sticky="e", padx=5, pady=5)
            
            if field_type == "entry":
                entry = tk.Entry(self.main_frame, textvariable=var, 
                               width=25, font=("Arial", 10))
                entry.grid(row=row, column=1, columnspan=2, sticky="w", padx=5, pady=5)
                
            elif field_type == "password":
                entry = tk.Entry(self.main_frame, textvariable=var, 
                               show="*", width=25, font=("Arial", 10))
                entry.grid(row=row, column=1, columnspan=2, sticky="w", padx=5, pady=5)
                
            elif field_type == "radio":
                radio_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
                radio_frame.grid(row=row, column=1, columnspan=2, sticky="w", padx=5, pady=5)
                
                tk.Radiobutton(radio_frame, text="男", variable=var, value="男", 
                             bg="#f0f0f0", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
                tk.Radiobutton(radio_frame, text="女", variable=var, value="女", 
                             bg="#f0f0f0", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
                tk.Radiobutton(radio_frame, text="保密", variable=var, value="保密", 
                             bg="#f0f0f0", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
                
            elif field_type == "combobox":
                colleges = [
                    "信息与智能工程学院",
                    "大数据与软件工程学院",
                    "商学院",
                    "物流与电子商务学院",
                    "生物与环境工程学院",
                    "外语学院",
                    "设计学院"
                ]
                combo = ttk.Combobox(self.main_frame, textvariable=var, 
                                   values=colleges, state="readonly", 
                                   width=23, font=("Arial", 10))
                combo.grid(row=row, column=1, columnspan=2, sticky="w", padx=5, pady=5)
    
    def create_buttons(self):
        button_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        button_frame.grid(row=12, column=0, columnspan=3, pady=20)
        
        register_btn = tk.Button(button_frame, text="注册", 
                               command=self.register, width=10, 
                               font=("Arial", 10), bg="#4CAF50", fg="white")
        register_btn.pack(side=tk.LEFT, padx=10)
        
        login_btn = tk.Button(button_frame, text="登录", 
                            command=self.login, width=10, 
                            font=("Arial", 10), bg="#2196F3", fg="white")
        login_btn.pack(side=tk.LEFT, padx=10)
    
    def validate_username(self, username):
        if not username:
            return False, "用户名不能为空！"
        
        has_letter = bool(re.search(r'[a-zA-Z]', username))
        has_digit = bool(re.search(r'\d', username))
        
        if not (has_letter and has_digit):
            return False, "用户名必须同时包含数字和字母！"
        
        return True, ""
    
    def validate_password(self, password):
        if not password:
            return False, "密码不能为空！"
        
        has_digit = bool(re.search(r'\d', password))
        has_letter = bool(re.search(r'[a-zA-Z]', password))
        special_chars = r'[~!@#$%^&*()_+\-*/<>,.\[\]\\]'
        has_special = bool(re.search(special_chars, password))
        
        if not (has_digit and has_letter and has_special):
            return False, "密码必须包含数字、字母和特殊字符(~!@#$%^&*()_+-*/<>,.[]\\/)"
        
        return True, ""
    
    def validate_id_number(self, id_number):
        if not id_number:
            return False, "身份证号码不能为空！"
        
        if len(id_number) != 18:
            return False, "身份证号码必须为18位！"
        
        # 检查格式：前17位为数字，最后一位为数字或x
        pattern = r'^[0-9]{17}[0-9xX]$'
        if not re.match(pattern, id_number):
            return False, "身份证号码格式不正确！只能包含数字0-9和字母x"
        
        return True, ""
    
    def validate_contact(self, contact):
        if not contact:
            return False, "联系方式不能为空！"
        
        if len(contact) != 11:
            return False, "手机号必须为11位！"
        
        if not contact.isdigit():
            return False, "手机号只能包含数字0-9！"
        
        if not contact.startswith('1'):
            return False, "手机号必须以1开头！"
        
        return True, ""
    
    def register(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        confirm_pwd = self.confirm_pwd_var.get().strip()
        gender = self.gender_var.get()
        contact = self.contact_var.get().strip()
        grade = self.grade_var.get().strip()
        class_name = self.class_var.get().strip()
        major = self.major_var.get().strip()
        id_number = self.id_number_var.get().strip()
        college = self.college_var.get()
        
        if not all([username, password, confirm_pwd, contact, grade, 
                   class_name, major, id_number, college]):
            messagebox.showerror("错误", "请填写所有必填项！")
            return
        
        valid, msg = self.validate_username(username)
        if not valid:
            messagebox.showerror("用户名验证失败", msg)
            return
        
        valid, msg = self.validate_password(password)
        if not valid:
            messagebox.showerror("密码验证失败", msg)
            return
        
        if password != confirm_pwd:
            messagebox.showerror("错误", "两次输入的密码不一致！")
            return
        
        valid, msg = self.validate_id_number(id_number)
        if not valid:
            messagebox.showerror("身份证验证失败", msg)
            return
        
        valid, msg = self.validate_contact(contact)
        if not valid:
            messagebox.showerror("联系方式验证失败", msg)
            return
        
        success_msg = f"""
注册成功！

学生信息：
用户名：{username}
性别：{gender}
联系方式：{contact}
学号：{grade}
班级：{class_name}
专业：{major}
身份证号：{id_number}
所在学院：{college}
        """
        messagebox.showinfo("注册成功", success_msg)
        
        self.clear_all_fields()
    
    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码！")
            return
        
        messagebox.showinfo("登录", f"用户 {username} 尝试登录\n(这是演示功能)")
    
    def clear_all_fields(self):
        self.username_var.set("")
        self.password_var.set("")
        self.confirm_pwd_var.set("")
        self.gender_var.set("男")
        self.contact_var.set("")
        self.grade_var.set("")
        self.class_var.set("")
        self.major_var.set("")
        self.id_number_var.set("")
        self.college_var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentRegistrationSystem(root)
    root.mainloop()
