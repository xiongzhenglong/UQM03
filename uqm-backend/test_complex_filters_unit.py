#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复杂过滤条件单元测试
确保嵌套AND/OR逻辑的正确性和向后兼容性
"""

import sys
import os
import json
import unittest
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.steps.query_step import QueryStep
from src.utils.exceptions import ValidationError


class TestComplexFilters(unittest.TestCase):
    """复杂过滤条件测试类"""
    
    def setUp(self):
        """设置测试数据"""
        self.test_data = [
            {"id": 1, "name": "Alice", "salary": 60000, "department": "Engineering", "active": True},
            {"id": 2, "name": "Bob", "salary": 45000, "department": "Engineering", "active": True},
            {"id": 3, "name": "Charlie", "salary": 80000, "department": "Sales", "active": False},
            {"id": 4, "name": "David", "salary": 40000, "department": "HR", "active": True},
            {"id": 5, "name": "Eve", "salary": 120000, "department": "Engineering", "active": True}
        ]
        
        self.basic_config = {
            "data_source": "test_table",
            "dimensions": ["id", "name", "salary", "department"]
        }
    
    def test_simple_filter_backward_compatibility(self):
        """测试简单过滤器的向后兼容性"""
        config = {
            **self.basic_config,
            "filters": [
                {"field": "salary", "operator": ">", "value": 50000},
                {"field": "department", "operator": "=", "value": "Engineering"}
            ]
        }
        
        query_step = QueryStep(config)
        result = query_step._apply_filters(self.test_data, config["filters"])
        
        # 预期：Alice (60000, Engineering) 和 Eve (120000, Engineering)
        expected_names = {"Alice", "Eve"}
        actual_names = {row["name"] for row in result}
        
        self.assertEqual(expected_names, actual_names)
    
    def test_simple_and_logic(self):
        """测试简单AND逻辑"""
        filters = [
            {
                "logic": "AND",
                "conditions": [
                    {"field": "salary", "operator": ">", "value": 50000},
                    {"field": "department", "operator": "=", "value": "Engineering"}
                ]
            }
        ]
        
        query_step = QueryStep(self.basic_config)
        result = query_step._apply_filters(self.test_data, filters)
        
        expected_names = {"Alice", "Eve"}
        actual_names = {row["name"] for row in result}
        
        self.assertEqual(expected_names, actual_names)
    
    def test_simple_or_logic(self):
        """测试简单OR逻辑"""
        filters = [
            {
                "logic": "OR",
                "conditions": [
                    {"field": "salary", "operator": ">", "value": 100000},
                    {"field": "department", "operator": "=", "value": "Sales"}
                ]
            }
        ]
        
        query_step = QueryStep(self.basic_config)
        result = query_step._apply_filters(self.test_data, filters)
        
        expected_names = {"Charlie", "Eve"}  # Charlie (Sales) 和 Eve (120000)
        actual_names = {row["name"] for row in result}
        
        self.assertEqual(expected_names, actual_names)
    
    def test_nested_and_or_logic(self):
        """测试嵌套AND/OR逻辑"""
        filters = [
            {
                "logic": "AND",
                "conditions": [
                    {
                        "logic": "OR",
                        "conditions": [
                            {"field": "salary", "operator": ">", "value": 70000},
                            {"field": "department", "operator": "=", "value": "Engineering"}
                        ]
                    },
                    {"field": "active", "operator": "=", "value": True}
                ]
            }
        ]
        
        query_step = QueryStep(self.basic_config)
        result = query_step._apply_filters(self.test_data, filters)
        
        # 预期：(salary > 70000 OR department = Engineering) AND active = True
        # Alice: Engineering AND active ✓
        # Bob: Engineering AND active ✓
        # Charlie: salary=80000 > 70000 但 active=False ✗
        # David: HR AND salary=40000 ✗
        # Eve: Engineering AND active ✓
        expected_names = {"Alice", "Bob", "Eve"}
        actual_names = {row["name"] for row in result}
        
        self.assertEqual(expected_names, actual_names)
    
    def test_complex_nested_logic(self):
        """测试复杂嵌套逻辑"""
        filters = [
            {
                "logic": "AND",
                "conditions": [
                    {
                        "logic": "OR",
                        "conditions": [
                            {
                                "logic": "AND",
                                "conditions": [
                                    {"field": "salary", "operator": ">", "value": 50000},
                                    {"field": "department", "operator": "=", "value": "Engineering"}
                                ]
                            },
                            {
                                "logic": "AND",
                                "conditions": [
                                    {"field": "salary", "operator": ">", "value": 70000},
                                    {"field": "department", "operator": "=", "value": "Sales"}
                                ]
                            }
                        ]
                    },
                    {"field": "active", "operator": "=", "value": True}
                ]
            }
        ]
        
        query_step = QueryStep(self.basic_config)
        result = query_step._apply_filters(self.test_data, filters)
        
        # 预期：((salary > 50000 AND dept = Engineering) OR (salary > 70000 AND dept = Sales)) AND active = True
        # Alice: salary=60000 > 50000 AND dept=Engineering AND active=True ✓
        # Bob: salary=45000 <= 50000 ✗
        # Charlie: salary=80000 > 70000 AND dept=Sales 但 active=False ✗
        # David: 不满足任何OR条件 ✗
        # Eve: salary=120000 > 50000 AND dept=Engineering AND active=True ✓
        expected_names = {"Alice", "Eve"}
        actual_names = {row["name"] for row in result}
        
        self.assertEqual(expected_names, actual_names)
    
    def test_mixed_simple_and_complex_filters(self):
        """测试混合简单和复杂过滤器"""
        filters = [
            {"field": "active", "operator": "=", "value": True},  # 简单过滤器
            {
                "logic": "OR",
                "conditions": [
                    {"field": "salary", "operator": ">", "value": 70000},
                    {"field": "department", "operator": "=", "value": "Engineering"}
                ]
            }
        ]
        
        query_step = QueryStep(self.basic_config)
        result = query_step._apply_filters(self.test_data, filters)
        
        # 预期：active = True AND (salary > 70000 OR department = Engineering)
        expected_names = {"Alice", "Bob", "Eve"}
        actual_names = {row["name"] for row in result}
        
        self.assertEqual(expected_names, actual_names)
    
    def test_empty_conditions(self):
        """测试空条件列表"""
        filters = [
            {
                "logic": "AND",
                "conditions": []
            }
        ]
        
        query_step = QueryStep(self.basic_config)
        result = query_step._apply_filters(self.test_data, filters)
        
        # 空条件应该返回所有数据
        self.assertEqual(len(result), len(self.test_data))
    
    def test_unsupported_logic_operator(self):
        """测试不支持的逻辑操作符（应该默认返回True）"""
        filters = [
            {
                "logic": "XOR",  # 不支持的操作符
                "conditions": [
                    {"field": "salary", "operator": ">", "value": 50000},
                    {"field": "department", "operator": "=", "value": "Engineering"}
                ]
            }
        ]
        
        query_step = QueryStep(self.basic_config)
        result = query_step._apply_filters(self.test_data, filters)
        
        # 不支持的逻辑操作符应该返回所有数据
        self.assertEqual(len(result), len(self.test_data))
    
    def test_invalid_filter_format(self):
        """测试无效的过滤器格式（应该默认返回True）"""
        filters = [
            {
                # 既没有logic/conditions也没有field/operator/value
                "invalid": "format"
            }
        ]
        
        query_step = QueryStep(self.basic_config)
        result = query_step._apply_filters(self.test_data, filters)
        
        # 无效格式应该返回所有数据
        self.assertEqual(len(result), len(self.test_data))
    
    def test_in_operator(self):
        """测试IN操作符"""
        filters = [
            {
                "logic": "OR",
                "conditions": [
                    {"field": "department", "operator": "IN", "value": ["Engineering", "Sales"]},
                    {"field": "salary", "operator": ">", "value": 100000}
                ]
            }
        ]
        
        query_step = QueryStep(self.basic_config)
        result = query_step._apply_filters(self.test_data, filters)
        
        expected_names = {"Alice", "Bob", "Charlie", "Eve"}
        actual_names = {row["name"] for row in result}
        
        self.assertEqual(expected_names, actual_names)
    
    def test_not_in_operator(self):
        """测试NOT IN操作符"""
        filters = [
            {
                "logic": "AND",
                "conditions": [
                    {"field": "department", "operator": "NOT IN", "value": ["HR"]},
                    {"field": "active", "operator": "=", "value": True}
                ]
            }
        ]
        
        query_step = QueryStep(self.basic_config)
        result = query_step._apply_filters(self.test_data, filters)
        
        expected_names = {"Alice", "Bob", "Eve"}  # 排除David（HR部门）
        actual_names = {row["name"] for row in result}
        
        self.assertEqual(expected_names, actual_names)


if __name__ == "__main__":
    unittest.main()
