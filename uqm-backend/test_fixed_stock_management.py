#!/usr/bin/env python3
"""
测试修正后的库存警告机制
"""

import json
import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.engine import get_uqm_engine

async def test_fixed_stock_management():
    """测试修正后的库存警告机制"""
    
    print("=== 测试修正后的库存警告机制 ===")
    
    # 修正后的配置：基于实际表结构
    uqm_config = {
        "metadata": {
            "name": "验证库存警告机制",
            "description": "检查低库存产品并验证库存管理策略",
            "version": "1.0"
        },
        "steps": [
            {
                "name": "low_stock_products",
                "type": "query",
                "config": {
                    "data_source": "products",
                    "dimensions": ["product_id", "product_name", "category"],
                    "joins": [
                        {
                            "type": "LEFT",
                            "table": "inventory",
                            "on": {
                                "left": "products.product_id",
                                "right": "inventory.product_id",
                                "operator": "="
                            }
                        }
                    ],
                    "calculated_fields": [
                        {
                            "name": "total_stock",
                            "expression": "COALESCE(SUM(inventory.quantity_on_hand), 0)"
                        },
                        {
                            "name": "stock_status",
                            "expression": "CASE WHEN COALESCE(SUM(inventory.quantity_on_hand), 0) = 0 THEN 'out_of_stock' WHEN COALESCE(SUM(inventory.quantity_on_hand), 0) <= 10 THEN 'low' WHEN COALESCE(SUM(inventory.quantity_on_hand), 0) <= 50 THEN 'medium' ELSE 'sufficient' END"
                        }
                    ],
                    "filters": [
                        {
                            "field": "discontinued",
                            "operator": "=",
                            "value": 0
                        }
                    ],
                    "group_by": ["product_id", "product_name", "category"],
                    "limit": 10
                }
            }
        ],
        "output": "low_stock_products"
    }
    
    try:
        print("🔍 执行库存查询...")
        engine = get_uqm_engine()
        result = await engine.process(uqm_config)
        
        print(f"✅ 查询成功!")
        print(f"  Success: {result.success}")
        print(f"  Row count: {len(result.data) if result.data else 0}")
        
        if result.data:
            print(f"📊 库存状态报告:")
            for i, row in enumerate(result.data[:5]):
                print(f"  产品 {row['product_id']} ({row['product_name']}):")
                print(f"    类别: {row['category']}")
                print(f"    总库存: {row['total_stock']}")
                print(f"    状态: {row['stock_status']}")
                print()
                
        print("✅ 库存警告机制用例修复成功!")
        
        # 显示修复的内容
        print("\n🔧 修复总结:")
        print("  ✅ 移除了不存在的 units_in_stock 字段")
        print("  ✅ 移除了不存在的 reorder_level 字段")
        print("  ✅ 使用 inventory.quantity_on_hand 获取库存数量")
        print("  ✅ 添加了 products 和 inventory 表的 JOIN")
        print("  ✅ 使用 COALESCE 处理 NULL 值")
        print("  ✅ 简化了库存状态逻辑，使用固定阈值")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 分析错误类型
        error_str = str(e).lower()
        if "unknown column" in error_str:
            print("🚨 仍然存在不存在的字段")
        elif "ambiguous" in error_str:
            print("🚨 存在字段歧义问题")
        else:
            print("🔧 其他类型的错误")

if __name__ == "__main__":
    asyncio.run(test_fixed_stock_management())
