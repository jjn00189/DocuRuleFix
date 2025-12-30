"""主题管理器

管理 CustomTkinter 的主题切换和偏好设置。
"""

import json
from pathlib import Path
import customtkinter as ctk


class ThemeManager:
    """主题管理器

    负责管理深色/浅色主题切换和保存用户偏好。
    """

    # 支持的主题模式
    MODES = {
        "dark": "深色",
        "light": "浅色",
        "system": "跟随系统"
    }

    # 支持的颜色主题
    COLOR_THEMES = {
        "blue": "蓝色",
        "green": "绿色",
        "dark-blue": "深蓝色"
    }

    def __init__(self, preferences_file: Path = None):
        """初始化主题管理器

        Args:
            preferences_file: 偏好设置文件路径，默认为 ~/.docurulefix/preferences.json
        """
        if preferences_file is None:
            preferences_file = Path.home() / ".docurulefix" / "preferences.json"

        self.preferences_file = preferences_file
        self.preferences = self._load_preferences()

    def _load_preferences(self) -> dict:
        """加载偏好设置

        Returns:
            偏好设置字典
        """
        default_preferences = {
            "appearance_mode": "dark",  # dark, light, system
            "color_theme": "blue",      # blue, green, dark-blue
            "title_mode": "2",          # 1=标准, 2=精简
            "auto_fix_errors": True,
            "create_backup": True,
            "skip_corrupted": False
        }

        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # 合并默认设置和加载的设置
                    default_preferences.update(loaded)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载偏好设置失败: {e}")

        return default_preferences

    def save_preferences(self) -> bool:
        """保存偏好设置

        Returns:
            是否保存成功
        """
        try:
            self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"保存偏好设置失败: {e}")
            return False

    def get(self, key: str, default=None):
        """获取偏好设置

        Args:
            key: 设置键
            default: 默认值

        Returns:
            设置值
        """
        return self.preferences.get(key, default)

    def set(self, key: str, value) -> bool:
        """设置偏好并保存

        Args:
            key: 设置键
            value: 设置值

        Returns:
            是否保存成功
        """
        self.preferences[key] = value
        return self.save_preferences()

    def get_appearance_mode(self) -> str:
        """获取外观模式

        Returns:
            外观模式 (dark, light, system)
        """
        return self.get("appearance_mode", "dark")

    def set_appearance_mode(self, mode: str) -> bool:
        """设置外观模式

        Args:
            mode: 外观模式 (dark, light, system)

        Returns:
            是否设置成功
        """
        if mode not in self.MODES:
            return False

        # 应用到 CustomTkinter
        ctk.set_appearance_mode(mode)

        # 保存到偏好
        return self.set("appearance_mode", mode)

    def get_color_theme(self) -> str:
        """获取颜色主题

        Returns:
            颜色主题
        """
        return self.get("color_theme", "blue")

    def set_color_theme(self, theme: str) -> bool:
        """设置颜色主题

        Args:
            theme: 颜色主题 (blue, green, dark-blue)

        Returns:
            是否设置成功
        """
        if theme not in self.COLOR_THEMES:
            return False

        # 应用到 CustomTkinter
        ctk.set_default_color_theme(theme)

        # 保存到偏好
        return self.set("color_theme", theme)

    def apply_saved_theme(self):
        """应用保存的主题设置"""
        mode = self.get_appearance_mode()
        theme = self.get_color_theme()

        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme(theme)

    def toggle_theme(self) -> str:
        """切换主题（深色<->浅色）

        Returns:
            切换后的主题
        """
        current = self.get_appearance_mode()
        if current == "dark":
            new_mode = "light"
        elif current == "light":
            new_mode = "dark"
        else:
            new_mode = "dark"  # system 模式默认切换到 dark

        self.set_appearance_mode(new_mode)
        return new_mode

    def get_title_mode(self) -> str:
        """获取标题模式

        Returns:
            标题模式 (1=标准, 2=精简)
        """
        return self.get("title_mode", "2")

    def set_title_mode(self, mode: str) -> bool:
        """设置标题模式

        Args:
            mode: 标题模式 (1=标准, 2=精简)

        Returns:
            是否设置成功
        """
        if mode not in ("1", "2"):
            return False
        return self.set("title_mode", mode)

    def get_auto_fix_errors(self) -> bool:
        """获取自动修复错误选项

        Returns:
            是否自动修复错误
        """
        return self.get("auto_fix_errors", True)

    def set_auto_fix_errors(self, value: bool) -> bool:
        """设置自动修复错误选项

        Args:
            value: 是否自动修复错误

        Returns:
            是否设置成功
        """
        return self.set("auto_fix_errors", bool(value))

    def get_create_backup(self) -> bool:
        """获取创建备份选项

        Returns:
            是否创建备份
        """
        return self.get("create_backup", True)

    def set_create_backup(self, value: bool) -> bool:
        """设置创建备份选项

        Args:
            value: 是否创建备份

        Returns:
            是否设置成功
        """
        return self.set("create_backup", bool(value))

    def get_skip_corrupted(self) -> bool:
        """获取跳过损坏文档选项

        Returns:
            是否跳过损坏文档
        """
        return self.get("skip_corrupted", False)

    def set_skip_corrupted(self, value: bool) -> bool:
        """设置跳过损坏文档选项

        Args:
            value: 是否跳过损坏文档

        Returns:
            是否设置成功
        """
        return self.set("skip_corrupted", bool(value))

    @property
    def appearance_mode_name(self) -> str:
        """获取外观模式的本地化名称"""
        return self.MODES.get(self.get_appearance_mode(), "未知")

    @property
    def color_theme_name(self) -> str:
        """获取颜色主题的本地化名称"""
        return self.COLOR_THEMES.get(self.get_color_theme(), "未知")
