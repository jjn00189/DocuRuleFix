"""线程辅助工具

提供线程安全的通信机制和工作线程管理。
"""

import queue
import threading
from typing import Callable, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass


class ProgressEventType(Enum):
    """进度事件类型"""
    PROGRESS = "progress"    # 进度更新
    LOG = "log"             # 日志消息
    COMPLETE = "complete"   # 处理完成
    ERROR = "error"         # 错误发生


@dataclass
class ProgressEvent:
    """进度事件数据类"""
    event_type: ProgressEventType
    data: Tuple[Any, ...]


class WorkerThread(threading.Thread):
    """工作线程基类

    在后台线程中执行任务，通过队列报告进度。
    """

    def __init__(self, progress_queue: queue.Queue, **kwargs):
        """初始化工作线程

        Args:
            progress_queue: 进度消息队列
            **kwargs: 其他参数
        """
        super().__init__(**kwargs, daemon=True)
        self.progress_queue = progress_queue
        self._cancel_flag = threading.Event()
        self._result: Optional[Any] = None
        self._error: Optional[Exception] = None

    def cancel(self):
        """请求取消任务"""
        self._cancel_flag.set()

    def is_cancelled(self) -> bool:
        """检查是否被取消"""
        return self._cancel_flag.is_set()

    def check_cancelled(self):
        """检查是否被取消，如果是则抛出异常"""
        if self._cancel_flag.is_set():
            raise InterruptedException("任务已被取消")

    @property
    def result(self) -> Any:
        """获取任务结果"""
        return self._result

    @property
    def error(self) -> Optional[Exception]:
        """获取任务错误"""
        return self._error

    def run(self):
        """运行任务（子类实现）"""
        try:
            self._result = self.execute()
            self.progress_queue.put((
                ProgressEventType.COMPLETE,
                self._result
            ))
        except InterruptedException:
            self.progress_queue.put((
                ProgressEventType.ERROR,
                "任务已被取消"
            ))
        except Exception as e:
            self._error = e
            self.progress_queue.put((
                ProgressEventType.ERROR,
                str(e)
            ))

    def execute(self) -> Any:
        """执行任务（子类实现）"""
        raise NotImplementedError

    def emit_progress(self, current: int, total: int, message: str = ""):
        """发送进度更新

        Args:
            current: 当前进度
            total: 总数
            message: 进度消息
        """
        self.check_cancelled()
        self.progress_queue.put((
            ProgressEventType.PROGRESS,
            current, total, message
        ))

    def emit_log(self, level: str, message: str):
        """发送日志消息

        Args:
            level: 日志级别 (INFO, WARNING, ERROR)
            message: 日志消息
        """
        self.check_cancelled()
        self.progress_queue.put((
            ProgressEventType.LOG,
            level, message
        ))


class InterruptedException(Exception):
    """任务被中断异常"""
    pass


class ProgressQueue(queue.Queue):
    """线程安全的进度队列

    继承自 queue.Queue，提供更方便的接口。
    """

    def put_progress(self, current: int, total: int, message: str = ""):
        """放入进度更新

        Args:
            current: 当前进度
            total: 总数
            message: 进度消息
        """
        self.put((ProgressEventType.PROGRESS, current, total, message))

    def put_log(self, level: str, message: str):
        """放入日志消息

        Args:
            level: 日志级别
            message: 日志消息
        """
        self.put((ProgressEventType.LOG, level, message))

    def put_complete(self, result: Any = None):
        """放入完成事件

        Args:
            result: 结果数据
        """
        self.put((ProgressEventType.COMPLETE, result))

    def put_error(self, error: str):
        """放入错误事件

        Args:
            error: 错误消息
        """
        self.put((ProgressEventType.ERROR, error))

    def get_event(self, timeout: Optional[float] = None) -> Optional[ProgressEvent]:
        """获取事件（非阻塞）

        Args:
            timeout: 超时时间（秒）

        Returns:
            ProgressEvent 或 None
        """
        try:
            event_type, *data = self.get_nowait()
            return ProgressEvent(event_type, tuple(data))
        except queue.Empty:
            return None


class ProcessCallback:
    """处理回调函数

    用于在 RuleEngine 中设置进度回调。
    """

    def __init__(self, progress_queue: queue.Queue, cancel_flag: threading.Event):
        """初始化处理回调

        Args:
            progress_queue: 进度消息队列
            cancel_flag: 取消标志
        """
        self.progress_queue = progress_queue
        self.cancel_flag = cancel_flag

    def __call__(self, current: int, total: int, message: str = ""):
        """作为回调函数被调用

        Args:
            current: 当前进度
            total: 总数
            message: 进度消息
        """
        if self.cancel_flag.is_set():
            raise InterruptedException("处理已被取消")

        self.progress_queue.put_progress(current, total, message)
