#!/usr/bin/env python3
"""
测试 Assert Range 修复
验证实际的断言逻辑是否正确工作
"""

import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.steps.assert_step import AssertStep


def test_assert_range_logic():
    """测试断言范围逻辑"""
    
    print("=== Assert Range 逻辑测试 ===\n")
    
    # 用户的配置
    config = {
        "source": "count_orders",
        "assertions": [
            {
                "type": "range",
                "field": "total_orders",  # 使用 field 而不是 column
                "min": 100,
                "max": 10000,
                "message": "订单数量应在100-10000之间"
            }
        ]
    }
    
    print("1. 测试配置初始化:")
    try:
        assert_step = AssertStep(config)
        print("✅ AssertStep 初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    print()
    
    # 测试不同的数据场景
    test_scenarios = [
        {
            "name": "实际用户数据 (13个订单)",
            "data": [{"total_orders": 13}],
            "expected_result": "fail",  # 13 < 100，应该失败
            "expected_message": "小于最小值"
        },
        {
            "name": "正常数据 (150个订单)",
            "data": [{"total_orders": 150}],
            "expected_result": "pass",  # 100 <= 150 <= 10000，应该通过
            "expected_message": "范围检查通过"
        },
        {
            "name": "超出最大值 (15000个订单)",
            "data": [{"total_orders": 15000}],
            "expected_result": "fail",  # 15000 > 10000，应该失败
            "expected_message": "大于最大值"
        },
        {
            "name": "边界值测试 - 最小值",
            "data": [{"total_orders": 100}],
            "expected_result": "pass",  # 100 == 100，应该通过
            "expected_message": "范围检查通过"
        },
        {
            "name": "边界值测试 - 最大值",
            "data": [{"total_orders": 10000}],
            "expected_result": "pass",  # 10000 == 10000，应该通过
            "expected_message": "范围检查通过"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 2):
        print(f"{i}. {scenario['name']}:")
        
        try:
            # 调用 _assert_range 方法
            assertion = config["assertions"][0]
            result = assert_step._assert_range(scenario["data"], assertion)
            
            print(f"   数据: {scenario['data']}")
            print(f"   断言配置: min={assertion['min']}, max={assertion['max']}")
            print(f"   执行结果: {result}")
            
            # 验证结果
            actual_passed = result.get("passed", True)
            expected_passed = (scenario["expected_result"] == "pass")
            
            if actual_passed == expected_passed:
                print(f"   ✅ 结果正确: {'通过' if actual_passed else '失败'}")
            else:
                print(f"   ❌ 结果错误: 期望{'通过' if expected_passed else '失败'}，实际{'通过' if actual_passed else '失败'}")
            
            # 检查错误消息
            message = result.get("message", "")
            if scenario["expected_message"] in message:
                print(f"   ✅ 错误消息正确: {message}")
            else:
                print(f"   ⚠️  错误消息: {message}")
                
        except Exception as e:
            print(f"   ❌ 执行失败: {e}")
        
        print()


def test_field_vs_column_compatibility():
    """测试 field 和 column 字段的兼容性"""
    
    print("=== Field vs Column 兼容性测试 ===\n")
    
    config = {
        "source": "test_data",
        "assertions": [
            {
                "type": "range",
                "field": "value",  # 使用 field
                "min": 0,
                "max": 100,
                "message": "值应在0-100之间"
            }
        ]
    }
    
    config_old = {
        "source": "test_data", 
        "assertions": [
            {
                "type": "range",
                "column": "value",  # 使用 column (旧格式)
                "min": 0,
                "max": 100,
                "message": "值应在0-100之间"
            }
        ]
    }
    
    test_data = [{"value": 50}]
    
    try:
        # 测试新格式 (field)
        assert_step_new = AssertStep(config)
        result_new = assert_step_new._assert_range(test_data, config["assertions"][0])
        print(f"1. 使用 'field' 格式: {result_new}")
        
        # 测试旧格式 (column)
        assert_step_old = AssertStep(config_old)
        result_old = assert_step_old._assert_range(test_data, config_old["assertions"][0])
        print(f"2. 使用 'column' 格式: {result_old}")
        
        # 验证兼容性
        if result_new.get("passed") == result_old.get("passed"):
            print("✅ 向后兼容性正常：field 和 column 都支持")
        else:
            print("❌ 向后兼容性问题：field 和 column 结果不一致")
            
    except Exception as e:
        print(f"❌ 兼容性测试失败: {e}")


def simulate_user_execution():
    """模拟用户的实际执行流程"""
    
    print("\n=== 模拟用户执行流程 ===\n")
    
    # 用户的完整配置
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
    }
    
    # 用户的实际数据（13个订单）
    user_data = [{"total_orders": 13}]
    
    try:
        assert_step = AssertStep(config)
        
        # 执行断言检查
        assertion_results = assert_step._perform_assertions(user_data)
        
        print("断言执行结果:")
        for result in assertion_results:
            print(f"  类型: {result['type']}")
            print(f"  通过: {result['passed']}")
            print(f"  消息: {result['message']}")
            print(f"  详情: {result.get('details', {})}")
        
        # 检查是否应该失败
        should_fail = any(not r["passed"] for r in assertion_results)
        
        print(f"\n分析:")
        print(f"  实际订单数: 13")
        print(f"  最小要求: 100") 
        print(f"  最大限制: 10000")
        print(f"  应该失败: {should_fail}")
        
        if should_fail:
            print("✅ 断言正确识别了问题：订单数量不足")
        else:
            print("❌ 断言错误通过了：应该检测出订单数量不足的问题")
            
    except Exception as e:
        print(f"❌ 执行流程失败: {e}")


if __name__ == "__main__":
    test_assert_range_logic()
    test_field_vs_column_compatibility()
    simulate_user_execution()
    
    print("=== 总结 ===")
    print("🔧 修复内容:")
    print("   - 修复了 _assert_range 中的字段名问题 (column -> field)")
    print("   - 添加了向后兼容性支持 (同时支持 field 和 column)")
    print("   - 改进了错误消息格式")
    print()
    print("📊 用户数据分析:")
    print("   - 实际订单数: 13")
    print("   - 断言要求: 100-10000")
    print("   - 期望结果: 断言应该失败")
    print()
    print("🎯 如果修复正确，断言应该会失败并返回错误信息")
