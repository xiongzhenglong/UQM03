#!/usr/bin/env python3
"""
测试多步骤查询功能
"""

import json
import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.engine import get_uqm_engine

async def test_multi_step_query():
    """测试多步骤查询"""
    
    # 测试查询配置
    uqm_data = {
        "metadata": {
            "name": "CalculateAverageRepurchaseRate_MultiStep",
            "description": "通过多步骤计算所有客户的平均复购率（复购客户数 / 至少购买过1次的客户总数）。",
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
                            "expression": "CASE WHEN order_count > 1 THEN 1 ELSE 0 END",
                            "alias": "is_repurchase_customer_flag"
                        },
                        {
                            "expression": "1",
                            "alias": "is_any_order_customer_flag"
                        }
                    ],
                    "metrics": []
                }
            },
            {
                "name": "calculate_average_repurchase_rate",
                "type": "query",
                "config": {
                    "data_source": "categorize_customers",
                    "dimensions": ["1"],
                    "metrics": [
                        {
                            "expression": "CAST(SUM(is_repurchase_customer_flag) AS DECIMAL(10, 4)) / NULLIF(CAST(SUM(is_any_order_customer_flag) AS DECIMAL(10, 4)), 0)",
                            "alias": "average_repurchase_rate"
                        }
                    ]
                }
            }
        ],
        "output": "calculate_average_repurchase_rate"
    }
    
    try:
        # 获取UQM引擎
        engine = get_uqm_engine()
        
        # 执行查询
        result = await engine.process(uqm_data)
        
        print("查询执行成功!")
        print(f"结果: {json.dumps(result.dict(), indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"查询执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_multi_step_query())
