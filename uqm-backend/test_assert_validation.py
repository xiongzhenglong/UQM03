#!/usr/bin/env python3
"""
UQM Assert 修复验证测试
验证修复后的 Assert 配置是否正确
"""

import json


def test_fixed_assert_config():
    """测试修复后的 Assert 配置"""
    
    print("=== UQM Assert 修复验证测试 ===\n")
    
    # 修复后的订单总数验证配置
    fixed_config = {
        "uqm": {
            "metadata": {
                "name": "验证订单总数_修复版",
                "description": "使用正确的assertions配置格式", 
                "version": "1.1"
            },
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
                        "assertions": [  # ✅ 使用正确的 assertions 字段
                            {
                                "type": "range",  # ✅ 指定断言类型
                                "field": "total_orders",
                                "min": 100,
                                "max": 10000,
                                "message": "订单数量应在100-10000之间"
                            }
                        ]
                    }
                }
            ],
            "output": "count_orders"
        },
        "parameters": {},
        "options": {}
    }
    
    print("✅ 修复后的配置:")
    print(json.dumps(fixed_config, indent=2, ensure_ascii=False))
    print()
    
    # 验证配置结构
    assert_step = fixed_config["uqm"]["steps"][1]
    assert_config = assert_step["config"]
    
    # 检查必需字段
    required_fields = ["source", "assertions"]
    for field in required_fields:
        if field in assert_config:
            print(f"✅ 包含必需字段: {field}")
        else:
            print(f"❌ 缺少必需字段: {field}")
    
    # 检查断言结构
    assertions = assert_config["assertions"]
    for i, assertion in enumerate(assertions):
        print(f"\n断言 {i + 1}:")
        if "type" in assertion:
            print(f"   ✅ 断言类型: {assertion['type']}")
        else:
            print(f"   ❌ 缺少断言类型")
        
        if "message" in assertion:
            print(f"   ✅ 错误消息: {assertion['message']}")
        else:
            print(f"   ❌ 缺少错误消息")


def test_assertion_types():
    """测试不同断言类型的配置"""
    
    print("\n=== 断言类型配置测试 ===\n")
    
    assertion_examples = {
        "range": {
            "type": "range",
            "field": "price",
            "min": 0,
            "max": 10000,
            "message": "价格应在0-10000之间"
        },
        "row_count": {
            "type": "row_count",
            "expected": 100,
            "message": "期望100行数据"
        },
        "not_null": {
            "type": "not_null",
            "columns": ["name", "email"],
            "message": "姓名和邮箱不能为空"
        },
        "unique": {
            "type": "unique",
            "columns": ["email"],
            "message": "邮箱必须唯一"
        },
        "regex": {
            "type": "regex",
            "column": "email",
            "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "message": "邮箱格式不正确"
        },
        "custom": {
            "type": "custom",
            "condition": "revenue > 1000 AND profit_margin > 0.1",
            "message": "收入应大于1000且利润率大于10%"
        },
        "value_in": {
            "type": "value_in",
            "field": "status",
            "values": ["active", "inactive", "pending"],
            "message": "状态值无效"
        }
    }
    
    for assertion_type, config in assertion_examples.items():
        print(f"{assertion_type}:")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        print()


def generate_complete_test_config():
    """生成完整的测试配置"""
    
    print("=== 完整测试配置 ===\n")
    
    complete_config = {
        "uqm": {
            "metadata": {
                "name": "完整断言测试",
                "description": "测试所有断言类型的综合配置",
                "version": "1.0"
            },
            "steps": [
                {
                    "name": "get_test_data",
                    "type": "query",
                    "config": {
                        "data_source": "orders",
                        "dimensions": ["order_id", "customer_id", "status"],
                        "metrics": [
                            {
                                "name": "order_id",
                                "aggregation": "COUNT",
                                "alias": "total_orders"
                            },
                            {
                                "expression": "AVG(total_amount)",
                                "alias": "avg_amount"
                            }
                        ]
                    }
                },
                {
                    "name": "comprehensive_assertions",
                    "type": "assert",
                    "config": {
                        "source": "get_test_data",
                        "assertions": [
                            {
                                "type": "row_count",
                                "min": 1,
                                "message": "至少应有1行数据"
                            },
                            {
                                "type": "not_null",
                                "columns": ["order_id", "customer_id"],
                                "message": "订单ID和客户ID不能为空"
                            },
                            {
                                "type": "range",
                                "field": "avg_amount",
                                "min": 0,
                                "max": 100000,
                                "message": "平均金额应在合理范围内"
                            },
                            {
                                "type": "value_in",
                                "field": "status",
                                "values": ["pending", "processing", "shipped", "delivered", "cancelled"],
                                "message": "订单状态无效"
                            }
                        ],
                        "on_failure": "error",
                        "stop_on_first_failure": False
                    }
                }
            ],
            "output": "get_test_data"
        },
        "parameters": {},
        "options": {}
    }
    
    print("完整测试配置:")
    print(json.dumps(complete_config, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_fixed_assert_config()
    test_assertion_types()
    generate_complete_test_config()
    
    print("\n=== 修复总结 ===")
    print("🔧 修复内容:")
    print("   1. ✅ 将所有 'conditions' 改为 'assertions'")
    print("   2. ✅ 为每个断言添加 'type' 字段")
    print("   3. ✅ 调整断言参数结构适配不同类型")
    print("   4. ✅ 更新语法说明和示例")
    print()
    print("📋 支持的断言类型:")
    print("   - range: 数值范围检查")
    print("   - row_count: 行数验证")
    print("   - not_null: 非空验证")
    print("   - unique: 唯一性验证")
    print("   - regex: 正则匹配")
    print("   - custom: 自定义条件")
    print("   - value_in: 值范围检查")
    print("   - column_exists: 列存在检查")
    print("   - data_type: 数据类型检查")
    print("   - relationship: 关系检查")
    print()
    print("✅ 现在你可以使用修复后的配置来运行Assert步骤了！")
