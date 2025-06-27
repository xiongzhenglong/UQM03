#!/usr/bin/env python3
"""
调试多步骤复购率计算问题
"""

import json
import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.engine import get_uqm_engine

async def debug_multi_step():
    """调试多步骤查询"""
    
    print("=== 调试原始多步骤查询 ===")
    
    # 原始的有问题的配置
    original_config = {
        "metadata": {
            "name": "CalculateAverageRepurchaseRate_MultiStep_Debug",
            "description": "调试多步骤复购率计算",
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
                        "order_count",
                        {
                            "expression": "CASE WHEN order_count > 1 THEN 1 ELSE 0 END",
                            "alias": "is_repurchase_customer"
                        }
                    ]
                }
            },
            {
                "name": "calculate_final_rate",
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
                        },
                        {
                            "expression": "CAST(SUM(is_repurchase_customer) AS DECIMAL(10,4)) / CAST(COUNT(customer_id) AS DECIMAL(10,4))",
                            "alias": "repurchase_rate"
                        }
                    ]
                }
            }
        ],
        "output": "calculate_final_rate"
    }
    
    try:
        engine = get_uqm_engine()
        result = await engine.process(original_config)
        
        print("查询执行成功!")
        print(f"结果: {json.dumps(result.data, indent=2, ensure_ascii=False)}")
        
        # 分步调试
        print("\n=== 分步调试 ===")
        
        # 第1步
        step1_config = {
            "metadata": {
                "name": "Step1_Debug",
                "description": "第1步调试",
                "version": "1.0"
            },
            "steps": [original_config["steps"][0]],
            "output": "get_customer_order_counts"
        }
        
        result1 = await engine.process(step1_config)
        print(f"第1步结果:")
        print(json.dumps(result1.data, indent=2, ensure_ascii=False))
        
        # 第2步
        step2_config = {
            "metadata": {
                "name": "Step2_Debug",
                "description": "第2步调试",
                "version": "1.0"
            },
            "steps": original_config["steps"][:2],
            "output": "categorize_customers"
        }
        
        result2 = await engine.process(step2_config)
        print(f"\n第2步结果:")
        print(json.dumps(result2.data, indent=2, ensure_ascii=False))
        
        # 手动验证第2步结果
        print(f"\n第2步手动验证:")
        for customer in result2.data:
            order_count = customer.get('order_count', 0)
            is_repurchase = customer.get('is_repurchase_customer')
            expected = 1 if order_count > 1 else 0
            print(f"Customer {customer.get('customer_id')}: order_count={order_count}, is_repurchase={is_repurchase}, expected={expected}")
        
        # 第3步
        result3 = await engine.process(original_config)
        print(f"\n第3步结果:")
        print(json.dumps(result3.data, indent=2, ensure_ascii=False))
        
        # 手动计算验证
        repurchase_count = sum(1 for c in result2.data if c.get('is_repurchase_customer') == 1)
        total_count = len(result2.data)
        manual_rate = repurchase_count / total_count if total_count > 0 else 0
        
        print(f"\n手动计算验证:")
        print(f"复购客户数: {repurchase_count}")
        print(f"总客户数: {total_count}")
        print(f"手动计算复购率: {manual_rate:.4f}")
        
        final_result = result3.data[0] if result3.data else {}
        print(f"系统计算复购客户数: {final_result.get('repurchase_customers')}")
        print(f"系统计算总客户数: {final_result.get('total_customers')}")
        print(f"系统计算复购率: {final_result.get('repurchase_rate')}")
        
    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_multi_step())
