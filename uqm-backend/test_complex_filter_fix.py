#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试复杂过滤条件修复
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.engine import UQMEngine


async def test_complex_filter_fix():
    """测试复杂过滤条件修复"""
    print("=== 测试复杂过滤条件修复 ===")
    
    # 简化的测试配置
    test_config = {
        "query_id": "test_complex_filter",
        "description": "测试复杂过滤条件",
        "steps": [
            {
                "step_id": "employees_query",
                "type": "query",
                "config": {
                    "data_source": "employees",
                    "dimensions": ["name", "salary", "department"],
                    "filters": [
                        {
                            "logic": "AND",
                            "conditions": [
                                {
                                    "logic": "OR",
                                    "conditions": [
                                        {
                                            "field": "salary",
                                            "operator": ">",
                                            "value": 50000
                                        },
                                        {
                                            "field": "department",
                                            "operator": "=",
                                            "value": "Engineering"
                                        }
                                    ]
                                },
                                {
                                    "field": "salary",
                                    "operator": "<=",
                                    "value": 100000
                                }
                            ]
                        }
                    ]
                }
            }
        ],
        "output": "filtered_employees"
    }
    
    # 创建测试数据
    test_data = [
        {"name": "Alice", "salary": 60000, "department": "Engineering"},
        {"name": "Bob", "salary": 45000, "department": "Engineering"},
        {"name": "Charlie", "salary": 80000, "department": "Sales"},
        {"name": "David", "salary": 40000, "department": "HR"},
        {"name": "Eve", "salary": 120000, "department": "Engineering"}
    ]
    
    print(f"原始数据: {len(test_data)} 条记录")
    for record in test_data:
        print(f"  {record}")
    
    # 手动测试过滤逻辑
    from src.steps.query_step import QueryStep
    
    query_step = QueryStep(test_config["steps"][0]["config"])
    
    # 直接测试过滤器
    filters = test_config["steps"][0]["config"]["filters"]
    filtered_data = query_step._apply_filters(test_data, filters)
    
    print(f"\n过滤后数据: {len(filtered_data)} 条记录")
    for record in filtered_data:
        print(f"  {record}")
    
    print("\n=== 过滤条件分析 ===")
    print("条件: (salary > 50000 OR department = 'Engineering') AND salary <= 100000")
    print("应该匹配:")
    print("  - Alice: salary=60000 > 50000 AND salary=60000 <= 100000 ✓")
    print("  - Bob: department='Engineering' AND salary=45000 <= 100000 ✓")
    print("  - Charlie: salary=80000 > 50000 AND salary=80000 <= 100000 ✓")
    print("不应该匹配:")
    print("  - David: salary=40000 <= 50000 AND department='HR' != 'Engineering' ✗")
    print("  - Eve: salary=120000 > 100000 ✗")
    
    expected_matches = ["Alice", "Bob", "Charlie"]
    actual_matches = [record["name"] for record in filtered_data]
    
    print(f"\n预期匹配: {expected_matches}")
    print(f"实际匹配: {actual_matches}")
    
    if set(expected_matches) == set(actual_matches):
        print("✅ 测试通过！过滤条件工作正常")
    else:
        print("❌ 测试失败！过滤条件未正确工作")
        missing = set(expected_matches) - set(actual_matches)
        extra = set(actual_matches) - set(expected_matches)
        if missing:
            print(f"缺少的记录: {missing}")
        if extra:
            print(f"多余的记录: {extra}")


async def test_simple_filter():
    """测试简单过滤条件仍然工作"""
    print("\n=== 测试简单过滤条件兼容性 ===")
    
    # 简单过滤配置
    simple_config = {
        "data_source": "employees",
        "dimensions": ["name", "salary"],
        "filters": [
            {
                "field": "salary",
                "operator": ">",
                "value": 50000
            },
            {
                "field": "department",
                "operator": "=", 
                "value": "Engineering"
            }
        ]
    }
    
    test_data = [
        {"name": "Alice", "salary": 60000, "department": "Engineering"},
        {"name": "Bob", "salary": 45000, "department": "Engineering"},
        {"name": "Charlie", "salary": 80000, "department": "Sales"}
    ]
    
    from src.steps.query_step import QueryStep
    query_step = QueryStep(simple_config)
    
    filtered_data = query_step._apply_filters(test_data, simple_config["filters"])
    
    print(f"原始数据: {len(test_data)} 条记录")
    print(f"过滤后数据: {len(filtered_data)} 条记录")
    
    # 应该只有Alice匹配（salary > 50000 AND department = 'Engineering'）
    expected_count = 1
    if len(filtered_data) == expected_count and filtered_data[0]["name"] == "Alice":
        print("✅ 简单过滤条件兼容性测试通过")
    else:
        print("❌ 简单过滤条件兼容性测试失败")


if __name__ == "__main__":
    asyncio.run(test_complex_filter_fix())
    asyncio.run(test_simple_filter())
