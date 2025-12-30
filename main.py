#!/usr/bin/env python3
"""DocuRuleFix - Word 文档处理工具

主入口文件
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 重要：在导入任何使用 python-docx 的模块之前，先应用补丁
from src.utils.docx_patch import apply_patch
apply_patch()

from loguru import logger
from src.core.rule_engine import RuleEngine
from src.core.document_processor import DocumentProcessor, CorruptedDocumentError
from src.rules.structure_rules import ThreeLineGroupValidationRule


def print_usage():
    """打印使用说明"""
    print("\n" + "="*50)
    print("DocuRuleFix - Word 文档处理工具")
    print("="*50)
    print("\n使用方法:")
    print("  python main.py <文件路径>                          # 校验文档（标准模式）")
    print("  python main.py <文件路径> --mode=simple            # 使用精简模式校验")
    print("  python main.py <文件路径> --mode=standard          # 使用标准模式校验")
    print("  python main.py <文件路径> --fix                    # 校验并修复文档")
    print("  python main.py <文件路径> --skip-corrupted         # 跳过损坏的文档")
    print("\n模式说明:")
    print("  --mode=standard (或 --mode=1)")
    print("      标准模式：标题必须包含 . _ ： 三个字符")
    print("      格式：序号.舆论场_来源：标题内容")
    print()
    print("  --mode=simple (或 --mode=2)")
    print("      精简模式：标题只需 序号.内容 格式")
    print("      格式：序号.标题内容")
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

# 跳过损坏的文档
try:
    result = processor.validate_only("test.docx", skip_corrupted=True)
except CorruptedDocumentError as e:
    print(f"跳过损坏的文档: {e.file_path}")
'''

    print(code_example)
    print("-" * 50)


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

    # 解析命令行参数
    title_mode = "1"  # 默认标准模式
    if "--mode=simple" in sys.argv or "--mode=2" in sys.argv:
        title_mode = "2"
    elif "--mode=standard" in sys.argv or "--mode=1" in sys.argv:
        title_mode = "1"

    skip_corrupted = "--skip-corrupted" in sys.argv
    fix_mode = "--fix" in sys.argv

    # 创建规则引擎
    rule_engine = RuleEngine()

    # 注册三行一组结构校验规则（使用指定的模式）
    structure_rule = ThreeLineGroupValidationRule(title_mode=title_mode, enabled=True)
    rule_engine.register_rule(structure_rule)

    mode_name = "精简模式" if title_mode == "2" else "标准模式"
    logger.info(f"使用模式: {mode_name}")
    logger.info(f"已注册 {rule_engine.get_rule_count()} 个规则")
    logger.info(f"已启用 {rule_engine.get_enabled_rule_count()} 个规则")

    # 如果提供了命令行参数，则处理文件
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            logger.info(f"处理文件: {file_path}")

            processor = DocumentProcessor(rule_engine, create_backup=True)

            try:
                # 先校验
                result = processor.validate_only(file_path, skip_corrupted=skip_corrupted)
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
                    if fix_mode:
                        print("\n正在修复...")

                        # 生成输出文件名：添加 _fixed 后缀
                        from pathlib import Path
                        path_obj = Path(file_path)
                        fixed_path = str(path_obj.parent / f"{path_obj.stem}_fixed{path_obj.suffix}")

                        result = processor.process(file_path, output_path=fixed_path, fix_errors=True, skip_corrupted=skip_corrupted)
                        print(f"修复结果: {result.message}")
                        print(f"修复后的文件: {fixed_path}")

                        # 再次校验修复后的文件
                        print("\n正在校验修复后的文件...")
                        result = processor.validate_only(fixed_path, skip_corrupted=skip_corrupted)
                        print(f"修复后校验: {result.message}")

                        # 显示修复后剩余的错误
                        errors_after = rule_engine.get_all_errors()
                        if errors_after:
                            print(f"\n修复后仍存在 {len(errors_after)} 个问题:")
                            for error in errors_after[:10]:
                                print(f"  [{error.line_type}] 行{error.line_index + 1}: {error.message}")
                            if len(errors_after) > 10:
                                print(f"  ... 还有 {len(errors_after) - 10} 个问题")
                        else:
                            print("\n修复完成，文档结构已正确！")
                else:
                    print("\n文档结构完全正确！")

            except CorruptedDocumentError as e:
                print(f"\n跳过损坏的文档: {e.file_path}")
                print(f"原因: {e.original_error}")
                logger.warning(f"文档损坏已跳过: {file_path}")

        else:
            logger.error(f"文件不存在: {file_path}")
    else:
        print_usage()
        print("\n提示: 使用 `python main.py <文件路径>` 来处理文档")
        print("      使用 `python main.py <文件路径> --mode=simple` 使用精简模式")
        print("      使用 `python main.py <文件路径> --fix` 来修复文档")
        print("      使用 `python main.py <文件路径> --skip-corrupted` 来跳过损坏文档")

    logger.info("DocuRuleFix 退出")


if __name__ == "__main__":
    main()
