#!/usr/bin/env python3
"""
测试 Assert 步骤修复
验证 Assert 配置格式问题
"""

import json
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.steps.assert_step import AssertStep
from src.utils.exceptions import ValidationError, ExecutionError


def test_assert_config_validation():
    """测试 Assert 配置验证"""
    
    print("=== UQM Assert 步骤配置验证测试 ===\n")
    
    # 测试1: 错误的配置格式 (使用 conditions)
    print("1. 测试错误配置格式 (使用 conditions):")
    wrong_config = {
        "source": "count_orders",
        "conditions": [  # ❌ 错误：应该使用 assertions
            {
                "field": "total_orders",
                "operator": ">=",
                "value": 100,
                "message": "订单数量不能少于100条"
            }
        ]
    }
    
    try:
        step = AssertStep(wrong_config)
        print("❌ 错误：应该抛出 ValidationError")
    except ValidationError as e:
        print(f"✅ 正确：捕获到预期的验证错误: {e}")
    except Exception as e:
        print(f"❌ 意外错误: {e}")
    
    print()
    
    # 测试2: 正确的配置格式 (使用 assertions)
    print("2. 测试正确配置格式 (使用 assertions):")
    correct_config = {
        "source": "count_orders",
        "assertions": [  # ✅ 正确：使用 assertions
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
        print("✅ 正确：Assert 步骤创建成功")
        print(f"   支持的断言类型: {list(step.supported_assertions.keys())}")
    except Exception as e:
        print(f"❌ 意外错误: {e}")
    
    print()
    
    # 测试3: 验证支持的断言类型
    print("3. 验证支持的断言类型:")
    supported_types = [
        'row_count', 'not_null', 'unique', 'range', 'regex',
        'custom', 'column_exists', 'data_type', 'value_in', 'relationship'
    ]
    
    for assertion_type in supported_types:
        test_config = {
            "source": "test_data",
            "assertions": [
                {
                    "type": assertion_type,
                    "message": f"测试 {assertion_type} 断言"
                }
            ]
        }
        
        try:
            step = AssertStep(test_config)
            print(f"   ✅ {assertion_type}: 支持")
        except ValidationError as e:
            if "不支持的断言类型" in str(e):
                print(f"   ❌ {assertion_type}: 不支持")
            else:
                print(f"   ⚠️  {assertion_type}: 其他验证错误 - {e}")
        except Exception as e:
            print(f"   ❌ {assertion_type}: 意外错误 - {e}")


def generate_corrected_assert_examples():
    """生成修正后的 Assert 配置示例"""
    
    print("\n=== 修正后的 Assert 配置示例 ===\n")
    
    examples = [
        {
            "name": "验证订单总数",
            "config": {
                "uqm": {
                    "steps": [
                        {
                            "name": "count_orders",
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
                        }
                    ]
                }
            }
        },
        {
            "name": "验证数据完整性",
            "config": {
                "uqm": {
                    "steps": [
                        {
                            "name": "get_customers",
                            "type": "query",
                            "config": {
                                "data_source": "customers",
                                "dimensions": ["customer_id", "customer_name", "email"]
                            }
                        },
                        {
                            "name": "assert_data_quality",
                            "type": "assert",
                            "config": {
                                "source": "get_customers",
                                "assertions": [
                                    {
                                        "type": "not_null",
                                        "columns": ["customer_name", "email"],
                                        "message": "客户姓名和邮箱不能为空"
                                    },
                                    {
                                        "type": "unique",
                                        "columns": ["email"],
                                        "message": "客户邮箱必须唯一"
                                    },
                                    {
                                        "type": "regex",
                                        "column": "email",
                                        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                                        "message": "邮箱格式不正确"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['name']}:")
        print(json.dumps(example['config'], indent=2, ensure_ascii=False))
        print()


if __name__ == "__main__":
    test_assert_config_validation()
    generate_corrected_assert_examples()
    
    print("\n=== 总结 ===")
    print("🔧 发现的问题:")
    print("   - AssertStep 期望配置字段为 'assertions'")
    print("   - 用户文档中使用了 'conditions' (不正确)")
    print("   - 这导致了 'AssertStep 缺少必需配置: assertions' 错误")
    print()
    print("✅ 修复方案:")
    print("   - 将配置中的 'conditions' 改为 'assertions'")
    print("   - 每个断言需要指定 'type' 字段")
    print("   - 根据断言类型提供相应的配置参数")
    print()
    print("📝 建议:")
    print("   - 更新所有文档中的 Assert 配置示例")
    print("   - 添加配置验证的单元测试")
    print("   - 考虑支持 'conditions' 作为 'assertions' 的别名以提高兼容性")
