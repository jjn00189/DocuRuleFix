"""进度面板

显示处理进度和实时日志。
"""

import customtkinter as ctk
from typing import Optional
from datetime import datetime


class ProgressPanel(ctk.CTkFrame):
    """进度面板

    显示进度条、状态和日志信息。
    """

    # 日志颜色映射
    LOG_COLORS = {
        "INFO": ("black", "gray90"),
        "WARNING": ("dark orange", "gray90"),
        "ERROR": ("dark red", "gray90"),
        "SUCCESS": ("dark green", "gray90")
    }

    def __init__(self, parent, **kwargs):
        """初始化进度面板

        Args:
            parent: 父组件
            **kwargs: 其他参数
        """
        super().__init__(parent, **kwargs)

        self._current_progress = 0
        self._total_progress = 100

        self._build_ui()

    def _build_ui(self):
        """构建用户界面"""
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="处理进度",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(0, 10), anchor="w")

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=400,
            height=20,
            progress_color=("blue", "dark blue")
        )
        self.progress_bar.pack(pady=(0, 5))
        self.progress_bar.set(0)

        # 状态标签
        self.status_label = ctk.CTkLabel(
            self,
            text="就绪",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.status_label.pack(fill="x", pady=(0, 10))

        # 日志区域
        log_frame = ctk.CTkFrame(self)
        log_frame.pack(fill="both", expand=True)

        # 日志标题和按钮
        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill="x", pady=(0, 5))

        log_title = ctk.CTkLabel(
            log_header,
            text="处理日志",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        log_title.pack(side="left")

        # 清除按钮
        clear_button = ctk.CTkButton(
            log_header,
            text="清除",
            width=60,
            height=24,
            command=self._clear_logs,
            font=ctk.CTkFont(size=10),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray20")
        )
        clear_button.pack(side="right")

        # 日志文本框
        self.log_textbox = ctk.CTkTextbox(
            log_frame,
            height=200,
            font=ctk.CTkFont(family="Courier", size=10)
        )
        self.log_textbox.pack(fill="both", expand=True)
        self.log_textbox.configure(state="disabled")

    def start_progress(self, total: int = 100):
        """开始进度

        Args:
            total: 总数
        """
        self._current_progress = 0
        self._total_progress = total
        self.progress_bar.set(0)
        self.set_status("正在处理...")

    def update_progress(self, current: int, total: Optional[int] = None, message: str = ""):
        """更新进度

        Args:
            current: 当前进度
            total: 总数（可选）
            message: 进度消息
        """
        if total is not None:
            self._total_progress = total

        self._current_progress = current

        # 计算进度百分比
        if self._total_progress > 0:
            progress = current / self._total_progress
        else:
            progress = 0

        self.progress_bar.set(progress)

        # 更新状态
        if message:
            self.set_status(message)
        else:
            percentage = int(progress * 100)
            self.set_status(f"处理中... {percentage}%")

    def set_status(self, message: str):
        """设置状态消息

        Args:
            message: 状态消息
        """
        self.status_label.configure(text=message)

    def add_log(self, level: str, message: str):
        """添加日志消息

        Args:
            level: 日志级别 (INFO, WARNING, ERROR, SUCCESS)
            message: 日志消息
        """
        # 生成时间戳
        timestamp = datetime.now().strftime("%H:%M:%S")

        # 格式化日志
        log_line = f"{timestamp} | {level: <7} | {message}\n"

        # 启用文本框以添加内容
        self.log_textbox.configure(state="normal")

        # 获取当前内容
        current_content = self.log_textbox.get("1.0", "end")

        # 添加新日志
        self.log_textbox.insert("end", log_line)

        # 如果日志太多，删除旧的
        line_count = int(self.log_textbox.index("end-1c").split(".")[0])
        if line_count > 500:
            self.log_textbox.delete("1.0", "100.0")

        # 滚动到底部
        self.log_textbox.see("end")

        # 禁用文本框
        self.log_textbox.configure(state="disabled")

    def log_info(self, message: str):
        """添加信息日志"""
        self.add_log("INFO", message)

    def log_warning(self, message: str):
        """添加警告日志"""
        self.add_log("WARNING", message)

    def log_error(self, message: str):
        """添加错误日志"""
        self.add_log("ERROR", message)

    def log_success(self, message: str):
        """添加成功日志"""
        self.add_log("SUCCESS", message)

    def _clear_logs(self):
        """清除日志"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

    def clear_logs(self):
        """清除所有日志和进度"""
        self._clear_logs()
        self.progress_bar.set(0)
        self.set_status("就绪")

    def finish_progress(self, success: bool, message: str = ""):
        """完成进度

        Args:
            success: 是否成功
            message: 完成消息
        """
        self.progress_bar.set(1.0)

        if success:
            self.set_status(message or "处理完成")
            self.log_success(message or "处理完成")
        else:
            self.set_status(message or "处理失败")
            self.log_error(message or "处理失败")
