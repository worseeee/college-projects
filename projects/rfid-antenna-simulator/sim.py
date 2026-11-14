"""
sim.py
主程序：PyQt5 窗口，集成天线几何输入、材料参数、匹配电路、
幅频特性绘制（嵌入 matplotlib）、实验数据导入与对比。

主要新增与改进：
- 在右侧嵌入 Matplotlib 画布和交互工具栏（缩放/保存）；
- 使用 coilpro.compute_freq_response 做矢量化扫频并绘图（性能优）；
- 支持用户自定义频率范围与点数；
- 支持 CSV 导入（第一列频率(Hz)，第二列为要比对的数据，如 |G| 或 S11）；
- 日志区显示详细计算中间量，便于与实验对照。
"""

import sys
import time
import numpy as np
import matplotlib

from matplotlib import rcParams

# 设置中文字体（Windows 推荐）
rcParams['font.sans-serif'] = ['SimHei']        # 黑体
rcParams['axes.unicode_minus'] = False          # 解决负号显示问题

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QGroupBox, QLabel,
                             QDoubleSpinBox, QComboBox, QTextEdit, QPushButton,
                             QFrame, QSplitter, QFileDialog, QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Matplotlib + PyQt5 集成
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import coilpro  # 计算模块
from smith import Ui_MainWindow as SmithUI  # 史密斯图窗口（简化）

# Canvas preview for coil drawing (kept simple)
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QRectF, QPointF


class AntennaCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shape_type = "方形"
        self.turns = 4
        self.width_mm = 0.8
        self.length_cm = 10.5
        self.setMinimumHeight(300)
        self.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3d3d3d;")

    def update_params(self, shape, turns, width, length):
        self.shape_type = shape
        self.turns = int(turns)
        self.width_mm = width
        self.length_cm = length
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 背景网格
        pen_grid = QPen(QColor("#3d3d3d"), 1, Qt.DotLine)
        painter.setPen(pen_grid)
        step = 40
        for x in range(0, self.width(), step):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), step):
            painter.drawLine(0, y, self.width(), y)
        # 画线圈
        pen_coil = QPen(QColor("#00ff00"))
        pen_coil.setWidthF(max(1.0, self.width_mm * 2.0))
        painter.setPen(pen_coil)
        cx, cy = self.width() / 2.0, self.height() / 2.0
        scale = min(self.width(), self.height()) / (self.length_cm * 2.5 + 1e-6) * 0.6
        base = self.length_cm * scale
        gap = self.width_mm * scale * 0.8
        for i in range(self.turns):
            size = base - (i * gap * 2)
            if size <= 0:
                break
            if self.shape_type == "圆形":
                r = size / 2.0
                painter.drawEllipse(QPointF(cx, cy), r, r)
            else:
                rect = QRectF(cx - size / 2.0, cy - size / 2.0, size, size)
                painter.drawRect(rect)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(10, 20, f"预览: {self.shape_type} | 匝数: {self.turns}")


class RFIDSimWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RFID 天线专业仿真软件 Pro")
        self.resize(1200, 800)
        self._init_ui()
        self._init_style()
        # 初始计算
        self.recalculate()

    def _init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # 左侧控制面板
        ctrl_frame = QFrame(self)
        ctrl_frame.setFixedWidth(360)
        ctrl_layout = QVBoxLayout(ctrl_frame)
        ctrl_layout.setSpacing(12)

        # 1. 天线几何参数
        grp_geo = QGroupBox("1. 天线几何参数")
        geo_layout = QGridLayout()
        self.spin_len = self._create_spinbox(10.5, 0.1, 1000.0, " cm", "线圈平均长度 (cm)")
        self.spin_width = self._create_spinbox(0.8, 0.01, 50.0, " mm", "线径宽度 (mm)")
        self.spin_turns = self._create_spinbox(4, 1, 200, " 匝", "线圈匝数", is_int=True)
        self.combo_shape = QComboBox()
        self.combo_shape.addItems(["方形", "圆形"])
        self.combo_shape.currentIndexChanged.connect(self.recalculate)

        geo_layout.addWidget(QLabel("线圈长度:"), 0, 0)
        geo_layout.addWidget(self.spin_len, 0, 1)
        geo_layout.addWidget(QLabel("线径宽度:"), 1, 0)
        geo_layout.addWidget(self.spin_width, 1, 1)
        geo_layout.addWidget(QLabel("线圈匝数:"), 2, 0)
        geo_layout.addWidget(self.spin_turns, 2, 1)
        geo_layout.addWidget(QLabel("线圈形状:"), 3, 0)
        geo_layout.addWidget(self.combo_shape, 3, 1)
        grp_geo.setLayout(geo_layout)
        ctrl_layout.addWidget(grp_geo)

        # 2. PCB 与材料参数
        grp_mat = QGroupBox("2. PCB 与材料参数")
        mat_layout = QGridLayout()
        self.spin_thick = self._create_spinbox(35, 1, 500, " um", "铜箔厚度 (um)")
        self.spin_pcb_h = self._create_spinbox(1.6, 0.1, 10.0, " mm", "PCB 厚度 (mm)")
        self.spin_pcb_er = self._create_spinbox(4.4, 1.0, 20.0, "", "介电常数")
        self.combo_mat = QComboBox()
        for m in coilpro.MATERIAL_RESISTIVITY.keys():
            self.combo_mat.addItem(m)
        self.combo_mat.setCurrentText('铜')
        self.combo_mat.currentIndexChanged.connect(self.recalculate)

        mat_layout.addWidget(QLabel("导线材料:"), 0, 0)
        mat_layout.addWidget(self.combo_mat, 0, 1)
        mat_layout.addWidget(QLabel("走线厚度:"), 1, 0)
        mat_layout.addWidget(self.spin_thick, 1, 1)
        mat_layout.addWidget(QLabel("PCB 厚度:"), 2, 0)
        mat_layout.addWidget(self.spin_pcb_h, 2, 1)
        mat_layout.addWidget(QLabel("介电常数:"), 3, 0)
        mat_layout.addWidget(self.spin_pcb_er, 3, 1)
        grp_mat.setLayout(mat_layout)
        ctrl_layout.addWidget(grp_mat)

        # 3. 匹配电路参数
        grp_cir = QGroupBox("3. 匹配电路参数")
        cir_layout = QGridLayout()
        self.spin_rext = self._create_spinbox(7.2, 0.0, 1000.0, " Ω", "外部匹配电阻")
        self.spin_c1 = self._create_spinbox(15.5, 0.0, 10000.0, " pF", "并联电容 C1 (pF)")
        self.spin_c2 = self._create_spinbox(147.9, 0.0, 10000.0, " pF", "串联电容 C2 (pF)")
        self.combo_type = QComboBox()
        self.combo_type.addItems(["单端电路", "差动电路"])
        self.combo_type.currentIndexChanged.connect(self.recalculate)

        cir_layout.addWidget(QLabel("电路类型:"), 0, 0)
        cir_layout.addWidget(self.combo_type, 0, 1)
        cir_layout.addWidget(QLabel("匹配电阻:"), 1, 0)
        cir_layout.addWidget(self.spin_rext, 1, 1)
        cir_layout.addWidget(QLabel("C1:"), 2, 0)
        cir_layout.addWidget(self.spin_c1, 2, 1)
        cir_layout.addWidget(QLabel("C2:"), 3, 0)
        cir_layout.addWidget(self.spin_c2, 3, 1)
        grp_cir.setLayout(cir_layout)
        ctrl_layout.addWidget(grp_cir)

        
        grp_freq = QGroupBox("4. 频率响应设置")
        freq_layout = QGridLayout()
        self.spin_fmin = self._create_spinbox(5.0, 0.1, 1000.0, " MHz", "频率下限 (MHz)")
        self.spin_fmax = self._create_spinbox(30.0, 0.2, 1000.0, " MHz", "频率上限 (MHz)")
        self.spin_points = QSpinBox()
        self.spin_points.setRange(50, 5000)
        self.spin_points.setValue(1000)
        self.spin_points.valueChanged.connect(self.recalculate)

        freq_layout.addWidget(QLabel("频率下限:"), 0, 0)
        freq_layout.addWidget(self.spin_fmin, 0, 1)
        freq_layout.addWidget(QLabel("频率上限:"), 1, 0)
        freq_layout.addWidget(self.spin_fmax, 1, 1)
        freq_layout.addWidget(QLabel("采样点数:"), 2, 0)
        freq_layout.addWidget(self.spin_points, 2, 1)

        grp_freq.setLayout(freq_layout)
        ctrl_layout.addWidget(grp_freq)

        
        self.btn_smith = QPushButton("打开 Smith 圆图")
        self.btn_plot = QPushButton("绘制幅频特性")
        self.btn_load_exp = QPushButton("导入实验曲线 (CSV)")

        self.btn_smith.clicked.connect(self.open_smith_chart)
        self.btn_plot.clicked.connect(self.plot_frequency_response)
        self.btn_load_exp.clicked.connect(self.load_experimental_curve)

        self.btn_smith.setFixedHeight(36)
        self.btn_plot.setFixedHeight(36)
        self.btn_load_exp.setFixedHeight(36)

        ctrl_layout.addWidget(self.btn_plot)
        ctrl_layout.addWidget(self.btn_load_exp)
        ctrl_layout.addWidget(self.btn_smith)
        ctrl_layout.addStretch()

        main_layout.addWidget(ctrl_frame)

        # 右侧：预览 + 幅频图 + 日志
        right_panel = QSplitter(Qt.Vertical)

        # 预览画布
        self.canvas = AntennaCanvas()
        right_panel.addWidget(self.canvas)

        # 幅频绘图区域（嵌入 matplotlib）
        plot_frame = QWidget()
        plot_layout = QVBoxLayout(plot_frame)
        self.freqFig = Figure(figsize=(6, 3.5))
        self.freqCanvas = FigureCanvas(self.freqFig)
        self.freqToolbar = NavigationToolbar(self.freqCanvas, self)
        plot_layout.addWidget(self.freqToolbar)
        plot_layout.addWidget(self.freqCanvas)
        self.freqAx = self.freqFig.add_subplot(111)
        self.freqAx.set_title("天线回路幅频特性")
        self.freqAx.set_xlabel("f (Hz)")
        self.freqAx.set_ylabel("|G|")
        right_panel.addWidget(plot_frame)

        # 日志区
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Consolas", 10))
        right_panel.addWidget(self.log_area)

        right_panel.setStretchFactor(0, 2)
        right_panel.setStretchFactor(1, 3)
        right_panel.setStretchFactor(2, 1)

        main_layout.addWidget(right_panel)

    def _init_style(self):
        style = """
            QMainWindow { background-color: #1e1e1e; color: #ffffff; }
            QGroupBox { font-weight: bold; border: 1px solid #555; margin-top: 10px; color: #ddd; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }
            QLabel { color: #ccc; }
            QDoubleSpinBox, QComboBox, QSpinBox { background: #333; color: #fff; border: 1px solid #555; padding: 4px; }
            QTextEdit { background: #252526; color: #00ff00; font-family: Consolas; border: 1px solid #444; }
            QPushButton { background-color: #007acc; color: white; border: none; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #0098ff; }
            QPushButton:pressed { background-color: #005c99; }
        """
        self.setStyleSheet(style)

    def _create_spinbox(self, val, min_v, max_v, suffix, tooltip, is_int=False):
        sb = QDoubleSpinBox()
        sb.setRange(min_v, max_v)
        sb.setValue(val)
        sb.setSuffix(suffix)
        sb.setToolTip(tooltip)
        if is_int:
            sb.setDecimals(0)
        else:
            sb.setDecimals(3)
        sb.valueChanged.connect(self.recalculate)
        return sb

    def recalculate(self):
        """
        读取当前参数并计算 L, R, C_eff 等（用于显示与后续仿真）。
        不在此处绘图以避免 UI 阻塞，绘图由按钮触发。
        """
        try:
            l_cm = self.spin_len.value()
            w_mm = self.spin_width.value()
            n_turns = int(self.spin_turns.value())
            shape = self.combo_shape.currentText()
            shape_key = 'circular' if shape == '圆形' else 'square'

            # 计算电感（uH）与电阻（Ω）
            L_uH = coilpro.calculate_inductance(n_turns, l_cm, shape_key)
            R_ohm = coilpro.calculate_resistance(n_turns, l_cm, w_mm, self.spin_thick.value(),
                                                self.combo_mat.currentText())
            # 粗略估算等效电容 (pF) —— 近似平板电容：C = eps0 * er * A / d
            pcb_er = max(1.0, self.spin_pcb_er.value())
            pcb_h_m = max(1e-4, self.spin_pcb_h.value() / 1000.0)  # mm -> m
            area_m2 = max(1e-8, (l_cm / 100.0) ** 2)
            C_eff_F = coilpro.EPS0 * pcb_er * area_m2 / pcb_h_m
            C_eff_pf = C_eff_F * 1e12

            # 保留到实例状态，并在日志输出
            self.current_L = round(L_uH, 6)
            self.current_R = round(R_ohm, 6)
            self.current_C = round(C_eff_pf, 6)

            # 日志
            log = f"--- 实时计算 [{time.strftime('%H:%M:%S')}] ---\n"
            log += f"几何: {shape}, 匝数: {n_turns}, 长: {l_cm} cm, 宽: {w_mm} mm\n"
            log += f"等效电感 L: {self.current_L} uH\n"
            log += f"等效电阻 R: {self.current_R} Ω\n"
            log += f"等效电容 C: {self.current_C} pF (近似)\n"
            # 匹配电路评估（简短）
            rext = self.spin_rext.value()
            c1 = self.spin_c1.value()
            c2 = self.spin_c2.value()
            cir_type = self.combo_type.currentText()
            if cir_type == "单端电路":
                stat = coilpro.Pro_cir_calc1(c1, c2, self.current_L, self.current_R + rext)
            else:
                stat = coilpro.Pro_cir_calc2(c1, c2, self.current_L, self.current_R + rext)
            log += f"匹配网络评估:\n{stat}\n"
            self.log_area.setText(log)

            # 更新预览画布参数
            self.canvas.update_params(shape, n_turns, w_mm, l_cm)

        except Exception as e:
            self.log_area.setText(f"计算错误: {e}")

    def plot_frequency_response(self):
        """ 使用 coilpro.compute_freq_response 进行矢量化扫频并绘图 """
        try:
            # 读取参数
            fmin_mhz = float(self.spin_fmin.value())
            fmax_mhz = float(self.spin_fmax.value())
            pts = int(self.spin_points.value())
            if fmin_mhz >= fmax_mhz:
                QMessageBox.warning(self, "输入错误", "频率下限应小于上限。")
                return
            fmin = fmin_mhz * 1e6
            fmax = fmax_mhz * 1e6

            # 使用当前估算的 L, R, C
            L_uH = getattr(self, 'current_L', None)
            R_ohm = getattr(self, 'current_R', None)
            C_pf = getattr(self, 'current_C', None)
            if L_uH is None or R_ohm is None or C_pf is None:
                QMessageBox.warning(self, "错误", "请先确认参数有效。")
                return

            # 调用计算函数（矢量化）
            freqs, Z_mag, G_mag, S11 = coilpro.compute_freq_response(
                R_ohm=float(R_ohm),
                L_uH=float(L_uH),
                C_pf=float(C_pf),
                f_min=fmin,
                f_max=fmax,
                num_points=pts,
                Z0=50.0
            )

            # 绘图（默认绘制 |G|）
            self.freqAx.clear()
            self.freqAx.plot(freqs, G_mag, label="仿真 |G|")
            # 也可以绘制 S11
            self.freqAx.plot(freqs, S11, label="仿真 |S11|", linestyle='--')
            self.freqAx.set_title("天线回路幅频特性")
            self.freqAx.set_xlabel("f (Hz)")
            self.freqAx.set_ylabel("|G| / |S11|")
            self.freqAx.grid(True)
            self.freqAx.legend()
            self.freqCanvas.draw()

            # 激活图例点击切换
            self._enable_legend_toggle()

            # 记录到日志
            peak_idx = np.argmax(G_mag)
            peak_f = freqs[peak_idx]
            peak_val = G_mag[peak_idx]
            self.log_area.append(f"\n仿真峰值: f = {peak_f:.0f} Hz, |G| = {peak_val:.6f}")
        except Exception as e:
            QMessageBox.critical(self, "绘图错误", str(e))

    def load_experimental_curve(self):
        """
        导入 CSV 并在当前图表上叠加实验曲线（CSV 格式要求：第一列频率(Hz)，第二列为数据）。
        """
        try:
            path, _ = QFileDialog.getOpenFileName(self, "选择实验曲线CSV文件", "", "CSV文件 (*.csv);;所有文件 (*)")
            if not path:
                return
            data = np.loadtxt(path, delimiter=',')
            if data.ndim == 1 and data.size >= 2:
                # 单行数据也允许
                f_exp = np.array([data[0]])
                y_exp = np.array([data[1]])
            else:
                f_exp = data[:, 0]
                y_exp = data[:, 1]
            # 绘制，并保持图例
            self.freqAx.plot(f_exp, y_exp, 'r--', label="实验曲线")
            self.freqAx.legend()
            self.freqCanvas.draw()
            self._enable_legend_toggle()
            self.log_area.append(f"\n已加载实验曲线: {path}")
        except Exception as e:
            QMessageBox.critical(self, "读取实验数据失败", str(e))

    def open_smith_chart(self):
        """ 打开史密斯圆图窗口（简化实现） """
        try:
            self.smith_window = QMainWindow()
            self.ui_smith = SmithUI()
            self.ui_smith.setupUi(self.smith_window)
            # 如需传入阻抗点，可调用 ui_smith.plot_impedance_point(...)
            self.smith_window.show()
            self.log_area.append("\n>> 已打开 Smith 圆图窗口")
        except Exception as e:
            QMessageBox.critical(self, "打开失败", str(e))

    def _enable_legend_toggle(self):
        """ 使图例可点击切换相应线条的显示（交互） """
        leg = self.freqAx.get_legend()
        if leg is None:
            return
        lines = self.freqAx.get_lines()
        leg_lines = leg.get_lines()
        # 为每个图例线条记录对应原始线对象
        for legline, origline in zip(leg_lines, lines):
            legline.set_picker(5)
            legline._orig_line = origline

        def on_pick(event):
            legend_line = event.artist
            orig_line = getattr(legend_line, "_orig_line", None)
            if orig_line is None:
                return
            vis = not orig_line.get_visible()
            orig_line.set_visible(vis)
            legend_line.set_alpha(1.0 if vis else 0.2)
            self.freqCanvas.draw_idle()

        # 先断开已有连接以避免重复注册
        try:
            self.freqCanvas.mpl_disconnect(self._pick_cid)
        except Exception:
            pass
        self._pick_cid = self.freqCanvas.mpl_connect('pick_event', on_pick)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = RFIDSimWindow()
    win.show()
    sys.exit(app.exec_())
