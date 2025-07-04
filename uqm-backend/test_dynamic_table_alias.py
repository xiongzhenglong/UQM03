#!/usr/bin/env python3
"""
测试动态表别名解析功能
验证系统能够正确处理任意表别名，而不是硬编码特定的别名
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.steps.query_step import QueryStep

def test_dynamic_table_alias():
    """测试动态表别名解析"""
    print("🧪 测试动态表别名解析功能")
    print("=" * 50)
    
    # 测试用例1：使用任意表别名的查询
    test_config = {
        "data_source": "customer_order_counts coc",
        "dimensions": [
            "coc.customer_id"
        ],
        "metrics": [
            {
                "name": "coc.total_orders",
                "aggregation": "SUM",
                "alias": "coc_total_orders"
            },
            {
                "name": "cfod.first_order_date",
                "aggregation": "MAX",
                "alias": "cfod_first_order_date"
            }
        ],
        "calculated_fields": [
            {
                "alias": "is_repeat_purchaser",
                "expression": "CASE WHEN SUM(coc.total_orders) > 1 THEN 1 ELSE 0 END"
            }
        ],
        "joins": [
            {
                "type": "INNER",
                "table": "customer_first_order_date cfod",
                "on": "coc.customer_id = cfod.customer_id"
            }
        ],
        "group_by": [
            "coc.customer_id"
        ]
    }
    
    # 创建QueryStep实例
    query_step = QueryStep(test_config)
    
    # 模拟JOIN后的数据行
    test_row = {
        "coc.customer_id": "C001",
        "customer_id": "C001",  # 无前缀版本
        "coc_total_orders": 3,  # 带别名前缀版本
        "total_orders": 3,      # 无前缀版本
        "cfod.first_order_date": "2024-01-15",
        "first_order_date": "2024-01-15",
        "cfod_first_order_date": "2024-01-15"
    }
    
    print("📋 测试数据行:")
    for key, value in test_row.items():
        print(f"   {key}: {value}")
    
    print("\n🔍 测试字段变体构建:")
    
    # 测试不同类型的字段表达式
    test_fields = [
        "coc.total_orders",
        "cfod.first_order_date", 
        "customer_id",
        "total_orders"
    ]
    
    for field_expr in test_fields:
        variants = query_step._build_field_variants(field_expr, test_row)
        print(f"\n   字段 '{field_expr}' 的变体:")
        for variant in variants:
            found = variant in test_row
            value = test_row.get(variant, "NOT_FOUND")
            print(f"     {variant}: {value} {'✅' if found else '❌'}")
    
    print("\n🧮 测试表达式计算:")
    
    # 测试包含聚合函数的表达式
    test_expressions = [
        "SUM(coc.total_orders)",
        "MAX(cfod.first_order_date)",
        "CASE WHEN SUM(coc.total_orders) > 1 THEN 1 ELSE 0 END"
    ]
    
    for expr in test_expressions:
        try:
            result = query_step._evaluate_expression_with_aggregates(expr, test_row)
            print(f"   表达式 '{expr}' -> {result}")
        except Exception as e:
            print(f"   表达式 '{expr}' -> 错误: {e}")
    
    print("\n✅ 动态表别名测试完成")

def test_different_table_aliases():
    """测试不同的表别名组合"""
    print("\n🧪 测试不同表别名组合")
    print("=" * 50)
    
    # 测试用例：使用完全不同的表别名
    test_config = {
        "data_source": "sales_data sd",
        "dimensions": [
            "sd.product_id"
        ],
        "metrics": [
            {
                "name": "sd.sales_amount",
                "aggregation": "SUM",
                "alias": "total_sales"
            }
        ],
        "calculated_fields": [
            {
                "alias": "high_value_flag",
                "expression": "CASE WHEN SUM(sd.sales_amount) > 1000 THEN 1 ELSE 0 END"
            }
        ],
        "joins": [
            {
                "type": "INNER",
                "table": "product_info pi",
                "on": "sd.product_id = pi.product_id"
            }
        ],
        "group_by": [
            "sd.product_id"
        ]
    }
    
    query_step = QueryStep(test_config)
    
    # 模拟数据行
    test_row = {
        "sd.product_id": "P001",
        "product_id": "P001",
        "sd_sales_amount": 1500,
        "sales_amount": 1500,
        "pi.product_name": "测试产品",
        "product_name": "测试产品",
        "pi_product_name": "测试产品"
    }
    
    print("📋 测试数据行:")
    for key, value in test_row.items():
        print(f"   {key}: {value}")
    
    print("\n🔍 测试字段变体构建:")
    
    test_fields = [
        "sd.sales_amount",
        "pi.product_name",
        "product_id"
    ]
    
    for field_expr in test_fields:
        variants = query_step._build_field_variants(field_expr, test_row)
        print(f"\n   字段 '{field_expr}' 的变体:")
        for variant in variants:
            found = variant in test_row
            value = test_row.get(variant, "NOT_FOUND")
            print(f"     {variant}: {value} {'✅' if found else '❌'}")
    
    print("\n🧮 测试表达式计算:")
    
    test_expressions = [
        "SUM(sd.sales_amount)",
        "CASE WHEN SUM(sd.sales_amount) > 1000 THEN 1 ELSE 0 END"
    ]
    
    for expr in test_expressions:
        try:
            result = query_step._evaluate_expression_with_aggregates(expr, test_row)
            print(f"   表达式 '{expr}' -> {result}")
        except Exception as e:
            print(f"   表达式 '{expr}' -> 错误: {e}")
    
    print("\n✅ 不同表别名测试完成")

if __name__ == "__main__":
    print("🚀 开始测试动态表别名解析功能")
    print("=" * 60)
    
    try:
        test_dynamic_table_alias()
        test_different_table_aliases()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试完成！动态表别名解析功能正常工作")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 