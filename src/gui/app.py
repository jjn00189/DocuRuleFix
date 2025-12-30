"""GUI 应用入口

DocuRuleFix 的 GUI 应用程序入口。
"""

import sys
import os

# 确保路径正确 - 支持开发环境和打包后的环境
if getattr(sys, 'frozen', False):
    # 打包后的环境
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包
        bundle_dir = sys._MEIPASS
        src_dir = os.path.dirname(bundle_dir)
    else:
        # 其他打包工具
        src_dir = os.path.dirname(sys.executable)
else:
    # 开发环境
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 应用补丁（在任何使用 python-docx 的导入之前）
from utils.docx_patch import apply_patch
apply_patch()

import customtkinter as ctk
from gui.main_window import MainWindow


def main():
    """主函数"""
    # 设置外观模式
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # 创建并运行主窗口
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
