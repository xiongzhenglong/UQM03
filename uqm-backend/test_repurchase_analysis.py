#!/usr/bin/env python3
"""
测试复购分析功能
"""

import json
import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.engine import get_uqm_engine

async def test_repurchase_analysis():
    """测试复购分析"""
    
    print("=== 测试1: 统计所有客户的平均复购率 ===")
    
    # 优化后的复购率计算查询
    repurchase_rate_query = {
        "metadata": {
            "name": "CalculateAverageRepurchaseRate",
            "description": "计算所有客户的平均复购率",
            "version": "1.0",
            "author": "UQM Expert"
        },
        "steps": [
            {
                "name": "get_customer_order_counts",
                "type": "query",
                "config": {
                    "data_source": "orders",
                    "dimensions": ["customer_id"],
                    "metrics": [
                        {
                            "name": "order_id",
                            "aggregation": "COUNT",
                            "alias": "order_count"
                        }
                    ],
                    "group_by": ["customer_id"]
                }
            },
            {
                "name": "categorize_customers",
                "type": "query",
                "config": {
                    "data_source": "get_customer_order_counts",
                    "dimensions": [
                        "customer_id",
                        {
                            "expression": "1 if order_count > 1 else 0",
                            "alias": "is_repurchase_customer"
                        }
                    ]
                }
            },
            {
                "name": "calculate_repurchase_rate",
                "type": "query",
                "config": {
                    "data_source": "categorize_customers",
                    "metrics": [
                        {
                            "name": "is_repurchase_customer",
                            "aggregation": "SUM", 
                            "alias": "repurchase_customers"
                        },
                        {
                            "name": "customer_id",
                            "aggregation": "COUNT",
                            "alias": "total_customers"
                        }
                    ]
                }
            }
        ],
        "output": "calculate_repurchase_rate"
    }
    
    try:
        engine = get_uqm_engine()
        result = await engine.process(repurchase_rate_query)
        
        print("查询执行成功!")
        data = result.data[0] if result.data else {}
        repurchase_customers = data.get('repurchase_customers', 0)
        total_customers = data.get('total_customers', 0)
        repurchase_rate = repurchase_customers / total_customers if total_customers > 0 else 0
        
        print(f"复购客户数: {repurchase_customers}")
        print(f"总客户数: {total_customers}")
        print(f"平均复购率: {repurchase_rate:.2%}")
        
    except Exception as e:
        print(f"查询执行失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试2: 找出复购次数最多的客户 ===")
    
    # 复购次数最多的客户查询
    top_repurchase_query = {
        "metadata": {
            "name": "FindTopRepurchaseCustomers",
            "description": "找出复购次数最多的客户",
            "version": "1.0",
            "author": "UQM Expert"
        },
        "steps": [
            {
                "name": "get_customer_order_counts",
                "type": "query",
                "config": {
                    "data_source": "orders",
                    "joins": [
                        {
                            "type": "INNER",
                            "table": "customers",
                            "on": "orders.customer_id = customers.customer_id"
                        }
                    ],
                    "dimensions": [
                        "customers.customer_id",
                        "customers.customer_name"
                    ],
                    "metrics": [
                        {
                            "name": "orders.order_id",
                            "aggregation": "COUNT",
                            "alias": "order_count"
                        }
                    ],
                    "group_by": ["customers.customer_id", "customers.customer_name"],
                    "order_by": [
                        {
                            "field": "order_count",
                            "direction": "DESC"
                        }
                    ],
                    "limit": 10
                }
            },
            {
                "name": "filter_repurchase_customers",
                "type": "query",
                "config": {
                    "data_source": "get_customer_order_counts",
                    "dimensions": ["customer_id", "customer_name", "order_count"],
                    "filters": [
                        {
                            "field": "order_count",
                            "operator": ">",
                            "value": 1
                        }
                    ]
                }
            }
        ],
        "output": "filter_repurchase_customers"
    }
    
    try:
        result = await engine.process(top_repurchase_query)
        
        print("查询执行成功!")
        if result.data:
            print("复购次数最多的客户:")
            for i, customer in enumerate(result.data, 1):
                print(f"{i}. {customer.get('customer_name')} - {customer.get('order_count')}次订单")
        else:
            print("没有找到复购客户")
            
    except Exception as e:
        print(f"查询执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_repurchase_analysis())
