"""
PostgreSQL数据库连接器
实现PostgreSQL数据库的连接和查询功能
"""

import asyncio
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool

from src.connectors.base import BaseConnector
from src.utils.exceptions import ConnectionError


class PostgresConnector(BaseConnector):
    """PostgreSQL连接器实现"""
    
    def __init__(self, connection_url: str):
        """
        初始化PostgreSQL连接器
        
        Args:
            connection_url: PostgreSQL连接URL
        """
        # 解析连接URL
        parsed_url = urlparse(connection_url)
        
        connection_config = {
            "host": parsed_url.hostname,
            "port": parsed_url.port or 5432,
            "database": parsed_url.path.lstrip('/'),
            "user": parsed_url.username,
            "password": parsed_url.password,
            "connection_url": connection_url
        }
        
        super().__init__(connection_config)
        self.connection_pool: Optional[SimpleConnectionPool] = None
    
    async def connect(self) -> None:
        """建立PostgreSQL连接"""
        try:
            self.log_info("正在连接PostgreSQL数据库", host=self.connection_config["host"])
            
            # 创建连接池
            self.connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=self.connection_config["host"],
                port=self.connection_config["port"],
                database=self.connection_config["database"],
                user=self.connection_config["user"],
                password=self.connection_config["password"],
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            
            # 测试连接
            conn = self.connection_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()
                self.log_info("PostgreSQL连接成功", version=version["version"])
            finally:
                self.connection_pool.putconn(conn)
            
            self.is_connected = True
            
        except Exception as e:
            self.log_error("PostgreSQL连接失败", error=str(e))
            self._handle_connection_error(e)
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        执行PostgreSQL查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果
        """
        if not self.is_connected or not self.connection_pool:
            await self.connect()
        
        conn = None
        try:
            self.log_debug("执行PostgreSQL查询", query=query[:200])
            
            # 从连接池获取连接
            conn = self.connection_pool.getconn()
            
            with conn.cursor() as cursor:
                # 执行查询
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # 获取结果
                if cursor.description:
                    # 有结果集的查询
                    rows = cursor.fetchall()
                    # 转换为字典列表
                    result = [dict(row) for row in rows]
                else:
                    # 没有结果集的查询（如INSERT, UPDATE, DELETE）
                    result = []
                
            # 提交事务
            conn.commit()
            
            self.log_debug(
                "PostgreSQL查询执行完成",
                row_count=len(result)
            )
            
            return result
            
        except Exception as e:
            if conn:
                conn.rollback()
            
            self.log_error("PostgreSQL查询执行失败", error=str(e), query=query[:200])
            raise ConnectionError(f"查询执行失败: {e}")
            
        finally:
            if conn and self.connection_pool:
                self.connection_pool.putconn(conn)
    
    async def close(self) -> None:
        """关闭PostgreSQL连接"""
        try:
            if self.connection_pool:
                self.connection_pool.closeall()
                self.connection_pool = None
            
            self.is_connected = False
            self.log_info("PostgreSQL连接已关闭")
            
        except Exception as e:
            self.log_error("关闭PostgreSQL连接失败", error=str(e))
    
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        获取PostgreSQL表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            表结构信息
        """
        try:
            query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
            """
            
            result = await self.execute_query(query, {"table_name": table_name})
            
            columns = []
            for row in result:
                columns.append({
                    "name": row["column_name"],
                    "type": row["data_type"],
                    "nullable": row["is_nullable"] == "YES",
                    "default": row["column_default"]
                })
            
            return {
                "table_name": table_name,
                "columns": columns
            }
            
        except Exception as e:
            self.log_error(f"获取PostgreSQL表 {table_name} 结构失败", error=str(e))
            raise ConnectionError(f"获取表结构失败: {e}")
    
    async def get_available_tables(self) -> List[str]:
        """
        获取PostgreSQL可用表列表
        
        Returns:
            表名列表
        """
        try:
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
            
            result = await self.execute_query(query)
            tables = [row["table_name"] for row in result]
            
            self.log_info(f"获取到 {len(tables)} 个PostgreSQL表")
            return tables
            
        except Exception as e:
            self.log_error("获取PostgreSQL表列表失败", error=str(e))
            raise ConnectionError(f"获取表列表失败: {e}")
    
    def _optimize_query_for_postgres(self, query: str) -> str:
        """
        为PostgreSQL优化查询
        
        Args:
            query: 原始查询
            
        Returns:
            优化后的查询
        """
        # 这里可以添加PostgreSQL特定的查询优化逻辑
        # 比如：
        # - 使用EXPLAIN分析查询计划
        # - 添加合适的索引提示
        # - 优化JOIN顺序
        
        return query
    
    def _handle_postgres_error(self, error: Exception) -> None:
        """
        处理PostgreSQL特定错误
        
        Args:
            error: 错误信息
        """
        error_msg = str(error)
        
        # 连接错误
        if "connection" in error_msg.lower():
            self.is_connected = False
            self.log_error("PostgreSQL连接断开")
        
        # 语法错误
        elif "syntax error" in error_msg.lower():
            self.log_error("PostgreSQL SQL语法错误", error=error_msg)
        
        # 权限错误
        elif "permission denied" in error_msg.lower():
            self.log_error("PostgreSQL权限不足", error=error_msg)
        
        # 其他错误
        else:
            self.log_error("PostgreSQL未知错误", error=error_msg)
    
    def _create_connection_string(self) -> str:
        """
        创建PostgreSQL连接字符串
        
        Returns:
            连接字符串
        """
        config = self.connection_config
        return (
            f"host={config['host']} "
            f"port={config['port']} "
            f"dbname={config['database']} "
            f"user={config['user']} "
            f"password={config['password']}"
        )
