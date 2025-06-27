#!/usr/bin/env python3
"""
调试用户提到的具体问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.steps.query_step import QueryStep

def test_user_case():
    """测试用户实际遇到的问题"""
    
    # 使用用户提供的实际数据
    test_data = [
        {"country": "中国", "category": "电子产品", "total_sales_amount": "1334.0500"},
        {"country": "中国", "category": "服装", "total_sales_amount": "531.2000"},
        {"country": "中国", "category": "图书", "total_sales_amount": "765.0000"},
        {"country": "加拿大", "category": "图书", "total_sales_amount": "267.0000"},
        {"country": "德国", "category": "家居用品", "total_sales_amount": "799.0000"},
        {"country": "意大利", "category": "服装", "total_sales_amount": "516.0000"},
        {"country": "新加坡", "category": "电子产品", "total_sales_amount": "639.0000"},
        {"country": "日本", "category": "电子产品", "total_sales_amount": "1570.3500"},
        {"country": "法国", "category": "家居用品", "total_sales_amount": "1519.0500"},
        {"country": "美国", "category": "电子产品", "total_sales_amount": "1677.2000"}
    ]

    # 第一步：聚合（模拟第一步的输出）
    print("=== 第一步数据（聚合后）===")
    for row in test_data:
        print(f"  {row}")

    # 第二步：排名
    config = {
        'data_source': 'test_data',
        'dimensions': ['country', 'category', 'total_sales_amount'],
        'calculated_fields': [
            {
                'alias': 'rank_by_sales',
                'expression': 'ROW_NUMBER() OVER (PARTITION BY country ORDER BY total_sales_amount DESC)'
            }
        ],
        'order_by': [
            {'field': 'country', 'direction': 'ASC'},
            {'field': 'rank_by_sales', 'direction': 'ASC'}
        ]
    }

    query_step = QueryStep(config)
    result = query_step._process_step_data(test_data)

    print("\n=== 第二步结果（排名后）===")
    for row in result:
        print(f"  {row}")
    
    # 检查中国的排名
    china_rows = [row for row in result if row['country'] == '中国']
    print(f"\n=== 中国数据分析 ===")
    
    # 按 total_sales_amount 排序中国数据
    china_sorted = sorted(china_rows, key=lambda x: float(x['total_sales_amount']), reverse=True)
    print("按销售额降序排列的中国数据:")
    for i, row in enumerate(china_sorted, 1):
        print(f"  {i}. {row['category']}: {row['total_sales_amount']} (排名: {row['rank_by_sales']})")
    
    # 验证问题
    electronics_row = next(row for row in china_rows if row['category'] == '电子产品')
    clothing_row = next(row for row in china_rows if row['category'] == '服装')
    books_row = next(row for row in china_rows if row['category'] == '图书')
    
    print(f"\n电子产品: 销售额={electronics_row['total_sales_amount']}, 排名={electronics_row['rank_by_sales']}")
    print(f"服装: 销售额={clothing_row['total_sales_amount']}, 排名={clothing_row['rank_by_sales']}")
    print(f"图书: 销售额={books_row['total_sales_amount']}, 排名={books_row['rank_by_sales']}")
    
    # 检查是否有问题
    if electronics_row['rank_by_sales'] != 1:
        print("❌ 发现问题：电子产品销售额最高但排名不是1")
        return False
    else:
        print("✅ 排名正确")
        return True

if __name__ == "__main__":
    test_user_case()
