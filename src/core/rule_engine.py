"""规则引擎模块

管理规则的注册、执行和错误处理
"""

from typing import List, Dict, Any, Optional, Callable
from docx import Document
from loguru import logger

from rules.base_rule import BaseRule, ValidationError
from rules.structure_rules import ThreeLineGroupValidationRule


class RuleEngine:
    """规则引擎

    负责管理所有规则并按顺序执行
    """

    def __init__(self):
        """初始化规则引擎"""
        self.rules: List[BaseRule] = []
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None

    def register_rule(self, rule: BaseRule) -> None:
        """注册规则

        Args:
            rule: 要注册的规则对象
        """
        if not isinstance(rule, BaseRule):
            raise TypeError(f"规则必须继承自 BaseRule，当前类型: {type(rule)}")

        self.rules.append(rule)
        logger.info(f"注册规则: {rule.name}")

    def unregister_rule(self, rule_name: str) -> bool:
        """注销规则

        Args:
            rule_name: 规则名称

        Returns:
            True表示成功注销，False表示未找到规则
        """
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                logger.info(f"注销规则: {rule_name}")
                return True
        return False

    def get_rule(self, rule_name: str) -> Optional[BaseRule]:
        """获取指定规则

        Args:
            rule_name: 规则名称

        Returns:
            规则对象，如果未找到则返回None
        """
        for rule in self.rules:
            if rule.name == rule_name:
                return rule
        return None

    def get_all_rules(self) -> List[BaseRule]:
        """获取所有已注册的规则

        Returns:
            规则列表
        """
        return self.rules.copy()

    def get_enabled_rules(self) -> List[BaseRule]:
        """获取所有已启用的规则

        Returns:
            已启用的规则列表
        """
        return [rule for rule in self.rules if rule.is_enabled()]

    def enable_rule(self, rule_name: str) -> bool:
        """启用指定规则

        Args:
            rule_name: 规则名称

        Returns:
            True表示成功，False表示未找到规则
        """
        rule = self.get_rule(rule_name)
        if rule:
            rule.enable()
            logger.info(f"启用规则: {rule_name}")
            return True
        return False

    def disable_rule(self, rule_name: str) -> bool:
        """禁用指定规则

        Args:
            rule_name: 规则名称

        Returns:
            True表示成功，False表示未找到规则
        """
        rule = self.get_rule(rule_name)
        if rule:
            rule.disable()
            logger.info(f"禁用规则: {rule_name}")
            return True
        return False

    def clear_all_errors(self) -> None:
        """清空所有规则的错误"""
        for rule in self.rules:
            rule.clear_errors()

    def get_all_errors(self) -> List[ValidationError]:
        """获取所有规则的错误

        Returns:
            所有错误列表
        """
        all_errors = []
        for rule in self.rules:
            all_errors.extend(rule.get_errors())
        return all_errors

    def get_error_summary(self) -> Dict[str, Dict[str, int]]:
        """获取所有规则的错误汇总

        Returns:
            按规则和类型分组的错误统计
        """
        summary = {}
        for rule in self.rules:
            if rule.has_errors():
                summary[rule.name] = rule.get_error_summary()
        return summary

    def validate(self, document: Document) -> List[ValidationError]:
        """使用所有已启用的规则校验文档

        Args:
            document: 要校验的Word文档对象

        Returns:
            所有错误列表
        """
        self.clear_all_errors()
        enabled_rules = self.get_enabled_rules()

        logger.info(f"开始校验文档，共{len(enabled_rules)}个规则")

        for i, rule in enumerate(enabled_rules):
            if self.progress_callback:
                self.progress_callback(i + 1, len(enabled_rules), f"执行规则: {rule.name}")

            try:
                rule.validate(document)
                logger.info(f"规则 {rule.name} 校验完成，发现 {len(rule.get_errors())} 个错误")
            except Exception as e:
                logger.error(f"规则 {rule.name} 执行失败: {str(e)}")

        return self.get_all_errors()

    def execute_rules(self, document: Document, fix_errors: bool = False) -> Document:
        """执行所有已启用的规则

        Args:
            document: 要处理的Word文档对象
            fix_errors: 是否自动修复错误

        Returns:
            处理后的文档对象
        """
        enabled_rules = self.get_enabled_rules()

        logger.info(f"开始执行规则，共{len(enabled_rules)}个规则，修复模式: {fix_errors}")

        for i, rule in enumerate(enabled_rules):
            if self.progress_callback:
                self.progress_callback(i + 1, len(enabled_rules), f"执行规则: {rule.name}")

            try:
                if fix_errors:
                    # 修复模式
                    document = rule.fix(document)
                else:
                    # 普通应用模式
                    document = rule.apply(document)

                logger.info(f"规则 {rule.name} 执行完成")
            except Exception as e:
                logger.error(f"规则 {rule.name} 执行失败: {str(e)}")

        return document

    def set_progress_callback(self, callback: Callable[[int, int, str], None]) -> None:
        """设置进度回调函数

        Args:
            callback: 回调函数，参数为 (current, total, message)
        """
        self.progress_callback = callback

    def get_rule_count(self) -> int:
        """获取规则总数

        Returns:
            规则总数
        """
        return len(self.rules)

    def get_enabled_rule_count(self) -> int:
        """获取已启用的规则数量

        Returns:
            已启用的规则数量
        """
        return len(self.get_enabled_rules())


class RuleFactory:
    """规则工厂

    根据配置创建规则实例
    """

    @staticmethod
    def create_rule(rule_config: Dict[str, Any]) -> BaseRule:
        """根据配置创建规则

        Args:
            rule_config: 规则配置字典，必须包含 'type' 字段

        Returns:
            规则实例

        Raises:
            ValueError: 不支持的规则类型
        """
        rule_type = rule_config.get('type')
        enabled = rule_config.get('enabled', True)
        config = rule_config.get('config', {})

        if rule_type == 'structure_validation':
            return ThreeLineGroupValidationRule(
                title_mode=config.get('title_mode', '1'),
                enabled=enabled
            )
        elif rule_type == 'text_replacement':
            # TODO: 实现文本替换规则
            raise NotImplementedError(f"规则类型 {rule_type} 尚未实现")
        elif rule_type == 'format_adjustment':
            # TODO: 实现格式调整规则
            raise NotImplementedError(f"规则类型 {rule_type} 尚未实现")
        elif rule_type == 'content_operation':
            # TODO: 实现内容操作规则
            raise NotImplementedError(f"规则类型 {rule_type} 尚未实现")
        elif rule_type == 'advanced':
            # TODO: 实现高级规则
            raise NotImplementedError(f"规则类型 {rule_type} 尚未实现")
        else:
            raise ValueError(f"不支持的规则类型: {rule_type}")

    @staticmethod
    def create_rules_from_config(configs: List[Dict[str, Any]]) -> List[BaseRule]:
        """根据配置列表创建多个规则

        Args:
            configs: 规则配置列表

        Returns:
            规则实例列表
        """
        rules = []
        for rule_config in configs:
            try:
                rule = RuleFactory.create_rule(rule_config)
                rules.append(rule)
            except Exception as e:
                logger.error(f"创建规则失败: {str(e)}, 配置: {rule_config}")
        return rules
