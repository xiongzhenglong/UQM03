#!/usr/bin/env python3
"""
测试客户属性宽转长修复
验证条件过滤器是否正确工作
"""

import asyncio
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'uqm-backend'))

from src.core.engine import get_uqm_engine


async def test_customer_unpivot_fix():
    """测试客户属性宽转长修复"""
    
    # 修复后的UQM配置
    uqm_config = {
        "uqm": {
            "metadata": {
                "name": "客户属性宽转长",
                "description": "将客户表中的邮箱、国家、城市、客户分层等属性宽转长，并自定义字段名。",
                "version": "1.0",
                "author": "UQM Expert",
                "tags": [
                    "customer",
                    "unpivot",
                    "attribute"
                ]
            },
            "parameters": [
                {
                    "name": "customer_ids",
                    "type": "array",
                    "default": None,
                    "description": "指定要处理的客户ID列表，如果为空则处理所有客户。"
                }
            ],
            "steps": [
                {
                    "name": "select_customer_attributes",
                    "type": "query",
                    "config": {
                        "data_source": "customers",
                        "dimensions": [
                            {
                                "expression": "customer_id",
                                "alias": "customer_id"
                            },
                            {
                                "expression": "customer_name",
                                "alias": "customer_name"
                            },
                            {
                                "expression": "email",
                                "alias": "email"
                            },
                            {
                                "expression": "country",
                                "alias": "country"
                            },
                            {
                                "expression": "city",
                                "alias": "city"
                            },
                            {
                                "expression": "registration_date",
                                "alias": "registration_date"
                            },
                            {
                                "expression": "customer_segment",
                                "alias": "customer_segment"
                            }
                        ],
                        "filters": [
                            {
                                "field": "customer_id",
                                "operator": "IN",
                                "value": "$customer_ids",
                                "conditional": {
                                    "type": "parameter_not_empty",
                                    "parameter": "customer_ids",
                                    "empty_values": [
                                        None,
                                        []
                                    ]
                                }
                            }
                        ]
                    }
                },
                {
                    "name": "unpivot_customer_attributes",
                    "type": "unpivot",
                    "config": {
                        "source": "select_customer_attributes",
                        "id_vars": [
                            "customer_id",
                            "customer_name",
                            "registration_date"
                        ],
                        "value_vars": [
                            "email",
                            "country",
                            "city",
                            "customer_segment"
                        ],
                        "var_name": "attribute_name",
                        "value_name": "attribute_value"
                    }
                }
            ],
            "output": "unpivot_customer_attributes"
        },
        "parameters": {
            "customer_ids": [1]
        },
        "options": {}
    }
    
    try:
        # 获取UQM引擎
        engine = get_uqm_engine()
        
        print("=== 测试客户属性宽转长修复 ===")
        print(f"参数: customer_ids = {uqm_config['parameters']['customer_ids']}")
        print()
        
        # 执行查询
        result = await engine.process(
            uqm_data=uqm_config["uqm"],
            parameters=uqm_config["parameters"],
            options=uqm_config["options"]
        )
        
        # 输出结果
        print("=== 执行结果 ===")
        print(f"成功: {result.success}")
        print(f"总行数: {result.execution_info['row_count']}")
        print(f"执行时间: {result.execution_info['total_time']:.4f}秒")
        print()
        
        # 输出步骤执行结果
        print("=== 步骤执行详情 ===")
        for step_result in result.step_results:
            print(f"步骤: {step_result.step_name}")
            print(f"  类型: {step_result.step_type}")
            print(f"  状态: {step_result.status}")
            print(f"  行数: {step_result.row_count}")
            print(f"  执行时间: {step_result.execution_time:.4f}秒")
            print(f"  缓存命中: {step_result.cache_hit}")
            if step_result.error:
                print(f"  错误: {step_result.error}")
            print()
        
        # 输出数据样本
        if result.data:
            print("=== 数据样本 ===")
            print(f"返回 {len(result.data)} 条记录:")
            for i, record in enumerate(result.data[:5]):  # 只显示前5条
                print(f"  {i+1}. {record}")
            if len(result.data) > 5:
                print(f"  ... 还有 {len(result.data) - 5} 条记录")
        else:
            print("=== 数据样本 ===")
            print("没有返回数据")
        
        print()
        print("=== 测试完成 ===")
        
        return result
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_without_filter():
    """测试不带过滤器的版本"""
    
    uqm_config = {
        "uqm": {
            "metadata": {
                "name": "客户属性宽转长_无过滤",
                "description": "不带过滤器的客户属性宽转长测试",
                "version": "1.0",
                "author": "UQM Expert",
                "tags": ["customer", "unpivot", "attribute"]
            },
            "parameters": [],
            "steps": [
                {
                    "name": "select_customer_attributes",
                    "type": "query",
                    "config": {
                        "data_source": "customers",
                        "dimensions": [
                            {"expression": "customer_id", "alias": "customer_id"},
                            {"expression": "customer_name", "alias": "customer_name"},
                            {"expression": "email", "alias": "email"},
                            {"expression": "country", "alias": "country"},
                            {"expression": "city", "alias": "city"},
                            {"expression": "registration_date", "alias": "registration_date"},
                            {"expression": "customer_segment", "alias": "customer_segment"}
                        ]
                    }
                },
                {
                    "name": "unpivot_customer_attributes",
                    "type": "unpivot",
                    "config": {
                        "source": "select_customer_attributes",
                        "id_vars": ["customer_id", "customer_name", "registration_date"],
                        "value_vars": ["email", "country", "city", "customer_segment"],
                        "var_name": "attribute_name",
                        "value_name": "attribute_value"
                    }
                }
            ],
            "output": "unpivot_customer_attributes"
        },
        "parameters": {},
        "options": {}
    }
    
    try:
        engine = get_uqm_engine()
        
        print("=== 测试无过滤器版本 ===")
        
        result = await engine.process(
            uqm_data=uqm_config["uqm"],
            parameters=uqm_config["parameters"],
            options=uqm_config["options"]
        )
        
        print(f"成功: {result.success}")
        print(f"总行数: {result.execution_info['row_count']}")
        print(f"执行时间: {result.execution_info['total_time']:.4f}秒")
        
        for step_result in result.step_results:
            print(f"步骤 {step_result.step_name}: {step_result.row_count} 行")
        
        return result
        
    except Exception as e:
        print(f"无过滤器测试失败: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(test_customer_unpivot_fix())
    print("\n" + "="*50 + "\n")
    asyncio.run(test_without_filter()) 