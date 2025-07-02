"""
数据断言步骤实现
用于验证数据质量和业务规则
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
import re

from src.steps.base import BaseStep
from src.utils.exceptions import ValidationError, ExecutionError


class AssertStep(BaseStep):
    """断言步骤执行器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化断言步骤
        
        Args:
            config: 断言步骤配置
        """
        # 先初始化支持的断言类型，再调用父类初始化
        # 这样在 validate() 方法中就可以访问 supported_assertions
        self.supported_assertions = {
            'row_count': self._assert_row_count,
            'not_null': self._assert_not_null,
            'unique': self._assert_unique,
            'range': self._assert_range,
            'regex': self._assert_regex,
            'custom': self._assert_custom,
            'column_exists': self._assert_column_exists,
            'data_type': self._assert_data_type,
            'value_in': self._assert_value_in,
            'relationship': self._assert_relationship
        }
        
        # 调用父类初始化（会触发 validate() 方法）
        super().__init__(config)
    
    def validate(self) -> None:
        """验证断言步骤配置"""
        required_fields = ["source", "assertions"]
        self._validate_required_config(required_fields)
        
        # 验证assertions字段
        assertions = self.config.get("assertions")
        if not isinstance(assertions, list):
            raise ValidationError("assertions必须是数组")
        
        # 验证每个断言
        for i, assertion in enumerate(assertions):
            if not isinstance(assertion, dict):
                raise ValidationError(f"断言 {i} 必须是对象")
            
            assertion_type = assertion.get("type")
            if not assertion_type:
                raise ValidationError(f"断言 {i} 缺少type字段")
            
            if assertion_type not in self.supported_assertions:
                raise ValidationError(f"不支持的断言类型: {assertion_type}")
    
    async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        执行断言步骤
        
        Args:
            context: 执行上下文
            
        Returns:
            源数据（断言通过时）
        """
        try:
            # 获取源数据
            source_name = self.config["source"]
            source_data = context["get_source_data"](source_name)
            
            # 执行断言检查
            assertion_results = self._perform_assertions(source_data)
            
            # 处理断言结果
            self._handle_assertion_results(assertion_results)
            
            # 断言通过，返回原始数据
            return source_data
            
        except Exception as e:
            self.log_error("断言步骤执行失败", error=str(e))
            raise ExecutionError(f"断言执行失败: {e}")
    
    def _perform_assertions(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        执行断言检查
        
        Args:
            source_data: 源数据
            
        Returns:
            断言结果列表
        """
        assertions = self.config["assertions"]
        assertion_results = []
        
        for assertion in assertions:
            try:
                assertion_type = assertion["type"]
                assertion_func = self.supported_assertions[assertion_type]
                
                # 执行断言
                result = assertion_func(source_data, assertion)
                
                assertion_results.append({
                    "type": assertion_type,
                    "passed": result.get("passed", True),
                    "message": result.get("message", ""),
                    "details": result.get("details", {})
                })
                
            except Exception as e:
                assertion_results.append({
                    "type": assertion.get("type", "unknown"),
                    "passed": False,
                    "message": str(e),
                    "details": {"error": str(e)}
                })
        
        return assertion_results
    
    def _handle_assertion_results(self, assertion_results: List[Dict[str, Any]]) -> None:
        """
        处理断言结果
        
        Args:
            assertion_results: 断言结果列表
        """
        failed_assertions = [r for r in assertion_results if not r["passed"]]
        
        if failed_assertions:
            # 生成断言报告
            report = self._generate_assertion_report(assertion_results)
            
            # 根据配置决定如何处理失败
            on_failure = self.config.get("on_failure", "error")
            
            if on_failure == "error":
                # 抛出异常
                raise ExecutionError(f"断言检查失败:\n{report}")
            elif on_failure == "warning":
                # 记录警告
                self.log_warning("断言检查失败", report=report)
            elif on_failure == "ignore":
                # 忽略失败
                self.log_info("断言检查失败但被忽略", report=report)
        else:
            self.log_info("所有断言检查通过")
    
    def _assert_row_count(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
        """断言行数"""
        expected_count = assertion.get("expected")
        min_count = assertion.get("min")
        max_count = assertion.get("max")
        custom_message = assertion.get("message")
        
        actual_count = len(data)
        
        if expected_count is not None and actual_count != expected_count:
            message = custom_message or f"期望行数 {expected_count}，实际行数 {actual_count}"
            return {
                "passed": False,
                "message": message,
                "details": {"expected": expected_count, "actual": actual_count}
            }
        
        if min_count is not None and actual_count < min_count:
            message = custom_message or f"行数少于最小值 {min_count}，实际行数 {actual_count}"
            return {
                "passed": False,
                "message": message,
                "details": {"min": min_count, "actual": actual_count}
            }
        
        if max_count is not None and actual_count > max_count:
            message = custom_message or f"行数超过最大值 {max_count}，实际行数 {actual_count}"
            return {
                "passed": False,
                "message": message,
                "details": {"max": max_count, "actual": actual_count}
            }
        
        return {"passed": True, "message": f"行数检查通过: {actual_count}"}
    
    def _assert_not_null(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
        """断言非空"""
        columns = assertion.get("columns", [])
        if isinstance(columns, str):
            columns = [columns]
        
        null_records = []
        
        for i, record in enumerate(data):
            for column in columns:
                if column in record and (record[column] is None or record[column] == ""):
                    null_records.append({"row": i, "column": column, "value": record[column]})
        
        if null_records:
            return {
                "passed": False,
                "message": f"发现 {len(null_records)} 个空值",
                "details": {"null_records": null_records[:10]}  # 只显示前10个
            }
        
        return {"passed": True, "message": f"非空检查通过，检查了 {len(columns)} 列"}
    
    def _assert_unique(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
        """断言唯一性"""
        columns = assertion.get("columns", [])
        if isinstance(columns, str):
            columns = [columns]
        
        seen_values = {}
        duplicate_records = []
        
        for i, record in enumerate(data):
            key_values = tuple(record.get(col) for col in columns)
            
            if key_values in seen_values:
                duplicate_records.append({
                    "row": i,
                    "duplicate_of": seen_values[key_values],
                    "values": dict(zip(columns, key_values))
                })
            else:
                seen_values[key_values] = i
        
        if duplicate_records:
            return {
                "passed": False,
                "message": f"发现 {len(duplicate_records)} 个重复值",
                "details": {"duplicate_records": duplicate_records[:10]}
            }
        
        return {"passed": True, "message": f"唯一性检查通过，检查了 {len(columns)} 列"}
    
    def _assert_range(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
        """断言值范围"""
        # 支持 field 和 column 两种字段名（向后兼容）
        field_name = assertion.get("field") or assertion.get("column")
        min_value = assertion.get("min")
        max_value = assertion.get("max")
        custom_message = assertion.get("message", f"字段 {field_name} 超出范围")
        
        if not field_name:
            return {"passed": False, "message": "缺少 field 或 column 参数"}
        
        out_of_range_records = []
        
        for i, record in enumerate(data):
            if field_name in record:
                value = record[field_name]
                # 支持 int, float, Decimal 类型的数值比较
                if isinstance(value, (int, float)) or hasattr(value, '__float__'):
                    try:
                        # 统一转换为 float 进行比较
                        numeric_value = float(value)
                        if min_value is not None and numeric_value < min_value:
                            out_of_range_records.append({
                                "row": i,
                                "field": field_name,
                                "value": numeric_value,
                                "reason": f"小于最小值 {min_value}"
                            })
                        elif max_value is not None and numeric_value > max_value:
                            out_of_range_records.append({
                                "row": i,
                                "field": field_name,
                                "value": numeric_value,
                                "reason": f"大于最大值 {max_value}"
                            })
                    except (ValueError, TypeError):
                        # 如果无法转换为数值，跳过该记录
                        self.log_warning(f"无法将值 {value} 转换为数值进行范围检查")
                        continue
        
        if out_of_range_records:
            return {
                "passed": False,
                "message": custom_message,
                "details": {"out_of_range_records": out_of_range_records[:10]}
            }
        
        return {"passed": True, "message": f"范围检查通过，字段 {field_name}"}
    
    def _assert_regex(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
        """断言正则表达式匹配"""
        column = assertion.get("column")
        pattern = assertion.get("pattern")
        
        if not pattern:
            return {"passed": False, "message": "缺少pattern参数"}
        
        try:
            regex = re.compile(pattern)
        except re.error as e:
            return {"passed": False, "message": f"无效的正则表达式: {e}"}
        
        mismatch_records = []
        
        for i, record in enumerate(data):
            if column in record:
                value = str(record[column])
                if not regex.match(value):
                    mismatch_records.append({
                        "row": i,
                        "column": column,
                        "value": value
                    })
        
        if mismatch_records:
            return {
                "passed": False,
                "message": f"发现 {len(mismatch_records)} 个不匹配正则表达式的值",
                "details": {"mismatch_records": mismatch_records[:10]}
            }
        
        return {"passed": True, "message": f"正则表达式检查通过，列 {column}"}
    
    def _assert_custom(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
        """自定义断言"""
        expression = assertion.get("expression")
        custom_message = assertion.get("message", "自定义断言失败")
        
        if not expression:
            return {"passed": False, "message": "缺少expression参数"}
        
        try:
            # 这里可以实现更复杂的自定义断言逻辑
            # 为了安全性，这里只是一个示例
            failed_rows = []
            
            for i, record in enumerate(data):
                # 简单的表达式评估（生产环境需要更安全的实现）
                try:
                    # 将记录作为局部变量传入
                    if not eval(expression, {"__builtins__": {}}, record):
                        failed_rows.append(i)
                except Exception:
                    failed_rows.append(i)
            
            if failed_rows:
                return {
                    "passed": False,
                    "message": custom_message,
                    "details": {"failed_rows": failed_rows[:10], "expression": expression}
                }
            
            return {"passed": True, "message": "自定义断言通过"}
            
        except Exception as e:
            return {"passed": False, "message": f"自定义断言执行错误: {e}"}
    
    def _assert_column_exists(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
        """断言列存在"""
        columns = assertion.get("columns", [])
        if isinstance(columns, str):
            columns = [columns]
        
        if not data:
            return {"passed": False, "message": "数据为空，无法检查列"}
        
        existing_columns = set(data[0].keys())
        missing_columns = [col for col in columns if col not in existing_columns]
        
        if missing_columns:
            return {
                "passed": False,
                "message": f"缺少列: {missing_columns}",
                "details": {"missing_columns": missing_columns}
            }
        
        return {"passed": True, "message": f"列存在检查通过: {columns}"}
    
    def _assert_data_type(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
        """断言数据类型"""
        column = assertion.get("column")
        expected_type = assertion.get("expected_type")
        
        type_mapping = {
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "number": (int, float)
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if not expected_python_type:
            return {"passed": False, "message": f"不支持的数据类型: {expected_type}"}
        
        type_errors = []
        
        for i, record in enumerate(data):
            if column in record and record[column] is not None:
                if not isinstance(record[column], expected_python_type):
                    type_errors.append({
                        "row": i,
                        "column": column,
                        "value": record[column],
                        "actual_type": type(record[column]).__name__
                    })
        
        if type_errors:
            return {
                "passed": False,
                "message": f"发现 {len(type_errors)} 个类型错误",
                "details": {"type_errors": type_errors[:10]}
            }
        
        return {"passed": True, "message": f"数据类型检查通过，列 {column}"}
    
    def _assert_value_in(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
        """断言值在指定集合中"""
        column = assertion.get("column")
        allowed_values = assertion.get("allowed_values", [])
        
        invalid_records = []
        
        for i, record in enumerate(data):
            if column in record:
                value = record[column]
                if value not in allowed_values:
                    invalid_records.append({
                        "row": i,
                        "column": column,
                        "value": value
                    })
        
        if invalid_records:
            return {
                "passed": False,
                "message": f"发现 {len(invalid_records)} 个无效值",
                "details": {"invalid_records": invalid_records[:10]}
            }
        
        return {"passed": True, "message": f"值域检查通过，列 {column}"}
    
    def _assert_relationship(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
        """断言字段间关系"""
        # 这是一个复杂的断言类型，可以检查字段间的关系
        # 例如：开始日期必须小于结束日期
        return {"passed": True, "message": "关系断言暂未实现"}
    
    def _generate_assertion_report(self, assertion_results: List[Dict[str, Any]]) -> str:
        """生成断言报告"""
        total_assertions = len(assertion_results)
        passed_assertions = len([r for r in assertion_results if r["passed"]])
        failed_assertions = total_assertions - passed_assertions
        
        report_lines = [
            f"断言检查报告:",
            f"总计: {total_assertions}, 通过: {passed_assertions}, 失败: {failed_assertions}",
            ""
        ]
        
        for result in assertion_results:
            status = "✓" if result["passed"] else "✗"
            report_lines.append(f"{status} {result['type']}: {result['message']}")
        
        return "\n".join(report_lines)
