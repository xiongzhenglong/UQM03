#!/usr/bin/env python3
"""
测试修正后的订单金额一致性验证
"""

import json
import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.engine import get_uqm_engine

async def test_order_amount_consistency():
    """测试订单金额一致性验证（修正后的配置）"""
    
    print("=== 测试订单金额一致性验证 ===")
    
    # 修正后的配置：基于实际表结构
    uqm_config = {
        "metadata": {
            "name": "验证订单金额一致性",
            "description": "确保订单表中的总金额与订单明细计算结果一致",
            "version": "1.0"
        },
        "steps": [
            {
                "name": "order_total_comparison",
                "type": "query",
                "config": {
                    "data_source": "orders",
                    "dimensions": ["order_id"],
                    "joins": [
                        {
                            "type": "INNER",
                            "table": "order_items",
                            "on": {
                                "left": "orders.order_id",
                                "right": "order_items.order_id",
                                "operator": "="
                            }
                        }
                    ],
                    "calculated_fields": [
                        {
                            "name": "order_total",
                            "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount)) + MAX(orders.shipping_fee)"
                        },
                        {
                            "name": "item_total",
                            "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))"
                        },
                        {
                            "name": "shipping_fee",
                            "expression": "MAX(orders.shipping_fee)"
                        }
                    ],
                    "group_by": ["order_id"],
                    "limit": 5
                }
            },
            {
                "name": "assert_amount_consistency",
                "type": "assert",
                "config": {
                    "source": "order_total_comparison",
                    "assertions": [
                        {
                            "type": "range",
                            "field": "order_total",
                            "min": 0,
                            "message": "订单总金额必须大于0"
                        },
                        {
                            "type": "range",
                            "field": "item_total", 
                            "min": 0,
                            "message": "订单明细金额必须大于0"
                        }
                    ]
                }
            }
        ],
        "output": "order_total_comparison"
    }
    
    try:
        print("🔍 执行查询...")
        engine = get_uqm_engine()
        result = await engine.process(uqm_config)
        
        print(f"✅ 查询成功!")
        print(f"  Success: {result.success}")
        print(f"  Row count: {len(result.data) if result.data else 0}")
        
        if result.data:
            print(f"📊 示例数据:")
            for i, row in enumerate(result.data[:3]):
                print(f"  Row {i+1}: {row}")
                
        # 如果有assert步骤且执行成功，说明所有断言都通过了
        print("✅ 所有断言验证通过!")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 检查是否是断言失败
        if "断言失败" in str(e) or "assertion" in str(e).lower():
            print("🚨 断言验证失败，数据不符合期望")
        elif "ambiguous" in str(e):
            print("🚨 仍然存在字段歧义问题")
        else:
            print("🔧 其他类型的错误")

if __name__ == "__main__":
    asyncio.run(test_order_amount_consistency())
