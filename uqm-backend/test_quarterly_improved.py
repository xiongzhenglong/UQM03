#!/usr/bin/env python3
"""
测试改进的季度销售分析配置
解决column_prefix语义混乱问题
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import UQMQueryEngine

def test_improved_quarterly_analysis():
    """测试改进的季度分析配置"""
    
    print("🧪 测试改进的季度销售分析配置")
    print("=" * 60)
    
    engine = UQMQueryEngine()
    
    # 方案1：单次透视，简洁清晰
    print("\n📊 方案1：单次透视分析")
    print("-" * 40)
    
    config1 = {
        "uqm": {
            "metadata": {
                "name": "QuarterlySalesTrendAnalysis_Simple",
                "description": "简洁的季度销售趋势分析"
            },
            "steps": [
                {
                    "name": "get_quarterly_sales",
                    "type": "query",
                    "config": {
                        "data_source": "orders",
                        "joins": [
                            {"type": "INNER", "table": "order_items", "on": "orders.order_id = order_items.order_id"},
                            {"type": "INNER", "table": "products", "on": "order_items.product_id = products.product_id"}
                        ],
                        "dimensions": [
                            {"expression": "products.category", "alias": "product_category"},
                            {"expression": "CASE WHEN MONTH(orders.order_date) IN (1,2,3) THEN 'Q1' WHEN MONTH(orders.order_date) IN (4,5,6) THEN 'Q2' WHEN MONTH(orders.order_date) IN (7,8,9) THEN 'Q3' ELSE 'Q4' END", "alias": "quarter"}
                        ],
                        "metrics": [
                            {"expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))", "alias": "total_sales_amount"}
                        ],
                        "group_by": ["products.category", "quarter"],
                        "filters": [
                            {"field": "YEAR(orders.order_date)", "operator": "=", "value": 2024}
                        ]
                    }
                },
                {
                    "name": "pivot_all_quarters",
                    "type": "pivot",
                    "config": {
                        "source": "get_quarterly_sales",
                        "index": "product_category",
                        "columns": "quarter",
                        "values": "total_sales_amount",
                        "agg_func": "sum",
                        "column_prefix": "销售额_",
                        "fill_value": 0
                    }
                }
            ],
            "output": "pivot_all_quarters"
        }
    }
    
    try:
        result1 = engine.execute(config1)
        if result1.get("success"):
            print("✅ 方案1执行成功")
            data1 = result1["data"]
            
            # 显示结果结构
            if data1:
                print(f"📋 结果行数: {len(data1)}")
                print("📋 列名结构:")
                for key in data1[0].keys():
                    print(f"   - {key}")
                
                print("\n📋 示例数据:")
                for item in data1[:2]:  # 只显示前2行
                    print(f"   {item}")
            
        else:
            print(f"❌ 方案1执行失败: {result1.get('error')}")
            
    except Exception as e:
        print(f"❌ 方案1执行异常: {str(e)}")
    
    # 方案2：多指标分析
    print("\n📊 方案2：多指标分析")
    print("-" * 40)
    
    config2 = {
        "uqm": {
            "metadata": {
                "name": "QuarterlySalesTrendAnalysis_MultiMetrics",
                "description": "多指标季度销售分析"
            },
            "steps": [
                {
                    "name": "get_quarterly_sales",
                    "type": "query",
                    "config": {
                        "data_source": "orders",
                        "joins": [
                            {"type": "INNER", "table": "order_items", "on": "orders.order_id = order_items.order_id"},
                            {"type": "INNER", "table": "products", "on": "order_items.product_id = products.product_id"}
                        ],
                        "dimensions": [
                            {"expression": "products.category", "alias": "product_category"},
                            {"expression": "CASE WHEN MONTH(orders.order_date) IN (1,2,3) THEN 'Q1' WHEN MONTH(orders.order_date) IN (4,5,6) THEN 'Q2' WHEN MONTH(orders.order_date) IN (7,8,9) THEN 'Q3' ELSE 'Q4' END", "alias": "quarter"}
                        ],
                        "metrics": [
                            {"expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))", "alias": "total_sales_amount"},
                            {"expression": "SUM(order_items.quantity)", "alias": "total_quantity"},
                            {"expression": "COUNT(DISTINCT orders.order_id)", "alias": "order_count"}
                        ],
                        "group_by": ["products.category", "quarter"],
                        "filters": [
                            {"field": "YEAR(orders.order_date)", "operator": "=", "value": 2024}
                        ]
                    }
                },
                {
                    "name": "pivot_sales_amount",
                    "type": "pivot",
                    "config": {
                        "source": "get_quarterly_sales",
                        "index": "product_category",
                        "columns": "quarter",
                        "values": "total_sales_amount",
                        "agg_func": "sum",
                        "column_prefix": "销售额_",
                        "fill_value": 0
                    }
                },
                {
                    "name": "pivot_sales_quantity",
                    "type": "pivot",
                    "config": {
                        "source": "get_quarterly_sales",
                        "index": "product_category",
                        "columns": "quarter",
                        "values": "total_quantity",
                        "agg_func": "sum",
                        "column_prefix": "销量_",
                        "fill_value": 0
                    }
                },
                {
                    "name": "pivot_order_count",
                    "type": "pivot",
                    "config": {
                        "source": "get_quarterly_sales",
                        "index": "product_category",
                        "columns": "quarter",
                        "values": "order_count",
                        "agg_func": "sum",
                        "column_prefix": "订单数_",
                        "fill_value": 0
                    }
                },
                {
                    "name": "enrich_with_quantity",
                    "type": "enrich",
                    "config": {
                        "source": "pivot_sales_amount",
                        "lookup": "pivot_sales_quantity",
                        "on": "product_category"
                    }
                },
                {
                    "name": "final_analysis",
                    "type": "enrich",
                    "config": {
                        "source": "enrich_with_quantity",
                        "lookup": "pivot_order_count",
                        "on": "product_category"
                    }
                }
            ],
            "output": "final_analysis"
        }
    }
    
    try:
        result2 = engine.execute(config2)
        if result2.get("success"):
            print("✅ 方案2执行成功")
            data2 = result2["data"]
            
            # 显示结果结构
            if data2:
                print(f"📋 结果行数: {len(data2)}")
                print("📋 列名结构:")
                for key in data2[0].keys():
                    print(f"   - {key}")
                
                print("\n📋 示例数据:")
                for item in data2[:2]:  # 只显示前2行
                    print(f"   {item}")
            
        else:
            print(f"❌ 方案2执行失败: {result2.get('error')}")
            
    except Exception as e:
        print(f"❌ 方案2执行异常: {str(e)}")

def analyze_column_naming_issue():
    """分析列名命名问题"""
    
    print("\n🔍 列名命名问题分析")
    print("=" * 60)
    
    print("❌ 原始配置的问题:")
    print("   - Q1销售额_Q2: 语义混乱，Q1前缀+Q2数据")
    print("   - 大量null值: 每个pivot包含所有季度")
    print("   - 数据冗余: 同样的数据重复出现在不同行")
    
    print("\n✅ 改进方案:")
    print("   方案1 - 单次透视:")
    print("     - 销售额_Q1, 销售额_Q2, 销售额_Q3, 销售额_Q4")
    print("     - 语义清晰，每列代表一个季度的销售额")
    print("     - 数据紧凑，无冗余")
    
    print("\n   方案2 - 多指标分析:")
    print("     - 销售额_Q1, 销售额_Q2 (销售金额)")
    print("     - 销量_Q1, 销量_Q2 (销售数量)")
    print("     - 订单数_Q1, 订单数_Q2 (订单数量)")
    print("     - 多维度对比，业务价值更高")

def main():
    """主函数"""
    test_improved_quarterly_analysis()
    analyze_column_naming_issue()
    
    print("\n🎯 建议:")
    print("   1. 优先使用方案1：简洁清晰，易于理解")
    print("   2. 复杂分析使用方案2：多指标对比")
    print("   3. 避免原始配置的语义混乱问题")

if __name__ == "__main__":
    main()
