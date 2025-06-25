"""
异常处理模块
定义自定义异常类和异常处理器
"""

from typing import Any, Dict
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.utils.logging import get_logger

logger = get_logger(__name__)


class UQMBaseException(Exception):
    """UQM基础异常类"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(UQMBaseException):
    """数据验证异常"""
    pass


class ExecutionError(UQMBaseException):
    """执行异常"""
    pass


class ConnectionError(UQMBaseException):
    """连接异常"""
    pass


class CacheError(UQMBaseException):
    """缓存异常"""
    pass


class ParseError(UQMBaseException):
    """解析异常"""
    pass


class TimeoutError(UQMBaseException):
    """超时异常"""
    pass


def setup_exception_handlers(app: FastAPI) -> None:
    """设置全局异常处理器"""
    
    @app.exception_handler(UQMBaseException)
    async def uqm_exception_handler(request: Request, exc: UQMBaseException) -> JSONResponse:
        """UQM自定义异常处理器"""
        logger.error(
            "UQM异常",
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            path=request.url.path,
            method=request.method
        )
        
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """请求验证异常处理器"""
        logger.error(
            "请求验证异常",
            errors=exc.errors(),
            path=request.url.path,
            method=request.method
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "请求数据验证失败",
                    "details": exc.errors()
                }
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """HTTP异常处理器"""
        logger.error(
            "HTTP异常",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
            method=request.method
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "details": {}
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """通用异常处理器"""
        logger.error(
            "未处理异常",
            exception_type=type(exc).__name__,
            exception_message=str(exc),
            path=request.url.path,
            method=request.method,
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "服务器内部错误",
                    "details": {}
                }
            }
        )
