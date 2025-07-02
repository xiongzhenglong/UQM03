#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试实际的复杂员工筛选查询用例
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


async def test_real_complex_employee_query():
    """测试真实的复杂员工筛选查询"""
    print("=== 测试实际复杂员工筛选查询用例 ===")
    
    # 使用真实的复杂参数查询配置
    query_config = {
        "query_id": "complex_employee_filter",
        "description": "复杂员工筛选查询",
        "steps": [
            {
                "step_id": "complex_employee_query",
                "type": "query",
                "config": {
                    "data_source": "employees",
                    "dimensions": [
                        "employees.employee_id",
                        "employees.name",
                        "employees.salary",
                        "departments.name AS department_name",
                        "employees.hire_date"
                    ],
                    "joins": [
                        {
                            "type": "LEFT JOIN",
                            "table": "departments",
                            "on": "employees.department_id = departments.department_id"
                        }
                    ],
                    "filters": [
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
                                                    "value": "$minItSalary"
                                                },
                                                {
                                                    "field": "departments.name",
                                                    "operator": "=",
                                                    "value": "$itDepartment"
                                                }
                                            ]
                                        },
                                        {
                                            "logic": "AND",
                                            "conditions": [
                                                {
                                                    "field": "employees.salary",
                                                    "operator": ">",
                                                    "value": "$minSalesSalary"
                                                },
                                                {
                                                    "field": "departments.name",
                                                    "operator": "=",
                                                    "value": "$salesDepartment"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "field": "employees.hire_date",
                                    "operator": ">",
                                    "value": "$hireAfterDate"
                                }
                            ]
                        }
                    ]
                }
            }
        ],
        "output": "complex_employee_filter"
    }
    
    # 测试参数
    parameters = {
        "minItSalary": 60000,
        "itDepartment": "信息技术部",
        "minSalesSalary": 80000,
        "salesDepartment": "销售部",
        "hireAfterDate": "2020-01-01"
    }
    
    # 创建模拟数据
    mock_employees_data = [
        {
            "employees.employee_id": 1,
            "employees.name": "张三",
            "employees.salary": 65000,
            "departments.name": "信息技术部",
            "employees.hire_date": "2021-03-15"
        },
        {
            "employees.employee_id": 2,
            "employees.name": "李四",
            "employees.salary": 55000,
            "departments.name": "信息技术部",
            "employees.hire_date": "2021-06-01"
        },
        {
            "employees.employee_id": 3,
            "employees.name": "王五",
            "employees.salary": 85000,
            "departments.name": "销售部",
            "employees.hire_date": "2020-08-10"
        },
        {
            "employees.employee_id": 4,
            "employees.name": "赵六",
            "employees.salary": 75000,
            "departments.name": "销售部",
            "employees.hire_date": "2019-12-01"
        },
        {
            "employees.employee_id": 5,
            "employees.name": "孙七",
            "employees.salary": 70000,
            "departments.name": "人力资源部",
            "employees.hire_date": "2021-01-20"
        }
    ]
    
    print(f"模拟员工数据: {len(mock_employees_data)} 条记录")
    for record in mock_employees_data:
        print(f"  {record}")
    
    # 手动测试过滤逻辑
    from src.steps.query_step import QueryStep
    from src.core.engine import UQMEngine
    
    # 创建UQM引擎来处理参数替换
    engine = UQMEngine()
    
    # 替换参数
    resolved_config = engine._substitute_parameters(query_config, parameters)
    
    print(f"\n参数替换后的过滤器:")
    print(json.dumps(resolved_config["steps"][0]["config"]["filters"], indent=2, ensure_ascii=False))
    
    # 应用过滤器
    query_step = QueryStep(resolved_config["steps"][0]["config"])
    filters = resolved_config["steps"][0]["config"]["filters"]
    filtered_data = query_step._apply_filters(mock_employees_data, filters)
    
    print(f"\n过滤后数据: {len(filtered_data)} 条记录")
    for record in filtered_data:
        print(f"  {record}")
    
    print("\n=== 过滤条件分析 ===")
    print("条件: ((salary > 60000 AND dept = '信息技术部') OR (salary > 80000 AND dept = '销售部')) AND hire_date > '2020-01-01'")
    print("应该匹配:")
    print("  - 张三: salary=65000 > 60000 AND dept='信息技术部' AND hire_date='2021-03-15' > '2020-01-01' ✓")
    print("  - 王五: salary=85000 > 80000 AND dept='销售部' AND hire_date='2020-08-10' > '2020-01-01' ✓")
    print("不应该匹配:")
    print("  - 李四: salary=55000 <= 60000 ✗")
    print("  - 赵六: hire_date='2019-12-01' <= '2020-01-01' ✗")
    print("  - 孙七: dept='人力资源部' 不匹配任何部门条件 ✗")
    
    expected_matches = ["张三", "王五"]
    actual_matches = [record["employees.name"] for record in filtered_data]
    
    print(f"\n预期匹配: {expected_matches}")
    print(f"实际匹配: {actual_matches}")
    
    if set(expected_matches) == set(actual_matches):
        print("✅ 复杂参数查询测试通过！过滤条件工作正常")
        return True
    else:
        print("❌ 复杂参数查询测试失败！过滤条件未正确工作")
        missing = set(expected_matches) - set(actual_matches)
        extra = set(actual_matches) - set(expected_matches)
        if missing:
            print(f"缺少的记录: {missing}")
        if extra:
            print(f"多余的记录: {extra}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_real_complex_employee_query())
    if result:
        print("\n🎉 修复成功！UQM框架现在支持复杂的嵌套AND/OR过滤条件")
    else:
        print("\n❌ 修复仍有问题，需要进一步调试")
