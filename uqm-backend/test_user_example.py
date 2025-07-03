#!/usr/bin/env python3
"""
测试用户提供的具体示例
"""
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.parser import UQMParser
from src.core.engine import UQMEngine

def test_user_example():
    """测试用户提供的具体示例"""
    
    # 读取示例文件
    with open('example_order_items_query.json', 'r', encoding='utf-8') as f:
        full_config = json.load(f)
    
    # 提取UQM配置和参数
    uqm_config = full_config['uqm']
    parameters = full_config['parameters']
    
    print("=== 测试用户示例：使用 ${order_id} 格式 ===")
    
    # 创建引擎实例
    engine = UQMEngine()
    
    try:
        # 解析配置
        parsed_data = engine.parser.parse(uqm_config)
        print("✓ 配置解析成功")
        
        # 进行参数替换
        processed_data = engine._substitute_parameters(parsed_data, parameters)
        print("✓ 参数替换成功")
        
        # 检查参数替换结果
        step_config = processed_data['steps'][0]['config']
        
        print("\n查询配置:")
        print(f"  数据源: {step_config['data_source']}")
        print(f"  维度字段: {step_config['dimensions']}")
        print(f"  计算字段: {step_config['calculated_fields']}")
        print(f"  连接: {step_config['joins']}")
        print(f"  过滤器: {step_config['filters']}")
        
        # 验证参数替换
        filter_item = step_config['filters'][0]
        if filter_item['value'] == 1:
            print(f"✓ order_id 参数替换成功: {filter_item['field']} {filter_item['operator']} {filter_item['value']}")
        else:
            print(f"✗ order_id 参数替换失败: {filter_item['value']}")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_user_example_both_formats():
    """测试两种格式的对比"""
    
    print("\n=== 格式对比测试 ===")
    
    # 创建两个版本的配置
    base_config = {
        "metadata": {
            "name": "GetOrderItemsDetails",
            "description": "查询特定订单的所有商品项及其详情",
            "version": "1.0",
            "author": "UQM Expert"
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
                        "products.product_name",
                        "order_items.quantity",
                        "order_items.unit_price",
                        "order_items.discount"
                    ],
                    "calculated_fields": [
                        {
                            "alias": "item_total_price",
                            "expression": "order_items.quantity * order_items.unit_price * (1 - order_items.discount)"
                        }
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
                            "value": "PLACEHOLDER"
                        }
                    ]
                }
            }
        ],
        "output": "query_order_items"
    }
    
    # 版本1：使用 ${order_id} 格式
    config_with_braces = json.loads(json.dumps(base_config))
    config_with_braces['steps'][0]['config']['filters'][0]['value'] = "${order_id}"
    
    # 版本2：使用 $order_id 格式
    config_without_braces = json.loads(json.dumps(base_config))
    config_without_braces['steps'][0]['config']['filters'][0]['value'] = "$order_id"
    
    parameters = {"order_id": 1}
    engine = UQMEngine()
    
    test_cases = [
        ("${order_id} 格式", config_with_braces),
        ("$order_id 格式", config_without_braces)
    ]
    
    for format_name, config in test_cases:
        print(f"\n--- 测试 {format_name} ---")
        try:
            parsed_data = engine.parser.parse(config)
            processed_data = engine._substitute_parameters(parsed_data, parameters)
            
            filter_value = processed_data['steps'][0]['config']['filters'][0]['value']
            print(f"参数替换结果: {filter_value}")
            
            if filter_value == 1:
                print(f"✓ {format_name} 测试成功")
            else:
                print(f"✗ {format_name} 测试失败")
                
        except Exception as e:
            print(f"✗ {format_name} 测试失败: {e}")

if __name__ == "__main__":
    test_user_example()
    test_user_example_both_formats()
