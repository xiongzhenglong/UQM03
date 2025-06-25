"""
日志配置模块
负责设置结构化日志记录
"""

import sys
import structlog
from typing import Any, Dict


def setup_logging(log_level: str = "INFO") -> None:
    """
    设置结构化日志记录
    
    Args:
        log_level: 日志级别
    """
    # 配置structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    获取日志记录器实例
    
    Args:
        name: 日志记录器名称
        
    Returns:
        结构化日志记录器实例
    """
    return structlog.get_logger(name)


class LoggerMixin:
    """日志记录器混入类"""
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """获取类专用的日志记录器"""
        return get_logger(self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs: Any) -> None:
        """记录信息日志"""
        self.logger.info(message, **kwargs)
    
    def log_error(self, message: str, **kwargs: Any) -> None:
        """记录错误日志"""
        self.logger.error(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs: Any) -> None:
        """记录警告日志"""
        self.logger.warning(message, **kwargs)
    
    def log_debug(self, message: str, **kwargs: Any) -> None:
        """记录调试日志"""
        self.logger.debug(message, **kwargs)
