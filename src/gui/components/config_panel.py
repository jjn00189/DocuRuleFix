"""配置面板

提供处理选项的配置界面。
"""

import customtkinter as ctk
from typing import Callable, Optional


class ConfigPanel(ctk.CTkFrame):
    """配置面板

    提供标题模式选择和各种处理选项的配置。
    """

    def __init__(self, parent, config_callback: Optional[Callable] = None, **kwargs):
        """初始化配置面板

        Args:
            parent: 父组件
            config_callback: 配置变化时的回调函数
            **kwargs: 其他参数
        """
        super().__init__(parent, **kwargs)

        self.config_callback = config_callback

        # 配置变量
        self.title_mode_var = ctk.StringVar(value="2")
        self.fix_errors_var = ctk.BooleanVar(value=True)
        self.create_backup_var = ctk.BooleanVar(value=True)
        self.skip_corrupted_var = ctk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self):
        """构建用户界面"""
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="配置选项",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(0, 10), anchor="w")

        # 标题模式选择
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", pady=(0, 15))

        mode_label = ctk.CTkLabel(
            mode_frame,
            text="标题模式:",
            font=ctk.CTkFont(size=12),
            width=80,
            anchor="w"
        )
        mode_label.pack(side="left", padx=(0, 10))

        # 标准模式
        self.standard_mode = ctk.CTkRadioButton(
            mode_frame,
            text="标准模式 (需要 . _ ：)",
            variable=self.title_mode_var,
            value="1",
            command=self._on_config_change
        )
        self.standard_mode.pack(side="left", padx=(0, 20))

        # 精简模式
        self.simple_mode = ctk.CTkRadioButton(
            mode_frame,
            text="精简模式 (只需 序号.内容)",
            variable=self.title_mode_var,
            value="2",
            command=self._on_config_change
        )
        self.simple_mode.pack(side="left")

        # 说明文本
        desc_label = ctk.CTkLabel(
            self,
            text="• 标准模式: 序号.舆论场_来源：标题内容\n"
                 "• 精简模式: 序号.标题内容",
            font=ctk.CTkFont(size=10),
            justify="left",
            anchor="w",
            fg_color=("gray85", "gray25"),
            corner_radius=5,
            padx=10,
            pady=8
        )
        desc_label.pack(fill="x", pady=(0, 15))

        # 选项复选框
        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.pack(fill="x", pady=(0, 10))

        # 自动修复错误
        self.fix_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="自动修复错误",
            variable=self.fix_errors_var,
            command=self._on_config_change,
            checkbox_width=20,
            checkbox_height=20
        )
        self.fix_checkbox.pack(anchor="w", pady=(0, 8))

        # 创建备份
        self.backup_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="创建备份文件",
            variable=self.create_backup_var,
            command=self._on_config_change,
            checkbox_width=20,
            checkbox_height=20
        )
        self.backup_checkbox.pack(anchor="w", pady=(0, 8))

        # 跳过损坏文档
        self.skip_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="跳过损坏的文档",
            variable=self.skip_corrupted_var,
            command=self._on_config_change,
            checkbox_width=20,
            checkbox_height=20
        )
        self.skip_checkbox.pack(anchor="w")

    def _on_config_change(self):
        """配置变化时的处理"""
        if self.config_callback:
            config = self.get_config()
            self.config_callback(config)

    def get_config(self) -> dict:
        """获取当前配置

        Returns:
            配置字典
        """
        return {
            "title_mode": self.title_mode_var.get(),
            "fix_errors": self.fix_errors_var.get(),
            "create_backup": self.create_backup_var.get(),
            "skip_corrupted": self.skip_corrupted_var.get()
        }

    def set_config(self, config: dict):
        """设置配置

        Args:
            config: 配置字典
        """
        if "title_mode" in config:
            self.title_mode_var.set(config["title_mode"])

        if "fix_errors" in config:
            self.fix_errors_var.set(config["fix_errors"])

        if "create_backup" in config:
            self.create_backup_var.set(config["create_backup"])

        if "skip_corrupted" in config:
            self.skip_corrupted_var.set(config["skip_corrupted"])

    def get_title_mode(self) -> str:
        """获取标题模式

        Returns:
            标题模式 ("1" 或 "2")
        """
        return self.title_mode_var.get()

    def set_title_mode(self, mode: str):
        """设置标题模式

        Args:
            mode: 标题模式 ("1" 或 "2")
        """
        self.title_mode_var.set(mode)
        self._on_config_change()

    def get_fix_errors(self) -> bool:
        """获取自动修复选项

        Returns:
            是否自动修复错误
        """
        return self.fix_errors_var.get()

    def set_fix_errors(self, value: bool):
        """设置自动修复选项

        Args:
            value: 是否自动修复错误
        """
        self.fix_errors_var.set(value)

    def get_create_backup(self) -> bool:
        """获取创建备份选项

        Returns:
            是否创建备份
        """
        return self.create_backup_var.get()

    def set_create_backup(self, value: bool):
        """设置创建备份选项

        Args:
            value: 是否创建备份
        """
        self.create_backup_var.set(value)

    def get_skip_corrupted(self) -> bool:
        """获取跳过损坏文档选项

        Returns:
            是否跳过损坏文档
        """
        return self.skip_corrupted_var.get()

    def set_skip_corrupted(self, value: bool):
        """设置跳过损坏文档选项

        Args:
            value: 是否跳过损坏文档
        """
        self.skip_corrupted_var.set(value)
