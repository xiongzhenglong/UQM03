"""
集合合并步骤实现
负责合并多个数据集
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd

from src.steps.base import BaseStep
from src.utils.exceptions import ValidationError, ExecutionError


class UnionStep(BaseStep):
    """合并步骤执行器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化合并步骤
        
        Args:
            config: 合并步骤配置
        """
        super().__init__(config)
    
    def validate(self) -> None:
        """验证合并步骤配置"""
        required_fields = ["sources"]
        self._validate_required_config(required_fields)
        
        # 验证sources字段
        sources = self.config.get("sources")
        if not isinstance(sources, list) or len(sources) < 2:
            raise ValidationError("sources必须是包含至少2个元素的数组")
        
        # 验证模式
        mode = self.config.get("mode", "union")
        if mode not in ["union", "union_all", "intersect", "except"]:
            raise ValidationError("mode必须是union、union_all、intersect或except之一")
    
    async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        执行合并步骤
        
        Args:
            context: 执行上下文
            
        Returns:
            合并后的数据
        """
        try:
            # 获取源数据
            sources = self.config["sources"]
            source_datasets = context["get_source_data"](sources)
            
            # 执行数据合并
            result = self._perform_union(source_datasets)
            
            return result
            
        except Exception as e:
            self.log_error("合并步骤执行失败", error=str(e))
            raise ExecutionError(f"合并执行失败: {e}")
    
    def _perform_union(self, source_datasets: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        执行数据合并
        
        Args:
            source_datasets: 源数据集字典
            
        Returns:
            合并后的数据
        """
        try:
            mode = self.config.get("mode", "union")
            
            if mode == "union":
                return self._union_distinct(source_datasets)
            elif mode == "union_all":
                return self._union_all(source_datasets)
            elif mode == "intersect":
                return self._intersect(source_datasets)
            elif mode == "except":
                return self._except(source_datasets)
            else:
                raise ValidationError(f"不支持的合并模式: {mode}")
                
        except Exception as e:
            self.log_error("执行数据合并失败", error=str(e))
            raise ExecutionError(f"数据合并失败: {e}")
    
    def _union_all(self, source_datasets: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """执行UNION ALL操作（保留重复）"""
        all_data = []
        
        # 验证并对齐列结构
        aligned_datasets = self._align_columns(source_datasets)
        
        for source_name, data in aligned_datasets.items():
            # 为每条记录添加来源标识（如果配置了）
            if self.config.get("add_source_column", False):
                source_column = self.config.get("source_column", "_source")
                for record in data:
                    record[source_column] = source_name
            
            all_data.extend(data)
        
        return all_data
    
    def _union_distinct(self, source_datasets: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """执行UNION操作（去除重复）"""
        # 先执行UNION ALL
        all_data = self._union_all(source_datasets)
        
        # 去除重复数据
        return self._remove_duplicates(all_data)
    
    def _intersect(self, source_datasets: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """执行INTERSECT操作（交集）"""
        if len(source_datasets) < 2:
            return []
        
        # 获取第一个数据集作为基准
        datasets = list(source_datasets.values())
        result_set = set()
        
        # 将第一个数据集转换为集合
        for record in datasets[0]:
            record_tuple = self._record_to_tuple(record)
            result_set.add(record_tuple)
        
        # 与其他数据集求交集
        for dataset in datasets[1:]:
            dataset_set = set()
            for record in dataset:
                record_tuple = self._record_to_tuple(record)
                dataset_set.add(record_tuple)
            
            result_set = result_set.intersection(dataset_set)
        
        # 转换回字典列表
        return [self._tuple_to_record(t, datasets[0][0].keys()) for t in result_set]
    
    def _except(self, source_datasets: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """执行EXCEPT操作（差集）"""
        if len(source_datasets) < 2:
            return list(source_datasets.values())[0] if source_datasets else []
        
        datasets = list(source_datasets.values())
        
        # 获取第一个数据集
        result_set = set()
        for record in datasets[0]:
            record_tuple = self._record_to_tuple(record)
            result_set.add(record_tuple)
        
        # 从结果中移除其他数据集的记录
        for dataset in datasets[1:]:
            for record in dataset:
                record_tuple = self._record_to_tuple(record)
                result_set.discard(record_tuple)
        
        # 转换回字典列表
        return [self._tuple_to_record(t, datasets[0][0].keys()) for t in result_set]
    
    def _align_columns(self, source_datasets: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """对齐列结构"""
        if not source_datasets:
            return source_datasets
        
        # 收集所有列名
        all_columns = set()
        for data in source_datasets.values():
            if data:
                all_columns.update(data[0].keys())
        
        # 对齐每个数据集的列
        aligned_datasets = {}
        for source_name, data in source_datasets.items():
            aligned_data = []
            for record in data:
                aligned_record = {}
                for col in all_columns:
                    aligned_record[col] = record.get(col, None)
                aligned_data.append(aligned_record)
            aligned_datasets[source_name] = aligned_data
        
        return aligned_datasets
    
    def _remove_duplicates(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """移除重复数据"""
        seen = set()
        unique_data = []
        
        for record in data:
            record_tuple = self._record_to_tuple(record)
            if record_tuple not in seen:
                seen.add(record_tuple)
                unique_data.append(record)
        
        return unique_data
    
    def _record_to_tuple(self, record: Dict[str, Any]) -> tuple:
        """将记录转换为元组（用于集合操作）"""
        return tuple(sorted(record.items()))
    
    def _tuple_to_record(self, record_tuple: tuple, columns: List[str]) -> Dict[str, Any]:
        """将元组转换回记录"""
        return dict(record_tuple)
    
    def _validate_schema_compatibility(self, source_datasets: Dict[str, List[Dict[str, Any]]]) -> None:
        """验证模式兼容性"""
        if not source_datasets:
            return
        
        # 获取第一个数据集的列结构作为基准
        first_dataset = list(source_datasets.values())[0]
        if not first_dataset:
            return
        
        base_columns = set(first_dataset[0].keys())
        
        # 检查其他数据集的列结构
        for source_name, data in source_datasets.items():
            if data:
                current_columns = set(data[0].keys())
                
                # 根据配置决定如何处理列差异
                strict_mode = self.config.get("strict_schema", False)
                if strict_mode and current_columns != base_columns:
                    missing_in_current = base_columns - current_columns
                    extra_in_current = current_columns - base_columns
                    
                    error_msg = f"数据集 {source_name} 的列结构不匹配"
                    if missing_in_current:
                        error_msg += f"，缺少列: {missing_in_current}"
                    if extra_in_current:
                        error_msg += f"，多余列: {extra_in_current}"
                    
                    raise ValidationError(error_msg)
    
    def _optimize_union_strategy(self, source_datasets: Dict[str, List[Dict[str, Any]]]) -> str:
        """优化合并策略"""
        total_records = sum(len(data) for data in source_datasets.values())
        dataset_count = len(source_datasets)
        
        if total_records < 10000 and dataset_count <= 5:
            return "memory_union"
        elif total_records < 100000:
            return "streaming_union"
        else:
            return "chunked_union"
