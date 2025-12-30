#!/usr/bin/env python3
"""DocuRuleFix - Word 文档处理工具

主入口文件
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from loguru import logger
from src.core.rule_engine import RuleEngine
from src.core.document_processor import DocumentProcessor
from src.rules.structure_rules import ThreeLineGroupValidationRule


def main():
    """主函数"""
    # 配置日志
    logger.remove()  # 移除默认处理器
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/docurulefix_{time:YYYY-MM-DD}.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        encoding="utf-8"
    )

    logger.info("DocuRuleFix 启动")

    # 创建规则引擎
    rule_engine = RuleEngine()

    # 注册三行一组结构校验规则
    structure_rule = ThreeLineGroupValidationRule(title_mode="1", enabled=True)
    rule_engine.register_rule(structure_rule)

    logger.info(f"已注册 {rule_engine.get_rule_count()} 个规则")
    logger.info(f"已启用 {rule_engine.get_enabled_rule_count()} 个规则")

    # TODO: 这里添加 GUI 启动代码或 CLI 命令处理
    print("\n" + "="*50)
    print("DocuRuleFix - Word 文档处理工具")
    print("="*50)
    print("\n当前版本仅支持命令行测试")
    print("使用方法:")
    print('  processor.validate_only("path/to/document.docx")  # 仅校验')
    print('  processor.process("path/to/document.docx")         # 处理文档')
    print("\n示例代码:")
    print("-" * 50)

    # 创建示例代码供测试
    code_example = '''
# 创建文档处理器
processor = DocumentProcessor(rule_engine, create_backup=True)

# 仅校验文档
result = processor.validate_only("test.docx")
print(f"校验结果: {result.message}")

# 处理文档（带修复）
result = processor.process("test.docx", fix_errors=True)
print(f"处理结果: {result.message}")
'''

    print(code_example)
    print("-" * 50)

    # 如果提供了命令行参数，则处理文件
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            logger.info(f"处理文件: {file_path}")

            processor = DocumentProcessor(rule_engine, create_backup=True)

            # 先校验
            result = processor.validate_only(file_path)
            print(f"\n校验结果: {result.message}")

            # 显示错误详情
            errors = rule_engine.get_all_errors()
            if errors:
                print(f"\n发现 {len(errors)} 个问题:")
                for error in errors[:10]:  # 只显示前10个
                    print(f"  [{error.line_type}] 行{error.line_index + 1}: {error.message}")
                if len(errors) > 10:
                    print(f"  ... 还有 {len(errors) - 10} 个问题")

                # 询问是否修复
                if len(sys.argv) > 2 and sys.argv[2] == "--fix":
                    print("\n正在修复...")
                    result = processor.process(file_path, fix_errors=True)
                    print(f"修复结果: {result.message}")

                    # 再次校验
                    result = processor.validate_only(file_path)
                    print(f"修复后校验: {result.message}")
            else:
                print("\n文档结构完全正确！")
        else:
            logger.error(f"文件不存在: {file_path}")
    else:
        print("\n提示: 使用 `python main.py <文件路径>` 来处理文档")
        print("      使用 `python main.py <文件路径> --fix` 来修复文档")

    logger.info("DocuRuleFix 退出")


if __name__ == "__main__":
    main()
