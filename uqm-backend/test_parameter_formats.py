#!/usr/bin/env python3
"""
测试参数引用的两种格式：${param_name} 和 $param_name
"""
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.parser import UQMParser
from src.core.engine import UQMEngine

def test_parameter_formats():
    """测试两种参数格式"""
    
    # 测试用例1：使用 ${param_name} 格式
    uqm_config_with_braces = {
        "metadata": {
            "name": "test_braces_format",
            "description": "测试${param_name}格式的参数引用",
            "version": "1.0"
        },
        "steps": [
            {
                "name": "query_order_items",
                "type": "query",
                "config": {
                    "data_source": "order_items",
                    "dimensions": [
                        "order_items.order_item_id",
                        "order_items.order_id",
                        "products.product_name"
                    ],
                    "joins": [
                        {
                            "type": "INNER",
                            "table": "products",
                            "on": "order_items.product_id = products.product_id"
                        }
                    ],
                    "filters": [
                        {
                            "field": "order_items.order_id",
                            "operator": "=",
                            "value": "${order_id}"
                        },
                        {
                            "field": "products.category",
                            "operator": "=",
                            "value": "${category}"
                        }
                    ]
                }
            }
        ],
        "output": "query_order_items"
    }
    
    # 测试用例2：使用 $param_name 格式
    uqm_config_without_braces = {
        "metadata": {
            "name": "test_no_braces_format",
            "description": "测试$param_name格式的参数引用",
            "version": "1.0"
        },
        "steps": [
            {
                "name": "query_order_items",
                "type": "query",
                "config": {
                    "data_source": "order_items",
                    "dimensions": [
                        "order_items.order_item_id",
                        "order_items.order_id",
                        "products.product_name"
                    ],
                    "joins": [
                        {
                            "type": "INNER",
                            "table": "products",
                            "on": "order_items.product_id = products.product_id"
                        }
                    ],
                    "filters": [
                        {
                            "field": "order_items.order_id",
                            "operator": "=",
                            "value": "$order_id"
                        },
                        {
                            "field": "products.category",
                            "operator": "=",
                            "value": "$category"
                        }
                    ]
                }
            }
        ],
        "output": "query_order_items"
    }
    
    # 测试用例3：混合使用两种格式
    uqm_config_mixed = {
        "metadata": {
            "name": "test_mixed_format",
            "description": "测试混合使用两种格式的参数引用",
            "version": "1.0"
        },
        "steps": [
            {
                "name": "query_order_items",
                "type": "query",
                "config": {
                    "data_source": "order_items",
                    "dimensions": [
                        "order_items.order_item_id",
                        "order_items.order_id",
                        "products.product_name"
                    ],
                    "joins": [
                        {
                            "type": "INNER",
                            "table": "products",
                            "on": "order_items.product_id = products.product_id"
                        }
                    ],
                    "filters": [
                        {
                            "field": "order_items.order_id",
                            "operator": "=",
                            "value": "${order_id}"
                        },
                        {
                            "field": "products.category",
                            "operator": "=",
                            "value": "$category"
                        }
                    ]
                }
            }
        ],
        "output": "query_order_items"
    }
    
    # 创建引擎实例
    engine = UQMEngine()
    
    # 测试参数
    parameters = {
        "order_id": 1,
        "category": "Electronics"
    }
    
    test_cases = [
        ("${param_name} 格式", uqm_config_with_braces),
        ("$param_name 格式", uqm_config_without_braces),
        ("混合格式", uqm_config_mixed)
    ]
    
    for test_name, config in test_cases:
        print(f"\n=== 测试 {test_name} ===")
        try:
            # 解析配置
            parsed_data = engine.parser.parse(config)
            print(f"✓ 配置解析成功")
            
            # 进行参数替换
            processed_data = engine._substitute_parameters(parsed_data, parameters)
            print(f"✓ 参数替换成功")
            
            # 检查参数是否被正确替换
            filters = processed_data['steps'][0]['config']['filters']
            
            print(f"过滤器配置:")
            for i, filter_item in enumerate(filters):
                print(f"  Filter {i+1}: {filter_item['field']} {filter_item['operator']} {filter_item['value']}")
                
            # 验证参数值
            order_id_filter = filters[0]
            category_filter = filters[1]
            
            if order_id_filter['value'] == 1:
                print(f"✓ order_id 参数替换成功: {order_id_filter['value']}")
            else:
                print(f"✗ order_id 参数替换失败: {order_id_filter['value']}")
                
            if category_filter['value'] == "Electronics":
                print(f"✓ category 参数替换成功: {category_filter['value']}")
            else:
                print(f"✗ category 参数替换失败: {category_filter['value']}")
                
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_parameter_formats()
