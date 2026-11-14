"""
smith.py
简单的史密斯图窗口：嵌入 matplotlib 极坐标绘制基础网格，
并预留接口以接受外部阻抗点进行标注。
"""

from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("SmithWindow")
        MainWindow.resize(600, 700)
        MainWindow.setWindowTitle("RFID 阻抗分析 - 史密斯圆图")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # 使用极坐标绘制史密斯背景（简化）
        self.figure, self.ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(5, 5))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.info_label = QtWidgets.QLabel("图中红点表示当前天线阻抗位置 (占位)")
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        MainWindow.setCentralWidget(self.centralwidget)
        self.draw_smith_grid()

    def draw_smith_grid(self):
        # 简化版背景：仅展示网格，真实史密斯图需要更多绘制逻辑
        self.ax.clear()
        self.ax.set_theta_zero_location('E')
        self.ax.set_yticklabels([])
        self.ax.set_xticklabels(['0', 'j1', '∞', '-j1'])
        self.ax.grid(True)
        # 占位点（若将来传入实部/虚部可定位）
        self.ax.plot([0.0], [0.0], 'ro')
        self.canvas.draw()

    def plot_impedance_point(self, re_z, im_z):
        """
        可扩展：接受复阻抗的实部/虚部并在史密斯图上做标注（目前占位）。
        """
        # TODO：将 (re_z, im_z) 转换为 Smith 坐标并绘制
        self.ax.plot([0.0], [0.0], 'ro')
        self.canvas.draw()
