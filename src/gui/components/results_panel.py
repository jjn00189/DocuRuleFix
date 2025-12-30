"""结果面板

显示校验结果和错误信息。
"""

import customtkinter as ctk
import json
from typing import List, Dict, Optional
from pathlib import Path


class ResultsPanel(ctk.CTkFrame):
    """结果面板

    显示校验错误，支持按类型分组和导出。
    """

    def __init__(self, parent, **kwargs):
        """初始化结果面板

        Args:
            parent: 父组件
            **kwargs: 其他参数
        """
        super().__init__(parent, **kwargs)

        self.current_errors: List = []
        self.error_groups: Dict[str, List] = {
            'all': [],
            'title': [],
            'url': [],
            'image': [],
            'structure': []
        }

        self._build_ui()

    def _build_ui(self):
        """构建用户界面"""
        # 标题框架
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="校验结果",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(side="left")

        # 错误计数标签
        self.count_label = ctk.CTkLabel(
            header_frame,
            text="共 0 个问题",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        self.count_label.pack(side="right")

        # 标签页
        self.tabview = ctk.CTkTabview(self, width=400, height=300)
        self.tabview.pack(fill="both", expand=True, pady=(0, 10))

        # 创建标签页
        self.tab_names = ["全部错误", "标题行错误", "URL错误", "图片错误"]
        for tab_name in self.tab_names:
            self.tabview.add(tab_name)

        # 为每个标签页创建滚动框架
        self.scroll_frames = {}
        for tab_name in self.tab_names:
            tab = self.tabview.tab(tab_name)
            scroll_frame = ctk.CTkScrollableFrame(tab, width=380, height=280)
            scroll_frame.pack(fill="both", expand=True)
            self.scroll_frames[tab_name] = scroll_frame

        # 导出按钮框架
        export_frame = ctk.CTkFrame(self, fg_color="transparent")
        export_frame.pack(fill="x")

        # 导出 JSON 按钮
        export_json_button = ctk.CTkButton(
            export_frame,
            text="导出 JSON",
            command=lambda: self._export_errors("json"),
            width=100
        )
        export_json_button.pack(side="left", padx=(0, 10))

        # 导出 CSV 按钮
        export_csv_button = ctk.CTkButton(
            export_frame,
            text="导出 CSV",
            command=lambda: self._export_errors("csv"),
            width=100
        )
        export_csv_button.pack(side="left")

    def display_errors(self, errors: List):
        """显示错误列表

        Args:
            errors: 错误列表
        """
        self.current_errors = errors
        self._group_errors(errors)
        self._update_count_label()
        self._render_errors()

    def _group_errors(self, errors: List):
        """分组错误

        Args:
            errors: 错误列表
        """
        # 清空分组
        for key in self.error_groups:
            self.error_groups[key] = []

        # 分组
        for error in errors:
            self.error_groups['all'].append(error)

            error_type = error.line_type
            if error_type not in self.error_groups:
                error_type = 'structure'
            self.error_groups[error_type].append(error)

    def _update_count_label(self):
        """更新错误计数标签"""
        total = len(self.current_errors)
        self.count_label.configure(text=f"共 {total} 个问题")

    def _render_errors(self):
        """渲染错误到界面"""
        # 清空所有滚动框架的内容
        for scroll_frame in self.scroll_frames.values():
            for widget in scroll_frame.winfo_children():
                widget.destroy()

        # 渲染各标签的错误
        self._render_tab_errors("全部错误", self.error_groups.get('all', []))
        self._render_tab_errors("标题行错误", self.error_groups.get('title', []))
        self._render_tab_errors("URL错误", self.error_groups.get('url', []))
        self._render_tab_errors("图片错误", self.error_groups.get('image', []))

    def _render_tab_errors(self, tab_name: str, errors: List):
        """渲染特定标签的错误

        Args:
            tab_name: 标签名称
            errors: 错误列表
        """
        scroll_frame = self.scroll_frames.get(tab_name)
        if not scroll_frame:
            return

        if not errors:
            # 无错误时显示提示
            no_errors_label = ctk.CTkLabel(
                scroll_frame,
                text="无错误",
                font=ctk.CTkFont(size=12),
                text_color=("gray60", "gray40")
            )
            no_errors_label.pack(pady=20)
            return

        # 按组索引分组显示
        groups: Dict[int, List] = {}
        for error in errors:
            group_index = error.line_index // 3 + 1
            if group_index not in groups:
                groups[group_index] = []
            groups[group_index].append(error)

        # 显示每个组
        for group_index in sorted(groups.keys()):
            group_errors = groups[group_index]

            # 组标题
            group_frame = ctk.CTkFrame(scroll_frame, fg_color=("gray85", "gray25"))
            group_frame.pack(fill="x", pady=(5, 0), padx=5)

            group_label = ctk.CTkLabel(
                group_frame,
                text=f"▼ 第{group_index}组 ({len(group_errors)}个错误)",
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="w"
            )
            group_label.pack(fill="x", padx=10, pady=5)

            # 组内容（嵌入到外层）
            group_content = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            group_content.pack(fill="x", padx=10, pady=(0, 10))

            for error in group_errors:
                error_item = self._create_error_item(group_content, error)
                error_item.pack(fill="x", pady=2)

    def _create_error_item(self, parent, error) -> ctk.CTkFrame:
        """创建错误项组件

        Args:
            parent: 父组件
            error: 错误对象

        Returns:
            错误项组件
        """
        error_frame = ctk.CTkFrame(
            parent,
            fg_color=("gray80", "gray20"),
            corner_radius=5
        )

        # 类型标签
        type_label = ctk.CTkLabel(
            error_frame,
            text=f"[{error.line_type}]",
            font=ctk.CTkFont(size=10),
            width=60
        )
        type_label.pack(side="left", padx=(10, 5))

        # 行号和消息
        text_label = ctk.CTkLabel(
            error_frame,
            text=f"行{error.line_index + 1}: {error.message}",
            font=ctk.CTkFont(size=10),
            anchor="w"
        )
        text_label.pack(side="left", padx=(0, 10), fill="x", expand=True)

        return error_frame

    def _export_errors(self, format: str):
        """导出错误到文件

        Args:
            format: 导出格式 ("json" 或 "csv")
        """
        if not self.current_errors:
            return

        # 获取保存路径
        from tkinter import filedialog
        from tkinter import Tk

        root = Tk()
        root.withdraw()

        if format == "json":
            file_types = [("JSON 文件", "*.json"), ("所有文件", "*.*")]
            default_ext = ".json"
        else:  # csv
            file_types = [("CSV 文件", "*.csv"), ("所有文件", "*.*")]
            default_ext = ".csv"

        file_path = filedialog.asksaveasfilename(
            title=f"导出错误为 {format.upper()}",
            defaultextension=default_ext,
            filetypes=file_types
        )

        root.destroy()

        if not file_path:
            return

        try:
            if format == "json":
                self._export_json(file_path)
            else:
                self._export_csv(file_path)
        except Exception as e:
            print(f"导出失败: {e}")

    def _export_json(self, file_path: str):
        """导出为 JSON 格式

        Args:
            file_path: 文件路径
        """
        errors_data = []
        for error in self.current_errors:
            errors_data.append({
                "line_index": error.line_index,
                "line_type": error.line_type,
                "message": error.message
            })

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(errors_data, f, ensure_ascii=False, indent=2)

    def _export_csv(self, file_path: str):
        """导出为 CSV 格式

        Args:
            file_path: 文件路径
        """
        import csv

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["行号", "类型", "消息"])

            for error in self.current_errors:
                writer.writerow([
                    error.line_index + 1,
                    error.line_type,
                    error.message
                ])

    def clear_results(self):
        """清除结果显示"""
        self.current_errors = []
        self.error_groups = {key: [] for key in self.error_groups}
        self._update_count_label()
        self._render_errors()
