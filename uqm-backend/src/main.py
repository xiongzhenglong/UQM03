"""
UQM Backend 主程序入口
负责启动FastAPI应用程序和配置相关服务
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from src.api.routes import router
from src.config.settings import get_settings
from src.core.cache import get_cache_manager
from src.utils.logging import setup_logging
from src.utils.exceptions import setup_exception_handlers


# 应用程序生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用程序启动和关闭时的生命周期管理"""
    # 启动时初始化
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)
    
    # 初始化缓存管理器
    cache_manager = get_cache_manager()
    await cache_manager.initialize()
    
    print("UQM Backend 服务启动完成")
    
    yield
    
    # 关闭时清理资源
    await cache_manager.close()
    print("UQM Backend 服务已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用程序实例"""
    settings = get_settings()
    
    # 创建FastAPI应用实例
    app = FastAPI(
        title="UQM Backend API",
        description="统一查询模型(UQM)后端执行引擎",
        version="0.1.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # 配置CORS中间件
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=settings.CORS_CREDENTIALS,
            allow_methods=settings.CORS_METHODS,
            allow_headers=settings.CORS_HEADERS,
        )
    
    # 配置信任主机中间件
    if settings.ALLOWED_HOSTS:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )
    
    # 注册路由
    app.include_router(router, prefix="/api/v1")
    
    # 设置异常处理器
    setup_exception_handlers(app)
    
    return app


# 创建应用实例
app = create_app()


def main():
    """主函数 - 启动应用程序"""
    settings = get_settings()
    
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        workers=1 if settings.DEBUG else 4
    )


if __name__ == "__main__":
    main()
