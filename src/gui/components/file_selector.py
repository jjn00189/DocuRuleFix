"""文件选择组件

提供拖拽支持和文件浏览功能。
"""

import customtkinter as ctk
from tkinterdnd2 import *
from typing import Callable, Optional
from pathlib import Path
import tkinter as tk
from tkinter import filedialog


class FileSelector(ctk.CTkFrame):
    """文件选择组件

    支持拖拽 .docx 文件和浏览文件对话框。
    """

    def __init__(self, parent, file_callback: Optional[Callable[[str], None]] = None, **kwargs):
        """初始化文件选择组件

        Args:
            parent: 父组件
            file_callback: 文件选择后的回调函数
            **kwargs: 其他参数
        """
        super().__init__(parent, **kwargs)

        self.file_callback = file_callback
        self.selected_file: Optional[str] = None

        self._build_ui()

        # 启用拖拽（需要通过 TkinterDnD）
        self._setup_drag_drop()

    def _build_ui(self):
        """构建用户界面"""
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="文件选择",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        # 拖拽区域
        self.drop_zone = ctk.CTkLabel(
            self,
            text="拖拽 .docx 文件到此处\n或点击下方按钮选择文件",
            font=ctk.CTkFont(size=12),
            width=400,
            height=100,
            fg_color=("gray85", "gray25"),
            corner_radius=10
        )
        self.drop_zone.pack(pady=(0, 10), fill="x")
        self.drop_zone.bind("<Button-1>", self._on_drop_zone_click)

        # 按钮框架
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x")

        # 浏览按钮
        self.browse_button = ctk.CTkButton(
            button_frame,
            text="浏览文件",
            command=self._browse_file,
            width=100
        )
        self.browse_button.pack(side="left", padx=(0, 10))

        # 清除按钮
        self.clear_button = ctk.CTkButton(
            button_frame,
            text="清除",
            command=self._clear_file,
            width=80,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray20")
        )
        self.clear_button.pack(side="left", padx=(0, 10))

        # 当前文件标签
        self.file_label = ctk.CTkLabel(
            self,
            text="未选择文件",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.file_label.pack(fill="x", pady=(10, 0))

    def _setup_drag_drop(self):
        """设置拖拽支持"""
        try:
            # 获取根窗口
            try:
                # 在 CustomTkinter 中，需要获取内部的 Tk 实例
                root = self.winfo_toplevel()
                TkinterDnD().bindroot(root)

                # 绑定拖拽事件
                self.drop_zone.drop_target_register(DND_FILES)
                self.drop_zone.dnd_bind('<<Drop>>', self._on_drop)
                self.drop_zone.dnd_bind('<<DragEnter>>', self._on_drag_enter)
                self.drop_zone.dnd_bind('<<DragLeave>>', self._on_drag_leave)
            except Exception as e:
                print(f"拖拽初始化失败（非致命）: {e}")
        except ImportError:
            print("tkinterdnd2 未安装，拖拽功能不可用")

    def _on_drop_zone_click(self, event=None):
        """点击拖拽区域时触发浏览"""
        self._browse_file()

    def _on_drag_enter(self, event):
        """拖拽进入时的高亮效果"""
        self.drop_zone.configure(fg_color=("gray70", "gray30"))

    def _on_drag_leave(self, event):
        """拖拽离开时的恢复效果"""
        self.drop_zone.configure(fg_color=("gray85", "gray25"))

    def _on_drop(self, event):
        """处理文件拖放"""
        try:
            # 获取拖放的文件路径
            files = event.data
            if isinstance(files, str):
                # Windows 路径可能使用大括号包裹
                files = files.strip("{}")

                # 可能包含多个文件（用空格分隔）
                # 尝试分割
                file_paths = []
                if files.startswith("{") and "}" in files:
                    # 处理 Windows 风格的路径
                    files = files.strip("{}")
                    if "\n" in files:
                        file_paths = files.split("\n")
                    else:
                        file_paths = [files]
                else:
                    file_paths = [files]

                # 处理每个文件
                for file_path in file_paths:
                    file_path = file_path.strip().strip('"').strip("'")
                    if file_path and self._validate_file(file_path):
                        self.set_file(file_path)
                        break  # 只处理第一个有效文件

        except Exception as e:
            print(f"处理拖放文件失败: {e}")

        self.drop_zone.configure(fg_color=("gray85", "gray25"))

    def _browse_file(self):
        """打开文件浏览对话框"""
        file_path = filedialog.askopenfilename(
            title="选择 Word 文档",
            filetypes=[
                ("Word 文档", "*.docx"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.set_file(file_path)

    def _clear_file(self):
        """清除选中的文件"""
        self.selected_file = None
        self.file_label.configure(text="未选择文件")
        self.drop_zone.configure(
            text="拖拽 .docx 文件到此处\n或点击下方按钮选择文件"
        )

        if self.file_callback:
            self.file_callback(None)

    def _validate_file(self, file_path: str) -> bool:
        """验证文件是否有效

        Args:
            file_path: 文件路径

        Returns:
            是否为有效的 .docx 文件
        """
        path = Path(file_path)

        # 检查扩展名
        if path.suffix.lower() != ".docx":
            return False

        # 检查文件是否存在
        if not path.exists():
            return False

        return True

    def set_file(self, file_path: str):
        """设置选中的文件

        Args:
            file_path: 文件路径
        """
        if not self._validate_file(file_path):
            return

        self.selected_file = file_path

        # 更新显示
        file_name = Path(file_path).name
        self.file_label.configure(text=f"当前文件: {file_name}")

        # 更新拖拽区域提示
        self.drop_zone.configure(
            text=f"已选择: {file_name}\n\n拖拽其他文件或点击按钮更换"
        )

        # 触发回调
        if self.file_callback:
            self.file_callback(file_path)

    def get_file(self) -> Optional[str]:
        """获取选中的文件路径

        Returns:
            文件路径，如果没有选择则返回 None
        """
        return self.selected_file

    def has_file(self) -> bool:
        """检查是否已选择文件

        Returns:
            是否已选择文件
        """
        return self.selected_file is not None
