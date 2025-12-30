#!/usr/bin/env python3
"""GUI 启动脚本

DocuRuleFix 的 GUI 启动脚本。
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 启动 GUI
from gui.app import main

if __name__ == "__main__":
    main()
