#!/usr/bin/env python3
"""
集成测试：验证断言失败是否正确抛出异常
"""

import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.steps.assert_step import AssertStep
from src.utils.exceptions import ExecutionError


def test_assertion_failure_handling():
    """测试断言失败的处理机制"""
    
    print("=== 断言失败处理机制测试 ===\n")
    
    # 用户的配置（默认 on_failure="error"）
    config = {
        "source": "count_orders",
        "assertions": [
            {
                "type": "range",
                "field": "total_orders",
                "min": 100,
                "max": 10000,
                "message": "订单数量应在100-10000之间"
            }
        ]
        # 注意：没有指定 on_failure，应该默认为 "error"
    }
    
    # 模拟用户的实际数据（13个订单，应该失败）
    user_data = [{"total_orders": 13}]
    
    # 模拟执行上下文
    mock_context = {
        "get_source_data": lambda source_name: user_data
    }
    
    print("1. 测试默认错误处理 (on_failure='error'):")
    try:
        assert_step = AssertStep(config)
        print(f"   配置中的 on_failure: {assert_step.config.get('on_failure', '默认值')}")
        
        # 这应该抛出 ExecutionError
        result = await_execute_step(assert_step, mock_context)
        
        print("   ❌ 错误：断言失败但没有抛出异常！")
        print(f"   返回结果: {result}")
        
    except ExecutionError as e:
        print("   ✅ 正确：断言失败并抛出了 ExecutionError")
        print(f"   错误信息: {e}")
        
    except Exception as e:
        print(f"   ❌ 意外异常: {e}")
    
    print()
    
    # 测试不同的 on_failure 设置
    test_cases = [
        {
            "name": "warning 模式",
            "on_failure": "warning",
            "should_throw": False
        },
        {
            "name": "ignore 模式", 
            "on_failure": "ignore",
            "should_throw": False
        },
        {
            "name": "error 模式（显式设置）",
            "on_failure": "error", 
            "should_throw": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 2):
        print(f"{i}. 测试 {test_case['name']}:")
        
        config_with_failure_mode = {
            **config,
            "on_failure": test_case["on_failure"]
        }
        
        try:
            assert_step = AssertStep(config_with_failure_mode)
            result = await_execute_step(assert_step, mock_context)
            
            if test_case["should_throw"]:
                print(f"   ❌ 错误：应该抛出异常但没有抛出")
                print(f"   返回结果: {result}")
            else:
                print(f"   ✅ 正确：没有抛出异常")
                print(f"   返回结果: 查询继续执行")
                
        except ExecutionError as e:
            if test_case["should_throw"]:
                print(f"   ✅ 正确：抛出了预期的异常")
                print(f"   错误信息: {e}")
            else:
                print(f"   ❌ 错误：不应该抛出异常")
                print(f"   错误信息: {e}")
                
        except Exception as e:
            print(f"   ❌ 意外异常: {e}")
        
        print()


def await_execute_step(assert_step, context):
    """模拟异步执行（同步版本）"""
    try:
        # 获取源数据
        source_name = assert_step.config["source"]
        source_data = context["get_source_data"](source_name)
        
        # 执行断言检查
        assertion_results = assert_step._perform_assertions(source_data)
        
        # 处理断言结果（这里可能抛出异常）
        assert_step._handle_assertion_results(assertion_results)
        
        # 如果没有异常，返回原始数据
        return source_data
        
    except Exception as e:
        # 重新抛出异常
        raise e


def analyze_user_response():
    """分析用户收到的响应"""
    
    print("=== 用户响应分析 ===\n")
    
    user_response = {
        "success": True,  # ❌ 应该是 False
        "data": [{"total_orders": 13}],
        "step_results": [
            {
                "step_name": "count_orders",
                "step_type": "query", 
                "status": "completed",
                "error": None
            },
            {
                "step_name": "assert_order_count",
                "step_type": "assert",
                "status": "completed",  # ❌ 应该是 "failed"
                "error": None           # ❌ 应该有错误信息
            }
        ]
    }
    
    print("用户收到的响应分析:")
    print(f"  整体成功状态: {user_response['success']} ❌ (应该是 False)")
    print(f"  订单数量: {user_response['data'][0]['total_orders']}")
    print(f"  断言步骤状态: {user_response['step_results'][1]['status']} ❌ (应该是 'failed')")
    print(f"  断言步骤错误: {user_response['step_results'][1]['error']} ❌ (应该有错误信息)")
    
    print()
    print("问题诊断:")
    print("  1. 断言逻辑现在正确工作（我们已修复）")
    print("  2. 但是异常没有被正确处理和传播")
    print("  3. 可能的原因：")
    print("     - UQM 引擎层面的异常捕获")
    print("     - 默认的 on_failure 行为不是 'error'")
    print("     - 异步执行框架的问题")
    
    print()
    print("期望的正确响应应该是:")
    expected_response = {
        "success": False,
        "error": {
            "code": "ASSERTION_FAILED",
            "message": "断言检查失败: 发现 1 个超出范围的值: 订单数量应在100-10000之间",
            "details": {
                "step_name": "assert_order_count",
                "assertion_type": "range", 
                "field": "total_orders",
                "actual_value": 13,
                "expected_range": "100-10000"
            }
        }
    }
    
    import json
    print(json.dumps(expected_response, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_assertion_failure_handling()
    analyze_user_response()
    
    print("\n=== 结论 ===")
    print("🔧 已修复的问题:")
    print("   ✅ _assert_range 字段名问题")
    print("   ✅ 断言逻辑现在正确识别失败")
    print()
    print("🚨 仍存在的问题:")
    print("   ❌ 断言失败没有正确传播到最终响应")
    print("   ❌ 用户收到了错误的 'success: true' 状态")
    print()
    print("🔍 需要进一步调查:")
    print("   - UQM 引擎如何处理 AssertStep 的异常")
    print("   - 是否有全局的异常捕获机制")
    print("   - on_failure 的默认值是否被覆盖")
    print()
    print("💡 临时解决方案:")
    print("   - 在配置中显式设置 'on_failure': 'error'")
    print("   - 检查 UQM 引擎的异常处理逻辑")
