# -*- coding: utf-8 -*-
"""Day2 L2/L3 综合服务端：遥控、红外避障和状态回传并行运行。"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.control_server import main


if __name__ == "__main__":
    main(enable_avoid=True, enable_status=True)
