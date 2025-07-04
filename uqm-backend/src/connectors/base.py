"""
数据连接器基类
定义所有连接器的通用接口和基础功能
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from functools import lru_cache

from src.utils.logging import LoggerMixin
from src.utils.exceptions import ConnectionError
from src.config.settings import get_settings


class BaseConnector(ABC, LoggerMixin):
    """数据连接器基类"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        """
        初始化连接器
        
        Args:
            connection_config: 连接配置
        """
        self.connection_config = connection_config
        self.connection = None
        self.is_connected = False
    
    @abstractmethod
    async def connect(self) -> None:
        """建立数据库连接"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        执行查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """关闭连接"""
        pass
    
    async def execute_batch(self, queries: List[str]) -> List[List[Dict[str, Any]]]:
        """
        批量执行查询
        
        Args:
            queries: 查询语句列表
            
        Returns:
            批量查询结果
        """
        results = []
        for query in queries:
            result = await self.execute_query(query)
            results.append(result)
        return results
    
    async def test_connection(self) -> bool:
        """
        测试连接有效性
        
        Returns:
            连接是否有效
        """
        try:
            if not self.is_connected:
                await self.connect()
            
            # 执行简单查询测试连接
            await self.execute_query("SELECT 1")
            return True
            
        except Exception as e:
            self.log_error("连接测试失败", error=str(e))
            return False
    
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        获取表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            表结构信息
        """
        # 默认实现，子类可以重写
        try:
            query = f"SELECT * FROM {table_name} LIMIT 0"
            await self.execute_query(query)
            return {"table_name": table_name, "columns": []}
        except Exception as e:
            self.log_error(f"获取表 {table_name} 结构失败", error=str(e))
            raise ConnectionError(f"获取表结构失败: {e}")
    
    async def get_available_tables(self) -> List[str]:
        """
        获取可用表列表
        
        Returns:
            表名列表
        """
        # 默认实现，子类可以重写
        return []
    
    def _handle_connection_error(self, error: Exception) -> None:
        """
        处理连接错误
        
        Args:
            error: 错误信息
        """
        self.log_error("数据库连接错误", error=str(error))
        self.is_connected = False
        raise ConnectionError(f"数据库连接失败: {error}")
    
    def _format_query_result(self, result: Any) -> List[Dict[str, Any]]:
        """
        格式化查询结果
        
        Args:
            result: 原始查询结果
            
        Returns:
            格式化后的结果
        """
        # 默认实现，子类可以重写
        if isinstance(result, list):
            return result
        return []


class BaseConnectorManager(LoggerMixin):
    """连接器管理器基类"""
    
    def __init__(self):
        """初始化连接器管理器"""
        self.connectors: Dict[str, BaseConnector] = {}
        self.settings = get_settings()
    
    def register_connector(self, name: str, connector: BaseConnector) -> None:
        """
        注册连接器
        
        Args:
            name: 连接器名称
            connector: 连接器实例
        """
        self.connectors[name] = connector
        self.log_info(f"连接器 {name} 注册成功")
    
    def get_connector(self, name: str) -> Optional[BaseConnector]:
        """
        获取连接器
        
        Args:
            name: 连接器名称
            
        Returns:
            连接器实例
        """
        return self.connectors.get(name)
    
    async def close_all(self) -> None:
        """关闭所有连接器"""
        for name, connector in self.connectors.items():
            try:
                await connector.close()
                self.log_info(f"连接器 {name} 已关闭")
            except Exception as e:
                self.log_error(f"关闭连接器 {name} 失败", error=str(e))


class DefaultConnectorManager(BaseConnectorManager):
    """默认连接器管理器实现"""
    
    def __init__(self):
        """初始化默认连接器管理器"""
        super().__init__()
        self._initialize_connectors()
    
    def _initialize_connectors(self) -> None:
        """初始化默认连接器"""
        try:
            # 导入具体的连接器实现
            from src.connectors.postgres import PostgresConnector
            from src.connectors.mysql import MySQLConnector
            from src.connectors.sqlite import SQLiteConnector
            
            # 获取数据库配置
            db_config = self.settings.get_database_config()
            
            # 注册PostgreSQL连接器
            if db_config.get("postgresql"):
                postgres_connector = PostgresConnector(db_config["postgresql"])
                self.register_connector("postgresql", postgres_connector)
            
            # 注册MySQL连接器
            if db_config.get("mysql"):
                mysql_connector = MySQLConnector(db_config["mysql"])
                self.register_connector("mysql", mysql_connector)
            
            # 注册SQLite连接器
            if db_config.get("sqlite"):
                sqlite_connector = SQLiteConnector(db_config["sqlite"])
                self.register_connector("sqlite", sqlite_connector)
            
            self.log_info("默认连接器初始化完成")
            
        except Exception as e:
            self.log_error("初始化默认连接器失败", error=str(e))
    
    async def get_default_connector(self) -> BaseConnector:
        """
        获取默认连接器
        
        Returns:
            默认连接器实例
        """
        # 优先使用配置指定的默认数据库类型
        default_type = self.settings.DEFAULT_DB_TYPE.lower()
        connector = self.get_connector(default_type)
        if connector:
            if await connector.test_connection():
                return connector
        # fallback到原有优先级
        for connector_name in ["postgresql", "mysql", "sqlite"]:
            if connector_name == default_type:
                continue
            connector = self.get_connector(connector_name)
            if connector:
                if await connector.test_connection():
                    return connector
        raise ConnectionError("没有可用的数据库连接器")


# 全局连接器管理器实例
_connector_manager: Optional[BaseConnectorManager] = None


@lru_cache()
def get_connector_manager() -> BaseConnectorManager:
    """获取连接器管理器实例(单例模式)"""
    global _connector_manager
    
    if _connector_manager is None:
        _connector_manager = DefaultConnectorManager()
    
    return _connector_manager
