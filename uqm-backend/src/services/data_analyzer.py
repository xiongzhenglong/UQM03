"""
数据分析服务
分析原始数据并生成相应的处理代码
"""

import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class ColumnAnalysis(BaseModel):
    name: str
    type: str
    null_count: int = 0
    unique_count: int = 0
    sample_values: List[Any] = Field(default_factory=list)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    avg_value: Optional[float] = None

class DataAnalysisResult(BaseModel):
    total_rows: int
    total_columns: int
    columns: List[ColumnAnalysis] = Field(default_factory=list)
    numeric_columns: List[str] = Field(default_factory=list)
    string_columns: List[str] = Field(default_factory=list)
    date_columns: List[str] = Field(default_factory=list)
    boolean_columns: List[str] = Field(default_factory=list)

class DataAnalyzer:
    def _is_numeric(self, val: Any) -> bool:
        if isinstance(val, (int, float)):
            return True
        if isinstance(val, str):
            try:
                float(val)
                return True
            except (ValueError, TypeError):
                return False
        return False

    def analyze_data(self, data: List[Dict[str, Any]]) -> DataAnalysisResult:
        if not data:
            return DataAnalysisResult(total_rows=0, total_columns=0)

        total_rows = len(data)
        if not isinstance(data[0], dict):
             return DataAnalysisResult(total_rows=total_rows, total_columns=0)

        columns = list(data[0].keys())
        total_columns = len(columns)
        
        result = DataAnalysisResult(total_rows=total_rows, total_columns=total_columns)

        for col_name in columns:
            col_analysis = ColumnAnalysis(name=col_name, type='unknown')
            values = [row.get(col_name) for row in data]
            
            non_null_values = [v for v in values if v is not None and v != '']
            col_analysis.null_count = total_rows - len(non_null_values)
            
            if not non_null_values:
                col_analysis.type = 'empty'
                result.columns.append(col_analysis)
                continue

            # Type inference
            if all(isinstance(v, bool) for v in non_null_values):
                col_analysis.type = 'boolean'
                result.boolean_columns.append(col_name)
            elif all(self._is_numeric(v) for v in non_null_values):
                col_analysis.type = 'number'
                result.numeric_columns.append(col_name)
                numeric_values = [float(v) for v in non_null_values]
                if numeric_values:
                    col_analysis.min_value = min(numeric_values)
                    col_analysis.max_value = max(numeric_values)
                    col_analysis.avg_value = sum(numeric_values) / len(numeric_values)
            else: # Default to string
                col_analysis.type = 'string'
                result.string_columns.append(col_name)

            unique_values = set()
            for v in non_null_values:
                # Pydantic models are not hashable
                if isinstance(v, (dict, list)):
                    unique_values.add(json.dumps(v))
                else:
                    unique_values.add(v)

            col_analysis.unique_count = len(unique_values)
            col_analysis.sample_values = list(unique_values)[:5]
            
            result.columns.append(col_analysis)

        return result

_data_analyzer: Optional[DataAnalyzer] = None

def get_data_analyzer() -> DataAnalyzer:
    global _data_analyzer
    if _data_analyzer is None:
        _data_analyzer = DataAnalyzer()
    return _data_analyzer 