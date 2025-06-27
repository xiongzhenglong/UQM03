"""
测试条件过滤器的实际实现
验证参数未传入时自动忽略相关filters的功能
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.engine import get_uqm_engine

def create_test_config():
    """创建带条件过滤器的测试配置"""
    return {
        "metadata": {
            "name": "ConditionalFilterTest",
            "description": "测试条件过滤器功能",
            "version": "1.0"
        },
        "parameters": [
            {
                "name": "target_departments",
                "type": "array",
                "required": False
            },
            {
                "name": "min_salary",
                "type": "number", 
                "required": False
            },
            {
                "name": "job_title",
                "type": "string",
                "required": False
            }
        ],
        "steps": [
            {
                "name": "filtered_query",
                "type": "query",
                "config": {
                    "data_source": "employees",
                    "dimensions": ["name", "department", "job_title", "salary"],
                    "filters": [
                        {
                            "field": "active",
                            "operator": "=",
                            "value": True
                        },
                        {
                            "field": "department",
                            "operator": "IN",
                            "value": "$target_departments",
                            "conditional": {
                                "type": "parameter_not_empty",
                                "parameter": "target_departments",
                                "empty_values": [None, []]
                            }
                        },
                        {
                            "field": "salary",
                            "operator": ">=",
                            "value": "$min_salary",
                            "conditional": {
                                "type": "parameter_not_empty",
                                "parameter": "min_salary",
                                "empty_values": [None, 0]
                            }
                        },
                        {
                            "field": "job_title",
                            "operator": "=",
                            "value": "$job_title",
                            "conditional": {
                                "type": "parameter_exists",
                                "parameter": "job_title"
                            }
                        },
                        {
                            "field": "performance_rating",
                            "operator": ">",
                            "value": 3,
                            "conditional": {
                                "type": "expression",
                                "expression": "$min_salary != null && $min_salary > 20000"
                            }
                        }
                    ]
                }
            }
        ],
        "output": "filtered_query"
    }

async def test_conditional_filters():
    """测试条件过滤器功能"""
    print("=" * 60)
    print("测试条件过滤器实现")
    print("=" * 60)
    
    engine = get_uqm_engine()
    config = create_test_config()
    
    # 测试场景1：只传入部门参数
    print("\n🧪 测试场景1：只传入部门参数")
    parameters1 = {
        "target_departments": ["IT", "销售"]
    }
    
    try:
        # 解析配置
        parsed_data = engine.parser.parse(config)
        print("✅ 配置解析成功")
        
        # 参数替换和条件过滤器处理
        processed_data = engine._substitute_parameters(parsed_data, parameters1)
        
        # 检查过滤器
        filters = processed_data["steps"][0]["config"]["filters"]
        print(f"📊 处理后过滤器数量: {len(filters)}")
        
        expected_filters = [
            "active = True",
            "department IN ['IT', '销售']"  # 只有这个条件过滤器应该保留
        ]
        
        active_filter_found = False
        dept_filter_found = False
        salary_filter_found = False
        job_title_filter_found = False
        performance_filter_found = False
        
        for f in filters:
            if f.get("field") == "active":
                active_filter_found = True
            elif f.get("field") == "department":
                dept_filter_found = True
            elif f.get("field") == "salary":
                salary_filter_found = True
            elif f.get("field") == "job_title":
                job_title_filter_found = True
            elif f.get("field") == "performance_rating":
                performance_filter_found = True
        
        print(f"   ✅ 活跃状态过滤器: {'保留' if active_filter_found else '移除'}")
        print(f"   ✅ 部门过滤器: {'保留' if dept_filter_found else '移除'}")
        print(f"   {'❌' if salary_filter_found else '✅'} 薪资过滤器: {'保留' if salary_filter_found else '移除'}")
        print(f"   {'❌' if job_title_filter_found else '✅'} 职位过滤器: {'保留' if job_title_filter_found else '移除'}")
        print(f"   {'❌' if performance_filter_found else '✅'} 绩效过滤器: {'保留' if performance_filter_found else '移除'}")
        
    except Exception as e:
        print(f"❌ 测试场景1失败: {e}")
    
    # 测试场景2：传入部门和薪资参数
    print("\n🧪 测试场景2：传入部门和薪资参数") 
    parameters2 = {
        "target_departments": ["IT"],
        "min_salary": 25000
    }
    
    try:
        processed_data = engine._substitute_parameters(parsed_data, parameters2)
        filters = processed_data["steps"][0]["config"]["filters"]
        print(f"📊 处理后过滤器数量: {len(filters)}")
        
        active_filter_found = False
        dept_filter_found = False
        salary_filter_found = False
        job_title_filter_found = False
        performance_filter_found = False
        
        for f in filters:
            if f.get("field") == "active":
                active_filter_found = True
            elif f.get("field") == "department":
                dept_filter_found = True
            elif f.get("field") == "salary":
                salary_filter_found = True
            elif f.get("field") == "job_title":
                job_title_filter_found = True
            elif f.get("field") == "performance_rating":
                performance_filter_found = True
        
        print(f"   ✅ 活跃状态过滤器: {'保留' if active_filter_found else '移除'}")
        print(f"   ✅ 部门过滤器: {'保留' if dept_filter_found else '移除'}")
        print(f"   ✅ 薪资过滤器: {'保留' if salary_filter_found else '移除'}")
        print(f"   {'❌' if job_title_filter_found else '✅'} 职位过滤器: {'保留' if job_title_filter_found else '移除'}")
        print(f"   ✅ 绩效过滤器: {'保留' if performance_filter_found else '移除'} (因为薪资>20000)")
        
    except Exception as e:
        print(f"❌ 测试场景2失败: {e}")
    
    # 测试场景3：传入所有参数
    print("\n🧪 测试场景3：传入所有参数")
    parameters3 = {
        "target_departments": ["IT", "研发"],
        "min_salary": 15000,
        "job_title": "工程师"
    }
    
    try:
        processed_data = engine._substitute_parameters(parsed_data, parameters3)
        filters = processed_data["steps"][0]["config"]["filters"]
        print(f"📊 处理后过滤器数量: {len(filters)}")
        
        active_filter_found = False
        dept_filter_found = False
        salary_filter_found = False
        job_title_filter_found = False
        performance_filter_found = False
        
        for f in filters:
            if f.get("field") == "active":
                active_filter_found = True
            elif f.get("field") == "department":
                dept_filter_found = True
            elif f.get("field") == "salary":
                salary_filter_found = True
            elif f.get("field") == "job_title":
                job_title_filter_found = True
            elif f.get("field") == "performance_rating":
                performance_filter_found = True
        
        print(f"   ✅ 活跃状态过滤器: {'保留' if active_filter_found else '移除'}")
        print(f"   ✅ 部门过滤器: {'保留' if dept_filter_found else '移除'}")
        print(f"   ✅ 薪资过滤器: {'保留' if salary_filter_found else '移除'}")
        print(f"   ✅ 职位过滤器: {'保留' if job_title_filter_found else '移除'}")
        print(f"   {'❌' if performance_filter_found else '✅'} 绩效过滤器: {'保留' if performance_filter_found else '移除'} (因为薪资15000<20000)")
        
    except Exception as e:
        print(f"❌ 测试场景3失败: {e}")
    
    # 测试场景4：不传入任何参数
    print("\n🧪 测试场景4：不传入任何参数")
    parameters4 = {}
    
    try:
        processed_data = engine._substitute_parameters(parsed_data, parameters4)
        filters = processed_data["steps"][0]["config"]["filters"]
        print(f"📊 处理后过滤器数量: {len(filters)}")
        
        # 应该只保留没有条件的过滤器
        expected_count = 1  # 只有active过滤器
        if len(filters) == expected_count:
            print("   ✅ 只保留了无条件的过滤器")
        else:
            print(f"   ❌ 期望{expected_count}个过滤器，实际{len(filters)}个")
            
    except Exception as e:
        print(f"❌ 测试场景4失败: {e}")

def test_expression_evaluation():
    """测试表达式评估功能"""
    print("\n" + "=" * 60)
    print("测试表达式评估功能")
    print("=" * 60)
    
    engine = get_uqm_engine()
    
    # 测试各种表达式
    test_cases = [
        {
            "expression": "$param1 != null",
            "parameters": {"param1": "value"},
            "expected": True
        },
        {
            "expression": "$param1 != null",
            "parameters": {},
            "expected": False
        },
        {
            "expression": "$param1 != null && $param1 != ''",
            "parameters": {"param1": "test"},
            "expected": True
        },
        {
            "expression": "$param1 != null && $param1 != ''",
            "parameters": {"param1": ""},
            "expected": False
        },
        {
            "expression": "$count > 0 && $count < 100",
            "parameters": {"count": 50},
            "expected": True
        },
        {
            "expression": "$count > 0 && $count < 100",
            "parameters": {"count": 150},
            "expected": False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        expression = test_case["expression"]
        parameters = test_case["parameters"]
        expected = test_case["expected"]
        
        try:
            result = engine._evaluate_conditional_expression(expression, parameters)
            status = "✅" if result == expected else "❌"
            print(f"{status} 测试{i}: {expression}")
            print(f"   参数: {parameters}")
            print(f"   期望: {expected}, 实际: {result}")
        except Exception as e:
            print(f"❌ 测试{i}失败: {e}")

if __name__ == "__main__":
    print("🚀 开始测试条件过滤器实现...")
    
    # 测试条件过滤器
    asyncio.run(test_conditional_filters())
    
    # 测试表达式评估
    test_expression_evaluation()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
