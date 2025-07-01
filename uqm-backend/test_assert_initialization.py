#!/usr/bin/env python3
"""
测试 AssertStep 初始化顺序修复
"""

import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.steps.assert_step import AssertStep
from src.utils.exceptions import ValidationError


def test_assert_step_initialization():
    """测试 AssertStep 初始化"""
    
    print("=== AssertStep 初始化顺序修复测试 ===\n")
    
    # 测试1: 正确的配置应该能够成功初始化
    print("1. 测试正确配置的初始化:")
    correct_config = {
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
    
    try:
        step = AssertStep(correct_config)
        print("✅ AssertStep 初始化成功")
        print(f"   支持的断言类型数量: {len(step.supported_assertions)}")
        print(f"   支持的断言类型: {list(step.supported_assertions.keys())}")
        
        # 验证所有断言方法都存在
        for assertion_type, method in step.supported_assertions.items():
            if callable(method):
                print(f"   ✅ {assertion_type}: 方法存在且可调用")
            else:
                print(f"   ❌ {assertion_type}: 方法不可调用")
                
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
    
    print()
    
    # 测试2: 错误的断言类型应该被捕获
    print("2. 测试无效断言类型的验证:")
    invalid_config = {
        "source": "test_data",
        "assertions": [
            {
                "type": "invalid_type",  # 无效的断言类型
                "message": "测试无效类型"
            }
        ]
    }
    
    try:
        step = AssertStep(invalid_config)
        print("❌ 应该抛出 ValidationError")
    except ValidationError as e:
        if "不支持的断言类型" in str(e):
            print("✅ 正确捕获无效断言类型错误")
            print(f"   错误信息: {e}")
        else:
            print(f"❌ 意外的验证错误: {e}")
    except Exception as e:
        print(f"❌ 意外错误: {e}")
    
    print()
    
    # 测试3: 缺少 assertions 字段
    print("3. 测试缺少 assertions 字段:")
    missing_assertions_config = {
        "source": "test_data"
        # 缺少 assertions 字段
    }
    
    try:
        step = AssertStep(missing_assertions_config)
        print("❌ 应该抛出 ValidationError")
    except ValidationError as e:
        if "assertions" in str(e):
            print("✅ 正确捕获缺少 assertions 字段错误")
            print(f"   错误信息: {e}")
        else:
            print(f"❌ 意外的验证错误: {e}")
    except Exception as e:
        print(f"❌ 意外错误: {e}")


def test_assertion_method_existence():
    """测试断言方法是否都存在"""
    
    print("\n=== 断言方法存在性测试 ===\n")
    
    config = {
        "source": "test_data",
        "assertions": [
            {
                "type": "range",
                "field": "test_field",
                "min": 0,
                "max": 100,
                "message": "测试范围断言"
            }
        ]
    }
    
    try:
        step = AssertStep(config)
        
        expected_methods = [
            'row_count', 'not_null', 'unique', 'range', 'regex',
            'custom', 'column_exists', 'data_type', 'value_in', 'relationship'
        ]
        
        print("检查断言方法:")
        for method_name in expected_methods:
            if method_name in step.supported_assertions:
                method = step.supported_assertions[method_name]
                method_full_name = f"_assert_{method_name}"
                
                if hasattr(step, method_full_name):
                    print(f"   ✅ {method_name}: 方法 {method_full_name} 存在")
                else:
                    print(f"   ❌ {method_name}: 方法 {method_full_name} 不存在")
            else:
                print(f"   ❌ {method_name}: 不在 supported_assertions 中")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    test_assert_step_initialization()
    test_assertion_method_existence()
    
    print("\n=== 修复总结 ===")
    print("🔧 发现的问题:")
    print("   - AssertStep.__init__() 中初始化顺序错误")
    print("   - super().__init__() 调用了 validate()")
    print("   - validate() 访问 self.supported_assertions")
    print("   - 但 supported_assertions 在 super().__init__() 之后才定义")
    print()
    print("✅ 修复方案:")
    print("   - 将 supported_assertions 的定义移到 super().__init__() 之前")
    print("   - 确保在 validate() 方法调用时，supported_assertions 已经可用")
    print()
    print("📝 建议:")
    print("   - 在父类设计中考虑初始化顺序问题")
    print("   - 添加更多的初始化测试用例")
    print("   - 考虑使用延迟初始化模式")
