#!/usr/bin/env python3
"""
专门测试用户报告的问题：中国的电子产品排名问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.steps.query_step import QueryStep

def test_china_ranking_issue():
    """测试中国排名问题"""
    print("=== 测试用户报告的中国排名问题 ===")
    
    # 使用用户原始报告中的精确数据
    test_data = [
        {"country": "中国", "category": "电子产品", "total_sales_amount": "1334.0500"},
        {"country": "中国", "category": "服装", "total_sales_amount": "531.2000"},
        {"country": "中国", "category": "图书", "total_sales_amount": "765.0000"},
    ]

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

    print("结果:")
    for row in result:
        print(f"  {row}")
    
    # 验证排名
    electronics = next(row for row in result if row['category'] == '电子产品')
    clothing = next(row for row in result if row['category'] == '服装')
    books = next(row for row in result if row['category'] == '图书')
    
    print(f"\n验证结果:")
    print(f"电子产品: 销售额={electronics['total_sales_amount']}, 排名={electronics['rank_by_sales']}")
    print(f"图书: 销售额={books['total_sales_amount']}, 排名={books['rank_by_sales']}")
    print(f"服装: 销售额={clothing['total_sales_amount']}, 排名={clothing['rank_by_sales']}")
    
    # 检查是否正确：按销售额降序应该是 电子产品(1334.05) > 图书(765.00) > 服装(531.20)
    expected_order = [
        ('电子产品', 1),
        ('图书', 2),
        ('服装', 3)
    ]
    
    success = True
    for category, expected_rank in expected_order:
        actual_row = next(row for row in result if row['category'] == category)
        actual_rank = actual_row['rank_by_sales']
        
        if actual_rank != expected_rank:
            print(f"❌ {category} 排名错误：期望{expected_rank}，实际{actual_rank}")
            success = False
        else:
            print(f"✅ {category} 排名正确：{actual_rank}")
    
    if success:
        print("\n🎉 用户报告的问题已修复！排名完全正确。")
    else:
        print("\n❌ 问题仍然存在。")
    
    return success

if __name__ == "__main__":
    test_china_ranking_issue()
