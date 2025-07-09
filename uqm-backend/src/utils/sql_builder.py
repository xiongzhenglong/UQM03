"""
SQL查询构建工具
提供构建各种SQL查询的功能
"""

from typing import Any, Dict, List, Optional, Union
from enum import Enum

from src.utils.logging import LoggerMixin
from src.utils.exceptions import ValidationError


class SQLDialect(Enum):
    """SQL方言枚举"""
    STANDARD = "standard"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class SQLBuilder(LoggerMixin):
    """SQL查询构建器"""
    
    def __init__(self, dialect: SQLDialect = SQLDialect.STANDARD):
        """
        初始化SQL构建器
        
        Args:
            dialect: SQL方言
        """
        self.dialect = dialect
    
    def build_select_query(self, 
                          select_fields: List[str],
                          from_table: str,
                          joins: Optional[List[Dict[str, Any]]] = None,
                          where_conditions: Optional[List[Dict[str, Any]]] = None,
                          group_by: Optional[List[str]] = None,
                          having: Optional[List[Dict[str, Any]]] = None,
                          order_by: Optional[List[Union[str, Dict[str, Any]]]] = None,
                          limit: Optional[int] = None,
                          offset: Optional[int] = None) -> str:
        """
        构建SELECT查询
        
        Args:
            select_fields: 选择字段列表
            from_table: 源表名
            joins: JOIN条件列表
            where_conditions: WHERE条件列表
            group_by: GROUP BY字段列表
            having: HAVING条件列表
            order_by: ORDER BY字段列表
            limit: 限制行数
            offset: 偏移量
            
        Returns:
            SQL查询语句
        """
        try:
            query_parts = []
            
            # SELECT子句
            select_clause = self._build_select_clause(select_fields)
            query_parts.append(select_clause)
            
            # FROM子句
            from_clause = self._build_from_clause(from_table)
            query_parts.append(from_clause)
            
            # JOIN子句
            if joins:
                join_clause = self._build_join_clause(joins)
                if join_clause:
                    query_parts.append(join_clause)
            
            # WHERE子句
            if where_conditions:
                where_clause = self._build_where_clause(where_conditions)
                if where_clause:
                    query_parts.append(where_clause)
            
            # GROUP BY子句
            if group_by:
                group_by_clause = self._build_group_by_clause(group_by)
                query_parts.append(group_by_clause)
            
            # HAVING子句
            if having:
                having_clause = self._build_having_clause(having)
                if having_clause:
                    query_parts.append(having_clause)
            
            # ORDER BY子句
            if order_by:
                order_by_clause = self._build_order_by_clause(order_by)
                if order_by_clause:
                    query_parts.append(order_by_clause)
            
            # LIMIT子句
            if limit is not None:
                limit_clause = self._build_limit_clause(limit, offset)
                if limit_clause:
                    query_parts.append(limit_clause)
            
            # 组合查询
            query = "\n".join(query_parts)
            
            return query
            
        except Exception as e:
            self.log_error("构建SELECT查询失败", error=str(e))
            raise ValidationError(f"构建SELECT查询失败: {e}")
    
    def _build_select_clause(self, select_fields: List[str]) -> str:
        """构建SELECT子句"""
        if not select_fields:
            return "SELECT *"
        
        return f"SELECT {', '.join(select_fields)}"
    
    def _build_from_clause(self, from_table: str) -> str:
        """构建FROM子句"""
        return f"FROM {from_table}"
    
    def _build_join_clause(self, joins: List[Dict[str, Any]]) -> str:
        """构建JOIN子句"""
        join_parts = []
        
        for join in joins:
            join_type = join.get("type", "INNER").upper()
            # 支持 target 字段（UQM 使用）和传统的 "table" 字段（兼容性）
            table = join.get("target") or join.get("table")
            condition = join.get("on")
            
            if not table or not condition:
                continue
            
            # 构建连接条件
            join_condition = self._build_join_condition(condition)
            join_part = f"{join_type} JOIN {table} ON {join_condition}"
            join_parts.append(join_part)
        
        return "\n".join(join_parts)
    
    def _build_where_clause(self, where_conditions: List[Dict[str, Any]]) -> str:
        """构建WHERE子句"""
        if not where_conditions:
            return ""
        
        conditions = []
        for condition in where_conditions:
            condition_str = self._build_condition(condition)
            if condition_str:
                conditions.append(condition_str)
        
        if not conditions:
            return ""
        
        # 如果只有一个条件，直接使用
        if len(conditions) == 1:
            return f"WHERE {conditions[0]}"
        
        # 多个条件用AND连接
        return f"WHERE ({') AND ('.join(conditions)})"
    
    def _build_group_by_clause(self, group_by: List[str]) -> str:
        """构建GROUP BY子句"""
        if not group_by:
            return ""
        
        return f"GROUP BY {', '.join(group_by)}"
    
    def _build_having_clause(self, having: List[Dict[str, Any]]) -> str:
        """构建HAVING子句"""
        if not having:
            return ""
        
        conditions = []
        for condition in having:
            condition_str = self._build_condition(condition)
            if condition_str:
                conditions.append(condition_str)
        
        if not conditions:
            return ""
        
        return f"HAVING {' AND '.join(conditions)}"
    
    def _build_order_by_clause(self, order_by: List[Union[str, Dict[str, Any]]]) -> str:
        """构建ORDER BY子句"""
        if not order_by:
            return ""
        
        order_parts = []
        for order_item in order_by:
            if isinstance(order_item, str):
                order_parts.append(order_item)
            elif isinstance(order_item, dict):
                field = order_item.get("field")
                direction = order_item.get("direction", "ASC")
                if field:
                    order_parts.append(f"{field} {direction}")
        
        if not order_parts:
            return ""
        
        return f"ORDER BY {', '.join(order_parts)}"
    
    def _build_limit_clause(self, limit: int, offset: Optional[int] = None) -> str:
        """构建LIMIT子句"""
        if self.dialect == SQLDialect.MYSQL:
            if offset is not None:
                return f"LIMIT {offset}, {limit}"
            else:
                return f"LIMIT {limit}"
        
        elif self.dialect == SQLDialect.POSTGRESQL:
            if offset is not None:
                return f"LIMIT {limit} OFFSET {offset}"
            else:
                return f"LIMIT {limit}"
        
        elif self.dialect == SQLDialect.SQLITE:
            if offset is not None:
                return f"LIMIT {limit} OFFSET {offset}"
            else:
                return f"LIMIT {limit}"
        
        else:
            # 标准SQL
            if offset is not None:
                return f"LIMIT {limit} OFFSET {offset}"
            else:
                return f"LIMIT {limit}"
    
    def _build_join_condition(self, condition: Union[str, Dict[str, Any]]) -> str:
        """构建连接条件"""
        if isinstance(condition, str):
            return condition
        
        elif isinstance(condition, dict):
            left = condition.get("left")
            right = condition.get("right")
            operator = condition.get("operator", "=")
            
            if left and right:
                return f"{left} {operator} {right}"
        
        return ""
    
    def _build_condition(self, condition: Union[str, Dict[str, Any]]) -> str:
        """构建条件表达式（支持嵌套逻辑）"""
        if isinstance(condition, str):
            return condition
        
        elif isinstance(condition, dict):
            # 检查是否是嵌套逻辑结构
            if "logic" in condition and "conditions" in condition:
                return self._build_logical_condition(condition)
            
            # 处理简单条件
            field = condition.get("field")
            operator = condition.get("operator", "=")
            value = condition.get("value")
            
            if not field:
                return ""
            
            # 处理不同的操作符
            if operator.upper() == "IN":
                if isinstance(value, list):
                    value_str = ", ".join([self._format_value(v) for v in value])
                    return f"{field} IN ({value_str})"
                else:
                    return f"{field} IN ({self._format_value(value)})"
            
            elif operator.upper() == "NOT IN":
                if isinstance(value, list):
                    value_str = ", ".join([self._format_value(v) for v in value])
                    return f"{field} NOT IN ({value_str})"
                else:
                    return f"{field} NOT IN ({self._format_value(value)})"
            
            elif operator.upper() == "BETWEEN":
                if isinstance(value, dict) and "min" in value and "max" in value:
                    return f"{field} BETWEEN {self._format_value(value['min'])} AND {self._format_value(value['max'])}"
                elif isinstance(value, list) and len(value) == 2:
                    return f"{field} BETWEEN {self._format_value(value[0])} AND {self._format_value(value[1])}"
            
            elif operator.upper() == "LIKE":
                return f"{field} LIKE {self._format_value(value)}"
            
            elif operator.upper() == "IS NULL":
                return f"{field} IS NULL"
            
            elif operator.upper() == "IS NOT NULL":
                return f"{field} IS NOT NULL"
            
            else:
                return f"{field} {operator} {self._format_value(value)}"
        
        return ""
    
    def _build_logical_condition(self, logical_condition: Dict[str, Any]) -> str:
        """构建逻辑条件（AND/OR）"""
        logic = logical_condition.get("logic", "AND").upper()
        conditions = logical_condition.get("conditions", [])
        
        if not conditions:
            return ""
        
        condition_strings = []
        for condition in conditions:
            condition_str = self._build_condition(condition)
            if condition_str:
                condition_strings.append(condition_str)
        
        if not condition_strings:
            return ""
        
        if len(condition_strings) == 1:
            return condition_strings[0]
        
        # 用括号包围逻辑条件
        if logic == "AND":
            return f"({' AND '.join(condition_strings)})"
        elif logic == "OR":
            return f"({' OR '.join(condition_strings)})"
        else:
            # 不支持的逻辑操作符，默认使用AND
            return f"({' AND '.join(condition_strings)})"
    
    def _format_value(self, value: Any) -> str:
        """格式化值"""
        if value is None:
            return "NULL"
        elif isinstance(value, str):
            # 转义单引号
            escaped_value = value.replace("'", "''")
            return f"'{escaped_value}'"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return f"'{str(value)}'"
    
    def build_insert_query(self, table_name: str, data: Dict[str, Any]) -> str:
        """构建INSERT查询"""
        columns = list(data.keys())
        values = [self._format_value(data[col]) for col in columns]
        
        columns_str = ", ".join(columns)
        values_str = ", ".join(values)
        
        return f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"
    
    def build_update_query(self, table_name: str, 
                          updates: Dict[str, Any],
                          where_conditions: List[Dict[str, Any]]) -> str:
        """构建UPDATE查询"""
        set_parts = []
        for column, value in updates.items():
            set_parts.append(f"{column} = {self._format_value(value)}")
        
        set_clause = ", ".join(set_parts)
        where_clause = self._build_where_clause(where_conditions)
        
        query = f"UPDATE {table_name} SET {set_clause}"
        if where_clause:
            query += f" {where_clause}"
        
        return query
    
    def build_delete_query(self, table_name: str, 
                          where_conditions: List[Dict[str, Any]]) -> str:
        """构建DELETE查询"""
        where_clause = self._build_where_clause(where_conditions)
        
        query = f"DELETE FROM {table_name}"
        if where_clause:
            query += f" {where_clause}"
        
        return query
