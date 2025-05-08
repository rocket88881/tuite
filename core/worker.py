from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot
from PyQt5.QtWidgets import QMessageBox
import traceback
import logging
from typing import Callable, Any, Optional, Dict

logger = logging.getLogger("Worker")

class WorkerSignals(QObject):
    """定义工作线程的信号"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(int, str)  # (进度百分比, 状态消息)

class Worker(QRunnable):
    """通用工作线程，用于执行耗时操作而不阻塞UI"""
    
    def __init__(self, fn: Callable, *args, **kwargs):
        """初始化工作线程
        
        Args:
            fn: 要执行的函数
            *args: 函数位置参数
            **kwargs: 函数关键字参数
        """
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
        # 添加进度回调到kwargs
        if 'progress_callback' not in kwargs:
            self.kwargs['progress_callback'] = self.signals.progress
    
    @pyqtSlot()
    def run(self):
        """执行工作线程"""
        try:
            logger.debug(f"开始执行工作线程: {self.fn.__name__}")
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
            logger.debug(f"工作线程完成: {self.fn.__name__}")
        except Exception as e:
            traceback_str = traceback.format_exc()
            error_msg = f"{str(e)}\n\n{traceback_str}"
            logger.error(f"工作线程错误: {error_msg}")
            self.signals.error.emit(error_msg)
        finally:
            self.signals.finished.emit()

class BatchWorker(Worker):
    """批量处理工作线程，带有进度报告"""
    
    def __init__(self, items: list, process_func: Callable, *args, **kwargs):
        """初始化批量工作线程
        
        Args:
            items: 要处理的项列表
            process_func: 处理单个项的函数
            *args: 传递给process_func的位置参数
            **kwargs: 传递给process_func的关键字参数
        """
        super().__init__(self._batch_process, items, process_func, *args, **kwargs)
        self.items = items
        self.process_func = process_func
    
    def _batch_process(self, items: list, process_func: Callable, 
                      progress_callback: Callable, *args, **kwargs):
        """批量处理项"""
        results = []
        total = len(items)
        
        for i, item in enumerate(items, 1):
            try:
                result = process_func(item, *args, **kwargs)
                results.append(result)
                progress = int((i / total) * 100)
                progress_callback.emit(progress, f"处理中 {i}/{total}")
            except Exception as e:
                logger.error(f"处理项失败: {str(e)}")
                progress_callback.emit(
                    int((i / total) * 100), 
                    f"处理失败 {i}/{total}: {str(e)}"
                )
                continue
        
        return results