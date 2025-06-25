"""
数据丰富化步骤实现
通过查找表来丰富源数据
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd

from src.steps.base import BaseStep
from src.utils.exceptions import ValidationError, ExecutionError


class EnrichStep(BaseStep):
    """丰富化步骤执行器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化丰富化步骤
        
        Args:
            config: 丰富化步骤配置
        """
        super().__init__(config)
    
    def validate(self) -> None:
        """验证丰富化步骤配置"""
        required_fields = ["source", "lookup", "on"]
        self._validate_required_config(required_fields)
        
        # 验证source字段
        source = self.config.get("source")
        if not isinstance(source, str):
            raise ValidationError("source必须是字符串")
        
        # 验证lookup字段
        lookup = self.config.get("lookup")
        if not isinstance(lookup, (str, dict)):
            raise ValidationError("lookup必须是字符串或对象")
        
        # 验证on字段
        on = self.config.get("on")
        if not isinstance(on, (str, dict, list)):
            raise ValidationError("on必须是字符串、对象或数组")
    
    async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        执行丰富化步骤
        
        Args:
            context: 执行上下文
            
        Returns:
            丰富化后的数据
        """
        try:
            # 获取源数据
            source_name = self.config["source"]
            source_data = context["get_source_data"](source_name)
            
            # 获取查找表数据
            lookup_data = await self._fetch_lookup_data(context)
            
            # 执行数据丰富化
            enriched_data = self._perform_enrichment(source_data, lookup_data)
            
            return enriched_data
            
        except Exception as e:
            self.log_error("丰富化步骤执行失败", error=str(e))
            raise ExecutionError(f"丰富化执行失败: {e}")
    
    async def _fetch_lookup_data(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        获取查找表数据
        
        Args:
            context: 执行上下文
            
        Returns:
            查找表数据
        """
        lookup_config = self.config["lookup"]
        
        if isinstance(lookup_config, str):
            # 从其他步骤获取数据
            return context["get_source_data"](lookup_config)
        
        elif isinstance(lookup_config, dict):
            # 从数据库表获取数据
            table_name = lookup_config.get("table")
            if not table_name:
                raise ValidationError("lookup配置中缺少table字段")
            
            # 构建查询
            columns = lookup_config.get("columns", ["*"])
            where_conditions = lookup_config.get("where", [])
            
            # 使用SQL构建器构建查询
            from src.utils.sql_builder import SQLBuilder
            sql_builder = SQLBuilder()
            
            query = sql_builder.build_select_query(
                select_fields=columns,
                from_table=table_name,
                where_conditions=where_conditions
            )
            
            # 执行查询
            connector_manager = context["connector_manager"]
            connector = await connector_manager.get_default_connector()
            
            return await connector.execute_query(query)
        
        else:
            raise ValidationError("无效的lookup配置")
    
    def _perform_enrichment(self, source_data: List[Dict[str, Any]], 
                           lookup_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        执行数据丰富化
        
        Args:
            source_data: 源数据
            lookup_data: 查找表数据
            
        Returns:
            丰富化后的数据
        """
        try:
            if not source_data:
                return []
            
            if not lookup_data:
                self.log_warning("查找表数据为空，返回原始数据")
                return source_data
            
            # 转换为DataFrame进行处理
            source_df = pd.DataFrame(source_data)
            lookup_df = pd.DataFrame(lookup_data)
            
            # 解析连接条件
            join_config = self._parse_join_config()
            
            # 执行连接
            result_df = self._perform_join(source_df, lookup_df, join_config)
            
            # 转换回字典列表
            return result_df.to_dict('records')
            
        except Exception as e:
            self.log_error("执行数据丰富化失败", error=str(e))
            raise ExecutionError(f"数据丰富化失败: {e}")
    
    def _parse_join_config(self) -> Dict[str, Any]:
        """
        解析连接配置
        
        Returns:
            连接配置字典
        """
        on_config = self.config["on"]
        join_type = self.config.get("join_type", "left")
        
        if isinstance(on_config, str):
            # 简单字段连接
            return {
                "type": join_type,
                "left_on": on_config,
                "right_on": on_config
            }
        
        elif isinstance(on_config, dict):
            # 复杂连接配置
            return {
                "type": join_type,
                "left_on": on_config.get("left"),
                "right_on": on_config.get("right"),
                "condition": on_config.get("condition")
            }
        
        elif isinstance(on_config, list):
            # 多字段连接
            return {
                "type": join_type,
                "left_on": on_config,
                "right_on": on_config
            }
        
        else:
            raise ValidationError("无效的连接配置")
    
    def _perform_join(self, source_df: pd.DataFrame, 
                     lookup_df: pd.DataFrame,
                     join_config: Dict[str, Any]) -> pd.DataFrame:
        """
        执行DataFrame连接
        
        Args:
            source_df: 源数据DataFrame
            lookup_df: 查找表DataFrame
            join_config: 连接配置
            
        Returns:
            连接后的DataFrame
        """
        join_type = join_config["type"]
        left_on = join_config["left_on"]
        right_on = join_config["right_on"]
        
        # 验证连接键是否存在
        self._validate_join_keys(source_df, lookup_df, left_on, right_on)
        
        # 根据连接类型执行连接
        if join_type.lower() == "left":
            how = "left"
        elif join_type.lower() == "right":
            how = "right"
        elif join_type.lower() == "inner":
            how = "inner"
        elif join_type.lower() == "outer":
            how = "outer"
        else:
            how = "left"  # 默认左连接
        
        # 执行连接
        result_df = source_df.merge(
            lookup_df,
            left_on=left_on,
            right_on=right_on,
            how=how,
            suffixes=('', '_lookup')
        )
        
        # 处理列名冲突
        result_df = self._handle_column_conflicts(result_df)
        
        return result_df
    
    def _validate_join_keys(self, source_df: pd.DataFrame, 
                           lookup_df: pd.DataFrame,
                           left_on: Union[str, List[str]],
                           right_on: Union[str, List[str]]) -> None:
        """
        验证连接键是否存在
        
        Args:
            source_df: 源数据DataFrame
            lookup_df: 查找表DataFrame
            left_on: 左连接键
            right_on: 右连接键
        """
        # 验证左连接键
        if isinstance(left_on, str):
            left_keys = [left_on]
        else:
            left_keys = left_on
        
        for key in left_keys:
            if key not in source_df.columns:
                raise ValidationError(f"源数据中不存在连接键: {key}")
        
        # 验证右连接键
        if isinstance(right_on, str):
            right_keys = [right_on]
        else:
            right_keys = right_on
        
        for key in right_keys:
            if key not in lookup_df.columns:
                raise ValidationError(f"查找表中不存在连接键: {key}")
    
    def _handle_column_conflicts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理列名冲突
        
        Args:
            df: 原始DataFrame
            
        Returns:
            处理后的DataFrame
        """
        # 获取需要重命名的列
        columns_to_rename = {}
        for col in df.columns:
            if col.endswith('_lookup'):
                original_name = col[:-7]  # 移除'_lookup'后缀
                new_name = self._get_unique_column_name(df, original_name)
                columns_to_rename[col] = new_name
        
        # 重命名列
        if columns_to_rename:
            df = df.rename(columns=columns_to_rename)
        
        return df
    
    def _get_unique_column_name(self, df: pd.DataFrame, base_name: str) -> str:
        """
        获取唯一的列名
        
        Args:
            df: DataFrame
            base_name: 基础名称
            
        Returns:
            唯一的列名
        """
        if base_name not in df.columns:
            return base_name
        
        counter = 1
        while True:
            new_name = f"{base_name}_{counter}"
            if new_name not in df.columns:
                return new_name
            counter += 1
    
    def _optimize_lookup_strategy(self, source_size: int, lookup_size: int) -> str:
        """
        优化查找策略
        
        Args:
            source_size: 源数据大小
            lookup_size: 查找表大小
            
        Returns:
            优化策略
        """
        # 根据数据大小选择不同的策略
        if source_size < 1000 and lookup_size < 1000:
            return "memory_join"
        elif lookup_size < 10000:
            return "hash_join"
        else:
            return "merge_join"
    
    def _handle_missing_keys(self, result_df: pd.DataFrame) -> pd.DataFrame:
        """
        处理缺失键值
        
        Args:
            result_df: 结果DataFrame
            
        Returns:
            处理后的DataFrame
        """
        missing_strategy = self.config.get("missing_strategy", "keep")
        
        if missing_strategy == "drop":
            # 删除包含缺失值的行
            result_df = result_df.dropna()
        elif missing_strategy == "fill":
            # 用默认值填充缺失值
            fill_value = self.config.get("fill_value", "")
            result_df = result_df.fillna(fill_value)
        # "keep"策略：保持缺失值不变
        
        return result_df
