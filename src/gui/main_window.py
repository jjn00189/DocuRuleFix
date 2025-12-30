"""主窗口

DocuRuleFix 的主窗口，整合所有组件。
"""

import customtkinter as ctk
from typing import Optional
import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import sys
from pathlib import Path
from loguru import logger

from gui.utils.theme_manager import ThemeManager
from gui.main_controller import MainController
from gui.components.file_selector import FileSelector
from gui.components.config_panel import ConfigPanel
from gui.components.progress_panel import ProgressPanel
from gui.components.results_panel import ResultsPanel
from gui.utils.threading_helpers import ProgressEventType


class MainWindow(ctk.CTk):
    """主窗口

    整合所有 GUI 组件的主窗口。
    """

    def __init__(self):
        """初始化主窗口"""
        super().__init__()

        # 设置窗口
        self.title("DocuRuleFix - Word 文档处理工具")
        self.geometry("900x800")

        # 设置窗口图标
        self._set_window_icon()

        # 初始化管理器
        self.theme_manager = ThemeManager()
        self.theme_manager.apply_saved_theme()

        self.controller = MainController(self.theme_manager)

        # 当前处理状态
        self.is_processing = False

        # 构建 UI
        self._build_ui()

        # 设置协议
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 启动进度队列处理
        self.after(100, self._process_progress_queue)

    def _build_ui(self):
        """构建用户界面"""
        # 创建主容器
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 顶部标题栏
        self._build_header(main_container)

        # 左侧面板（文件选择 + 配置）
        left_panel = ctk.CTkFrame(main_container)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # 文件选择组件
        self.file_selector = FileSelector(
            left_panel,
            file_callback=self._on_file_selected
        )
        self.file_selector.pack(fill="x", pady=(0, 20))

        # 配置面板
        self.config_panel = ConfigPanel(
            left_panel,
            config_callback=self._on_config_change
        )
        self.config_panel.pack(fill="x")

        # 右侧面板（操作按钮 + 进度 + 结果）
        right_panel = ctk.CTkFrame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)

        # 操作按钮
        self._build_action_buttons(right_panel)

        # 进度面板
        self.progress_panel = ProgressPanel(right_panel)
        self.progress_panel.pack(fill="x", pady=(10, 20))

        # 结果面板
        self.results_panel = ResultsPanel(right_panel)
        self.results_panel.pack(fill="both", expand=True)

    def _set_window_icon(self):
        """设置窗口图标"""
        # 尝试多个可能的图标路径
        # macOS 优先使用 PNG/ICNS，Windows 优先使用 ICO
        if sys.platform == 'darwin':  # macOS
            icon_paths = [
                # 开发环境路径 - 优先 PNG（通过 tk.PhotoImage）
                Path(__file__).parent.parent / "resources" / "icons" / "icon_512x512.png",
                Path(__file__).parent.parent / "resources" / "icons" / "icon_256x256.png",
                # 打包后的路径
                Path("resources") / "icons" / "icon_512x512.png",
                Path("resources") / "icons" / "icon_256x256.png",
            ]
        else:  # Windows/Linux
            icon_paths = [
                # 开发环境路径 - 优先 ICO
                Path(__file__).parent.parent / "resources" / "icons" / "DocuRuleFix.ico",
                Path(__file__).parent.parent / "resources" / "icons" / "icon_256x256.png",
                # 打包后的路径
                Path("resources") / "icons" / "DocuRuleFix.ico",
                Path("resources") / "icons" / "icon_256x256.png",
            ]

        for icon_path in icon_paths:
            if icon_path.exists():
                # Windows: 尝试使用 iconbitmap
                if sys.platform == 'win32' and icon_path.suffix == '.ico':
                    try:
                        self.iconbitmap(str(icon_path))
                        return
                    except Exception:
                        pass

                # macOS/Linux: 使用 PhotoImage
                # 注意：需要保持对 icon 的引用，否则会被垃圾回收
                try:
                    self._icon = tk.PhotoImage(file=str(icon_path))
                    self.iconphoto(True, self._icon)
                    logger.info(f"图标已设置: {icon_path}")
                    return
                except Exception:
                    pass

        # macOS 特殊处理：尝试设置 dock icon
        if sys.platform == 'darwin':
            self._set_macos_dock_icon()

    def _set_macos_dock_icon(self):
        """macOS Dock 图标设置

        注意：在 macOS 上，Tkinter/CustomTkinter 的窗口图标设置功能有限。
        窗口标题栏的图标可以通过 iconphoto() 设置，但 Dock 中的图标需要：
        1. 将应用打包为 .app bundle，并在 Info.plist 中指定 CFBundleIconFile
        2. 或者使用 Cocoa API 调用（通过 pyobjc）
        """
        # 尝试使用 Cocoa API 设置 Dock 图标
        try:
            # 查找 icns 文件
            icns_paths = [
                Path(__file__).parent.parent / "resources" / "icons" / "DocuRuleFix.icns",
                Path("resources") / "icons" / "DocuRuleFix.icns",
            ]

            for icns_path in icns_paths:
                if icns_path.exists():
                    self._icns_path = str(icns_path)
                    # 尝试使用 pyobjc 设置 Dock 图标
                    try:
                        import AppKit

                        # 初始化 NSApplication（如果还没有）
                        app = AppKit.NSApplication.sharedApplication()

                        # 使用 PNG 图片设置 Dock 图标
                        png_path = Path(__file__).parent.parent / "resources" / "icons" / "icon_512x512.png"
                        if png_path.exists():
                            image = AppKit.NSImage.alloc().initWithContentsOfFile_(str(png_path))
                            if image and image.isValid():
                                app.setApplicationIconImage_(image)
                                logger.info(f"已通过 Cocoa API 设置 Dock 图标: {png_path}")
                                return
                    except ImportError:
                        pass

                    logger.info(f"找到 macOS 图标文件: {icns_path}")
                    logger.info("提示: 安装 pyobjc 可获得更好的 Dock 图标支持 (pip install pyobjc)")
                    break
        except Exception as e:
            logger.debug(f"macOS Dock 图标设置失败: {e}")

    def _build_header(self, parent):
        """构建顶部标题栏

        Args:
            parent: 父组件
        """
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        # 标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="DocuRuleFix - Word 文档处理工具",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left")

        # 主题切换按钮
        theme_button = ctk.CTkButton(
            header_frame,
            text="切换主题",
            width=80,
            command=self._toggle_theme,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray20")
        )
        theme_button.pack(side="right", padx=(10, 0))

    def _build_action_buttons(self, parent):
        """构建操作按钮区域

        Args:
            parent: 父组件
        """
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 10))

        # 仅校验按钮
        self.validate_button = ctk.CTkButton(
            button_frame,
            text="仅校验",
            command=self._on_validate_click,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.validate_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # 校验并修复按钮
        self.fix_button = ctk.CTkButton(
            button_frame,
            text="校验并修复",
            command=self._on_fix_click,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("dark blue", "blue")
        )
        self.fix_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # 打开输出文件按钮
        self.open_output_button = ctk.CTkButton(
            button_frame,
            text="打开输出文件",
            command=self._on_open_output,
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray20")
        )
        self.open_output_button.pack(side="left", fill="x", expand=True)
        self.open_output_button.configure(state="disabled")

    def _process_progress_queue(self):
        """处理进度队列（定时调用）"""
        event = self.controller.progress_queue.get_event()

        if event:
            if event.event_type == ProgressEventType.PROGRESS:
                current, total, message = event.data
                self.progress_panel.update_progress(current, total, message)

            elif event.event_type == ProgressEventType.LOG:
                level, message = event.data
                self.progress_panel.add_log(level, message)

            elif event.event_type == ProgressEventType.COMPLETE:
                result = event.data[0]
                self._on_processing_complete(result)

            elif event.event_type == ProgressEventType.ERROR:
                error_msg = event.data[0]
                self.progress_panel.log_error(error_msg)
                self._set_processing_state(False)

        # 继续处理队列
        self.after(100, self._process_progress_queue)

    def _on_file_selected(self, file_path: Optional[str]):
        """文件选择回调

        Args:
            file_path: 选中的文件路径
        """
        # 清除之前的结果
        self.results_panel.clear_results()
        self.progress_panel.clear_logs()

    def _on_config_change(self, config: dict):
        """配置变化回调

        Args:
            config: 配置字典
        """
        # 更新控制器的配置
        self.controller.update_config(**config)

    def _on_validate_click(self):
        """仅校验按钮点击"""
        if not self.file_selector.has_file():
            self.progress_panel.log_warning("请先选择文件")
            return

        if self.is_processing:
            return

        file_path = self.file_selector.get_file()
        self._set_processing_state(True)
        self.progress_panel.clear_logs()
        self.progress_panel.log_info(f"开始校验: {file_path}")

        # 启动异步校验
        self.controller.validate_file_async(file_path)

    def _on_fix_click(self):
        """校验并修复按钮点击"""
        if not self.file_selector.has_file():
            self.progress_panel.log_warning("请先选择文件")
            return

        if self.is_processing:
            return

        file_path = self.file_selector.get_file()
        self._set_processing_state(True)
        self.progress_panel.clear_logs()
        self.progress_panel.log_info(f"开始校验并修复: {file_path}")

        # 启动异步处理
        self.controller.process_file_async(file_path, fix_errors=True)

    def _on_open_output(self):
        """打开输出文件按钮点击"""
        if self.controller.last_result and self.controller.last_result.output_path:
            output_path = self.controller.last_result.output_path
            if os.path.exists(output_path):
                # 使用系统默认程序打开文件
                if os.name == 'nt':  # Windows
                    os.startfile(output_path)
                elif os.name == 'posix':  # macOS / Linux
                    subprocess.run(['open', output_path] if sys.platform == 'darwin' else ['xdg-open', output_path])

    def _on_processing_complete(self, result):
        """处理完成回调

        Args:
            result: 处理结果
        """
        self._set_processing_state(False)

        # 显示结果
        errors = self.controller.get_all_errors()
        self.results_panel.display_errors(errors)

        # 启用/禁用输出按钮
        if result.output_path and result.output_path != result.input_path:
            self.open_output_button.configure(state="normal")
        else:
            self.open_output_button.configure(state="disabled")

        self.progress_panel.finish_progress(result.success, result.message)

    def _set_processing_state(self, processing: bool):
        """设置处理状态

        Args:
            processing: 是否正在处理
        """
        self.is_processing = processing

        # 启用/禁用按钮
        state = "disabled" if processing else "normal"
        self.validate_button.configure(state=state)
        self.fix_button.configure(state=state)

    def _toggle_theme(self):
        """切换主题"""
        new_mode = self.theme_manager.toggle_theme()
        mode_name = "深色" if new_mode == "dark" else "浅色"
        self.progress_panel.log_info(f"已切换到{mode_name}模式")

    def on_closing(self):
        """关闭窗口"""
        # 取消正在进行的任务
        if self.is_processing:
            self.controller.cancel_processing()

        # 保存偏好
        self.theme_manager.save_preferences()

        # 销毁窗口
        self.destroy()
