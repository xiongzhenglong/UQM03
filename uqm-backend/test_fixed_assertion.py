#!/usr/bin/env python3
"""
测试修复后的完整流程
"""

import json
import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.engine import get_uqm_engine

async def test_fixed_assertion():
    """测试修复后的断言流程"""
    
    print("=== 测试修复后的完整断言流程 ===")
    
    # 测试1: 断言失败的情况
    print("\n🔍 测试1: 断言应该失败的情况")
    uqm_config_fail = {
        "metadata": {
            "name": "测试断言失败",
            "version": "1.0"
        },
        "steps": [
            {
                "name": "product_price_stats",
                "type": "query",
                "config": {
                    "data_source": "products",
                    "metrics": [
                        {
                            "name": "unit_price",
                            "aggregation": "MIN",
                            "alias": "min_price"
                        }
                    ]
                }
            },
            {
                "name": "assert_price",
                "type": "assert",
                "config": {
                    "source": "product_price_stats",
                    "assertions": [
                        {
                            "type": "range",
                            "field": "min_price",
                            "min": 1000,  # 这会失败，因为实际是89
                            "message": "最低价格必须≥1000"
                        }
                    ]
                }
            }
        ],
        "output": "product_price_stats"
    }
    
    try:
        engine = get_uqm_engine()
        result = await engine.process(uqm_config_fail)
        print("❌ 异常：断言应该失败但却成功了")
        print(f"  result.success: {result.success}")
    except Exception as e:
        print("✅ 正确：断言失败并抛出异常")
        print(f"  异常类型: {type(e).__name__}")
        print(f"  异常消息: {str(e)[:200]}...")
    
    # 测试2: 断言成功的情况
    print("\n🔍 测试2: 断言应该成功的情况")
    uqm_config_pass = {
        "metadata": {
            "name": "测试断言成功",
            "version": "1.0"
        },
        "steps": [
            {
                "name": "product_price_stats",
                "type": "query",
                "config": {
                    "data_source": "products",
                    "metrics": [
                        {
                            "name": "unit_price",
                            "aggregation": "MIN",
                            "alias": "min_price"
                        }
                    ]
                }
            },
            {
                "name": "assert_price",
                "type": "assert",
                "config": {
                    "source": "product_price_stats",
                    "assertions": [
                        {
                            "type": "range",
                            "field": "min_price",
                            "min": 50,  # 这会成功，因为实际是89
                            "max": 200,
                            "message": "最低价格应在50-200之间"
                        }
                    ]
                }
            }
        ],
        "output": "product_price_stats"
    }
    
    try:
        result = await engine.process(uqm_config_pass)
        print("✅ 正确：断言成功")
        print(f"  result.success: {result.success}")
        print(f"  min_price: {result.data[0].get('min_price')}")
    except Exception as e:
        print("❌ 异常：断言应该成功但却失败了")
        print(f"  异常: {e}")

if __name__ == "__main__":
    asyncio.run(test_fixed_assertion())
