"""
ElderGuard 核心业务模块包
包含数据库、传感器、分析器、报警控制器
"""

from .database import DatabaseManager
from .sensor import SensorManager
from .analyzer import BehaviorAnalyzer
from .alarm import AlarmController

__all__ = [
    'DatabaseManager',
    'SensorManager', 
    'BehaviorAnalyzer',
    'AlarmController'
]

__version__ = '1.0.0'