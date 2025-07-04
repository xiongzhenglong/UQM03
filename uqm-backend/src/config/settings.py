"""
应用程序配置管理模块
负责加载和管理所有配置项
"""

import os
from typing import List, Optional
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用程序配置类"""
    
    # 基础配置
    DEBUG: bool = Field(default=False, description="调试模式开关")
    HOST: str = Field(default="0.0.0.0", description="服务器主机地址")
    PORT: int = Field(default=8000, description="服务器端口")
    SECRET_KEY: str = Field(default="change-me-in-production", description="应用程序密钥")
    
    # 数据库配置
    DATABASE_URL: Optional[str] = Field(default=None, description="主数据库连接URL")
    MYSQL_URL: Optional[str] = Field(default=None, description="MySQL数据库连接URL")
    SQLITE_URL: Optional[str] = Field(default="sqlite:///./uqm.db", description="SQLite数据库连接URL")
    
    # Redis配置
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis连接URL")
    
    # 缓存配置
    CACHE_TYPE: str = Field(default="memory", description="缓存类型")
    CACHE_DEFAULT_TIMEOUT: int = Field(default=3600, description="默认缓存超时时间(秒)")
    CACHE_MAX_SIZE: int = Field(default=1000, description="内存缓存最大条目数")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FORMAT: str = Field(default="json", description="日志格式")
    
    # 查询配置
    MAX_QUERY_TIMEOUT: int = Field(default=300, description="最大查询超时时间(秒)")
    MAX_CONCURRENT_QUERIES: int = Field(default=10, description="最大并发查询数")
    QUERY_RESULT_LIMIT: int = Field(default=10000, description="查询结果行数限制")
    
    # 安全配置
    ALLOWED_HOSTS: List[str] = Field(default=["localhost", "127.0.0.1"], description="允许的主机列表")
    CORS_ORIGINS: List[str] = Field(default=[], description="CORS允许的源")
    CORS_CREDENTIALS: bool = Field(default=True, description="CORS是否允许凭证")
    CORS_METHODS: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], description="CORS允许的HTTP方法")
    CORS_HEADERS: List[str] = Field(default=["*"], description="CORS允许的请求头")
    
    # 监控配置
    ENABLE_METRICS: bool = Field(default=True, description="是否启用指标监控")
    METRICS_PATH: str = Field(default="/metrics", description="指标接口路径")
    
    # 新增：全局默认数据库类型
    DEFAULT_DB_TYPE: str = Field(default="postgresql", description="全局默认数据库类型，可选：postgresql、mysql、sqlite")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    def get_database_config(self) -> dict:
        """获取数据库配置信息"""
        return {
            "postgresql": self.DATABASE_URL,
            "mysql": self.MYSQL_URL,
            "sqlite": self.SQLITE_URL,
        }
    
    def get_cache_config(self) -> dict:
        """获取缓存配置信息"""
        return {
            "type": self.CACHE_TYPE,
            "redis_url": self.REDIS_URL,
            "default_timeout": self.CACHE_DEFAULT_TIMEOUT,
            "max_size": self.CACHE_MAX_SIZE,
        }
    
    def get_logging_config(self) -> dict:
        """获取日志配置信息"""
        return {
            "level": self.LOG_LEVEL,
            "format": self.LOG_FORMAT,
        }
    
    def validate_config(self) -> bool:
        """验证配置有效性"""
        try:
            # 验证必需的配置项
            if not self.SECRET_KEY or self.SECRET_KEY == "change-me-in-production":
                if not self.DEBUG:
                    raise ValueError("生产环境必须设置有效的SECRET_KEY")
            
            # 验证数据库配置
            if not any([self.DATABASE_URL, self.MYSQL_URL, self.SQLITE_URL]):
                raise ValueError("至少需要配置一个数据库连接")
            
            # 验证端口范围
            if not (1 <= self.PORT <= 65535):
                raise ValueError("端口号必须在1-65535范围内")
            
            # 验证超时配置
            if self.MAX_QUERY_TIMEOUT <= 0:
                raise ValueError("查询超时时间必须大于0")
            
            # 验证并发配置
            if self.MAX_CONCURRENT_QUERIES <= 0:
                raise ValueError("最大并发查询数必须大于0")
            
            return True
            
        except ValueError as e:
            print(f"配置验证失败: {e}")
            return False


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例(单例模式)"""
    settings = Settings()
    
    # 验证配置
    if not settings.validate_config():
        raise RuntimeError("配置验证失败，请检查配置文件")
    
    return settings
