"""文档处理引擎模块

负责单个文档的处理、保存和备份
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from datetime import datetime
from docx import Document
from loguru import logger

from core.rule_engine import RuleEngine


class CorruptedDocumentError(Exception):
    """文档损坏异常

    当文档内部结构损坏时抛出，用于跳过损坏的文档
    """

    def __init__(self, file_path: str, original_error: str):
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(f"文档损坏: {file_path}, 原因: {original_error}")


class ProcessingResult:
    """处理结果"""

    def __init__(self, success: bool, input_path: str, output_path: str,
                 errors_count: int = 0, message: str = ""):
        self.success = success
        self.input_path = input_path
        self.output_path = output_path
        self.errors_count = errors_count
        self.message = message
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "errors_count": self.errors_count,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }


class DocumentProcessor:
    """文档处理器

    负责处理单个Word文档
    """

    def __init__(self, rule_engine: RuleEngine, create_backup: bool = True):
        """

        Args:
            rule_engine: 规则引擎实例
            create_backup: 是否创建备份
        """
        self.rule_engine = rule_engine
        self.create_backup = create_backup
        self.backup_dir: Optional[str] = None

    def set_backup_dir(self, backup_dir: str) -> None:
        """设置备份目录

        Args:
            backup_dir: 备份目录路径
        """
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
        logger.info(f"设置备份目录: {backup_dir}")

    def process(self, input_path: str, output_path: Optional[str] = None,
                fix_errors: bool = False, skip_corrupted: bool = False) -> ProcessingResult:
        """处理单个文档

        Args:
            input_path: 输入文档路径
            output_path: 输出文档路径，如果为None则覆盖原文件
            fix_errors: 是否自动修复错误
            skip_corrupted: 是否跳过损坏的文档（抛出CorruptedDocumentError异常），
                           True表示跳过（抛出异常让调用者处理），False表示返回错误结果

        Returns:
            处理结果对象

        Raises:
            CorruptedDocumentError: 当skip_corrupted=True且文档损坏时
        """
        try:
            # 验证输入文件
            if not os.path.exists(input_path):
                return ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path=output_path or input_path,
                    message=f"输入文件不存在: {input_path}"
                )

            logger.info(f"开始处理文档: {input_path}")

            # 加载文档
            document = Document(input_path)

            # 创建备份（如果需要且是覆盖模式）
            if output_path is None and self.create_backup:
                backup_path = self._create_backup(input_path)
                logger.info(f"创建备份: {backup_path}")

            # 执行规则
            document = self.rule_engine.execute_rules(document, fix_errors=fix_errors)

            # 获取错误信息
            errors = self.rule_engine.get_all_errors()
            errors_count = len(errors)

            # 确定输出路径
            if output_path is None:
                output_path = input_path

            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # 保存文档
            document.save(output_path)
            logger.info(f"文档保存成功: {output_path}")

            # 构建结果消息
            if errors_count > 0:
                message = f"处理完成，发现 {errors_count} 个问题"
            else:
                message = "处理完成，未发现问题"

            return ProcessingResult(
                success=True,
                input_path=input_path,
                output_path=output_path,
                errors_count=errors_count,
                message=message
            )

        except KeyError as e:
            # 处理文档内部引用损坏的情况（如 ../NULL 引用）
            error_msg = str(e)
            if "NULL" in error_msg or "archive" in error_msg:
                logger.error(f"文档内部结构损坏: {input_path}, {error_msg}")

                if skip_corrupted:
                    # 抛出异常让调用者跳过此文档
                    raise CorruptedDocumentError(input_path, error_msg)
                else:
                    # 返回错误结果
                    return ProcessingResult(
                        success=False,
                        input_path=input_path,
                        output_path=output_path or input_path,
                        message=f"文档内部结构损坏（可能有损坏的图片引用）。建议用Word打开并另存为新文件。错误: {error_msg}"
                    )
            raise
        except Exception as e:
            logger.error(f"处理文档失败: {input_path}, 错误: {str(e)}")
            return ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=output_path or input_path,
                message=f"处理失败: {str(e)}"
            )

    def validate_only(self, input_path: str, skip_corrupted: bool = False) -> ProcessingResult:
        """仅校验文档不修改

        Args:
            input_path: 输入文档路径
            skip_corrupted: 是否跳过损坏的文档（抛出CorruptedDocumentError异常），
                           True表示跳过（抛出异常让调用者处理），False表示返回错误结果

        Returns:
            处理结果对象

        Raises:
            CorruptedDocumentError: 当skip_corrupted=True且文档损坏时
        """
        try:
            if not os.path.exists(input_path):
                return ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path=input_path,
                    message=f"输入文件不存在: {input_path}"
                )

            logger.info(f"开始校验文档: {input_path}")

            # 加载文档
            document = Document(input_path)

            # 执行校验
            errors = self.rule_engine.validate(document)
            errors_count = len(errors)

            logger.info(f"校验完成，发现 {errors_count} 个问题")

            return ProcessingResult(
                success=True,
                input_path=input_path,
                output_path=input_path,
                errors_count=errors_count,
                message=f"校验完成，发现 {errors_count} 个问题"
            )

        except KeyError as e:
            # 处理文档内部引用损坏的情况（如 ../NULL 引用）
            error_msg = str(e)
            if "NULL" in error_msg or "archive" in error_msg:
                logger.error(f"文档内部结构损坏: {input_path}, {error_msg}")

                if skip_corrupted:
                    # 抛出异常让调用者跳过此文档
                    raise CorruptedDocumentError(input_path, error_msg)
                else:
                    # 返回错误结果
                    return ProcessingResult(
                        success=False,
                        input_path=input_path,
                        output_path=input_path,
                        message=f"文档内部结构损坏（可能有损坏的图片引用）。建议用Word打开并另存为新文件。错误: {error_msg}"
                    )
            raise
        except Exception as e:
            logger.error(f"校验文档失败: {input_path}, 错误: {str(e)}")
            return ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=input_path,
                message=f"校验失败: {str(e)}"
            )

    def _create_backup(self, file_path: str) -> str:
        """创建文件备份

        Args:
            file_path: 原文件路径

        Returns:
            备份文件路径
        """
        # 确定备份目录
        if self.backup_dir:
            backup_dir = self.backup_dir
        else:
            # 默认在原文件同目录下创建 backups 子目录
            file_dir = os.path.dirname(file_path)
            backup_dir = os.path.join(file_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)

        # 生成备份文件名
        file_name = Path(file_path).name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{timestamp}_{file_name}"
        backup_path = os.path.join(backup_dir, backup_name)

        # 复制文件
        shutil.copy2(file_path, backup_path)

        return backup_path

    def get_backup_files(self, file_path: str) -> list[str]:
        """获取指定文件的所有备份

        Args:
            file_path: 原文件路径

        Returns:
            备份文件路径列表，按时间倒序
        """
        # 确定备份目录
        if self.backup_dir:
            backup_dir = self.backup_dir
        else:
            file_dir = os.path.dirname(file_path)
            backup_dir = os.path.join(file_dir, "backups")

        if not os.path.exists(backup_dir):
            return []

        file_name = Path(file_path).name

        # 查找所有备份文件
        backups = []
        for file in os.listdir(backup_dir):
            if file.endswith(file_name):
                backup_path = os.path.join(backup_dir, file)
                backups.append(backup_path)

        # 按修改时间倒序排序
        backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        return backups

    def restore_from_backup(self, file_path: str, backup_path: str) -> bool:
        """从备份恢复文件

        Args:
            file_path: 要恢复的文件路径
            backup_path: 备份文件路径

        Returns:
            True表示成功，False表示失败
        """
        try:
            if not os.path.exists(backup_path):
                logger.error(f"备份文件不存在: {backup_path}")
                return False

            shutil.copy2(backup_path, file_path)
            logger.info(f"从备份恢复文件: {backup_path} -> {file_path}")
            return True

        except Exception as e:
            logger.error(f"恢复文件失败: {str(e)}")
            return False

    def clean_old_backups(self, file_path: str, keep_count: int = 5) -> int:
        """清理旧备份，保留最近的几个

        Args:
            file_path: 原文件路径
            keep_count: 保留的备份数量

        Returns:
            删除的备份数量
        """
        backups = self.get_backup_files(file_path)

        if len(backups) <= keep_count:
            return 0

        # 删除多余的备份
        deleted_count = 0
        for backup in backups[keep_count:]:
            try:
                os.remove(backup)
                logger.info(f"删除旧备份: {backup}")
                deleted_count += 1
            except Exception as e:
                logger.error(f"删除备份失败: {backup}, 错误: {str(e)}")

        return deleted_count
