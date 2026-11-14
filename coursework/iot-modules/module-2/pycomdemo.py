# -*- coding: utf-8 -*-
# 导入系统模块
import sys
# 导入串口模块
import serial
import serial.tools.list_ports
# 导入线程模块
import threading
# 导入信号处理模块
import signal
# 导入二进制转换模块
import binascii
# 导入时间模块
import time

# 导入自定义的中文字符串模块
import strings_zh as strings

import queue

# 根据Python版本导入不同的GUI模块
if sys.version_info.major == 2:
    import Tkinter as tk
    import tkMessageBox as msgbox
elif sys.version_info.major == 3:
    import tkinter as tk
    from tkinter import messagebox as msgbox


# 设置窗口大小和位置（宽度x高度+x坐标+y坐标）
WINDOWSIZE = '950x850+50+50'
# 通用串口参数设置
# 定义波特率选项
BAUDRATES = (1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200)
# 定义数据位选项
BYTESIZES = (5, 6, 7, 8)
# 定义校验位选项（无校验、偶校验、奇校验、标记校验、空格校验）
PARITIES = {'None': 'N', 'Even': 'E', 'Odd': 'O', 'Mark': 'M', 'Space': 'S'}
# 定义停止位选项
STOPBITS = (1, 1.5, 2)
# 定义字节类型选项
BYTETYPES = ('1 Byte', '2 Bytes', '4 Bytes')

# 设置串口超时时间（秒）
TIMEOUT = 0.015

# 定义字体
font = ("宋体", 10, "normal")
font_text = ("Courier", 9, "normal")
font_bold = ("宋体", 10, "bold")


# 格式化十六进制数据
def format_data(data):
    # 将数据按空格分割
    li = data.split(' ')
    result = []
    k = 0
    # 处理每个分割后的数据项
    for each in li:
        # 如果长度小于等于2，直接添加
        if len(each) <= 2:
            result.append(each)

        # 如果长度大于2，每两个字符分割一次
        if len(each) > 2:
            while k < len(each):
                result.append(each[k: k + 2])
                k = k + 2
            k = 0

    # 对于单字符的十六进制数，前面补0
    for i in range(len(result)):
        if len(result[i]) == 1:
            result[i] = '0' + result[i]

    return result


# 获取系统中可用的串口列表
def getAvailabelSerialPort():
    available_ports = []
    # 获取所有串口设备
    coms = serial.tools.list_ports.comports()
    if coms is not None:
        for com in coms:
            # Windows系统下的处理
            if sys.platform == 'win32':
                available_ports.append(com.device)
            # Linux系统下的处理
            elif sys.platform == 'linux2':
                if com[2] != 'n/a':
                    available_ports.append(com[0])
    return tuple(available_ports)


# 根据操作系统类型获取串口列表
if sys.platform == 'win32':
    # Windows下按照COM口编号排序
    PORTS = sorted(getAvailabelSerialPort(), key=lambda n: int(n[3:]))
else:
    PORTS = getAvailabelSerialPort()


# 串口助手的图形界面类
class SerialAssistantGUI(object):
    def __init__(self):

        self.root = tk.Tk()

        self.root.title('%s v%s by %s' %
                        (strings.APP_NAME,
                         strings.APP_VER,
                         strings.AUTHOR))

        # 窗口放大
        self.root.geometry('950x850+50+50')

        self.root.resizable(width=False,
                            height=False)

        # 接收队列
        self.rx_queue = queue.Queue()

        # ===== 实时数据变量 =====

        self.n1_temp = tk.StringVar(value="--")
        self.n1_humi = tk.StringVar(value="--")
        self.n1_gas = tk.StringVar(value="--")
        self.n1_light = tk.StringVar(value="--")
        self.n1_pir = tk.StringVar(value="--")
        self.n1_relay = tk.StringVar(value="关闭")

        self.n2_temp = tk.StringVar(value="--")
        self.n2_humi = tk.StringVar(value="--")
        self.n2_gas = tk.StringVar(value="--")
        self.n2_light = tk.StringVar(value="--")
        self.n2_pir = tk.StringVar(value="--")
        self.n2_relay = tk.StringVar(value="关闭")

        # ===== 阈值变量 =====

        self.temp_threshold_min = tk.StringVar(value="18")
        self.temp_threshold_max = tk.StringVar(value="28")
        self.humi_threshold_min = tk.StringVar(value="30")
        self.humi_threshold_max = tk.StringVar(value="70")
        self.gas_threshold = tk.StringVar(value="300")
        self.light_threshold = tk.StringVar(value="500")

        self.auto_mode = tk.IntVar(value=1)

        # 继电器状态记录（避免重复发送）
        self.relay_status = {1: 0, 2: 0}

        # ===== 创建界面 =====

        self.__data_area()

        self.__threshold_area()

        self.__control_area()

        self.__recv_area()

        self.__send_area()

        self.__cmd_area()

        self.__opt_area()

    def __data_area(self):

        data_frame = tk.LabelFrame(self.root,
                                   text="终端节点实时数据",
                                   font=font_bold)

        data_frame.pack(fill=tk.X,
                        padx=5,
                        pady=5)

        # ================= 节点1 =================

        node1_frame = tk.LabelFrame(data_frame,
                                    text="节点1",
                                    font=font)

        node1_frame.pack(side=tk.LEFT,
                         padx=10,
                         pady=5)

        tk.Label(node1_frame,
                 text="温度(℃):",
                 font=font).grid(row=0,
                                 column=0,
                                 sticky=tk.W,
                                 padx=5,
                                 pady=2)

        tk.Label(node1_frame,
                 textvariable=self.n1_temp,
                 font=font,
                 width=10,
                 relief=tk.SUNKEN).grid(row=0,
                                        column=1,
                                        padx=5,
                                        pady=2)

        tk.Label(node1_frame,
                 text="湿度(%):",
                 font=font).grid(row=1,
                                 column=0,
                                 sticky=tk.W,
                                 padx=5,
                                 pady=2)

        tk.Label(node1_frame,
                 textvariable=self.n1_humi,
                 font=font,
                 width=10,
                 relief=tk.SUNKEN).grid(row=1,
                                        column=1,
                                        padx=5,
                                        pady=2)

        tk.Label(node1_frame,
                 text="烟雾值:",
                 font=font).grid(row=2,
                                 column=0,
                                 sticky=tk.W,
                                 padx=5,
                                 pady=2)

        tk.Label(node1_frame,
                 textvariable=self.n1_gas,
                 font=font,
                 width=10,
                 relief=tk.SUNKEN).grid(row=2,
                                        column=1,
                                        padx=5,
                                        pady=2)

        tk.Label(node1_frame,
                 text="光照值:",
                 font=font).grid(row=3,
                                 column=0,
                                 sticky=tk.W,
                                 padx=5,
                                 pady=2)

        tk.Label(node1_frame,
                 textvariable=self.n1_light,
                 font=font,
                 width=10,
                 relief=tk.SUNKEN).grid(row=3,
                                        column=1,
                                        padx=5,
                                        pady=2)

        tk.Label(node1_frame,
                 text="PIR状态:",
                 font=font).grid(row=4,
                                 column=0,
                                 sticky=tk.W,
                                 padx=5,
                                 pady=2)

        tk.Label(node1_frame,
                 textvariable=self.n1_pir,
                 font=font,
                 width=10,
                 relief=tk.SUNKEN).grid(row=4,
                                        column=1,
                                        padx=5,
                                        pady=2)

        tk.Label(node1_frame,
                 text="继电器:",
                 font=font).grid(row=5,
                                 column=0,
                                 sticky=tk.W,
                                 padx=5,
                                 pady=2)

        self.n1_relay_lbl = tk.Label(node1_frame,
                                     textvariable=self.n1_relay,
                                     font=font,
                                     width=10,
                                     relief=tk.SUNKEN,
                                     bg='lightgray')
        self.n1_relay_lbl.grid(row=5,
                               column=1,
                               padx=5,
                               pady=2)

        # ================= 节点2 =================

        node2_frame = tk.LabelFrame(data_frame,
                                    text="节点2",
                                    font=font)

        node2_frame.pack(side=tk.LEFT,
                         padx=10,
                         pady=5)

        tk.Label(node2_frame,
                 text="温度(℃):",
                 font=font).grid(row=0,
                                 column=0,
                                 sticky=tk.W,
                                 padx=5,
                                 pady=2)

        tk.Label(node2_frame,
                 textvariable=self.n2_temp,
                 font=font,
                 width=10,
                 relief=tk.SUNKEN).grid(row=0,
                                        column=1,
                                        padx=5,
                                        pady=2)

        tk.Label(node2_frame,
                 text="湿度(%):",
                 font=font).grid(row=1,
                                 column=0,
                                 sticky=tk.W,
                                 padx=5,
                                 pady=2)

        tk.Label(node2_frame,
                 textvariable=self.n2_humi,
                 font=font,
                 width=10,
                 relief=tk.SUNKEN).grid(row=1,
                                        column=1,
                                        padx=5,
                                        pady=2)

        tk.Label(node2_frame,
                 text="烟雾值:",
                 font=font).grid(row=2,
                                 column=0,
                                 sticky=tk.W,
                                 padx=5,
                                 pady=2)

        tk.Label(node2_frame,
                 textvariable=self.n2_gas,
                 font=font,
                 width=10,
                 relief=tk.SUNKEN).grid(row=2,
                                        column=1,
                                        padx=5,
                                        pady=2)

        tk.Label(node2_frame,
                 text="光照值:",
                 font=font).grid(row=3,
                                 column=0,
                                 sticky=tk.W,
                                 padx=5,
                                 pady=2)

        tk.Label(node2_frame,
                 textvariable=self.n2_light,
                 font=font,
                 width=10,
                 relief=tk.SUNKEN).grid(row=3,
                                        column=1,
                                        padx=5,
                                        pady=2)

        tk.Label(node2_frame,
                 text="PIR状态:",
                 font=font).grid(row=4,
                                 column=0,
                                 sticky=tk.W,
                                 padx=5,
                                 pady=2)

        tk.Label(node2_frame,
                 textvariable=self.n2_pir,
                 font=font,
                 width=10,
                 relief=tk.SUNKEN).grid(row=4,
                                        column=1,
                                        padx=5,
                                        pady=2)

        tk.Label(node2_frame,
                 text="继电器:",
                 font=font).grid(row=5,
                                 column=0,
                                 sticky=tk.W,
                                 padx=5,
                                 pady=2)

        self.n2_relay_lbl = tk.Label(node2_frame,
                                     textvariable=self.n2_relay,
                                     font=font,
                                     width=10,
                                     relief=tk.SUNKEN,
                                     bg='lightgray')
        self.n2_relay_lbl.grid(row=5,
                               column=1,
                               padx=5,
                               pady=2)

    def __threshold_area(self):

        th_frame = tk.LabelFrame(self.root,
                                 text="阈值设置",
                                 font=font_bold)

        th_frame.pack(fill=tk.X,
                      padx=5,
                      pady=5)

        # 第一行：温度阈值
        tk.Label(th_frame,
                 text="温度范围(℃):",
                 font=font).grid(row=0,
                                 column=0,
                                 padx=5,
                                 pady=5,
                                 sticky=tk.W)

        tk.Entry(th_frame,
                 textvariable=self.temp_threshold_min,
                 width=8,
                 font=font).grid(row=0,
                                 column=1,
                                 padx=2)

        tk.Label(th_frame,
                 text="~",
                 font=font).grid(row=0,
                                 column=2)

        tk.Entry(th_frame,
                 textvariable=self.temp_threshold_max,
                 width=8,
                 font=font).grid(row=0,
                                 column=3,
                                 padx=2)

        # 第二行：湿度阈值
        tk.Label(th_frame,
                 text="湿度范围(%):",
                 font=font).grid(row=0,
                                 column=4,
                                 padx=5,
                                 pady=5,
                                 sticky=tk.W)

        tk.Entry(th_frame,
                 textvariable=self.humi_threshold_min,
                 width=8,
                 font=font).grid(row=0,
                                 column=5,
                                 padx=2)

        tk.Label(th_frame,
                 text="~",
                 font=font).grid(row=0,
                                 column=6)

        tk.Entry(th_frame,
                 textvariable=self.humi_threshold_max,
                 width=8,
                 font=font).grid(row=0,
                                 column=7,
                                 padx=2)

        # 第三行：烟雾和光照阈值
        tk.Label(th_frame,
                 text="烟雾阈值:",
                 font=font).grid(row=1,
                                 column=0,
                                 padx=5,
                                 pady=5,
                                 sticky=tk.W)

        tk.Entry(th_frame,
                 textvariable=self.gas_threshold,
                 width=10,
                 font=font).grid(row=1,
                                 column=1,
                                 columnspan=2,
                                 padx=2)

        tk.Label(th_frame,
                 text="光照阈值:",
                 font=font).grid(row=1,
                                 column=4,
                                 padx=5,
                                 pady=5,
                                 sticky=tk.W)

        tk.Entry(th_frame,
                 textvariable=self.light_threshold,
                 width=10,
                 font=font).grid(row=1,
                                 column=5,
                                 columnspan=2,
                                 padx=2)

        # 自动控制开关
        tk.Checkbutton(th_frame,
                       text="启用自动控制",
                       variable=self.auto_mode,
                       font=font_bold,
                       fg='red').grid(row=1,
                                      column=7,
                                      columnspan=2,
                                      padx=20)

    def __control_area(self):
        """手动控制区域"""
        ctrl_frame = tk.LabelFrame(self.root,
                                   text="手动控制",
                                   font=font_bold)

        ctrl_frame.pack(fill=tk.X,
                        padx=5,
                        pady=5)

        # 节点1控制
        tk.Label(ctrl_frame,
                 text="节点1继电器:",
                 font=font).grid(row=0,
                                 column=0,
                                 padx=10,
                                 pady=5)

        tk.Button(ctrl_frame,
                  text="打开",
                  width=8,
                  font=font,
                  bg='green',
                  fg='white',
                  command=lambda: self.manual_control_relay(1, 1)).grid(row=0,
                                                                        column=1,
                                                                        padx=5)

        tk.Button(ctrl_frame,
                  text="关闭",
                  width=8,
                  font=font,
                  bg='red',
                  fg='white',
                  command=lambda: self.manual_control_relay(1, 0)).grid(row=0,
                                                                        column=2,
                                                                        padx=5)

        # 节点2控制
        tk.Label(ctrl_frame,
                 text="节点2继电器:",
                 font=font).grid(row=0,
                                 column=3,
                                 padx=10,
                                 pady=5)

        tk.Button(ctrl_frame,
                  text="打开",
                  width=8,
                  font=font,
                  bg='green',
                  fg='white',
                  command=lambda: self.manual_control_relay(2, 1)).grid(row=0,
                                                                        column=4,
                                                                        padx=5)

        tk.Button(ctrl_frame,
                  text="关闭",
                  width=8,
                  font=font,
                  bg='red',
                  fg='white',
                  command=lambda: self.manual_control_relay(2, 0)).grid(row=0,
                                                                        column=5,
                                                                        padx=5)

    # 创建接收区域
    def __recv_area(self):
        recv_lframe = tk.LabelFrame(self.root,
                                    text=strings.recv_buf_text,
                                    height=200)
        recv_lframe.pack(fill=tk.X, padx=5)

        recv_optframe = tk.Frame(recv_lframe)
        recv_txtframe = tk.Frame(recv_lframe)
        recv_optframe.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)
        recv_txtframe.pack(fill=tk.Y, side=tk.RIGHT, padx=5, pady=5)

        self.recv_mode = tk.IntVar()
        self.recv_mode.set(0)
        recv_radbtn1 = tk.Radiobutton(recv_optframe,
                                      text=strings.text_mode_text,
                                      font=font,
                                      variable=self.recv_mode, value=0)
        recv_radbtn2 = tk.Radiobutton(recv_optframe,
                                      text=strings.hex_mode_text,
                                      font=font,
                                      variable=self.recv_mode, value=1)
        recv_clrbtn = tk.Button(recv_optframe, width=15,
                                text=strings.clear_recv_text,
                                font=font,
                                command=self.clear_received)
        recv_radbtn1.pack(anchor=tk.W)
        recv_radbtn2.pack(anchor=tk.W)
        recv_clrbtn.pack(fill=tk.X)

        self.recv_txtarea = tk.Text(recv_txtframe, height=12, width=74,
                                    font=font_text)
        self.recv_txtarea.pack(side=tk.LEFT, fill=tk.X)

        recv_scrbar = tk.Scrollbar(recv_txtframe)
        recv_scrbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.recv_txtarea['yscrollcommand'] = recv_scrbar.set
        recv_scrbar['command'] = self.recv_txtarea.yview

    # 创建发送区域
    def __send_area(self):
        send_lframe = tk.LabelFrame(self.root,
                                    text=strings.send_buf_text,
                                    height=100)
        send_lframe.pack(fill=tk.X, padx=5)

        send_optframe = tk.Frame(send_lframe)
        send_txtframe = tk.Frame(send_lframe)
        send_optframe.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)
        send_txtframe.pack(fill=tk.Y, side=tk.RIGHT, padx=5, pady=5)

        self.send_mode = tk.IntVar()
        self.send_mode.set(0)
        send_radbtn1 = tk.Radiobutton(send_optframe,
                                      text=strings.text_mode_text,
                                      font=font,
                                      variable=self.send_mode, value=0)
        send_radbtn2 = tk.Radiobutton(send_optframe,
                                      text=strings.hex_mode_text,
                                      font=font,
                                      variable=self.send_mode, value=1)
        self.linebreak = tk.IntVar()
        if sys.platform == 'win32':
            self.linebreak.set(1)
        elif sys.platform == 'linux2':
            self.linebreak.set(0)
        send_chkbtn = tk.Checkbutton(send_optframe,
                                     text=strings.line_break_text,
                                     font=font,
                                     variable=self.linebreak)
        send_clrbtn = tk.Button(send_optframe,
                                text=strings.clear_send_text,
                                font=font,
                                width=15,
                                command=self.clear_sent)
        send_radbtn1.pack(anchor=tk.W)
        send_radbtn2.pack(anchor=tk.W)
        send_chkbtn.pack(anchor=tk.W)
        send_clrbtn.pack(fill=tk.X)

        self.send_txtarea = tk.Text(send_txtframe, height=5, width=74,
                                    font=font_text)
        self.send_txtarea.pack(side=tk.LEFT, fill=tk.X)
        send_scrbar = tk.Scrollbar(send_txtframe)
        send_scrbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.send_txtarea['yscrollcommand'] = send_scrbar.set
        send_scrbar['command'] = self.send_txtarea.yview

    # 创建命令区域
    def __cmd_area(self):
        cmd_frame = tk.Frame(self.root)
        cmd_frame.pack(fill=tk.X, padx=5, pady=5)
        cmd_btn = tk.Button(cmd_frame,
                            text=strings.send_btn_text,
                            font=font,
                            command=self.send_data)
        cmd_btn.pack(side=tk.LEFT)

    # 创建选项区域
    def __opt_area(self):
        opt_frame = tk.Frame(self.root)
        opt_frame.pack(fill=tk.X, padx=5, pady=5)

        # 串口设置
        port_label = tk.Label(opt_frame,
                              text=strings.port_lbl_text,
                              font=font)

        self.port_var = tk.StringVar()
        self.port_var.set(strings.select_port)

        if len(PORTS) == 0:
            port_opmenu = tk.OptionMenu(opt_frame, self.port_var, '')
        else:
            port_opmenu = tk.OptionMenu(opt_frame, self.port_var, *PORTS)
        port_opmenu.config(anchor=tk.W,
                           width=10,
                           font=font)
        port_label.pack(side=tk.LEFT)
        port_opmenu.pack(side=tk.LEFT)

        # 波特率设置
        brt_label = tk.Label(opt_frame,
                             text=strings.baud_lbl_text,
                             font=font)
        self.brt_var = tk.StringVar()
        self.brt_var.set(BAUDRATES[3])
        brt_opmenu = tk.OptionMenu(opt_frame, self.brt_var, *BAUDRATES)
        brt_opmenu.config(anchor=tk.W,
                          width=5,
                          font=font)
        brt_label.pack(side=tk.LEFT)
        brt_opmenu.pack(side=tk.LEFT)

        # 数据位设置
        size_label = tk.Label(opt_frame,
                              text=strings.size_lbl_text,
                              font=font)
        self.size_var = tk.StringVar()
        self.size_var.set(BYTESIZES[3])
        size_opmenu = tk.OptionMenu(opt_frame, self.size_var, *BYTESIZES)
        size_opmenu.config(anchor=tk.W,
                           width=3,
                           font=font)
        size_label.pack(side=tk.LEFT)
        size_opmenu.pack(side=tk.LEFT)

        # 校验位设置
        parity_label = tk.Label(opt_frame,
                                text=strings.parity_lbl_text,
                                font=font)
        self.parity_var = tk.StringVar()
        self.parity_var.set('None')
        parity_opmenu = tk.OptionMenu(opt_frame, self.parity_var,
                                      *PARITIES)
        parity_opmenu.config(anchor=tk.W,
                             width=3,
                             font=font)
        parity_label.pack(side=tk.LEFT)
        parity_opmenu.pack(side=tk.LEFT)

        # 停止位设置
        stop_label = tk.Label(opt_frame,
                              text=strings.stopbit_lbl_text,
                              font=font)
        self.stop_var = tk.StringVar()
        self.stop_var.set(STOPBITS[0])
        stop_opmenu = tk.OptionMenu(opt_frame, self.stop_var, *STOPBITS)
        stop_opmenu.config(anchor=tk.W,
                           width=3,
                           font=font)
        stop_label.pack(side=tk.LEFT)
        stop_opmenu.pack(side=tk.LEFT)

        # 设置按钮
        control_frame = tk.Frame(self.root, width=300)
        status_frame = tk.Frame(self.root, width=300)
        control_frame.pack(side=tk.LEFT)
        status_frame.pack(side=tk.RIGHT)

        start_btn = tk.Button(control_frame,
                              text=strings.start_port_text,
                              width=12,
                              command=self.start_port)
        close_btn = tk.Button(control_frame,
                              text=strings.close_port_text,
                              width=12,
                              command=self.close_port)
        start_btn.pack(side=tk.LEFT, padx=5)
        close_btn.pack(side=tk.LEFT, padx=5)
        self.state_lbl = tk.Label(control_frame, text='')
        self.state_lbl.pack(side=tk.LEFT, padx=5)

        # 状态框架组件
        send_cnt_label = tk.Label(status_frame,
                                  text=strings.send_lbl_text,
                                  font=font)
        self.send_cnt = tk.StringVar()
        self.send_cnt.set(0)
        send_cnt_entry = tk.Entry(status_frame,
                                  textvariable=self.send_cnt, width=10,
                                  font=font,
                                  relief=tk.SUNKEN,
                                  state=tk.DISABLED,
                                  justify=tk.RIGHT)
        send_cnt_label.pack(side=tk.LEFT)
        send_cnt_entry.pack(side=tk.LEFT)

        recv_cnt_label = tk.Label(status_frame,
                                  text=strings.recv_lbl_text,
                                  font=font)
        self.recv_cnt = tk.StringVar()
        self.recv_cnt.set(0)
        recv_cnt_entry = tk.Entry(status_frame,
                                  textvariable=self.recv_cnt, width=10,
                                  font=font,
                                  relief=tk.SUNKEN,
                                  state=tk.DISABLED,
                                  justify=tk.RIGHT)
        recv_cnt_label.pack(side=tk.LEFT)
        recv_cnt_entry.pack(side=tk.LEFT)

        clr_btn = tk.Button(status_frame,
                            text=strings.clear_btn_text,
                            font=font,
                            command=self.clear_count)
        clr_btn.pack()

    # 清除接收区域内容
    def clear_received(self):
        self.recv_txtarea.delete(0.0, tk.END)

    # 清除发送区域内容
    def clear_sent(self):
        self.send_txtarea.delete(0.0, tk.END)

    # 清除计数器
    def clear_count(self):
        pass

    # 启动串口
    def start_port(self):
        pass

    # 发送数据
    def send_data(self):
        pass

    # 接收数据
    def recv_data(self):
        pass

    # 手动控制继电器
    def manual_control_relay(self, node, state):
        pass


# 串口助手功能实现类，继承自图形界面类
class SerialAssistant(SerialAssistantGUI):

    portisopen = 0
    TX = 0
    RX = 0

    def __init__(self):
        super(SerialAssistant, self).__init__()

    def process_rx_queue(self):
        """处理接收队列中的数据"""
        try:
            while not self.rx_queue.empty():
                data = self.rx_queue.get()
                self.handle_sensor_packet(data)
        except Exception as e:
            print("process_rx_queue error:", e)

        if self.portisopen:
            self.root.after(50, self.process_rx_queue)

    def handle_sensor_packet(self, data):
        """处理传感器数据包"""
        try:
            # 添加原始数据打印
            print(f"收到原始数据(hex): {data.hex()}")

            if len(data) != 12:
                print(f"数据长度错误: {len(data)}")
                return

            # 数据是ASCII字符格式
            try:
                data_str = data.decode('ascii', errors='ignore')
                print(f"收到原始数据(ASCII): {data_str}")

                # 解析各个字段
                node_id = int(data_str[0])
                temp = int(data_str[1:3])
                humi = int(data_str[3:5])
                gas = int(data_str[5:8])
                light = int(data_str[8:11])
                pir = int(data_str[11])

                print(f"解析成功 - 节点:{node_id}, 温度:{temp}, 湿度:{humi}, 烟雾:{gas}, 光照:{light}, PIR:{pir}")

            except (ValueError, IndexError) as e:
                print(f"数据解析错误: {e}")
                return

            # 原始数据显示
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            msg = f"[{timestamp}] 节点{node_id} - 温度:{temp}℃ 湿度:{humi}% 烟雾:{gas} 光照:{light} PIR:{pir}\n"

            self.root.after(0, lambda m=msg: self.recv_txtarea.insert(tk.END, m))
            self.root.after(0, lambda: self.recv_txtarea.see(tk.END))

            # 更新实时显示
            self.root.after(0, lambda: self.update_sensor_display(node_id, temp, humi, gas, light, pir))

            # 自动控制（在自动模式下）
            if self.auto_mode.get():
                self.root.after(0, lambda: self.auto_control(node_id, temp, humi, gas, light, pir))

        except Exception as e:
            print(f"handle_sensor_packet error: {e}")
            import traceback
            traceback.print_exc()

    def update_sensor_display(self, node, temp, humi, gas, light, pir):
        """更新传感器显示"""
        try:
            pir_status = "有人" if pir == 1 else "无人"

            if node == 1:
                self.n1_temp.set(str(temp))
                self.n1_humi.set(str(humi))
                self.n1_gas.set(str(gas))
                self.n1_light.set(str(light))
                self.n1_pir.set(pir_status)
                print(f"节点1显示已更新")
            elif node == 2:
                self.n2_temp.set(str(temp))
                self.n2_humi.set(str(humi))
                self.n2_gas.set(str(gas))
                self.n2_light.set(str(light))
                self.n2_pir.set(pir_status)
                print(f"节点2显示已更新")

            self.root.update_idletasks()

        except Exception as e:
            print(f"update_sensor_display error: {e}")

    def auto_control(self, node, temp, humi, gas, light, pir):
        """自动控制逻辑"""
        try:
            # 获取阈值
            temp_min = float(self.temp_threshold_min.get())
            temp_max = float(self.temp_threshold_max.get())
            humi_min = float(self.humi_threshold_min.get())
            humi_max = float(self.humi_threshold_max.get())
            gas_limit = float(self.gas_threshold.get())
            light_limit = float(self.light_threshold.get())

            need_relay_on = False
            reason = ""

            # 判断是否需要开启继电器
            if temp < temp_min or temp > temp_max:
                need_relay_on = True
                reason += f"温度异常({temp}℃) "

            if humi < humi_min or humi > humi_max:
                need_relay_on = True
                reason += f"湿度异常({humi}%) "

            if gas > gas_limit:
                need_relay_on = True
                reason += f"烟雾超标({gas}) "

            if light < light_limit:
                need_relay_on = True
                reason += f"光照不足({light}) "

            # 发送控制命令
            if need_relay_on:
                if self.relay_status.get(node, 0) == 0:  # 避免重复发送
                    self.send_relay_command(node, 1)
                    print(f"自动控制: 节点{node}继电器开启 - {reason}")
            else:
                if self.relay_status.get(node, 0) == 1:
                    self.send_relay_command(node, 0)
                    print(f"自动控制: 节点{node}继电器关闭 - 数据正常")

        except ValueError:
            print("阈值设置错误，请检查输入")
        except Exception as e:
            print(f"auto_control error: {e}")

    def manual_control_relay(self, node, state):
        """手动控制继电器"""
        if not self.portisopen:
            msgbox.showwarning("警告", "请先打开串口!")
            return

        if self.auto_mode.get():
            result = msgbox.askyesno("确认", "当前处于自动控制模式，手动控制可能被自动模式覆盖。\n是否继续？")
            if not result:
                return

        self.send_relay_command(node, state)
        action = "打开" if state == 1 else "关闭"
        print(f"手动控制: 节点{node}继电器{action}")

    def send_relay_command(self, node, state):
        """发送继电器控制命令"""
        if not self.portisopen:
            return

        try:
            # 构造控制命令：帧头(0xAA) + 节点ID + 状态
            cmd = bytearray()
            cmd.append(0xAA)  # 帧头
            cmd.append(node)  # 节点ID
            cmd.append(state)  # 继电器状态：1=开，0=关

            self.s.write(cmd)
            self.TX += 3
            self.send_cnt.set(self.TX)

            # 更新继电器状态记录
            self.relay_status[node] = state

            # 更新界面显示
            relay_text = "打开" if state == 1 else "关闭"
            relay_color = "green" if state == 1 else "lightgray"

            if node == 1:
                self.n1_relay.set(relay_text)
                self.n1_relay_lbl.config(bg=relay_color)
            elif node == 2:
                self.n2_relay.set(relay_text)
                self.n2_relay_lbl.config(bg=relay_color)

            # 在接收区显示发送的命令
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            msg = f"[{timestamp}] 发送命令: 节点{node}继电器{relay_text} (hex: {cmd.hex()})\n"
            self.recv_txtarea.insert(tk.END, msg)
            self.recv_txtarea.see(tk.END)

            print(f"发送继电器命令成功: 节点{node}, 状态{state}, 数据: {cmd.hex()}")

        except Exception as e:
            print(f"send_relay_command error: {e}")
            msgbox.showerror("错误", f"发送命令失败: {str(e)}")

    def recv_data(self):
        """接收数据线程"""
        print("接收线程已启动")

        while self.portisopen:
            try:
                if self.s.in_waiting > 0:
                    data = self.s.read(12)

                    if len(data) > 0:
                        print(f"收到 {len(data)} 字节")

                        self.RX += len(data)
                        self.root.after(0, lambda: self.recv_cnt.set(self.RX))

                        if len(data) == 12:
                            self.rx_queue.put(data)
                        else:
                            print(f"数据长度不正确: {len(data)}")
                else:
                    time.sleep(0.01)

            except Exception as e:
                if self.portisopen:
                    print(f"recv error: {e}")
                    import traceback
                    traceback.print_exc()
                break

        print("接收线程已退出")

    def start_port(self):
        """启动串口"""
        port = self.port_var.get()

        if port == strings.select_port or port == '':
            msgbox.showerror("错误", "请先选择串口!")
            return

        baudrate = int(self.brt_var.get())
        bytesize = int(self.size_var.get())
        parity = PARITIES[self.parity_var.get()]
        stopbits = float(self.stop_var.get())

        try:
            self.s = serial.Serial(port=port,
                                   baudrate=baudrate,
                                   bytesize=bytesize,
                                   parity=parity,
                                   stopbits=stopbits,
                                   timeout=TIMEOUT)
        except serial.SerialException as e:
            msgbox.showerror("OpenError", str(e))
            return
        except Exception as e:
            msgbox.showerror("OpenError", str(e))
            return

        self.portisopen = 1
        self.state_lbl.config(background='green',
                              text=port + strings.opening)

        # 创建并启动接收线程
        self.th = threading.Thread(target=self.recv_data)
        self.th.daemon = True
        self.th.start()

        # 启动队列处理
        self.root.after(50, self.process_rx_queue)
        print("串口已打开，开始接收数据...")

        # 在接收区显示提示
        msg = f"===== 串口已打开: {port}, 波特率: {baudrate} =====\n"
        self.recv_txtarea.insert(tk.END, msg)

    def send_data(self):
        """发送数据"""
        if self.portisopen:
            data_fmt = []
            data = self.send_txtarea.get(0.0, tk.END)

            if len(data) == 1:
                return

            if self.send_mode.get():  # 十六进制模式
                if data[-1] == '\x0a':
                    data = data[0:-1]
                data_fmt = format_data(data)

                for each in data_fmt:
                    try:
                        x = binascii.a2b_hex(each)
                    except TypeError:
                        x = b'\x00'

                    self.s.write(x)
                    self.TX += 1
            else:  # 文本模式
                if data[-1] == '\n':
                    data = data[0:-1]
                if self.linebreak.get():
                    data = data.replace('\n', '\r\n')

                self.s.write(data.encode('utf-8'))
                self.TX += len(data)

            self.send_cnt.set(self.TX)

            # 显示发送的数据
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            msg = f"[{timestamp}] 发送: {data}\n"
            self.recv_txtarea.insert(tk.END, msg)
            self.recv_txtarea.see(tk.END)
        else:
            msgbox.showerror("Error", "Port NOT open!")
            return

    def close_port(self):
        """关闭串口"""
        if self.portisopen:
            self.portisopen = 0
            self.s.close()
            self.state_lbl.config(background='red',
                                  text=self.port_var.get() + strings.closed)
            print("串口已关闭")

            # 在接收区显示提示
            msg = f"===== 串口已关闭 =====\n"
            self.recv_txtarea.insert(tk.END, msg)
        else:
            return

    def clear_count(self):
        """清除计数"""
        self.TX = 0
        self.RX = 0
        self.send_cnt.set(0)
        self.recv_cnt.set(0)

    def handler(self, signum, frame):
        """信号处理"""
        self.portisopen = 0
        if hasattr(self, 'th'):
            self.th.join()

    def __del__(self):
        """析构函数"""
        self.close_port()
        signal.signal(signal.SIGINT, self.handler)


# 主函数
def main():
    app = SerialAssistant()
    app.root.mainloop()


if __name__ == '__main__':
    main()