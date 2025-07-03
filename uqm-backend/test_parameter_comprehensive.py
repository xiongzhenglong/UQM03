#!/usr/bin/env python3
"""
测试参数引用的各种使用场景
"""
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.parser import UQMParser
from src.core.engine import UQMEngine

def test_comprehensive_parameter_scenarios():
    """测试各种参数使用场景"""
    
    # 测试用例：各种类型的参数
    uqm_config = {
        "metadata": {
            "name": "comprehensive_parameter_test",
            "description": "测试各种类型的参数引用",
            "version": "1.0"
        },
        "steps": [
            {
                "name": "query_complex",
                "type": "query",
                "config": {
                    "data_source": "employees",
                    "dimensions": [
                        "employee_id",
                        "first_name",
                        "last_name"
                    ],
                    "calculated_fields": [
                        {
                            "alias": "full_name",
                            "expression": "CONCAT(first_name, ' ', last_name)"
                        },
                        {
                            "alias": "salary_category",
                            "expression": "CASE WHEN salary > ${high_salary_threshold} THEN 'High' WHEN salary > $medium_salary_threshold THEN 'Medium' ELSE 'Low' END"
                        }
                    ],
                    "filters": [
                        {
                            "field": "department_id",
                            "operator": "IN",
                            "value": "${department_ids}"
                        },
                        {
                            "field": "salary",
                            "operator": "BETWEEN",
                            "value": "$salary_range"
                        },
                        {
                            "field": "is_active",
                            "operator": "=",
                            "value": "${is_active}"
                        },
                        {
                            "field": "first_name",
                            "operator": "LIKE",
                            "value": "$name_pattern"
                        }
                    ],
                    "order_by": [
                        {
                            "field": "salary",
                            "direction": "DESC"
                        }
                    ],
                    "limit": "$limit_count"
                }
            }
        ],
        "output": "query_complex"
    }
    
    # 测试参数（包含各种类型）
    parameters = {
        "department_ids": [1, 2, 3],          # 数组
        "salary_range": [5000, 15000],        # 数组作为BETWEEN值
        "high_salary_threshold": 12000,       # 数字
        "medium_salary_threshold": 8000,      # 数字
        "is_active": True,                    # 布尔值
        "name_pattern": "John%",              # 字符串
        "limit_count": 50                     # 数字
    }
    
    # 创建引擎实例
    engine = UQMEngine()
    
    print("=== 测试综合参数场景 ===")
    try:
        # 解析配置
        parsed_data = engine.parser.parse(uqm_config)
        print("✓ 配置解析成功")
        
        # 进行参数替换
        processed_data = engine._substitute_parameters(parsed_data, parameters)
        print("✓ 参数替换成功")
        
        # 检查各种参数替换结果
        step_config = processed_data['steps'][0]['config']
        
        print("\n计算字段:")
        for i, calc_field in enumerate(step_config['calculated_fields']):
            print(f"  {calc_field['alias']}: {calc_field['expression']}")
        
        print("\n过滤器配置:")
        for i, filter_item in enumerate(step_config['filters']):
            print(f"  Filter {i+1}: {filter_item['field']} {filter_item['operator']} {filter_item['value']}")
        
        print(f"\nLimit: {step_config.get('limit', 'N/A')}")
        
        # 验证具体的参数替换
        filters = step_config['filters']
        
        # 验证数组参数
        if filters[0]['value'] == [1, 2, 3]:
            print("✓ department_ids 数组参数替换成功")
        else:
            print("✗ department_ids 数组参数替换失败")
        
        # 验证BETWEEN参数
        if filters[1]['value'] == [5000, 15000]:
            print("✓ salary_range BETWEEN参数替换成功")
        else:
            print("✗ salary_range BETWEEN参数替换失败")
        
        # 验证布尔参数
        if filters[2]['value'] is True:
            print("✓ is_active 布尔参数替换成功")
        else:
            print("✗ is_active 布尔参数替换失败")
        
        # 验证字符串参数
        if filters[3]['value'] == "John%":
            print("✓ name_pattern 字符串参数替换成功")
        else:
            print("✗ name_pattern 字符串参数替换失败")
        
        # 验证数字参数
        if step_config['limit'] == 50:
            print("✓ limit_count 数字参数替换成功")
        else:
            print("✗ limit_count 数字参数替换失败")
            
        # 验证表达式中的参数
        salary_category_expr = step_config['calculated_fields'][1]['expression']
        if "12000" in salary_category_expr and "8000" in salary_category_expr:
            print("✓ 表达式中的参数替换成功")
        else:
            print("✗ 表达式中的参数替换失败")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_edge_cases():
    """测试边界情况"""
    
    print("\n=== 测试边界情况 ===")
    
    # 测试包含特殊字符的参数名
    uqm_config = {
        "metadata": {
            "name": "edge_case_test",
            "description": "测试边界情况",
            "version": "1.0"
        },
        "steps": [
            {
                "name": "query_edge",
                "type": "query",
                "config": {
                    "data_source": "test_table",
                    "dimensions": ["id"],
                    "filters": [
                        {
                            "field": "field1",
                            "operator": "=",
                            "value": "${param_with_underscore}"
                        },
                        {
                            "field": "field2",
                            "operator": "=",
                            "value": "$param123"
                        },
                        {
                            "field": "field3",
                            "operator": "=",
                            "value": "${param_with_number_123}"
                        }
                    ]
                }
            }
        ],
        "output": "query_edge"
    }
    
    parameters = {
        "param_with_underscore": "test_value",
        "param123": 456,
        "param_with_number_123": "special_value"
    }
    
    engine = UQMEngine()
    
    try:
        # 解析和替换
        parsed_data = engine.parser.parse(uqm_config)
        processed_data = engine._substitute_parameters(parsed_data, parameters)
        
        filters = processed_data['steps'][0]['config']['filters']
        
        print("边界情况测试结果:")
        for i, filter_item in enumerate(filters):
            print(f"  Filter {i+1}: {filter_item['field']} = {filter_item['value']}")
        
        # 验证结果
        if (filters[0]['value'] == "test_value" and 
            filters[1]['value'] == 456 and
            filters[2]['value'] == "special_value"):
            print("✓ 边界情况测试通过")
        else:
            print("✗ 边界情况测试失败")
            
    except Exception as e:
        print(f"✗ 边界情况测试失败: {e}")

if __name__ == "__main__":
    test_comprehensive_parameter_scenarios()
    test_edge_cases()
