import logging
from pathlib import Path
from datetime import datetime
import sys
from typing import Optional

def setup_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """设置并返回一个配置好的logger
    
    Args:
        name: logger名称
        log_dir: 日志目录
        
    Returns:
        配置好的Logger对象
    """
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 防止重复添加handler
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器 - 每天一个日志文件
    log_file = log_path / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_exceptions(logger: Optional[logging.Logger] = None):
    """装饰器，用于捕获和记录函数异常"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if logger:
                    logger.error(f"函数 {func.__name__} 执行出错: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator