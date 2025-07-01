#!/usr/bin/env python3
"""
测试产品价格断言逻辑
"""

import json
import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.engine import get_uqm_engine

async def test_price_assertion():
    """测试产品价格断言逻辑"""
    
    print("=== 测试产品价格断言逻辑 ===")
    
    # 用户的配置
    uqm_config = {
        "metadata": {
            "name": "验证产品价格合理性",
            "description": "确保产品价格数据的有效性",
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
                        },
                        {
                            "name": "unit_price",
                            "aggregation": "MAX",
                            "alias": "max_price"
                        },
                        {
                            "name": "unit_price",
                            "aggregation": "AVG",
                            "alias": "avg_price"
                        },
                        {
                            "name": "product_id",
                            "aggregation": "COUNT",
                            "alias": "total_products"
                        }
                    ]
                }
            },
            {
                "name": "assert_price_validity",
                "type": "assert",
                "config": {
                    "source": "product_price_stats",
                    "assertions": [
                        {
                            "type": "range",
                            "field": "min_price",
                            "min": 1000,
                            "message": "产品最低价格必须大于1000"
                        },
                        {
                            "type": "range",
                            "field": "max_price",
                            "max": 100000,
                            "message": "产品最高价格不能超过100000元"
                        },
                        {
                            "type": "range",
                            "field": "avg_price",
                            "min": 10,
                            "max": 5000,
                            "message": "产品平均价格应在10-5000元之间"
                        }
                    ]
                }
            }
        ],
        "output": "product_price_stats"
    }
    
    try:
        print("🔍 执行查询...")
        engine = get_uqm_engine()
        result = await engine.process(uqm_config)
        
        print(f"📊 返回结果:")
        print(f"  Success: {result.success}")
        print(f"  Data: {result.data}")
        
        if result.data:
            data = result.data[0]
            min_price = float(data.get('min_price', 0))
            print(f"\n🔢 数据分析:")
            print(f"  实际最低价格: {min_price}")
            print(f"  断言要求: >= 1000")
            print(f"  应该失败: {min_price < 1000}")
        
        print(f"\n📋 步骤结果:")
        for step_result in result.step_results:
            print(f"  {step_result.step_name}: {step_result.status}")
            if step_result.error:
                print(f"    错误: {step_result.error}")
        
        # 检查问题
        assert_step = next((s for s in result.step_results if s.step_name == "assert_price_validity"), None)
        if assert_step:
            if assert_step.status == "completed" and result.success:
                print(f"\n❌ 问题确认: 断言应该失败但显示成功")
                print(f"   - min_price ({min_price}) < 1000 应该触发断言失败")
                print(f"   - 但 assert_price_validity 状态为: {assert_step.status}")
            elif assert_step.status == "failed":
                print(f"\n✅ 断言正确失败")
        
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_price_assertion())
