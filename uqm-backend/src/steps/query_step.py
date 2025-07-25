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
        
        # 验证计算字段
        calculated_fields = self.config.get("calculated_fields", [])
        if not isinstance(calculated_fields, list):
            raise ValidationError("calculated_fields必须是数组")
        
        # 至少需要有维度、指标或计算字段之一
        if not dimensions and not metrics and not calculated_fields:
            raise ValidationError("至少需要指定dimensions、metrics或calculated_fields之一")
    
    async def execute(self, context: Dict[str, Any]) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        执行查询步骤
        
        Args:
            context: 执行上下文
            
        Returns:
            查询结果，如果有分页则返回{"data": [...], "total_count": N}，否则返回[...]
        """
        try:
            data_source = self.config["data_source"]
            
            # 检查数据源是否是前面步骤的结果
            if self._is_step_data_source(data_source, context):
                # 使用步骤数据作为数据源
                return await self._execute_with_step_data(context)
            else:
                # 使用数据库表作为数据源
                return await self._execute_with_database(context)
            
        except Exception as e:
            self.log_error("查询步骤执行失败", error=str(e))
            raise ExecutionError(f"查询执行失败: {e}")
    
    def _is_step_data_source(self, data_source: str, context: Dict[str, Any]) -> bool:
        """
        检查数据源是否是步骤数据
        
        Args:
            data_source: 数据源名称（可能包含别名，如 "step_name alias"）
            context: 执行上下文
            
        Returns:
            是否是步骤数据源
        """
        step_data = context.get("step_data", {})
        
        # 处理带别名的步骤引用，如 "latest_order_date lod"
        # 提取步骤名称（第一个单词）
        step_name = data_source.split()[0]
        
        return step_name in step_data
    
    async def _execute_with_step_data(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        使用步骤数据执行查询
        
        Args:
            context: 执行上下文
            
        Returns:
            查询结果
        """
        data_source = self.config["data_source"]
        get_source_data = context["get_source_data"]
        
        # 处理带别名的步骤引用，如 "customer_order_counts coc"
        # 提取步骤名称（第一个单词）
        step_name = data_source.split()[0]
        
        # 获取源数据
        source_data = get_source_data(step_name)
        
        # 检查是否有JOIN操作
        joins = self.config.get("joins", [])
        if joins:
            # 处理JOIN操作
            result = self._process_step_data_with_joins(source_data, joins, get_source_data)
        else:
            # 对源数据进行处理
            result = self._process_step_data(source_data)
        
        return result
    
    async def _execute_with_database(self, context: Dict[str, Any]) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        使用数据库执行查询，支持分页
        
        Args:
            context: 执行上下文
            
        Returns:
            查询结果，如果有分页则返回{"data": [...], "total_count": N}，否则返回[...]
        """
        # 获取连接器管理器
        connector_manager = context["connector_manager"]
        connector = await connector_manager.get_default_connector()
        
        # 获取分页选项
        options = context.get("options", {})
        page = options.get("page")
        page_size = options.get("page_size")
        
        total_count = None
        
        # 如果提供了分页参数，执行分页逻辑
        if page and page_size:
            self.log_info(f"执行分页查询: page={page}, page_size={page_size}")
            
            # 1. 执行COUNT查询获取总记录数
            count_query = self.build_count_query()
            self.log_debug("COUNT查询", query=count_query)
            
            count_result = await connector.execute_query(count_query)
            total_count = count_result[0].get('total', 0) if count_result else 0
            
            self.log_info(f"查询总记录数: {total_count}")
            
            # 2. 修改配置以应用分页
            original_limit = self.config.get("limit")
            original_offset = self.config.get("offset")
            
            # 计算分页的limit和offset
            self.config["limit"] = page_size
            self.config["offset"] = (page - 1) * page_size
            
            # 3. 执行分页数据查询
            data_query = self.build_query()
            self.log_debug("分页数据查询", query=data_query)
            
            data_result = await connector.execute_query(data_query)
            
            # 4. 恢复原始配置
            if original_limit is not None:
                self.config["limit"] = original_limit
            else:
                self.config.pop("limit", None)
                
            if original_offset is not None:
                self.config["offset"] = original_offset
            else:
                self.config.pop("offset", None)
            
            return {
                "data": data_result,
                "total_count": total_count
            }
        else:
            # 普通查询，不分页
            query = self.build_query()
            self.log_debug("普通查询", query=query)
            
            result = await connector.execute_query(query)
            return result
    
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
            
            # 如果有JOIN，需要处理字段歧义问题
            has_joins = joins and len(joins) > 0
            
            # 构建SELECT子句
            select_fields = []
            
            # 添加维度字段
            for dim in dimensions:
                if isinstance(dim, str):
                    field_name = self._resolve_field_name(dim, data_source, has_joins)
                    select_fields.append(field_name)
                elif isinstance(dim, dict):
                    field_expr = self._build_field_expression(dim, data_source, has_joins)
                    select_fields.append(field_expr)
            
            # 添加指标字段
            for metric in metrics:
                if isinstance(metric, str):
                    field_name = self._resolve_field_name(metric, data_source, has_joins)
                    select_fields.append(field_name)
                elif isinstance(metric, dict):
                    metric_expr = self._build_metric_expression(metric, data_source, has_joins)
                    select_fields.append(metric_expr)
            
            # 添加计算字段
            calculated_fields = self.config.get("calculated_fields", [])
            for calc_field in calculated_fields:
                calc_expr = self._build_calculated_field(calc_field)
                select_fields.append(calc_expr)
            
            if not select_fields:
                select_fields = ["*"]
            
            # 处理GROUP BY字段的歧义
            resolved_group_by = []
            for field in group_by:
                if isinstance(field, str):
                    resolved_field = self._resolve_field_name(field, data_source, has_joins)
                    resolved_group_by.append(resolved_field)
                else:
                    resolved_group_by.append(field)
            
            # 使用SQL构建器构建查询
            query = self.sql_builder.build_select_query(
                select_fields=select_fields,
                from_table=data_source,
                joins=joins,
                where_conditions=self._resolve_filter_aliases(filters, has_joins),
                group_by=resolved_group_by,
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
    
    def build_count_query(self) -> str:
        """
        构建用于获取总行数的SQL COUNT查询
        
        Returns:
            COUNT查询语句
        """
        try:
            data_source = self.config["data_source"]
            filters = self.config.get("filters", [])
            joins = self.config.get("joins", [])
            group_by = self.config.get("group_by", [])
            having = self.config.get("having", [])
            
            # 如果有JOIN，需要处理字段歧义问题
            has_joins = joins and len(joins) > 0
            
            # 处理GROUP BY字段的歧义
            resolved_group_by = []
            for field in group_by:
                if isinstance(field, str):
                    resolved_field = self._resolve_field_name(field, data_source, has_joins)
                    resolved_group_by.append(resolved_field)
                else:
                    resolved_group_by.append(field)
            
            # 使用SQL构建器构建COUNT查询
            query = self.sql_builder.build_select_query(
                select_fields=["COUNT(*) as total"],
                from_table=data_source,
                joins=joins,
                where_conditions=self._resolve_filter_aliases(filters, has_joins),
                group_by=resolved_group_by,
                having=having
                # 注意：COUNT查询不需要 ORDER BY, LIMIT, OFFSET
            )
            
            # 如果存在GROUP BY，我们需要计算分组后的总数
            if resolved_group_by:
                query = f"SELECT COUNT(*) as total FROM ({query}) as subquery"
            
            self.log_debug("构建的COUNT查询", query=query)
            return query
            
        except Exception as e:
            self.log_error("构建COUNT查询失败", error=str(e))
            raise ValidationError(f"构建COUNT查询失败: {e}")
    
    def _build_field_expression(self, field_config: Dict[str, Any], main_table: str = None, has_joins: bool = False) -> str:
        """
        构建字段表达式
        
        Args:
            field_config: 字段配置
            main_table: 主表名
            has_joins: 是否有JOIN
            
        Returns:
            字段表达式
        """
        name = field_config.get("name")
        alias = field_config.get("alias")
        expression = field_config.get("expression")
        
        if expression:
            # 使用自定义表达式，验证表别名
            result = self._validate_and_resolve_aliases(expression) if has_joins else expression
        elif name:
            # 使用字段名，处理歧义
            resolved_name = self._resolve_field_name(name, main_table, has_joins) if main_table else name
            result = resolved_name
        else:
            raise ValidationError("字段配置必须包含name或expression")
        
        # 添加别名
        if alias:
            result = f"{result} AS {alias}"
        
        return result
    
    def _validate_and_resolve_aliases(self, expression: str) -> str:
        """
        验证并解析表达式中的表别名
        
        Args:
            expression: 字段表达式
            
        Returns:
            解析后的表达式
        """
        # 获取 JOIN 配置中定义的表别名映射
        alias_mapping = self._get_table_alias_mapping()
        
        # 检查表达式是否包含表别名前缀
        if '.' in expression:
            parts = expression.split('.', 1)
            potential_alias = parts[0]
            field_name = parts[1]
            
            # 如果这个别名在 JOIN 中有定义，则保留；否则移除前缀
            if potential_alias in alias_mapping:
                return expression  # 别名有效，保持原样
            else:
                # 别名无效，移除前缀，只保留字段名
                return field_name
        
        return expression
    
    def _get_table_alias_mapping(self) -> Dict[str, str]:
        """
        获取表别名到实际表名的映射
        
        Returns:
            别名映射字典
        """
        alias_mapping = {}
        
        # 处理主表别名
        data_source = self.config.get("data_source", "")
        if ' ' in data_source:
            parts = data_source.split()
            table_name = parts[0]
            table_alias = parts[1]
            alias_mapping[table_alias] = table_name
        
        # 处理 JOIN 表别名
        joins = self.config.get("joins", [])
        for join in joins:
            target = join.get("target", "")
            if ' ' in target:
                parts = target.split()
                table_name = parts[0]
                table_alias = parts[1]
                alias_mapping[table_alias] = table_name
        
        return alias_mapping
    
    def _resolve_filter_aliases(self, filters: List[Dict[str, Any]], has_joins: bool) -> List[Dict[str, Any]]:
        """
        解析过滤条件中的表别名
        
        Args:
            filters: 过滤条件列表
            has_joins: 是否有JOIN
            
        Returns:
            解析后的过滤条件列表
        """
        if not has_joins or not filters:
            return filters
        
        resolved_filters = []
        for filter_condition in filters:
            resolved_condition = self._resolve_single_filter_alias(filter_condition)
            resolved_filters.append(resolved_condition)
        
        return resolved_filters
    
    def _resolve_single_filter_alias(self, filter_condition: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析单个过滤条件中的表别名
        
        Args:
            filter_condition: 过滤条件
            
        Returns:
            解析后的过滤条件
        """
        if "logic" in filter_condition and "conditions" in filter_condition:
            # 处理逻辑组合条件
            resolved_condition = filter_condition.copy()
            resolved_conditions = []
            for condition in filter_condition["conditions"]:
                resolved_conditions.append(self._resolve_single_filter_alias(condition))
            resolved_condition["conditions"] = resolved_conditions
            return resolved_condition
        
        elif "field" in filter_condition:
            # 处理简单字段条件
            resolved_condition = filter_condition.copy()
            field = filter_condition["field"]
            resolved_field = self._validate_and_resolve_aliases(field)
            resolved_condition["field"] = resolved_field
            return resolved_condition
        
        return filter_condition
    
    def _build_metric_expression(self, metric_config: Dict[str, Any], main_table: str = None, has_joins: bool = False) -> str:
        """
        构建指标表达式
        
        Args:
            metric_config: 指标配置
            main_table: 主表名
            has_joins: 是否有JOIN
            
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
            # 使用聚合函数，处理字段名歧义
            resolved_name = self._resolve_field_name(name, main_table, has_joins) if main_table else name
            result = f"{agg_function}({resolved_name})"
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
        expression = calc_config.get("expression")
        alias = calc_config.get("alias")
        name = calc_config.get("name")
        
        if not expression:
            raise ValidationError("计算字段必须包含expression")
        
        # 如果没有alias，使用name作为别名
        if not alias:
            if name:
                alias = name
            else:
                raise ValidationError("计算字段必须包含alias或name")
        
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
    
    def _process_step_data(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理步骤数据
        
        Args:
            source_data: 源数据
            
        Returns:
            处理后的数据
        """
        if not source_data:
            return []
        # 获取配置
        dimensions = self.config.get("dimensions", [])
        metrics = self.config.get("metrics", [])
        calculated_fields = self.config.get("calculated_fields", [])
        filters = self.config.get("filters", [])
        group_by = self.config.get("group_by", [])
        having = self.config.get("having", [])
        order_by = self.config.get("order_by", [])
        limit = self.config.get("limit")
        offset = self.config.get("offset")

        # 如果没有任何处理配置，直接返回源数据
        if not dimensions and not metrics and not calculated_fields and not filters and not group_by and not having and not order_by and not limit:
            return source_data

        # 应用过滤器
        filtered_data = self._apply_filters(source_data, filters)

        # 新增：如果metrics只有聚合指标且没有group_by，则全表聚合
        if metrics and not group_by and all(self._is_aggregation_metric(metric) for metric in metrics):
            agg_row = {}
            metric_expr_map = {}
            for metric in metrics:
                if isinstance(metric, dict):
                    field_name = metric.get("name")
                    alias = metric.get("alias", field_name)
                    aggregation = metric.get("aggregation", "SUM")
                    expression = metric.get("expression")
                    if expression:
                        agg_row[alias] = self._aggregate_expression(expression, filtered_data)
                        metric_expr_map[expression.strip().upper()] = alias
                    elif field_name:
                        agg_row[alias] = self._aggregate_field(field_name, aggregation, filtered_data)
                        metric_expr_map[f"{aggregation}({field_name})".upper()] = alias
            # 添加计算字段
            if calculated_fields:
                for calc_field in calculated_fields:
                    alias = calc_field.get("alias")
                    expression = calc_field.get("expression")
                    if alias and expression:
                        expr_key = expression.strip().upper()
                        # 如果表达式和metrics聚合表达式一致，直接赋值
                        if expr_key in metric_expr_map:
                            agg_row[alias] = agg_row[metric_expr_map[expr_key]]
                        else:
                            try:
                                agg_row[alias] = self._evaluate_expression_with_aggregates(expression, agg_row)
                            except Exception as e:
                                self.log_warning(f"全表聚合计算字段 {alias} 计算失败: {e}")
                                agg_row[alias] = None
            return [agg_row]

        # 处理分组和聚合
        if group_by or any(self._is_aggregation_metric(metric) for metric in metrics):
            grouped_data = self._apply_grouping_and_aggregation(filtered_data, dimensions, metrics, group_by)
        else:
            # 不需要分组，只选择字段
            grouped_data = self._select_fields(filtered_data, dimensions, metrics)

        # 添加计算字段
        if calculated_fields:
            grouped_data = self._add_calculated_fields(grouped_data, calculated_fields)

        # 应用Having条件
        if having:
            grouped_data = self._apply_having(grouped_data, having)

        # 排序
        if order_by:
            grouped_data = self._apply_sorting(grouped_data, order_by)

        # 应用限制和偏移
        if offset or limit:
            grouped_data = self._apply_limit_offset(grouped_data, limit, offset)

        return grouped_data
    
    def _apply_filters(self, data: List[Dict[str, Any]], filters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """应用过滤条件"""
        if not filters:
            return data
        
        filtered_data = []
        for row in data:
            if self._evaluate_filters(row, filters):
                filtered_data.append(row)
        
        return filtered_data
    
    def _evaluate_filters(self, row: Dict[str, Any], filters: List[Dict[str, Any]]) -> bool:
        """评估过滤条件"""
        if not filters:
            return True
        
        for filter_config in filters:
            if not self._evaluate_filter_condition(row, filter_config):
                return False
        
        return True
    
    def _evaluate_filter_condition(self, row: Dict[str, Any], filter_config: Dict[str, Any]) -> bool:
        """评估单个过滤条件（支持嵌套逻辑）"""
        # 检查是否是嵌套逻辑结构
        if "logic" in filter_config and "conditions" in filter_config:
            return self._evaluate_logical_condition(row, filter_config)
        
        # 检查是否是简单过滤条件
        elif "field" in filter_config and "operator" in filter_config:
            field = filter_config.get("field")
            operator = filter_config.get("operator")
            value = filter_config.get("value")
            return self._evaluate_single_filter(row, field, operator, value)
        
        else:
            self.log_warning(f"未识别的过滤条件格式: {filter_config}")
            return True
    
    def _evaluate_logical_condition(self, row: Dict[str, Any], logical_config: Dict[str, Any]) -> bool:
        """评估逻辑条件（AND/OR）"""
        logic = logical_config.get("logic", "AND").upper()
        conditions = logical_config.get("conditions", [])
        
        if not conditions:
            return True
        
        if logic == "AND":
            # 所有条件都必须为真
            for condition in conditions:
                if not self._evaluate_filter_condition(row, condition):
                    return False
            return True
        
        elif logic == "OR":
            # 至少一个条件为真
            for condition in conditions:
                if self._evaluate_filter_condition(row, condition):
                    return True
            return False
        
        else:
            self.log_warning(f"不支持的逻辑操作符: {logic}")
            return True
    
    def _evaluate_single_filter(self, row: Dict[str, Any], field: str, operator: str, value: Any) -> bool:
        """评估单个过滤条件"""
        row_value = row.get(field)
        
        # 如果过滤值是SQL表达式，先计算它
        computed_value = self._compute_filter_value(value)
        
        if operator == "=":
            return row_value == computed_value
        elif operator == "!=":
            return row_value != computed_value
        elif operator == ">":
            return row_value is not None and self._compare_values(row_value, computed_value, ">")
        elif operator == ">=":
            return row_value is not None and self._compare_values(row_value, computed_value, ">=")
        elif operator == "<":
            return row_value is not None and self._compare_values(row_value, computed_value, "<")
        elif operator == "<=":
            return row_value is not None and self._compare_values(row_value, computed_value, "<=")
        elif operator == "IN":
            return row_value in computed_value if isinstance(computed_value, list) else False
        elif operator == "NOT IN":
            return row_value not in computed_value if isinstance(computed_value, list) else True
        elif operator == "IS NULL":
            return row_value is None
        elif operator == "IS NOT NULL":
            return row_value is not None
        elif operator == "LIKE":
            if row_value is None:
                return False
            return str(computed_value).replace("%", ".*").replace("_", ".") in str(row_value)
        else:
            self.log_warning(f"不支持的过滤操作符: {operator}")
            return True
    
    def _compute_filter_value(self, value: Any) -> Any:
        """计算过滤值，支持SQL表达式"""
        if not isinstance(value, str):
            return value
        
        # 检查是否是日期函数表达式
        if "DATE_SUB" in value.upper() or "CURDATE" in value.upper() or "CURRENT_DATE" in value.upper():
            return self._evaluate_date_expression(value)
        
        # 检查是否是其他SQL函数表达式
        if any(func in value.upper() for func in ["NOW()", "CURRENT_TIMESTAMP", "UNIX_TIMESTAMP"]):
            return self._evaluate_date_expression(value)
        
        return value
    
    def _evaluate_date_expression(self, expression: str) -> Any:
        """计算日期表达式"""
        from datetime import datetime, timedelta
        import re
        
        # 处理 DATE_SUB(CURDATE(), INTERVAL n MONTH/DAY/YEAR)
        if "DATE_SUB" in expression.upper():
            # 提取间隔信息
            interval_match = re.search(r'INTERVAL\s+(\d+)\s+(MONTH|DAY|YEAR)', expression.upper())
            if interval_match:
                interval_value = int(interval_match.group(1))
                interval_unit = interval_match.group(2)
                
                current_date = datetime.now().date()
                
                if interval_unit == "MONTH":
                    # 近似计算月份减法
                    year = current_date.year
                    month = current_date.month - interval_value
                    if month <= 0:
                        year -= abs(month) // 12 + 1
                        month = 12 + month % 12
                    result_date = current_date.replace(year=year, month=month)
                elif interval_unit == "DAY":
                    result_date = current_date - timedelta(days=interval_value)
                elif interval_unit == "YEAR":
                    result_date = current_date.replace(year=current_date.year - interval_value)
                
                return result_date.strftime("%Y-%m-%d")
        
        # 处理 CURDATE() 或 CURRENT_DATE()
        if "CURDATE" in expression.upper() or "CURRENT_DATE" in expression.upper():
            return datetime.now().date().strftime("%Y-%m-%d")
        
        # 如果无法解析，返回原值
        return expression
    
    def _compare_values(self, val1: Any, val2: Any, operator: str) -> bool:
        """比较两个值，支持日期比较"""
        # 尝试日期比较
        try:
            from datetime import datetime
            
            # 尝试解析为日期
            if isinstance(val1, str) and isinstance(val2, str):
                # 尝试多种日期格式
                date_formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d", "%m/%d/%Y"]
                
                date1 = None
                date2 = None
                
                for fmt in date_formats:
                    try:
                        date1 = datetime.strptime(val1, fmt)
                        break
                    except:
                        continue
                
                for fmt in date_formats:
                    try:
                        date2 = datetime.strptime(val2, fmt)
                        break
                    except:
                        continue
                
                if date1 and date2:
                    if operator == ">":
                        return date1 > date2
                    elif operator == ">=":
                        return date1 >= date2
                    elif operator == "<":
                        return date1 < date2
                    elif operator == "<=":
                        return date1 <= date2
        except:
            pass
        
        # 回退到基本比较
        try:
            if operator == ">":
                return val1 > val2
            elif operator == ">=":
                return val1 >= val2
            elif operator == "<":
                return val1 < val2
            elif operator == "<=":
                return val1 <= val2
        except:
            return False
        
        return False
    
    def _is_aggregation_metric(self, metric: Union[str, Dict[str, Any]]) -> bool:
        """检查是否是聚合指标"""
        if isinstance(metric, dict):
            return metric.get("aggregation") is not None or "SUM(" in metric.get("expression", "") or "COUNT(" in metric.get("expression", "") or "AVG(" in metric.get("expression", "") or "MAX(" in metric.get("expression", "") or "MIN(" in metric.get("expression", "")
        return False
    
    def _select_fields(self, data: List[Dict[str, Any]], dimensions: List[Union[str, Dict[str, Any]]], metrics: List[Union[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """选择字段"""
        if not dimensions and not metrics:
            return data
        
        result = []
        for row in data:
            new_row = {}
            
            # 处理维度字段
            for dim in dimensions:
                if isinstance(dim, str):
                    if dim in row:
                        new_row[dim] = row[dim]
                elif isinstance(dim, dict):
                    field_name = dim.get("name")
                    alias = dim.get("alias", field_name)
                    expression = dim.get("expression")
                    
                    if expression:
                        # 计算表达式（简单实现）
                        try:
                            new_row[alias] = self._evaluate_expression(expression, row)
                        except:
                            new_row[alias] = None
                    elif field_name and field_name in row:
                        new_row[alias] = row[field_name]
            
            # 处理指标字段（非聚合）
            for metric in metrics:
                if isinstance(metric, str):
                    if metric in row:
                        new_row[metric] = row[metric]
                elif isinstance(metric, dict):
                    field_name = metric.get("name")
                    alias = metric.get("alias", field_name)
                    expression = metric.get("expression")
                    
                    if expression:
                        # 计算表达式
                        try:
                            new_row[alias] = self._evaluate_expression(expression, row)
                        except:
                            new_row[alias] = None
                    elif field_name and field_name in row:
                        new_row[alias] = row[field_name]
            
            result.append(new_row)
        
        return result
    
    def _apply_grouping_and_aggregation(self, data: List[Dict[str, Any]], dimensions: List[Union[str, Dict[str, Any]]], metrics: List[Union[str, Dict[str, Any]]], group_by: List[str]) -> List[Dict[str, Any]]:
        """应用分组和聚合"""
        if not group_by:
            # 使用所有维度作为分组字段
            group_by = []
            for dim in dimensions:
                if isinstance(dim, str):
                    group_by.append(dim)
                elif isinstance(dim, dict):
                    alias = dim.get("alias", dim.get("name"))
                    if alias:
                        group_by.append(alias)
        
        # 检查是否需要分组 - 修复逻辑
        needs_grouping = bool(group_by) or any(self._is_aggregation_metric(metric) for metric in metrics)
        
        if not needs_grouping:
            # 如果不需要分组，直接选择字段
            return self._select_fields(data, dimensions, metrics)
        
        # 按分组字段分组
        groups = {}
        for row in data:
            # 构建分组键 - 支持带前缀的字段名
            group_key_values = []
            for field in group_by:
                # 尝试多种字段名格式
                value = None
                if field in row:
                    value = row[field]
                else:
                    # 尝试寻找带前缀的字段名
                    for row_key in row.keys():
                        if row_key.endswith(f".{field}") or row_key == field:
                            value = row[row_key]
                            break
                group_key_values.append(value)
            
            group_key = tuple(group_key_values)
            
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(row)
        
        # 对每个组进行聚合
        result = []
        for group_key, group_rows in groups.items():
            aggregated_row = {}
            
            # 添加分组字段
            for i, field in enumerate(group_by):
                aggregated_row[field] = group_key[i]
            
            # 添加维度字段（非聚合）
            for dim in dimensions:
                if isinstance(dim, str):
                    if dim not in group_by and dim in group_rows[0]:
                        aggregated_row[dim] = group_rows[0][dim]
                elif isinstance(dim, dict):
                    field_name = dim.get("name")
                    alias = dim.get("alias", field_name)
                    expression = dim.get("expression")
                    
                    if alias not in group_by:
                        if expression:
                            try:
                                aggregated_row[alias] = self._evaluate_expression(expression, group_rows[0])
                            except:
                                aggregated_row[alias] = None
                        elif field_name and field_name in group_rows[0]:
                            aggregated_row[alias] = group_rows[0][field_name]
            
            # 计算聚合指标
            for metric in metrics:
                if isinstance(metric, dict):
                    field_name = metric.get("name")
                    alias = metric.get("alias", field_name)
                    aggregation = metric.get("aggregation", "SUM")
                    expression = metric.get("expression")
                    
                    if expression:
                        # 处理表达式聚合
                        aggregated_row[alias] = self._aggregate_expression(expression, group_rows)
                    elif field_name:
                        # 处理带前缀的字段名
                        actual_field_name = field_name
                        if field_name not in group_rows[0]:
                            # 寻找带前缀的字段名
                            for row_key in group_rows[0].keys():
                                if row_key.endswith(f".{field_name}") or row_key == field_name:
                                    actual_field_name = row_key
                                    break
                        
                        # 标准聚合
                        aggregated_row[alias] = self._aggregate_field(actual_field_name, aggregation, group_rows)
            
            result.append(aggregated_row)
        
        return result
    
    def _aggregate_field(self, field_name: str, aggregation: str, rows: List[Dict[str, Any]]) -> Any:
        """聚合字段，支持字段名变体"""
        # 支持字段名变体
        values = []
        for row in rows:
            for variant in self._build_field_variants(field_name, row):
                if variant in row and row[variant] is not None:
                    values.append(row[variant])
                    break
        if not values:
            return None
        if aggregation == "SUM":
            return sum(float(v) for v in values if self._is_numeric(v))
        elif aggregation == "COUNT":
            return len(values)
        elif aggregation == "AVG":
            numeric_values = [float(v) for v in values if self._is_numeric(v)]
            return sum(numeric_values) / len(numeric_values) if numeric_values else None
        elif aggregation == "MAX":
            return max(values)
        elif aggregation == "MIN":
            return min(values)
        else:
            self.log_warning(f"不支持的聚合函数: {aggregation}")
            return None

    def _aggregate_expression(self, expression: str, rows: List[Dict[str, Any]]) -> Any:
        """聚合表达式（支持字段名变体）"""
        import re
        # 首先尝试直接的SUM或COUNT或AVG
        if "SUM(" in expression.upper() and "/" not in expression:
            match = re.search(r'SUM\(([^)]+)\)', expression, re.IGNORECASE)
            if match:
                field_expr = match.group(1).strip()
                total = 0
                for row in rows:
                    for variant in self._build_field_variants(field_expr, row):
                        if variant in row and self._is_numeric(row[variant]):
                            total += float(row[variant])
                            break
                return total
        elif "COUNT(" in expression.upper() and "/" not in expression:
            return len(rows)
        elif "AVG(" in expression.upper() and "/" not in expression:
            match = re.search(r'AVG\(([^)]+)\)', expression, re.IGNORECASE)
            if match:
                field_expr = match.group(1).strip()
                values = []
                for row in rows:
                    for variant in self._build_field_variants(field_expr, row):
                        if variant in row and self._is_numeric(row[variant]):
                            values.append(float(row[variant]))
                            break
                if values:
                    return sum(values) / len(values)
                else:
                    return None
        else:
            # 处理复杂表达式，如 SUM(field1) / COUNT(field2)
            return self._evaluate_complex_aggregate_expression(expression, rows)
        return None
    
    def _evaluate_complex_aggregate_expression(self, expression: str, rows: List[Dict[str, Any]]) -> Any:
        """计算复杂的聚合表达式"""
        import re
        
        # 替换表达式中的聚合函数
        result_expr = expression
        
        # 查找所有SUM函数调用（更精确的匹配）
        sum_pattern = r'SUM\(([^)]+)\)'
        sum_matches = list(re.finditer(sum_pattern, expression, re.IGNORECASE))
        
        # 从后往前替换，避免位置偏移问题
        for match in reversed(sum_matches):
            start, end = match.span()
            field_expr = match.group(1).strip()
            total = 0
            for row in rows:
                try:
                    value = self._evaluate_expression(field_expr, row)
                    if self._is_numeric(value):
                        total += float(value)
                except:
                    pass
            result_expr = result_expr[:start] + str(total) + result_expr[end:]
        
        # 查找所有COUNT函数调用
        count_pattern = r'COUNT\(([^)]+)\)'
        count_matches = list(re.finditer(count_pattern, result_expr, re.IGNORECASE))
        
        # 从后往前替换COUNT函数
        for match in reversed(count_matches):
            start, end = match.span()
            field_expr = match.group(1).strip()
            count = len(rows)
            result_expr = result_expr[:start] + str(count) + result_expr[end:]
          # 移除CAST函数 - 使用递归方法处理嵌套括号
        def remove_cast_functions(expr):
            while 'CAST(' in expr.upper():
                # 找到CAST的位置
                cast_start = expr.upper().find('CAST(')
                if cast_start == -1:
                    break
                    
                # 找到对应的闭合括号
                paren_count = 0
                cast_end = -1
                for i in range(cast_start + 5, len(expr)):  # 从CAST(后开始
                    if expr[i] == '(':
                        paren_count += 1
                    elif expr[i] == ')':
                        if paren_count == 0:
                            cast_end = i
                            break
                        paren_count -= 1
                
                if cast_end == -1:
                    break
                    
                # 提取CAST函数内容
                cast_content = expr[cast_start + 5:cast_end]  # 去掉CAST(
                
                # 找到AS关键字
                as_pos = cast_content.upper().rfind(' AS ')
                if as_pos != -1:
                    # 提取AS前的表达式
                    inner_expr = cast_content[:as_pos].strip()
                    # 替换整个CAST函数
                    expr = expr[:cast_start] + inner_expr + expr[cast_end + 1:]
                else:
                    # 如果没有AS，就去掉CAST包装
                    expr = expr[:cast_start] + cast_content + expr[cast_end + 1:]
            
            return expr
        
        result_expr = remove_cast_functions(result_expr)
        
        # 处理NULLIF函数 - NULLIF(expr1, expr2) 如果expr1 == expr2返回NULL，否则返回expr1
        # 在除法上下文中，我们将其转换为安全除法：如果分母为0则返回None，否则正常除法
        def handle_nullif(expr):
            while 'NULLIF(' in expr.upper():
                nullif_start = expr.upper().find('NULLIF(')
                if nullif_start == -1:
                    break
                    
                # 找到对应的闭合括号
                paren_count = 0
                nullif_end = -1
                for i in range(nullif_start + 7, len(expr)):  # 从NULLIF(后开始
                    if expr[i] == '(':
                        paren_count += 1
                    elif expr[i] == ')':
                        if paren_count == 0:
                            nullif_end = i
                            break
                        paren_count -= 1
                
                if nullif_end == -1:
                    break
                    
                # 提取NULLIF函数内容并解析参数
                nullif_content = expr[nullif_start + 7:nullif_end]  # 去掉NULLIF(
                
                # 简单解析参数（假设用逗号分隔且没有嵌套函数调用）
                # 更复杂的解析可能需要专门的表达式解析器
                params = nullif_content.split(',')
                if len(params) == 2:
                    expr1 = params[0].strip()
                    expr2 = params[1].strip()
                    
                    # 对于常见的除零保护模式 NULLIF(expr, 0)，我们转换为Python的三元表达式
                    if expr2 == '0':
                        # 如果分母为0，返回None（相当于NULL），否则返回原值
                        safe_expr = f"(None if {expr1} == 0 else {expr1})"
                        expr = expr[:nullif_start] + safe_expr + expr[nullif_end + 1:]
                    else:
                        # 通用NULLIF处理
                        safe_expr = f"(None if {expr1} == {expr2} else {expr1})"
                        expr = expr[:nullif_start] + safe_expr + expr[nullif_end + 1:]
                else:
                    # 如果解析失败，跳过
                    break
            
            return expr
        
        result_expr = handle_nullif(result_expr)
        
        # 计算最终结果
        try:
            result = eval(result_expr)
            # 如果结果涉及None（SQL的NULL），处理除法
            if result is None:
                return None
            return result
        except Exception as e:
            self.log_warning(f"复杂聚合表达式计算失败: {expression} -> {result_expr}, error: {e}")
            return None
    
    def _evaluate_expression(self, expression: str, row: Dict[str, Any]) -> Any:
        """计算表达式（简单实现）"""
        # 这是一个简化的表达式计算器
        # 在实际应用中可能需要更复杂的解析器
        
        import re
        
        # 处理 CASE WHEN 表达式
        if "CASE" in expression.upper() and "WHEN" in expression.upper():
            return self._evaluate_case_when_expression(expression, row)
        
        # 检查是否包含聚合函数
        if any(func in expression.upper() for func in ['SUM(', 'COUNT(', 'AVG(', 'MAX(', 'MIN(']):
            return self._evaluate_expression_with_aggregates(expression, row)
        
        # 替换字段名
        result_expr = expression
        
        # 查找所有字段引用 - 只匹配真正的字段名，排除SQL关键字
        field_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        fields = re.findall(field_pattern, expression)
        
        # 排除常见的SQL关键字和函数名
        sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'IS', 'NULL',
            'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN',
            'CAST', 'AS', 'DECIMAL', 'INTEGER', 'VARCHAR', 'CHAR', 'DATE', 'TIMESTAMP'
        }
        
        for field in fields:
            if field.upper() not in sql_keywords and field in row:
                value = row[field]
                if isinstance(value, str):
                    # 只替换完整的单词匹配
                    result_expr = re.sub(r'\b' + re.escape(field) + r'\b', f"'{value}'", result_expr)
                else:
                    # 只替换完整的单词匹配
                    result_expr = re.sub(r'\b' + re.escape(field) + r'\b', str(value), result_expr)
        
        # 尝试计算表达式
        try:
            # 注意：这里使用eval有安全风险，在生产环境中应该使用更安全的表达式解析器
            return eval(result_expr)
        except Exception as e:
            self.log_warning(f"表达式计算失败: {expression} -> {result_expr}, error: {e}")
            return None
    
    def _evaluate_expression_with_aggregates(self, expression: str, row: Dict[str, Any]) -> Any:
        """计算包含聚合函数的表达式"""
        import re
        
        result_expr = expression
        
        # 处理各种聚合函数
        for func_name in ['SUM', 'COUNT', 'AVG', 'MAX', 'MIN']:
            func_pattern = f'{func_name}\\(([^)]+)\\)'
            func_matches = re.findall(func_pattern, expression, re.IGNORECASE)
            
            for field_expr in func_matches:
                # 动态构建字段名变体，而不是硬编码
                field_variants = self._build_field_variants(field_expr, row)
                
                field_value = None
                for variant in field_variants:
                    if variant in row:
                        field_value = row[variant]
                        break
                
                if field_value is not None:
                    # 替换聚合函数调用
                    func_call = f"{func_name}({field_expr})"
                    result_expr = result_expr.replace(func_call, str(field_value))
        
        # 如果替换后表达式还包含SQL聚合函数，说明本地无法处理，直接返回None并警告
        if re.search(r'(SUM|COUNT|AVG|MAX|MIN)\\(', result_expr, re.IGNORECASE):
            self.log_warning(f"本地无法处理聚合表达式: {expression} -> {result_expr}")
            return None
        
        # 尝试计算表达式
        try:
            return eval(result_expr)
        except Exception as e:
            self.log_warning(f"聚合表达式计算失败: {expression} -> {result_expr}, error: {e}")
            return None
    
    def _build_field_variants(self, field_expr: str, row: Dict[str, Any]) -> List[str]:
        """
        动态构建字段名变体
        
        Args:
            field_expr: 字段表达式，如 "coc.total_orders"
            row: 当前行数据
            
        Returns:
            字段名变体列表
        """
        variants = [field_expr]  # 原始字段名
        
        # 如果字段名包含表别名（如 "coc.total_orders"）
        if '.' in field_expr:
            table_alias, field_name = field_expr.split('.', 1)
            variants.extend([
                field_name,  # 去掉前缀：total_orders
                f"{table_alias}_{field_name}"  # 加上别名前缀：coc_total_orders
            ])
        else:
            # 如果字段名不包含表别名，尝试从行数据中推断可能的表别名
            # 查找所有以该字段名结尾的键
            for key in row.keys():
                if key.endswith(f"_{field_expr}"):
                    variants.append(key)
        
        # 从当前查询配置中获取表别名信息，构建更多变体
        variants.extend(self._get_table_alias_variants(field_expr))
        
        return list(set(variants))  # 去重
    
    def _get_table_alias_variants(self, field_expr: str) -> List[str]:
        """
        从查询配置中获取表别名变体
        
        Args:
            field_expr: 字段表达式
            
        Returns:
            基于表别名的字段变体列表
        """
        variants = []
        
        # 获取当前查询的配置信息
        joins = self.config.get("joins", [])
        data_source = self.config.get("data_source", "")
        
        # 解析data_source中的表别名
        if ' ' in data_source:
            main_table_alias = data_source.split()[1]  # 如 "orders o" -> "o"
            if '.' not in field_expr:
                variants.append(f"{main_table_alias}_{field_expr}")
        
        # 从JOIN配置中获取表别名
        for join_config in joins:
            join_table = join_config.get("table", "")
            if ' ' in join_table:
                join_alias = join_table.split()[1]  # 如 "customer_first_order_date cfod" -> "cfod"
                if '.' not in field_expr:
                    variants.append(f"{join_alias}_{field_expr}")
        
        return variants
    
    def _evaluate_case_when_expression(self, expression: str, row: Dict[str, Any]) -> Any:
        """计算 CASE WHEN 表达式"""
        import re
        
        # 简化的 CASE WHEN 表达式解析器
        # 格式: CASE WHEN condition THEN value1 ELSE value2 END
        
        # 提取 WHEN 条件和 THEN/ELSE 值
        case_pattern = r'CASE\s+WHEN\s+(.+?)\s+THEN\s+(.+?)\s+ELSE\s+(.+?)\s+END'
        match = re.search(case_pattern, expression, re.IGNORECASE)
        
        if not match:
            self.log_warning(f"无法解析 CASE WHEN 表达式: {expression}")
            return None
        
        condition = match.group(1)
        then_value = match.group(2)
        else_value = match.group(3)
        
        # 计算条件
        condition_result = self._evaluate_condition(condition, row)
        
        if condition_result:
            return self._parse_value(then_value)
        else:
            return self._parse_value(else_value)
    
    def _evaluate_condition(self, condition: str, row: Dict[str, Any]) -> bool:
        """计算条件表达式"""
        import re
        
        # 处理聚合函数表达式
        if any(func in condition.upper() for func in ['SUM(', 'COUNT(', 'AVG(', 'MAX(', 'MIN(']):
            return self._evaluate_condition_with_aggregates(condition, row)
        
        # 替换字段名
        result_condition = condition
        
        # 查找所有字段引用
        field_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        fields = re.findall(field_pattern, condition)
        
        # 排除操作符和SQL关键字
        operators = {'>', '<', '>=', '<=', '=', '!=', 'AND', 'OR', 'NOT', 'SUM', 'COUNT', 'AVG', 'MAX', 'MIN'}
        
        for field in fields:
            if field.upper() not in operators and field in row:
                value = row[field]
                # 只替换完整的单词匹配
                result_condition = re.sub(r'\b' + re.escape(field) + r'\b', str(value), result_condition)
        
        # 将 SQL 操作符转换为 Python 操作符
        result_condition = result_condition.replace(' = ', ' == ')
        result_condition = result_condition.replace('=', '==')
        
        try:
            return bool(eval(result_condition))
        except Exception as e:
            self.log_warning(f"条件计算失败: {condition} -> {result_condition}, error: {e}")
            return False
    
    def _evaluate_condition_with_aggregates(self, condition: str, row: Dict[str, Any]) -> bool:
        """计算包含聚合函数的条件表达式"""
        import re
        
        # 处理 SUM(field_name) > value 这样的条件
        # 在这个上下文中，我们假设聚合已经在当前行中计算完成
        result_condition = condition
        
        # 替换SUM(field)为实际值
        sum_pattern = r'SUM\(([^)]+)\)'
        sum_matches = re.findall(sum_pattern, condition, re.IGNORECASE)
        
        for field_expr in sum_matches:
            # 动态构建字段名变体，而不是硬编码
            field_variants = self._build_field_variants(field_expr, row)
            
            field_value = None
            for variant in field_variants:
                if variant in row:
                    field_value = row[variant]
                    break
            
            if field_value is not None:
                # 替换SUM函数调用
                sum_call = f"SUM({field_expr})"
                result_condition = result_condition.replace(sum_call, str(field_value))
        
        # 处理其他聚合函数（类似方式）
        for func_name in ['COUNT', 'AVG', 'MAX', 'MIN']:
            func_pattern = f'{func_name}\\(([^)]+)\\)'
            func_matches = re.findall(func_pattern, condition, re.IGNORECASE)
            
            for field_expr in func_matches:
                # 动态构建字段名变体，而不是硬编码
                field_variants = self._build_field_variants(field_expr, row)
                
                field_value = None
                for variant in field_variants:
                    if variant in row:
                        field_value = row[variant]
                        break
                
                if field_value is not None:
                    func_call = f"{func_name}({field_expr})"
                    result_condition = result_condition.replace(func_call, str(field_value))
        
        # 将 SQL 操作符转换为 Python 操作符
        result_condition = result_condition.replace(' = ', ' == ')
        result_condition = result_condition.replace('=', '==')
        
        try:
            return bool(eval(result_condition))
        except Exception as e:
            self.log_warning(f"聚合条件计算失败: {condition} -> {result_condition}, error: {e}")
            return False
    
    def _parse_value(self, value_str: str) -> Any:
        """解析值字符串"""
        value_str = value_str.strip()
        
        # 尝试解析为数字
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            # 如果不是数字，返回字符串（去掉引号）
            if value_str.startswith("'") and value_str.endswith("'"):
                return value_str[1:-1]
            elif value_str.startswith('"') and value_str.endswith('"'):
                return value_str[1:-1]
            else:
                return value_str
    
    def _is_numeric(self, value: Any) -> bool:
        """检查是否是数值"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _apply_having(self, data: List[Dict[str, Any]], having: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """应用Having条件"""
        return self._apply_filters(data, having)
    
    def _apply_sorting(self, data: List[Dict[str, Any]], order_by: List[Union[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """应用排序"""
        if not order_by:
            return data
        
        def sort_key(row):
            sort_values = []
            for order_config in order_by:
                if isinstance(order_config, str):
                    field = order_config
                    direction = "ASC"
                elif isinstance(order_config, dict):
                    field = order_config.get("field")
                    direction = order_config.get("direction", "ASC")
                else:
                    continue
                
                value = row.get(field, "")
                # 处理降序
                if direction.upper() == "DESC":
                    if isinstance(value, (int, float)):
                        value = -value
                    elif isinstance(value, str):
                        # 对于字符串，使用负序排序会比较复杂，这里简化处理
                        pass
                
                sort_values.append(value)
            
            return sort_values
        
        try:
            return sorted(data, key=sort_key)
        except Exception as e:
            self.log_warning(f"排序失败: {e}")
            return data
    
    def _apply_limit_offset(self, data: List[Dict[str, Any]], limit: Optional[int], offset: Optional[int]) -> List[Dict[str, Any]]:
        """应用限制和偏移"""
        start_index = offset or 0
        end_index = start_index + limit if limit else len(data)
        
        return data[start_index:end_index]

    def _add_calculated_fields(self, data: List[Dict[str, Any]], calculated_fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        添加计算字段
        
        Args:
            data: 源数据
            calculated_fields: 计算字段配置列表
            
        Returns:
            添加了计算字段的数据
        """
        if not calculated_fields or not data:
            return data
        
        result = []
        for row in data:
            new_row = row.copy()
            
            # 处理每个计算字段
            for calc_field in calculated_fields:
                alias = calc_field.get("alias")
                expression = calc_field.get("expression")
                
                if not alias or not expression:
                    self.log_warning("计算字段配置不完整，跳过", config=calc_field)
                    continue
                
                try:
                    # 计算表达式值
                    calculated_value = self._evaluate_calculated_expression(expression, row, data)
                    new_row[alias] = calculated_value
                except Exception as e:
                    self.log_warning(f"计算字段 {alias} 计算失败: {e}")
                    new_row[alias] = None
            
            result.append(new_row)
        
        return result

    def _evaluate_calculated_expression(self, expression: str, current_row: Dict[str, Any], all_data: List[Dict[str, Any]]) -> Any:
        """
        计算表达式值，支持窗口函数
        
        Args:
            expression: 表达式
            current_row: 当前行数据
            all_data: 所有数据（用于窗口函数）
            
        Returns:
            计算结果
        """
        import re
        
        # 检查是否是窗口函数
        if "ROW_NUMBER()" in expression and "OVER" in expression:
            return self._evaluate_window_function(expression, current_row, all_data)
        elif "RANK()" in expression and "OVER" in expression:
            return self._evaluate_window_function(expression, current_row, all_data)
        else:
            # 普通表达式计算
            return self._evaluate_expression(expression, current_row)

    def _evaluate_window_function(self, expression: str, current_row: Dict[str, Any], all_data: List[Dict[str, Any]]) -> Any:
        """
        计算窗口函数
        
        Args:
            expression: 窗口函数表达式
            current_row: 当前行
            all_data: 所有数据
            
        Returns:
            窗口函数结果
        """
        import re
        
        # 解析窗口函数表达式
        # 例如: ROW_NUMBER() OVER (PARTITION BY country ORDER BY total_sales_amount DESC)
        window_pattern = r'(ROW_NUMBER|RANK|DENSE_RANK)\(\)\s+OVER\s*\(\s*(.*?)\s*\)'
        match = re.search(window_pattern, expression, re.IGNORECASE)
        
        if not match:
            self.log_warning(f"无法解析窗口函数表达式: {expression}")
            return None
        
        function_name = match.group(1).upper()
        over_clause = match.group(2)
        
        # 解析 PARTITION BY 和 ORDER BY
        partition_by = []
        order_by = []
        
        # 解析 PARTITION BY - 使用正确的正则表达式
        partition_pattern = r'PARTITION\s+BY\s+(.+?)\s+ORDER\s+BY'
        partition_match = re.search(partition_pattern, over_clause, re.IGNORECASE)
        if partition_match:
            partition_by = [field.strip() for field in partition_match.group(1).split(',')]
        

        
        # 解析 ORDER BY - 修复正则表达式
        order_pattern = r'ORDER\s+BY\s+(.+?)$'
        order_match = re.search(order_pattern, over_clause, re.IGNORECASE)
        if order_match:
            order_clause = order_match.group(1)
            # 解析排序字段和方向
            order_parts = order_clause.split(',')
            for part in order_parts:
                part = part.strip()
                if ' DESC' in part.upper():
                    field = part.replace(' DESC', '').replace(' desc', '').strip()
                    order_by.append((field, 'DESC'))
                elif ' ASC' in part.upper():
                    field = part.replace(' ASC', '').replace(' asc', '').strip()
                    order_by.append((field, 'ASC'))
                else:
                    order_by.append((part, 'ASC'))
        
        # 如果有分区，先按分区分组
        if partition_by:
            # 找到当前行所属的分区
            partition_key = tuple(current_row.get(field, None) for field in partition_by)
            partition_data = [row for row in all_data 
                            if tuple(row.get(field, None) for field in partition_by) == partition_key]
        else:
            partition_data = all_data
        
        # 按 ORDER BY 排序分区数据
        if order_by:
            try:
                # 简化排序逻辑：分别处理每个字段的排序方向
                from operator import itemgetter
                
                # 为了支持多字段混合排序，我们需要逐个字段进行排序
                sorted_partition = list(partition_data)
                
                # 反向处理order_by，确保最重要的排序字段最后处理
                for field, direction in reversed(order_by):
                    def get_sort_value(row):
                        value = row.get(field)
                        
                        # 处理 None 值
                        if value is None:
                            # None值统一处理为特殊值
                            return float('-inf') if direction == 'DESC' else float('inf')
                        
                        # 处理数值转换
                        if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                            value = float(value)
                        
                        return value
                    
                    # 按方向排序
                    reverse_sort = (direction == 'DESC')
                    sorted_partition = sorted(sorted_partition, key=get_sort_value, reverse=reverse_sort)
                
            except Exception as e:
                self.log_warning(f"窗口函数排序失败: {e}")
                sorted_partition = partition_data
        else:
            sorted_partition = partition_data
        
        # 计算窗口函数结果
        try:
            # 找到当前行在排序后数据中的位置
            current_row_index = None
            for i, row in enumerate(sorted_partition):
                # 通过比较所有字段值来确定是否是同一行
                if all(str(row.get(k, '')) == str(current_row.get(k, '')) for k in current_row.keys()):
                    current_row_index = i
                    break
            
            if current_row_index is None:
                self.log_warning("在分区数据中找不到当前行")
                return None
            
            if function_name == 'ROW_NUMBER':
                return current_row_index + 1
            elif function_name == 'RANK':
                # 计算并列排名
                rank = 1
                if current_row_index > 0:
                    # 检查前面有多少个不同的值
                    current_values = [current_row.get(field, 0) for field, _ in order_by]
                    for i in range(current_row_index):
                        prev_values = [sorted_partition[i].get(field, 0) for field, _ in order_by]
                        if prev_values != current_values:
                            rank = i + 2
                            break
                return rank
            elif function_name == 'DENSE_RANK':
                # 密集排名实现
                if current_row_index == 0:
                    return 1
                # 简化实现，与 RANK 相同
                return current_row_index + 1
            else:
                return current_row_index + 1
                
        except Exception as e:
            self.log_warning(f"窗口函数计算失败: {e}")
            return None
    
    def _resolve_field_name(self, field_name: str, main_table: str, has_joins: bool) -> str:
        """
        解决字段名歧义问题
        
        Args:
            field_name: 字段名
            main_table: 主表名
            has_joins: 是否有JOIN
            
        Returns:
            解决歧义后的字段名
        """
        # 如果没有JOIN，直接返回原字段名
        if not has_joins:
            return field_name
        
        # 如果字段名已经包含表前缀，直接返回
        if "." in field_name:
            return field_name
        
        # 为字段名添加主表前缀
        return f"{main_table}.{field_name}"
    
    def _process_step_data_with_joins(self, main_data: List[Dict[str, Any]], joins: List[Dict[str, Any]], get_source_data) -> List[Dict[str, Any]]:
        """
        处理带JOIN的步骤数据
        
        Args:
            main_data: 主表数据
            joins: JOIN配置
            get_source_data: 获取源数据的函数
            
        Returns:
            JOIN后的数据
        """
        result_data = main_data
        
        # 处理每个JOIN
        for join_config in joins:
            join_type = join_config.get("type", "INNER").upper()
            join_table = join_config.get("table", "")
            join_condition = join_config.get("on", "")
            
            # 解析JOIN表名和别名
            join_table_parts = join_table.split()
            if len(join_table_parts) >= 2:
                join_step_name = join_table_parts[0]
                join_alias = join_table_parts[1]
            else:
                join_step_name = join_table
                join_alias = join_table
            
            # 获取JOIN表数据
            join_data = get_source_data(join_step_name)
            
            # 执行JOIN操作
            result_data = self._perform_step_data_join(result_data, join_data, join_condition, join_type, join_alias)
        
        # 处理其他配置（维度、指标、过滤等）
        return self._process_step_data(result_data)

    def _perform_step_data_join(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]], 
                               join_condition: str, join_type: str, right_alias: str = None) -> List[Dict[str, Any]]:
        """
        执行步骤数据的JOIN操作
        
        Args:
            left_data: 左表数据
            right_data: 右表数据
            join_condition: JOIN条件，如 "coc.customer_id = cfod.customer_id"
            join_type: JOIN类型
            right_alias: 右表别名
            
        Returns:
            JOIN后的数据
        """
        import re
        
        # 解析JOIN条件
        # 例如: "coc.customer_id = cfod.customer_id"
        condition_match = re.match(r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', join_condition.strip())
        if not condition_match:
            self.log_warning(f"无法解析JOIN条件: {join_condition}")
            return left_data
        
        left_alias, left_field = condition_match.group(1), condition_match.group(2)
        right_alias_from_condition, right_field = condition_match.group(3), condition_match.group(4)
        
        result = []
        
        if join_type == "INNER":
            # INNER JOIN
            for left_row in left_data:
                left_value = left_row.get(left_field)
                
                for right_row in right_data:
                    right_value = right_row.get(right_field)
                    
                    if left_value == right_value:
                        # 合并行数据
                        merged_row = {}
                        
                        # 添加左表数据（带别名前缀）
                        for key, value in left_row.items():
                            merged_row[f"{left_alias}.{key}"] = value
                            # 同时保留无前缀的字段名以保持兼容性
                            if key not in merged_row:
                                merged_row[key] = value
                        
                        # 添加右表数据（带别名前缀）
                        for key, value in right_row.items():
                            prefixed_key = f"{right_alias_from_condition}.{key}"
                            merged_row[prefixed_key] = value
                            # 如果左表没有同名字段，也添加无前缀版本
                            if key not in left_row:
                                merged_row[key] = value
                        
                        result.append(merged_row)
                        
        elif join_type == "LEFT":
            # LEFT JOIN
            for left_row in left_data:
                left_value = left_row.get(left_field)
                joined = False
                
                for right_row in right_data:
                    right_value = right_row.get(right_field)
                    
                    if left_value == right_value:
                        # 合并行数据
                        merged_row = {}
                        
                        # 添加左表数据
                        for key, value in left_row.items():
                            merged_row[f"{left_alias}.{key}"] = value
                            if key not in merged_row:
                                merged_row[key] = value
                        
                        # 添加右表数据
                        for key, value in right_row.items():
                            prefixed_key = f"{right_alias_from_condition}.{key}"
                            merged_row[prefixed_key] = value
                            if key not in left_row:
                                merged_row[key] = value
                        
                        result.append(merged_row)
                        joined = True
                
                # 如果没有匹配的右表记录，添加左表记录（右表字段为None）
                if not joined:
                    merged_row = {}
                    for key, value in left_row.items():
                        merged_row[f"{left_alias}.{key}"] = value
                        merged_row[key] = value
                    result.append(merged_row)
        
        return result
