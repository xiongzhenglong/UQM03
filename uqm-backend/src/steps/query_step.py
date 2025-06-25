"""
查询步骤实现
负责执行SQL查询并返回结果
"""

from typing import Any, Dict, List, Optional, Union

from src.steps.base import BaseStep
from src.utils.sql_builder import SQLBuilder
from src.utils.exceptions import ValidationError, ExecutionError


class QueryStep(BaseStep):
    """查询步骤执行器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化查询步骤
        
        Args:
            config: 查询步骤配置
        """
        super().__init__(config)
        self.sql_builder = SQLBuilder()
    
    def validate(self) -> None:
        """验证查询步骤配置"""
        required_fields = ["data_source"]
        self._validate_required_config(required_fields)
        
        # 验证数据源
        data_source = self.config.get("data_source")
        if not isinstance(data_source, str):
            raise ValidationError("data_source必须是字符串")
        
        # 验证维度字段
        dimensions = self.config.get("dimensions", [])
        if not isinstance(dimensions, list):
            raise ValidationError("dimensions必须是数组")
        
        # 验证指标字段
        metrics = self.config.get("metrics", [])
        if not isinstance(metrics, list):
            raise ValidationError("metrics必须是数组")
        
        # 至少需要有维度或指标
        if not dimensions and not metrics:
            raise ValidationError("至少需要指定dimensions或metrics")
    
    async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        执行查询步骤
        
        Args:
            context: 执行上下文
            
        Returns:
            查询结果
        """
        try:
            # 获取连接器管理器
            connector_manager = context["connector_manager"]
            
            # 构建SQL查询
            query = self.build_query()
            
            # 获取默认连接器（或根据配置选择特定连接器）
            connector = await connector_manager.get_default_connector()
            
            # 执行查询
            result = await connector.execute_query(query)
            
            return result
            
        except Exception as e:
            self.log_error("查询步骤执行失败", error=str(e))
            raise ExecutionError(f"查询执行失败: {e}")
    
    def build_query(self) -> str:
        """
        构建SQL查询
        
        Returns:
            SQL查询语句
        """
        try:
            data_source = self.config["data_source"]
            dimensions = self.config.get("dimensions", [])
            metrics = self.config.get("metrics", [])
            filters = self.config.get("filters", [])
            joins = self.config.get("joins", [])
            group_by = self.config.get("group_by", [])
            having = self.config.get("having", [])
            order_by = self.config.get("order_by", [])
            limit = self.config.get("limit")
            offset = self.config.get("offset")
            
            # 构建SELECT子句
            select_fields = []
            
            # 添加维度字段
            for dim in dimensions:
                if isinstance(dim, str):
                    select_fields.append(dim)
                elif isinstance(dim, dict):
                    field_expr = self._build_field_expression(dim)
                    select_fields.append(field_expr)
            
            # 添加指标字段
            for metric in metrics:
                if isinstance(metric, str):
                    select_fields.append(metric)
                elif isinstance(metric, dict):
                    metric_expr = self._build_metric_expression(metric)
                    select_fields.append(metric_expr)
            
            # 添加计算字段
            calculated_fields = self.config.get("calculated_fields", [])
            for calc_field in calculated_fields:
                calc_expr = self._build_calculated_field(calc_field)
                select_fields.append(calc_expr)
            
            if not select_fields:
                select_fields = ["*"]
            
            # 使用SQL构建器构建查询
            query = self.sql_builder.build_select_query(
                select_fields=select_fields,
                from_table=data_source,
                joins=joins,
                where_conditions=filters,
                group_by=group_by,
                having=having,
                order_by=order_by,
                limit=limit,
                offset=offset
            )
            
            self.log_debug("构建的SQL查询", query=query)
            return query
            
        except Exception as e:
            self.log_error("构建SQL查询失败", error=str(e))
            raise ValidationError(f"构建查询失败: {e}")
    
    def _build_field_expression(self, field_config: Dict[str, Any]) -> str:
        """
        构建字段表达式
        
        Args:
            field_config: 字段配置
            
        Returns:
            字段表达式
        """
        name = field_config.get("name")
        alias = field_config.get("alias")
        expression = field_config.get("expression")
        
        if expression:
            # 使用自定义表达式
            result = expression
        elif name:
            # 使用字段名
            result = name
        else:
            raise ValidationError("字段配置必须包含name或expression")
        
        # 添加别名
        if alias:
            result = f"{result} AS {alias}"
        
        return result
    
    def _build_metric_expression(self, metric_config: Dict[str, Any]) -> str:
        """
        构建指标表达式
        
        Args:
            metric_config: 指标配置
            
        Returns:
            指标表达式
        """
        name = metric_config.get("name")
        alias = metric_config.get("alias", name)
        agg_function = metric_config.get("aggregation", "SUM")
        expression = metric_config.get("expression")
        
        if expression:
            # 使用自定义表达式
            result = expression
        elif name:
            # 使用聚合函数
            result = f"{agg_function}({name})"
        else:
            raise ValidationError("指标配置必须包含name或expression")
        
        # 添加别名
        if alias:
            result = f"{result} AS {alias}"
        
        return result
    
    def _build_calculated_field(self, calc_config: Dict[str, Any]) -> str:
        """
        构建计算字段表达式
        
        Args:
            calc_config: 计算字段配置
            
        Returns:
            计算字段表达式
        """
        alias = calc_config.get("alias")
        expression = calc_config.get("expression")
        
        if not expression:
            raise ValidationError("计算字段必须包含expression")
        
        if not alias:
            raise ValidationError("计算字段必须包含alias")
        
        return f"{expression} AS {alias}"
    
    def _build_window_function(self, window_config: Dict[str, Any]) -> str:
        """
        构建窗口函数表达式
        
        Args:
            window_config: 窗口函数配置
            
        Returns:
            窗口函数表达式
        """
        function = window_config.get("function")
        partition_by = window_config.get("partition_by", [])
        order_by = window_config.get("order_by", [])
        alias = window_config.get("alias")
        
        if not function:
            raise ValidationError("窗口函数必须指定function")
        
        # 构建窗口函数表达式
        window_expr = function
        
        # 添加OVER子句
        over_parts = []
        
        if partition_by:
            partition_clause = "PARTITION BY " + ", ".join(partition_by)
            over_parts.append(partition_clause)
        
        if order_by:
            if isinstance(order_by, list):
                order_clause = "ORDER BY " + ", ".join(order_by)
            else:
                order_clause = f"ORDER BY {order_by}"
            over_parts.append(order_clause)
        
        if over_parts:
            over_clause = " ".join(over_parts)
        else:
            over_clause = ""
        
        result = f"{window_expr} OVER ({over_clause})"
        
        # 添加别名
        if alias:
            result = f"{result} AS {alias}"
        
        return result
