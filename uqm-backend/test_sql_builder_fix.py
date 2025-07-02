#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQL构建器的复杂过滤条件支持
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.sql_builder import SQLBuilder


def test_sql_builder_complex_filters():
    """测试SQL构建器的复杂过滤条件"""
    print("=== 测试SQL构建器复杂过滤条件支持 ===")
    
    sql_builder = SQLBuilder()
    
    # 测试用户的复杂查询条件
    where_conditions = [
        {
            "logic": "AND",
            "conditions": [
                {
                    "logic": "OR",
                    "conditions": [
                        {
                            "logic": "AND",
                            "conditions": [
                                {
                                    "field": "employees.salary",
                                    "operator": ">",
                                    "value": 50000
                                },
                                {
                                    "field": "departments.name",
                                    "operator": "=",
                                    "value": "信息技术部"
                                }
                            ]
                        },
                        {
                            "logic": "AND",
                            "conditions": [
                                {
                                    "field": "employees.salary",
                                    "operator": ">",
                                    "value": 50000
                                },
                                {
                                    "field": "departments.name",
                                    "operator": "=",
                                    "value": "销售部"
                                }
                            ]
                        }
                    ]
                },
                {
                    "field": "employees.hire_date",
                    "operator": ">",
                    "value": "2022-01-01"
                }
            ]
        }
    ]
    
    # 构建完整的SQL查询
    select_fields = [
        "employees.employee_id",
        "employees.first_name",
        "employees.last_name",
        "employees.salary",
        "employees.hire_date",
        "departments.name AS department_name"
    ]
    
    joins = [
        {
            "type": "INNER",
            "table": "departments",
            "on": {
                "left": "employees.department_id",
                "right": "departments.department_id",
                "operator": "="
            }
        }
    ]
    
    query = sql_builder.build_select_query(
        select_fields=select_fields,
        from_table="employees",
        joins=joins,
        where_conditions=where_conditions
    )
    
    print("生成的SQL查询:")
    print(query)
    print()
    
    # 预期的WHERE子句模式
    expected_patterns = [
        "WHERE",
        "employees.salary > 50000",
        "departments.name = '信息技术部'",
        "departments.name = '销售部'",
        "employees.hire_date > '2022-01-01'",
        "AND",
        "OR"
    ]
    
    print("检查SQL是否包含预期的元素:")
    for pattern in expected_patterns:
        if pattern in query:
            print(f"✅ 包含: {pattern}")
        else:
            print(f"❌ 缺少: {pattern}")
    
    # 验证逻辑结构
    if "OR" in query and "AND" in query:
        print("\n✅ SQL包含AND/OR逻辑")
    else:
        print("\n❌ SQL缺少AND/OR逻辑")
    
    # 验证括号结构
    if "(" in query and ")" in query:
        print("✅ SQL包含括号分组")
    else:
        print("❌ SQL缺少括号分组")
    
    return query


def test_simple_filters_compatibility():
    """测试简单过滤器的向后兼容性"""
    print("\n=== 测试简单过滤器向后兼容性 ===")
    
    sql_builder = SQLBuilder()
    
    # 简单过滤器
    where_conditions = [
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
    
    query = sql_builder.build_select_query(
        select_fields=["*"],
        from_table="employees",
        where_conditions=where_conditions
    )
    
    print("简单过滤器生成的SQL:")
    print(query)
    
    # 验证向后兼容性
    expected_elements = ["salary > 50000", "department = 'Engineering'", "AND"]
    
    all_present = all(element in query for element in expected_elements)
    if all_present:
        print("✅ 简单过滤器向后兼容性测试通过")
    else:
        print("❌ 简单过滤器向后兼容性测试失败")
    
    return query


def test_in_and_between_operators():
    """测试IN和BETWEEN操作符"""
    print("\n=== 测试IN和BETWEEN操作符 ===")
    
    sql_builder = SQLBuilder()
    
    where_conditions = [
        {
            "logic": "AND",
            "conditions": [
                {
                    "field": "department",
                    "operator": "IN",
                    "value": ["Engineering", "Sales"]
                },
                {
                    "field": "salary",
                    "operator": "BETWEEN",
                    "value": {
                        "min": 30000,
                        "max": 80000
                    }
                },
                {
                    "field": "city",
                    "operator": "NOT IN",
                    "value": ["Beijing", "Shanghai"]
                }
            ]
        }
    ]
    
    query = sql_builder.build_select_query(
        select_fields=["*"],
        from_table="employees",
        where_conditions=where_conditions
    )
    
    print("IN/BETWEEN操作符生成的SQL:")
    print(query)
    
    # 验证操作符
    checks = [
        ("IN", "department IN ('Engineering', 'Sales')"),
        ("BETWEEN", "salary BETWEEN 30000 AND 80000"),
        ("NOT IN", "city NOT IN ('Beijing', 'Shanghai')")
    ]
    
    for operator, expected in checks:
        if expected in query:
            print(f"✅ {operator} 操作符正确")
        else:
            print(f"❌ {operator} 操作符错误")
    
    return query


if __name__ == "__main__":
    query1 = test_sql_builder_complex_filters()
    query2 = test_simple_filters_compatibility()
    query3 = test_in_and_between_operators()
    
    print("\n" + "="*60)
    print("SQL构建器复杂过滤条件测试完成")
    print("="*60)
