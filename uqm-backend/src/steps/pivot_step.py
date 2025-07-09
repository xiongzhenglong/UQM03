"""
数据透视步骤实现
将数据从长格式转换为宽格式
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
import numpy as np

from src.steps.base import BaseStep
from src.utils.exceptions import ValidationError, ExecutionError


class PivotStep(BaseStep):
    """透视步骤执行器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化透视步骤
        
        Args:
            config: 透视步骤配置
        """
        # 先初始化支持的聚合函数，在调用 super().__init__ 之前
        # 因为 BaseStep.__init__ 会调用 validate()，而 validate() 需要访问 supported_agg_functions
        self.supported_agg_functions = {
            'sum': 'sum',
            'mean': 'mean',
            'avg': 'mean',
            'count': 'count',
            'min': 'min',
            'max': 'max',
            'std': 'std',
            'var': 'var',
            'first': 'first',
            'last': 'last'
        }
        
        # 然后调用父类初始化
        super().__init__(config)
    
    def validate(self) -> None:
        """验证透视步骤配置"""
        required_fields = ["source", "index", "columns", "values"]
        self._validate_required_config(required_fields)
        
        # 验证source字段
        source = self.config.get("source")
        if not isinstance(source, str):
            raise ValidationError("source必须是字符串")
        
        # 验证index字段
        index = self.config.get("index")
        if not isinstance(index, (str, list)):
            raise ValidationError("index必须是字符串或数组")
        
        # 验证columns字段
        columns = self.config.get("columns")
        if not isinstance(columns, (str, list)):
            raise ValidationError("columns必须是字符串或数组")
        
        # 验证values字段
        values = self.config.get("values")
        if not isinstance(values, (str, list)):
            raise ValidationError("values必须是字符串或数组")
        
        # 验证聚合函数
        agg_func = self.config.get("agg_func", "sum")
        if isinstance(agg_func, str):
            if agg_func.lower() not in self.supported_agg_functions:
                raise ValidationError(f"不支持的聚合函数: {agg_func}")
        elif isinstance(agg_func, dict):
            for func in agg_func.values():
                if func.lower() not in self.supported_agg_functions:
                    raise ValidationError(f"不支持的聚合函数: {func}")
    
    async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        执行透视步骤
        
        Args:
            context: 执行上下文
            
        Returns:
            透视后的数据
        """
        try:
            # 获取源数据
            source_name = self.config["source"]
            source_data = context["get_source_data"](source_name)
            
            if not source_data:
                self.log_warning("源数据为空")
                return []
            
            # 执行数据透视
            pivoted_data = self._perform_pivot(source_data)
            
            return pivoted_data
            
        except Exception as e:
            self.log_error("透视步骤执行失败", error=str(e))
            raise ExecutionError(f"透视执行失败: {e}")
    
    def _perform_pivot(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        执行数据透视
        
        Args:
            source_data: 源数据
            
        Returns:
            透视后的数据
        """
        try:
            # 转换为DataFrame
            df = pd.DataFrame(source_data)
            
            # 获取透视参数
            index = self.config["index"]
            columns = self.config["columns"]
            values = self.config["values"]
            agg_func = self.config.get("agg_func", "sum")
            fill_value = self.config.get("fill_value", 0)
            
            # 验证透视列是否存在
            self._validate_pivot_columns(df, index, columns, values)
            
            # 准备透视数据
            df_clean = self._prepare_pivot_data(df, index, columns, values)
            
            # 执行透视
            if isinstance(agg_func, str):
                # 单一聚合函数
                agg_function = self.supported_agg_functions[agg_func.lower()]
                pivot_df = df_clean.pivot_table(
                    index=index,
                    columns=columns,
                    values=values,
                    aggfunc=agg_function,
                    fill_value=fill_value
                )
            else:
                # 多个聚合函数
                # 创建聚合函数字典，将输出列名映射到聚合函数
                agg_functions = {}
                for output_name, func_name in agg_func.items():
                    agg_functions[output_name] = self.supported_agg_functions[func_name.lower()]
                
                # 对于多聚合函数，我们需要对每个聚合函数分别调用pivot_table，然后合并结果
                pivot_dfs = []
                
                for output_name, func in agg_functions.items():
                    temp_pivot = df_clean.pivot_table(
                        index=index,
                        columns=columns,
                        values=values,
                        aggfunc=func,
                        fill_value=fill_value
                    )
                    
                    # 为列名添加聚合函数前缀
                    if isinstance(temp_pivot.columns, pd.MultiIndex):
                        # 多级列名，在最后一级添加前缀
                        new_columns = []
                        for col in temp_pivot.columns:
                            if isinstance(col, tuple):
                                col_list = list(col)
                                col_list[-1] = f"{output_name}_{col_list[-1]}"
                                new_columns.append(tuple(col_list))
                            else:
                                new_columns.append(f"{output_name}_{col}")
                        temp_pivot.columns = pd.MultiIndex.from_tuples(new_columns)
                    else:
                        # 单级列名
                        temp_pivot.columns = [f"{output_name}_{col}" for col in temp_pivot.columns]
                    
                    pivot_dfs.append(temp_pivot)
                
                # 合并所有透视结果
                pivot_df = pd.concat(pivot_dfs, axis=1)
            
            # 处理多级列名
            pivot_df = self._flatten_column_names(pivot_df)
            
            # 重置索引
            pivot_df = pivot_df.reset_index()
            
            # 格式化透视结果（处理column_prefix等）
            pivot_df = self._format_pivot_result(pivot_df)
            
            # 转换回字典列表
            result = pivot_df.to_dict('records')
            
            self.log_info(
                "透视操作完成",
                original_rows=len(df),
                pivoted_rows=len(result),
                pivoted_columns=len(pivot_df.columns)
            )
            
            return result
            
        except Exception as e:
            self.log_error("执行透视操作失败", error=str(e))
            raise ExecutionError(f"透视操作失败: {e}")
    
    def _validate_pivot_columns(self, df: pd.DataFrame, 
                               index: Union[str, List[str]],
                               columns: Union[str, List[str]],
                               values: Union[str, List[str]]) -> None:
        """
        验证透视列是否存在
        
        Args:
            df: 数据DataFrame
            index: 索引列
            columns: 透视列
            values: 值列
        """
        # 收集所有需要的列
        required_columns = []
        
        if isinstance(index, str):
            required_columns.append(index)
        else:
            required_columns.extend(index)
        
        if isinstance(columns, str):
            required_columns.append(columns)
        else:
            required_columns.extend(columns)
        
        if isinstance(values, str):
            required_columns.append(values)
        else:
            required_columns.extend(values)
        
        # 验证列是否存在
        missing_columns = []
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            raise ValidationError(f"数据中缺少以下列: {missing_columns}")
    
    def _prepare_pivot_data(self, df: pd.DataFrame,
                           index: Union[str, List[str]],
                           columns: Union[str, List[str]],
                           values: Union[str, List[str]]) -> pd.DataFrame:
        """
        准备透视数据
        
        Args:
            df: 原始DataFrame
            index: 索引列
            columns: 透视列
            values: 值列
            
        Returns:
            准备好的DataFrame
        """
        # 选择需要的列
        required_columns = []
        
        if isinstance(index, str):
            required_columns.append(index)
        else:
            required_columns.extend(index)
        
        if isinstance(columns, str):
            required_columns.append(columns)
        else:
            required_columns.extend(columns)
        
        if isinstance(values, str):
            required_columns.append(values)
        else:
            required_columns.extend(values)
        
        # 去重列名
        required_columns = list(set(required_columns))
        
        # 选择列
        df_clean = df[required_columns].copy()
        
        # 处理缺失值
        missing_strategy = self.config.get("missing_strategy", "drop")
        if missing_strategy == "drop":
            df_clean = df_clean.dropna()
        elif missing_strategy == "fill":
            fill_value = self.config.get("missing_fill_value", 0)
            df_clean = df_clean.fillna(fill_value)
        
        # 处理数据类型
        if isinstance(values, str):
            value_columns = [values]
        else:
            value_columns = values
        
        for col in value_columns:
            if col in df_clean.columns:
                # 尝试转换为数值类型
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        return df_clean
    
    def _flatten_column_names(self, pivot_df: pd.DataFrame) -> pd.DataFrame:
        """
        展平多级列名
        
        Args:
            pivot_df: 透视后的DataFrame
            
        Returns:
            列名展平后的DataFrame
        """
        if isinstance(pivot_df.columns, pd.MultiIndex):
            # 处理多级列名
            new_columns = []
            for col in pivot_df.columns:
                if isinstance(col, tuple):
                    # 组合列名，过滤空字符串
                    col_parts = [str(c) for c in col if str(c) != ""]
                    col_name = "_".join(col_parts)
                    new_columns.append(col_name)
                else:
                    new_columns.append(str(col))
            
            pivot_df.columns = new_columns
        
        return pivot_df
    
    def _handle_null_values(self, pivot_df: pd.DataFrame) -> pd.DataFrame:
        """
        处理透视后的空值
        
        Args:
            pivot_df: 透视后的DataFrame
            
        Returns:
            处理空值后的DataFrame
        """
        null_strategy = self.config.get("null_strategy", "keep")
        
        if null_strategy == "drop":
            # 删除包含空值的行
            pivot_df = pivot_df.dropna()
        elif null_strategy == "fill":
            # 用指定值填充空值
            fill_value = self.config.get("null_fill_value", 0)
            pivot_df = pivot_df.fillna(fill_value)
        elif null_strategy == "zero":
            # 用0填充空值
            pivot_df = pivot_df.fillna(0)
        # "keep"策略：保持空值不变
        
        return pivot_df
    
    def _format_pivot_result(self, pivot_df: pd.DataFrame) -> pd.DataFrame:
        """
        格式化透视结果
        
        Args:
            pivot_df: 透视后的DataFrame
            
        Returns:
            格式化后的DataFrame
        """
        # 处理列名
        column_prefix = self.config.get("column_prefix", "")
        column_suffix = self.config.get("column_suffix", "")
        
        if column_prefix or column_suffix:
            new_columns = {}
            index_cols = self.config.get("index", [])
            if isinstance(index_cols, str):
                index_cols = [index_cols]
            
            for col in pivot_df.columns:
                if col not in index_cols:
                    new_col = f"{column_prefix}{col}{column_suffix}"
                    new_columns[col] = new_col
            
            if new_columns:
                pivot_df = pivot_df.rename(columns=new_columns)
        
        # 排序
        sort_by = self.config.get("sort_by")
        if sort_by:
            if isinstance(sort_by, str):
                sort_columns = [sort_by]
            else:
                sort_columns = sort_by
            
            # 验证排序列是否存在
            valid_sort_columns = [col for col in sort_columns if col in pivot_df.columns]
            if valid_sort_columns:
                sort_ascending = self.config.get("sort_ascending", True)
                pivot_df = pivot_df.sort_values(valid_sort_columns, ascending=sort_ascending)
        
        return pivot_df
