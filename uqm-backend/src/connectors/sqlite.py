"""
SQLite数据库连接器
实现SQLite数据库的连接和查询功能
"""

import sqlite3
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from src.connectors.base import BaseConnector
from src.utils.exceptions import ConnectionError


class SQLiteConnector(BaseConnector):
    """SQLite连接器实现"""
    
    def __init__(self, connection_url: str):
        """
        初始化SQLite连接器
        
        Args:
            connection_url: SQLite连接URL (如: sqlite:///path/to/db.sqlite)
        """
        # 解析连接URL
        parsed_url = urlparse(connection_url)
        database_path = parsed_url.path
        
        # 处理相对路径
        if database_path.startswith('/'):
            database_path = database_path[1:]  # 移除开头的 /
        
        connection_config = {
            "database_path": database_path,
            "connection_url": connection_url
        }
        
        super().__init__(connection_config)
        self.connection: Optional[sqlite3.Connection] = None
    
    async def connect(self) -> None:
        """建立SQLite连接"""
        try:
            database_path = self.connection_config["database_path"]
            self.log_info("正在连接SQLite数据库", path=database_path)
            
            # 确保数据库目录存在
            db_file = Path(database_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建SQLite连接
            self.connection = sqlite3.connect(
                database_path,
                check_same_thread=False,
                timeout=30.0
            )
            
            # 设置行工厂，返回字典格式
            self.connection.row_factory = sqlite3.Row
            
            # 启用外键约束
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            # 设置WAL模式以提高并发性能
            self.connection.execute("PRAGMA journal_mode = WAL")
            
            # 测试连接
            cursor = self.connection.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()
            self.log_info("SQLite连接成功", version=version[0])
            
            self.is_connected = True
            
        except Exception as e:
            self.log_error("SQLite连接失败", error=str(e))
            self._handle_connection_error(e)
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        执行SQLite查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果
        """
        if not self.is_connected or not self.connection:
            await self.connect()
        
        try:
            self.log_debug("执行SQLite查询", query=query[:200])
            
            cursor = self.connection.cursor()
            
            # 执行查询
            if params:
                # 处理参数格式
                if isinstance(params, dict):
                    # 命名参数
                    cursor.execute(query, params)
                else:
                    # 位置参数
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
                # 没有结果集的查询
                result = []
            
            # 提交事务
            self.connection.commit()
            
            self.log_debug(
                "SQLite查询执行完成",
                row_count=len(result)
            )
            
            return result
            
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            
            self.log_error("SQLite查询执行失败", error=str(e), query=query[:200])
            self._handle_sqlite_error(e)
            raise ConnectionError(f"查询执行失败: {e}")
    
    async def close(self) -> None:
        """关闭SQLite连接"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
            
            self.is_connected = False
            self.log_info("SQLite连接已关闭")
            
        except Exception as e:
            self.log_error("关闭SQLite连接失败", error=str(e))
    
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        获取SQLite表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            表结构信息
        """
        try:
            query = f"PRAGMA table_info({table_name})"
            result = await self.execute_query(query)
            
            columns = []
            for row in result:
                columns.append({
                    "name": row["name"],
                    "type": row["type"],
                    "nullable": row["notnull"] == 0,
                    "default": row["dflt_value"],
                    "primary_key": row["pk"] == 1
                })
            
            return {
                "table_name": table_name,
                "columns": columns
            }
            
        except Exception as e:
            self.log_error(f"获取SQLite表 {table_name} 结构失败", error=str(e))
            raise ConnectionError(f"获取表结构失败: {e}")
    
    async def get_available_tables(self) -> List[str]:
        """
        获取SQLite可用表列表
        
        Returns:
            表名列表
        """
        try:
            query = """
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
            
            result = await self.execute_query(query)
            tables = [row["name"] for row in result]
            
            self.log_info(f"获取到 {len(tables)} 个SQLite表")
            return tables
            
        except Exception as e:
            self.log_error("获取SQLite表列表失败", error=str(e))
            raise ConnectionError(f"获取表列表失败: {e}")
    
    async def get_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """
        获取表的索引信息
        
        Args:
            table_name: 表名
            
        Returns:
            索引信息列表
        """
        try:
            query = f"PRAGMA index_list({table_name})"
            result = await self.execute_query(query)
            
            indexes = []
            for row in result:
                # 获取索引详细信息
                index_name = row["name"]
                index_query = f"PRAGMA index_info({index_name})"
                index_info = await self.execute_query(index_query)
                
                columns = [info["name"] for info in index_info]
                
                indexes.append({
                    "name": index_name,
                    "unique": row["unique"] == 1,
                    "columns": columns
                })
            
            return indexes
            
        except Exception as e:
            self.log_error(f"获取SQLite表 {table_name} 索引失败", error=str(e))
            return []
    
    def _optimize_query_for_sqlite(self, query: str) -> str:
        """
        为SQLite优化查询
        
        Args:
            query: 原始查询
            
        Returns:
            优化后的查询
        """
        # SQLite特定的查询优化
        # 比如：
        # - 使用INDEXED BY提示
        # - 优化复杂的JOIN查询
        # - 使用SQLite特定的函数
        
        return query
    
    def _handle_sqlite_error(self, error: Exception) -> None:
        """
        处理SQLite特定错误
        
        Args:
            error: 错误信息
        """
        error_msg = str(error)
        
        # 数据库锁定
        if "database is locked" in error_msg.lower():
            self.log_error("SQLite数据库被锁定")
        
        # 语法错误
        elif "syntax error" in error_msg.lower():
            self.log_error("SQLite SQL语法错误", error=error_msg)
        
        # 表不存在
        elif "no such table" in error_msg.lower():
            self.log_error("SQLite表不存在", error=error_msg)
        
        # 磁盘空间不足
        elif "disk" in error_msg.lower():
            self.log_error("SQLite磁盘空间不足", error=error_msg)
        
        # 其他错误
        else:
            self.log_error("SQLite未知错误", error=error_msg)
    
    async def vacuum(self) -> None:
        """
        执行VACUUM操作以优化数据库
        """
        try:
            self.log_info("开始执行SQLite VACUUM操作")
            await self.execute_query("VACUUM")
            self.log_info("SQLite VACUUM操作完成")
            
        except Exception as e:
            self.log_error("SQLite VACUUM操作失败", error=str(e))
    
    async def analyze(self) -> None:
        """
        执行ANALYZE操作以更新统计信息
        """
        try:
            self.log_info("开始执行SQLite ANALYZE操作")
            await self.execute_query("ANALYZE")
            self.log_info("SQLite ANALYZE操作完成")
            
        except Exception as e:
            self.log_error("SQLite ANALYZE操作失败", error=str(e))
