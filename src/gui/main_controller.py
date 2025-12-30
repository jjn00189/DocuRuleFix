"""主控制器

连接 GUI 和核心逻辑，管理处理流程。
"""

import threading
import queue
from typing import Optional, List, Callable, Dict, Any
from pathlib import Path
from loguru import logger

# 导入核心模块
from core.rule_engine import RuleEngine
from core.document_processor import DocumentProcessor, ProcessingResult, CorruptedDocumentError
from rules.structure_rules import ThreeLineGroupValidationRule

# 导入 GUI 工具
from gui.utils.theme_manager import ThemeManager
from gui.utils.threading_helpers import (
    ProgressQueue, WorkerThread, ProcessCallback, InterruptedException
)


class MainController:
    """主控制器

    管理 GUI 和核心逻辑之间的交互。
    """

    def __init__(self, theme_manager: ThemeManager):
        """初始化主控制器

        Args:
            theme_manager: 主题管理器
        """
        self.theme_manager = theme_manager

        # 核心组件
        self.rule_engine: Optional[RuleEngine] = None
        self.processor: Optional[DocumentProcessor] = None

        # 进度队列和线程
        self.progress_queue = ProgressQueue()
        self.worker_thread: Optional[WorkerThread] = None
        self.cancel_flag = threading.Event()

        # 状态
        self.current_file: Optional[str] = None
        self.processing: bool = False
        self.last_result: Optional[ProcessingResult] = None

        # 初始化核心组件
        self._initialize_core()

    def _initialize_core(self):
        """初始化核心组件（规则引擎和文档处理器）"""
        # 创建规则引擎
        self.rule_engine = RuleEngine()

        # 获取标题模式配置
        title_mode = self.theme_manager.get_title_mode()

        # 注册三行一组结构校验规则
        structure_rule = ThreeLineGroupValidationRule(
            title_mode=title_mode,
            enabled=True
        )
        self.rule_engine.register_rule(structure_rule)

        # 创建文档处理器
        create_backup = self.theme_manager.get_create_backup()
        self.processor = DocumentProcessor(
            rule_engine=self.rule_engine,
            create_backup=create_backup
        )

        logger.info(f"主控制器初始化完成，标题模式: {title_mode}")

    def reinitialize_with_mode(self, title_mode: str):
        """使用新的标题模式重新初始化

        Args:
            title_mode: 标题模式 ("1" 或 "2")
        """
        # 保存到偏好
        self.theme_manager.set_title_mode(title_mode)

        # 重新初始化核心组件
        self._initialize_core()

    def update_config(self, **kwargs):
        """更新配置

        Args:
            **kwargs: 配置选项
                - title_mode: 标题模式
                - create_backup: 是否创建备份
        """
        if 'title_mode' in kwargs:
            self.theme_manager.set_title_mode(kwargs['title_mode'])
        if 'create_backup' in kwargs:
            self.theme_manager.set_create_backup(kwargs['create_backup'])

        # 重新初始化核心组件
        self._initialize_core()

    def validate_file_async(self, file_path: str) -> bool:
        """异步校验文件

        Args:
            file_path: 文件路径

        Returns:
            是否成功启动校验
        """
        if self.processing:
            logger.warning("已有任务在处理中")
            return False

        self.current_file = file_path
        self.cancel_flag.clear()

        # 创建工作线程
        self.worker_thread = ValidateWorker(
            progress_queue=self.progress_queue,
            controller=self,
            file_path=file_path
        )
        self.worker_thread.start()

        self.processing = True
        return True

    def process_file_async(self, file_path: str, fix_errors: bool = False) -> bool:
        """异步处理文件

        Args:
            file_path: 文件路径
            fix_errors: 是否修复错误

        Returns:
            是否成功启动处理
        """
        if self.processing:
            logger.warning("已有任务在处理中")
            return False

        self.current_file = file_path
        self.cancel_flag.clear()

        # 创建工作线程
        self.worker_thread = ProcessWorker(
            progress_queue=self.progress_queue,
            controller=self,
            file_path=file_path,
            fix_errors=fix_errors
        )
        self.worker_thread.start()

        self.processing = True
        return True

    def cancel_processing(self):
        """取消当前处理"""
        if self.worker_thread and self.worker_thread.is_alive():
            self.cancel_flag.set()
            logger.info("已请求取消处理")

    def get_error_groups(self) -> Dict[str, List]:
        """获取按类型分组的错误

        Returns:
            按错误类型分组的错误字典
        """
        if not self.rule_engine:
            return {}

        errors = self.rule_engine.get_all_errors()
        groups: Dict[str, List] = {
            'title': [],
            'url': [],
            'image': [],
            'structure': []
        }

        for error in errors:
            error_type = error.line_type
            if error_type not in groups:
                error_type = 'structure'
            groups[error_type].append(error)

        return groups

    def get_all_errors(self) -> List:
        """获取所有错误

        Returns:
            错误列表
        """
        if not self.rule_engine:
            return []
        return self.rule_engine.get_all_errors()


class ValidateWorker(WorkerThread):
    """校验工作线程"""

    def __init__(self, progress_queue: queue.Queue, controller: MainController, file_path: str):
        """初始化校验工作线程

        Args:
            progress_queue: 进度队列
            controller: 主控制器
            file_path: 文件路径
        """
        super().__init__(progress_queue)
        self.controller = controller
        self.file_path = file_path

    def execute(self) -> ProcessingResult:
        """执行校验

        Returns:
            处理结果
        """
        self.emit_log("INFO", f"开始校验文档: {self.file_path}")

        # 创建回调
        callback = ProcessCallback(self.progress_queue, self._cancel_flag)

        # 执行校验
        result = self.controller.processor.validate_only(
            self.file_path,
            skip_corrupted=self.controller.theme_manager.get_skip_corrupted()
        )

        self.emit_log("INFO", f"校验完成，发现 {result.errors_count} 个问题")

        # 保存结果
        self.controller.last_result = result
        self.controller.processing = False

        return result


class ProcessWorker(WorkerThread):
    """处理工作线程"""

    def __init__(self, progress_queue: queue.Queue, controller: MainController,
                 file_path: str, fix_errors: bool = False):
        """初始化处理工作线程

        Args:
            progress_queue: 进度队列
            controller: 主控制器
            file_path: 文件路径
            fix_errors: 是否修复错误
        """
        super().__init__(progress_queue)
        self.controller = controller
        self.file_path = file_path
        self.fix_errors = fix_errors

    def execute(self) -> ProcessingResult:
        """执行处理

        Returns:
            处理结果
        """
        action = "修复" if self.fix_errors else "校验"
        self.emit_log("INFO", f"开始{action}文档: {self.file_path}")

        # 生成输出文件名
        if self.fix_errors:
            from pathlib import Path
            path_obj = Path(self.file_path)
            output_path = str(path_obj.parent / f"{path_obj.stem}_fixed{path_obj.suffix}")
            self.emit_log("INFO", f"输出文件: {output_path}")
        else:
            output_path = None

        # 执行处理
        result = self.controller.processor.process(
            self.file_path,
            output_path=output_path,
            fix_errors=self.fix_errors,
            skip_corrupted=self.controller.theme_manager.get_skip_corrupted()
        )

        self.emit_log("INFO", f"{action}完成，发现 {result.errors_count} 个问题")

        # 保存结果
        self.controller.last_result = result
        self.controller.processing = False

        return result
