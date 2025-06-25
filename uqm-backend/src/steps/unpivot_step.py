"""
数据逆透视步骤实现
将数据从宽格式转换为长格式
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd

from src.steps.base import BaseStep
from src.utils.exceptions import ValidationError, ExecutionError


class UnpivotStep(BaseStep):
    """逆透视步骤执行器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化逆透视步骤"""
        super().__init__(config)
    
    def validate(self) -> None:
        """验证逆透视步骤配置"""
        required_fields = ["source", "id_vars", "value_vars"]
        self._validate_required_config(required_fields)
    
    async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行逆透视步骤"""
        try:
            # 获取源数据
            source_name = self.config["source"]
            source_data = context["get_source_data"](source_name)
            
            if not source_data:
                return []
            
            # 执行逆透视
            result = self._perform_unpivot(source_data)
            return result
            
        except Exception as e:
            self.log_error("逆透视步骤执行失败", error=str(e))
            raise ExecutionError(f"逆透视执行失败: {e}")
    
    def _perform_unpivot(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """执行逆透视操作"""
        df = pd.DataFrame(source_data)
        
        id_vars = self.config["id_vars"]
        value_vars = self.config["value_vars"]
        var_name = self.config.get("var_name", "variable")
        value_name = self.config.get("value_name", "value")
        
        # 执行melt操作
        melted_df = df.melt(
            id_vars=id_vars,
            value_vars=value_vars,
            var_name=var_name,
            value_name=value_name
        )
        
        return melted_df.to_dict('records')


class UnionStep(BaseStep):
    """合并步骤执行器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化合并步骤"""
        super().__init__(config)
    
    def validate(self) -> None:
        """验证合并步骤配置"""
        required_fields = ["sources"]
        self._validate_required_config(required_fields)
    
    async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行合并步骤"""
        try:
            sources = self.config["sources"]
            source_datasets = context["get_source_data"](sources)
            
            # 执行数据合并
            result = self._perform_union(source_datasets)
            return result
            
        except Exception as e:
            self.log_error("合并步骤执行失败", error=str(e))
            raise ExecutionError(f"合并执行失败: {e}")
    
    def _perform_union(self, source_datasets: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """执行数据合并"""
        all_data = []
        
        for source_name, data in source_datasets.items():
            # 为每条记录添加来源标识
            if self.config.get("add_source_column", False):
                source_column = self.config.get("source_column", "source")
                for record in data:
                    record[source_column] = source_name
            
            all_data.extend(data)
        
        # 处理重复数据
        if self.config.get("remove_duplicates", False):
            # 简单去重（转换为字符串比较）
            seen = set()
            unique_data = []
            for record in all_data:
                record_str = str(sorted(record.items()))
                if record_str not in seen:
                    seen.add(record_str)
                    unique_data.append(record)
            return unique_data
        
        return all_data


class AssertStep(BaseStep):
    """断言步骤执行器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化断言步骤"""
        super().__init__(config)
    
    def validate(self) -> None:
        """验证断言步骤配置"""
        required_fields = ["source", "assertions"]
        self._validate_required_config(required_fields)
    
    async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行断言步骤"""
        try:
            # 获取源数据
            source_name = self.config["source"]
            source_data = context["get_source_data"](source_name)
            
            # 执行断言检查
            self._perform_assertions(source_data)
            
            # 断言通过，返回原始数据
            return source_data
            
        except Exception as e:
            self.log_error("断言步骤执行失败", error=str(e))
            raise ExecutionError(f"断言执行失败: {e}")
    
    def _perform_assertions(self, source_data: List[Dict[str, Any]]) -> None:
        """执行断言检查"""
        assertions = self.config["assertions"]
        
        for assertion in assertions:
            assertion_type = assertion.get("type")
            
            if assertion_type == "row_count":
                self._assert_row_count(source_data, assertion)
            elif assertion_type == "not_null":
                self._assert_not_null(source_data, assertion)
            elif assertion_type == "unique":
                self._assert_unique(source_data, assertion)
            elif assertion_type == "range":
                self._assert_range(source_data, assertion)
            else:
                self.log_warning(f"未知的断言类型: {assertion_type}")
    
    def _assert_row_count(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> None:
        """断言行数"""
        expected_count = assertion.get("expected")
        min_count = assertion.get("min")
        max_count = assertion.get("max")
        
        actual_count = len(data)
        
        if expected_count is not None and actual_count != expected_count:
            raise ExecutionError(f"行数断言失败: 期望{expected_count}，实际{actual_count}")
        
        if min_count is not None and actual_count < min_count:
            raise ExecutionError(f"最小行数断言失败: 期望至少{min_count}，实际{actual_count}")
        
        if max_count is not None and actual_count > max_count:
            raise ExecutionError(f"最大行数断言失败: 期望最多{max_count}，实际{actual_count}")
    
    def _assert_not_null(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> None:
        """断言非空"""
        columns = assertion.get("columns", [])
        
        for record in data:
            for column in columns:
                if column in record and (record[column] is None or record[column] == ""):
                    raise ExecutionError(f"非空断言失败: 列 {column} 包含空值")
    
    def _assert_unique(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> None:
        """断言唯一性"""
        columns = assertion.get("columns", [])
        
        seen_values = set()
        for record in data:
            key_values = tuple(record.get(col) for col in columns)
            if key_values in seen_values:
                raise ExecutionError(f"唯一性断言失败: 列 {columns} 存在重复值")
            seen_values.add(key_values)
    
    def _assert_range(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> None:
        """断言值范围"""
        column = assertion.get("column")
        min_value = assertion.get("min")
        max_value = assertion.get("max")
        
        for record in data:
            if column in record:
                value = record[column]
                if isinstance(value, (int, float)):
                    if min_value is not None and value < min_value:
                        raise ExecutionError(f"范围断言失败: 列 {column} 值 {value} 小于最小值 {min_value}")
                    if max_value is not None and value > max_value:
                        raise ExecutionError(f"范围断言失败: 列 {column} 值 {value} 大于最大值 {max_value}")
