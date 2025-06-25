"""
MySQL数据库连接器
实现MySQL数据库的连接和查询功能
"""

import asyncio
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import pymysql
from pymysql.connections import Connection

from src.connectors.base import BaseConnector
from src.utils.exceptions import ConnectionError


class MySQLConnector(BaseConnector):
    """MySQL连接器实现"""
    
    def __init__(self, connection_url: str):
        """
        初始化MySQL连接器
        
        Args:
            connection_url: MySQL连接URL
        """
        # 解析连接URL
        parsed_url = urlparse(connection_url)
        
        connection_config = {
            "host": parsed_url.hostname,
            "port": parsed_url.port or 3306,
            "database": parsed_url.path.lstrip('/'),
            "user": parsed_url.username,
            "password": parsed_url.password,
            "connection_url": connection_url
        }
        
        super().__init__(connection_config)
        self.connection: Optional[Connection] = None
    
    async def connect(self) -> None:
        """建立MySQL连接"""
        try:
            self.log_info("正在连接MySQL数据库", host=self.connection_config["host"])
            
            # 创建MySQL连接
            self.connection = pymysql.connect(
                host=self.connection_config["host"],
                port=self.connection_config["port"],
                user=self.connection_config["user"],
                password=self.connection_config["password"],
                database=self.connection_config["database"],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            
            # 测试连接
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                self.log_info("MySQL连接成功", version=version["VERSION()"])
            
            self.is_connected = True
            
        except Exception as e:
            self.log_error("MySQL连接失败", error=str(e))
            self._handle_connection_error(e)
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        执行MySQL查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果
        """
        if not self.is_connected or not self.connection:
            await self.connect()
        
        try:
            self.log_debug("执行MySQL查询", query=query[:200])
            
            with self.connection.cursor() as cursor:
                # 执行查询
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # 获取结果
                if cursor.description:
                    # 有结果集的查询
                    result = cursor.fetchall()
                    if not isinstance(result, list):
                        result = [result] if result else []
                else:
                    # 没有结果集的查询
                    result = []
            
            self.log_debug(
                "MySQL查询执行完成",
                row_count=len(result)
            )
            
            return result
            
        except Exception as e:
            self.log_error("MySQL查询执行失败", error=str(e), query=query[:200])
            self._handle_mysql_error(e)
            raise ConnectionError(f"查询执行失败: {e}")
    
    async def close(self) -> None:
        """关闭MySQL连接"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
            
            self.is_connected = False
            self.log_info("MySQL连接已关闭")
            
        except Exception as e:
            self.log_error("关闭MySQL连接失败", error=str(e))
    
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        获取MySQL表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            表结构信息
        """
        try:
            query = """
            SELECT 
                COLUMN_NAME as column_name,
                DATA_TYPE as data_type,
                IS_NULLABLE as is_nullable,
                COLUMN_DEFAULT as column_default,
                COLUMN_KEY as column_key,
                EXTRA as extra
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
            """
            
            result = await self.execute_query(query, [table_name])
            
            columns = []
            for row in result:
                columns.append({
                    "name": row["column_name"],
                    "type": row["data_type"],
                    "nullable": row["is_nullable"] == "YES",
                    "default": row["column_default"],
                    "key": row["column_key"],
                    "extra": row["extra"]
                })
            
            return {
                "table_name": table_name,
                "columns": columns
            }
            
        except Exception as e:
            self.log_error(f"获取MySQL表 {table_name} 结构失败", error=str(e))
            raise ConnectionError(f"获取表结构失败: {e}")
    
    async def get_available_tables(self) -> List[str]:
        """
        获取MySQL可用表列表
        
        Returns:
            表名列表
        """
        try:
            query = """
            SELECT TABLE_NAME as table_name
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
            """
            
            result = await self.execute_query(query)
            tables = [row["table_name"] for row in result]
            
            self.log_info(f"获取到 {len(tables)} 个MySQL表")
            return tables
            
        except Exception as e:
            self.log_error("获取MySQL表列表失败", error=str(e))
            raise ConnectionError(f"获取表列表失败: {e}")
    
    def _optimize_query_for_mysql(self, query: str) -> str:
        """
        为MySQL优化查询
        
        Args:
            query: 原始查询
            
        Returns:
            优化后的查询
        """
        # MySQL特定的查询优化
        # 比如：
        # - 使用FORCE INDEX提示
        # - 优化LIMIT和OFFSET
        # - 使用MySQL特定的函数
        
        return query
    
    def _handle_mysql_error(self, error: Exception) -> None:
        """
        处理MySQL特定错误
        
        Args:
            error: 错误信息
        """
        error_msg = str(error)
        
        # 连接错误
        if "lost connection" in error_msg.lower() or "gone away" in error_msg.lower():
            self.is_connected = False
            self.log_error("MySQL连接断开")
        
        # 语法错误
        elif "syntax" in error_msg.lower():
            self.log_error("MySQL SQL语法错误", error=error_msg)
        
        # 表不存在
        elif "doesn't exist" in error_msg.lower():
            self.log_error("MySQL表不存在", error=error_msg)
        
        # 权限错误
        elif "access denied" in error_msg.lower():
            self.log_error("MySQL权限不足", error=error_msg)
        
        # 其他错误
        else:
            self.log_error("MySQL未知错误", error=error_msg)
    
    def _create_connection_string(self) -> str:
        """
        创建MySQL连接字符串
        
        Returns:
            连接字符串
        """
        config = self.connection_config
        return (
            f"mysql://{config['user']}:{config['password']}"
            f"@{config['host']}:{config['port']}/{config['database']}"
        )
