"""规则基类模块

定义所有规则的抽象基类，提供统一的规则接口
"""

from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional
from docx import Document


class ValidationError:
    """校验错误

    用于记录文档校验过程中发现的错误
    """

    def __init__(self, line_index: int, line_type: str, message: str, severity: str = "error"):
        """

        Args:
            line_index: 错误所在的段落索引（从0开始）
            line_type: 行类型（'title', 'url', 'image', 'structure'等）
            message: 错误描述信息
            severity: 严重程度（'error', 'warning', 'info'）
        """
        self.line_index = line_index
        self.line_type = line_type
        self.message = message
        self.severity = severity

    def __repr__(self) -> str:
        return f"ValidationError(index={self.line_index}, type={self.line_type}, message={self.message})"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "line_index": self.line_index,
            "line_type": self.line_type,
            "message": self.message,
            "severity": self.severity
        }


class BaseRule(ABC):
    """规则抽象基类

    所有文档处理规则必须继承此类并实现相应方法
    """

    def __init__(self, name: str, enabled: bool = True):
        """

        Args:
            name: 规则名称
            enabled: 是否启用该规则
        """
        self.name = name
        self.enabled = enabled
        self.errors: List[ValidationError] = []

    @abstractmethod
    def validate(self, document: Document) -> List[ValidationError]:
        """校验文档

        Args:
            document: 要校验的Word文档对象

        Returns:
            发现的错误列表
        """
        pass

    @abstractmethod
    def apply(self, document: Document) -> Document:
        """应用规则到文档

        Args:
            document: 要处理的Word文档对象

        Returns:
            处理后的文档对象
        """
        pass

    def fix(self, document: Document) -> Document:
        """自动修复文档

        默认实现为返回原文档，子类可以覆盖此方法实现自动修复逻辑

        Args:
            document: 要修复的Word文档对象

        Returns:
            修复后的文档对象
        """
        return document

    def get_errors(self) -> List[ValidationError]:
        """获取校验错误列表

        Returns:
            错误列表
        """
        return self.errors

    def clear_errors(self) -> None:
        """清空错误列表"""
        self.errors.clear()

    def has_errors(self) -> bool:
        """是否有错误

        Returns:
            True表示有错误，False表示无错误
        """
        return len(self.errors) > 0

    def get_error_summary(self) -> Dict[str, int]:
        """获取错误汇总信息

        Returns:
            按类型分组的错误数量统计
        """
        summary: Dict[str, int] = {}
        for error in self.errors:
            if error.line_type not in summary:
                summary[error.line_type] = 0
            summary[error.line_type] += 1
        return summary

    def is_enabled(self) -> bool:
        """检查规则是否启用

        Returns:
            True表示已启用，False表示未启用
        """
        return self.enabled

    def enable(self) -> None:
        """启用规则"""
        self.enabled = True

    def disable(self) -> None:
        """禁用规则"""
        self.enabled = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, enabled={self.enabled})"
