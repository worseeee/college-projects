# -*- coding: utf-8 -*-
"""Day2 L1：小车端 TCP 遥控服务。"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.control_server import main


if __name__ == "__main__":
    main(enable_avoid=False, enable_status=True)
