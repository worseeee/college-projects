"""
ElderGuard 用户界面模块包
包含Tkinter仪表盘和pyecharts报表生成器
"""

from .dashboard import DashboardUI
from .report import ReportGenerator

__all__ = [
    'DashboardUI',
    'ReportGenerator'
]

__version__ = '1.0.0'