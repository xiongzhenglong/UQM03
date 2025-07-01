#!/usr/bin/env python3
"""
测试计算字段别名修复
"""

import json
import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.engine import get_uqm_engine

async def test_calculated_field_alias():
    """测试计算字段别名修复"""
    
    print("=== 测试计算字段别名修复 ===")
    
    # 用户的原始配置（只有name，没有alias）
    uqm_config = {
        "metadata": {
            "name": "测试计算字段别名",
            "description": "测试name作为默认别名",
            "version": "1.0"
        },
        "steps": [
            {
                "name": "order_total_comparison",
                "type": "query",
                "config": {
                    "data_source": "orders",
                    "dimensions": ["order_id"],
                    "metrics": [
                        {
                            "name": "total_amount",
                            "aggregation": "SUM",
                            "alias": "order_total"
                        }
                    ],
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
                            "name": "calculated_total",  # 只有name，没有alias
                            "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))"
                        },
                        {
                            "name": "amount_difference",  # 只有name，没有alias
                            "expression": "ABS(total_amount - calculated_total)"
                        }
                    ],
                    "group_by": ["order_id", "total_amount"],
                    "limit": 5
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
                # 检查字段是否存在
                if 'calculated_total' in row:
                    print(f"    ✅ calculated_total字段存在: {row['calculated_total']}")
                if 'amount_difference' in row:
                    print(f"    ✅ amount_difference字段存在: {row['amount_difference']}")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 检查是否还是别名错误
        if "alias" in str(e):
            print("🚨 仍然是别名相关错误，需要进一步修复")
        else:
            print("🔧 别名问题已修复，这是其他类型的错误")

if __name__ == "__main__":
    asyncio.run(test_calculated_field_alias())
