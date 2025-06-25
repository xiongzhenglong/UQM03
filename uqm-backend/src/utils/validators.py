"""
数据验证工具模块

提供各种数据验证功能，包括 UQM 配置验证、数据格式验证、业务逻辑验证等。
"""

import re
import json
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import logging

from ..utils.exceptions import ValidationError

logger = logging.getLogger(__name__)


class DataValidator:
    """数据验证器基类"""
    
    def __init__(self):
        self.errors = []
    
    def add_error(self, field: str, message: str, value: Any = None):
        """添加验证错误"""
        self.errors.append({
            'field': field,
            'message': message,
            'value': value,
            'timestamp': datetime.now().isoformat()
        })
    
    def clear_errors(self):
        """清空错误列表"""
        self.errors = []
    
    def has_errors(self) -> bool:
        """检查是否有验证错误"""
        return len(self.errors) > 0
    
    def get_errors(self) -> List[Dict[str, Any]]:
        """获取所有验证错误"""
        return self.errors.copy()
    
    def raise_if_errors(self):
        """如果有错误则抛出异常"""
        if self.has_errors():
            raise ValidationError(f"验证失败: {len(self.errors)} 个错误", details=self.errors)


class UQMValidator(DataValidator):
    """UQM 配置验证器"""
    
    # 支持的步骤类型
    SUPPORTED_STEP_TYPES = {
        'query', 'enrich', 'pivot', 'unpivot', 'union', 'assert',
        'filter', 'sort', 'group', 'aggregate', 'join', 'transform'
    }
    
    # 支持的数据源类型
    SUPPORTED_DATASOURCE_TYPES = {
        'postgres', 'mysql', 'sqlite', 'oracle', 'sqlserver',
        'mongodb', 'redis', 'elasticsearch', 'api', 'file'
    }
    
    def validate_uqm_config(self, config: Dict[str, Any]) -> bool:
        """验证完整的 UQM 配置"""
        self.clear_errors()
        
        # 验证根级字段
        self._validate_root_fields(config)
        
        # 验证数据源配置
        if 'datasources' in config:
            self._validate_datasources(config['datasources'])
        
        # 验证步骤配置
        if 'steps' in config:
            self._validate_steps(config['steps'])
        
        # 验证输出配置
        if 'output' in config:
            self._validate_output(config['output'])
        
        return not self.has_errors()
    
    def _validate_root_fields(self, config: Dict[str, Any]):
        """验证根级必需字段"""
        required_fields = ['name', 'version', 'steps']
        
        for field in required_fields:
            if field not in config:
                self.add_error(field, f"缺少必需字段: {field}")
        
        # 验证版本格式
        if 'version' in config:
            version = config['version']
            if not isinstance(version, str) or not re.match(r'^\d+\.\d+(\.\d+)?$', version):
                self.add_error('version', f"版本格式无效: {version}")
        
        # 验证名称
        if 'name' in config:
            name = config['name']
            if not isinstance(name, str) or len(name.strip()) == 0:
                self.add_error('name', f"名称无效: {name}")
    
    def _validate_datasources(self, datasources: Dict[str, Any]):
        """验证数据源配置"""
        if not isinstance(datasources, dict):
            self.add_error('datasources', "数据源配置必须是字典类型")
            return
        
        for ds_name, ds_config in datasources.items():
            self._validate_single_datasource(ds_name, ds_config)
    
    def _validate_single_datasource(self, name: str, config: Dict[str, Any]):
        """验证单个数据源配置"""
        if not isinstance(config, dict):
            self.add_error(f'datasources.{name}', "数据源配置必须是字典类型")
            return
        
        # 验证类型
        if 'type' not in config:
            self.add_error(f'datasources.{name}.type', "缺少数据源类型")
        elif config['type'] not in self.SUPPORTED_DATASOURCE_TYPES:
            self.add_error(f'datasources.{name}.type', 
                          f"不支持的数据源类型: {config['type']}")
        
        # 验证连接配置
        if 'connection' not in config:
            self.add_error(f'datasources.{name}.connection', "缺少连接配置")
        elif not isinstance(config['connection'], dict):
            self.add_error(f'datasources.{name}.connection', "连接配置必须是字典类型")
    
    def _validate_steps(self, steps: List[Dict[str, Any]]):
        """验证步骤配置"""
        if not isinstance(steps, list):
            self.add_error('steps', "步骤配置必须是列表类型")
            return
        
        if len(steps) == 0:
            self.add_error('steps', "至少需要一个步骤")
            return
        
        step_names = set()
        for i, step in enumerate(steps):
            self._validate_single_step(i, step, step_names)
    
    def _validate_single_step(self, index: int, step: Dict[str, Any], step_names: set):
        """验证单个步骤配置"""
        if not isinstance(step, dict):
            self.add_error(f'steps[{index}]', "步骤配置必须是字典类型")
            return
        
        # 验证必需字段
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in step:
                self.add_error(f'steps[{index}].{field}', f"缺少必需字段: {field}")
        
        # 验证步骤名称唯一性
        if 'name' in step:
            name = step['name']
            if name in step_names:
                self.add_error(f'steps[{index}].name', f"步骤名称重复: {name}")
            else:
                step_names.add(name)
        
        # 验证步骤类型
        if 'type' in step:
            step_type = step['type']
            if step_type not in self.SUPPORTED_STEP_TYPES:
                self.add_error(f'steps[{index}].type', 
                              f"不支持的步骤类型: {step_type}")
        
        # 验证依赖关系
        if 'depends_on' in step:
            self._validate_dependencies(index, step['depends_on'], step_names)
    
    def _validate_dependencies(self, step_index: int, dependencies: List[str], 
                             available_steps: set):
        """验证步骤依赖关系"""
        if not isinstance(dependencies, list):
            self.add_error(f'steps[{step_index}].depends_on', 
                          "依赖配置必须是列表类型")
            return
        
        for dep in dependencies:
            if not isinstance(dep, str):
                self.add_error(f'steps[{step_index}].depends_on', 
                              f"依赖名称必须是字符串: {dep}")
            elif dep not in available_steps:
                self.add_error(f'steps[{step_index}].depends_on', 
                              f"引用了不存在的步骤: {dep}")
    
    def _validate_output(self, output: Dict[str, Any]):
        """验证输出配置"""
        if not isinstance(output, dict):
            self.add_error('output', "输出配置必须是字典类型")
            return
        
        # 验证输出格式
        if 'format' in output:
            supported_formats = {'json', 'csv', 'excel', 'parquet', 'sql'}
            if output['format'] not in supported_formats:
                self.add_error('output.format', 
                              f"不支持的输出格式: {output['format']}")


class DataTypeValidator(DataValidator):
    """数据类型验证器"""
    
    def validate_dataframe(self, df: pd.DataFrame, schema: Dict[str, Any]) -> bool:
        """验证 DataFrame 结构和数据"""
        self.clear_errors()
        
        if not isinstance(df, pd.DataFrame):
            self.add_error('dataframe', "输入不是有效的 DataFrame")
            return False
        
        # 验证列结构
        if 'columns' in schema:
            self._validate_columns(df, schema['columns'])
        
        # 验证数据约束
        if 'constraints' in schema:
            self._validate_constraints(df, schema['constraints'])
        
        return not self.has_errors()
    
    def _validate_columns(self, df: pd.DataFrame, column_schema: Dict[str, Any]):
        """验证列结构"""
        # 检查必需列
        if 'required' in column_schema:
            for col in column_schema['required']:
                if col not in df.columns:
                    self.add_error('columns', f"缺少必需列: {col}")
        
        # 检查列数据类型
        if 'types' in column_schema:
            for col, expected_type in column_schema['types'].items():
                if col in df.columns:
                    self._validate_column_type(df, col, expected_type)
    
    def _validate_column_type(self, df: pd.DataFrame, column: str, expected_type: str):
        """验证列数据类型"""
        actual_type = str(df[column].dtype)
        
        # 类型映射
        type_mapping = {
            'int': ['int64', 'int32', 'int16', 'int8'],
            'float': ['float64', 'float32'],
            'string': ['object', 'string'],
            'datetime': ['datetime64[ns]', 'datetime64'],
            'bool': ['bool']
        }
        
        if expected_type in type_mapping:
            if actual_type not in type_mapping[expected_type]:
                self.add_error(f'columns.{column}', 
                              f"列类型不匹配，期望: {expected_type}, 实际: {actual_type}")
    
    def _validate_constraints(self, df: pd.DataFrame, constraints: Dict[str, Any]):
        """验证数据约束"""
        # 检查非空约束
        if 'not_null' in constraints:
            for col in constraints['not_null']:
                if col in df.columns and df[col].isnull().any():
                    null_count = df[col].isnull().sum()
                    self.add_error(f'constraints.not_null.{col}', 
                                  f"列包含 {null_count} 个空值")
        
        # 检查唯一性约束
        if 'unique' in constraints:
            for col in constraints['unique']:
                if col in df.columns and df[col].duplicated().any():
                    dup_count = df[col].duplicated().sum()
                    self.add_error(f'constraints.unique.{col}', 
                                  f"列包含 {dup_count} 个重复值")
        
        # 检查值范围约束
        if 'range' in constraints:
            for col, range_config in constraints['range'].items():
                if col in df.columns:
                    self._validate_value_range(df, col, range_config)
    
    def _validate_value_range(self, df: pd.DataFrame, column: str, 
                            range_config: Dict[str, Any]):
        """验证值范围"""
        if 'min' in range_config:
            min_val = range_config['min']
            if (df[column] < min_val).any():
                violation_count = (df[column] < min_val).sum()
                self.add_error(f'constraints.range.{column}.min', 
                              f"{violation_count} 个值小于最小值 {min_val}")
        
        if 'max' in range_config:
            max_val = range_config['max']
            if (df[column] > max_val).any():
                violation_count = (df[column] > max_val).sum()
                self.add_error(f'constraints.range.{column}.max', 
                              f"{violation_count} 个值大于最大值 {max_val}")


class SchemaValidator(DataValidator):
    """Schema 验证器"""
    
    def validate_json_schema(self, data: Any, schema: Dict[str, Any]) -> bool:
        """验证 JSON Schema"""
        self.clear_errors()
        
        try:
            # 这里应该使用 jsonschema 库进行验证
            # 由于简化实现，这里只做基本验证
            self._validate_basic_schema(data, schema)
        except Exception as e:
            self.add_error('schema', f"Schema 验证失败: {str(e)}")
        
        return not self.has_errors()
    
    def _validate_basic_schema(self, data: Any, schema: Dict[str, Any]):
        """基本 Schema 验证"""
        # 验证类型
        if 'type' in schema:
            expected_type = schema['type']
            if not self._check_type(data, expected_type):
                self.add_error('type', f"类型不匹配，期望: {expected_type}")
        
        # 验证必需属性（对象类型）
        if isinstance(data, dict) and 'required' in schema:
            for field in schema['required']:
                if field not in data:
                    self.add_error('required', f"缺少必需字段: {field}")
        
        # 验证属性（对象类型）
        if isinstance(data, dict) and 'properties' in schema:
            for key, value in data.items():
                if key in schema['properties']:
                    # 递归验证子属性
                    sub_validator = SchemaValidator()
                    if not sub_validator.validate_json_schema(value, schema['properties'][key]):
                        self.errors.extend(sub_validator.get_errors())
    
    def _check_type(self, data: Any, expected_type: str) -> bool:
        """检查数据类型"""
        type_mapping = {
            'string': str,
            'number': (int, float, Decimal),
            'integer': int,
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None)
        }
        
        if expected_type in type_mapping:
            return isinstance(data, type_mapping[expected_type])
        
        return True


def validate_sql_injection(sql: str) -> Tuple[bool, List[str]]:
    """验证 SQL 注入风险"""
    dangerous_patterns = [
        r';\s*(drop|delete|truncate|update)\s+',
        r'union\s+select',
        r'exec\s*\(',
        r'xp_cmdshell',
        r'sp_executesql',
        r'--|#',
        r'/\*.*\*/',
        r'@@version',
        r'information_schema',
        r'sys\.',
    ]
    
    risks = []
    sql_lower = sql.lower()
    
    for pattern in dangerous_patterns:
        if re.search(pattern, sql_lower, re.IGNORECASE):
            risks.append(f"检测到潜在的 SQL 注入模式: {pattern}")
    
    return len(risks) == 0, risks


def validate_column_name(name: str) -> Tuple[bool, str]:
    """验证列名格式"""
    if not isinstance(name, str):
        return False, "列名必须是字符串"
    
    if len(name.strip()) == 0:
        return False, "列名不能为空"
    
    # 检查 SQL 保留字
    sql_keywords = {
        'select', 'from', 'where', 'group', 'order', 'by', 'having',
        'insert', 'update', 'delete', 'drop', 'create', 'alter',
        'table', 'database', 'index', 'view', 'procedure'
    }
    
    if name.lower() in sql_keywords:
        return False, f"列名不能使用 SQL 保留字: {name}"
    
    # 检查字符格式
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
        return False, "列名只能包含字母、数字和下划线，且必须以字母开头"
    
    return True, ""


def validate_expression(expression: str) -> Tuple[bool, str]:
    """验证表达式安全性"""
    if not isinstance(expression, str):
        return False, "表达式必须是字符串"
    
    # 检查危险函数调用
    dangerous_functions = [
        'eval', 'exec', 'compile', '__import__',
        'open', 'file', 'input', 'raw_input',
        'reload', 'vars', 'globals', 'locals'
    ]
    
    for func in dangerous_functions:
        if func in expression:
            return False, f"表达式包含危险函数: {func}"
    
    # 检查危险属性访问
    if '__' in expression and ('__class__' in expression or '__base__' in expression):
        return False, "表达式包含危险的属性访问"
    
    return True, ""


class BusinessValidator(DataValidator):
    """业务逻辑验证器"""
    
    def validate_pivot_config(self, config: Dict[str, Any]) -> bool:
        """验证透视配置"""
        self.clear_errors()
        
        required_fields = ['index_columns', 'pivot_column', 'value_columns']
        for field in required_fields:
            if field not in config:
                self.add_error(field, f"透视配置缺少必需字段: {field}")
        
        # 验证列名列表
        for field in ['index_columns', 'value_columns']:
            if field in config:
                if not isinstance(config[field], list):
                    self.add_error(field, f"{field} 必须是列表类型")
                elif len(config[field]) == 0:
                    self.add_error(field, f"{field} 不能为空")
        
        return not self.has_errors()
    
    def validate_join_config(self, config: Dict[str, Any]) -> bool:
        """验证连接配置"""
        self.clear_errors()
        
        required_fields = ['left_on', 'right_on', 'how']
        for field in required_fields:
            if field not in config:
                self.add_error(field, f"连接配置缺少必需字段: {field}")
        
        # 验证连接类型
        if 'how' in config:
            valid_joins = {'inner', 'left', 'right', 'outer', 'cross'}
            if config['how'] not in valid_joins:
                self.add_error('how', f"不支持的连接类型: {config['how']}")
        
        return not self.has_errors()
    
    def validate_aggregation_config(self, config: Dict[str, Any]) -> bool:
        """验证聚合配置"""
        self.clear_errors()
        
        if 'group_by' not in config and 'agg_functions' not in config:
            self.add_error('config', "聚合配置必须包含 group_by 或 agg_functions")
        
        # 验证聚合函数
        if 'agg_functions' in config:
            valid_functions = {
                'sum', 'count', 'avg', 'min', 'max', 'std', 'var', 'median'
            }
            
            for col, func in config['agg_functions'].items():
                if isinstance(func, str):
                    if func not in valid_functions:
                        self.add_error('agg_functions', 
                                      f"不支持的聚合函数: {func}")
                elif isinstance(func, list):
                    for f in func:
                        if f not in valid_functions:
                            self.add_error('agg_functions', 
                                          f"不支持的聚合函数: {f}")
        
        return not self.has_errors()


# 全局验证器实例
uqm_validator = UQMValidator()
data_type_validator = DataTypeValidator()
schema_validator = SchemaValidator()
business_validator = BusinessValidator()
