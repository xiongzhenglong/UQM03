#!/usr/bin/env python3
"""
调试断言失败异常传播的问题
检查UQM引擎处理断言失败的完整流程
"""

import json
import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.engine import get_uqm_engine

async def debug_assertion_response():
    """调试断言失败的响应处理"""
    
    print("=== 调试断言失败响应处理 ===")
    
    # 使用实际的用户配置（断言应该失败）
    uqm_config = {
        "metadata": {
            "name": "Assert_Order_Count_Debug",
            "description": "调试断言失败响应",
            "version": "1.0"
        },
        "steps": [
            {
                "name": "get_order_count",
                "type": "query",
                "config": {
                    "data_source": "orders",
                    "metrics": [
                        {
                            "name": "order_id",
                            "aggregation": "COUNT",
                            "alias": "total_orders"
                        }
                    ]
                }
            },
            {
                "name": "assert_order_count",
                "type": "assert",
                "config": {
                    "source": "get_order_count", 
                    "assertions": [
                        {
                            "type": "range",
                            "field": "total_orders",
                            "min": 100,
                            "max": 10000,
                            "on_failure": "error"
                        }
                    ]
                }
            }
        ],
        "output": "assert_order_count"
    }
    
    try:
        print("🔍 测试1: 使用默认选项")
        engine = get_uqm_engine()
        
        # 测试默认情况
        result = await engine.process(uqm_config)
        
        print(f"📊 结果分析:")
        print(f"  Success: {result.success}")
        print(f"  Data: {result.data}")
        print(f"  Execution Info: {result.execution_info}")
        
        if result.step_results:
            print(f"  步骤结果:")
            for step_result in result.step_results:
                print(f"    - {step_result.step_name}: {step_result.status}")
                if step_result.error:
                    print(f"      Error: {step_result.error}")
        
        # 检查是否有步骤失败但整体返回成功
        failed_steps = [step for step in result.step_results if step.status == "failed"]
        if failed_steps and result.success:
            print("❌ 问题确认：有步骤失败但返回success=True")
            for step in failed_steps:
                print(f"   失败步骤: {step.step_name}, 错误: {step.error}")
        
        print("\n" + "="*60)
        
        print("🔍 测试2: 显式设置 continue_on_error=False")
        result2 = await engine.process(uqm_config, options={"continue_on_error": False})
        
        print(f"📊 结果分析:")
        print(f"  Success: {result2.success}")
        print(f"  Data: {result2.data}")
        
        print("\n" + "="*60)
        
        print("🔍 测试3: 显式设置 continue_on_error=True")
        result3 = await engine.process(uqm_config, options={"continue_on_error": True})
        
        print(f"📊 结果分析:")
        print(f"  Success: {result3.success}")  
        print(f"  Data: {result3.data}")
        
        if result3.step_results:
            print(f"  步骤结果:")
            for step_result in result3.step_results:
                print(f"    - {step_result.step_name}: {step_result.status}")
                if step_result.error:
                    print(f"      Error: {step_result.error}")
        
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_assertion_response())
