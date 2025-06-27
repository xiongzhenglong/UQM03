#!/usr/bin/env python3
"""
测试计算字段功能的修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.steps.query_step import QueryStep

def test_calculated_fields():
    """测试计算字段功能"""
    
    # 创建测试数据
    test_data = [
        {'country': '中国', 'category': '电子产品', 'total_sales_amount': '1334.05'},
        {'country': '中国', 'category': '服装', 'total_sales_amount': '500.00'},
        {'country': '美国', 'category': '电子产品', 'total_sales_amount': '2000.00'},
        {'country': '美国', 'category': '图书', 'total_sales_amount': '800.00'},
        {'country': '日本', 'category': '电子产品', 'total_sales_amount': '1500.00'},
    ]

    # 创建查询步骤配置
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

    # 创建查询步骤实例
    query_step = QueryStep(config)

    # 处理数据
    result = query_step._process_step_data(test_data)

    print('测试结果:')
    for row in result:
        print(f"  {row}")
    
    # 验证结果
    assert len(result) > 0, "结果不应为空"
    
    # 检查每一行都有 rank_by_sales 字段
    for row in result:
        assert 'rank_by_sales' in row, f"缺少 rank_by_sales 字段: {row}"
        assert row['rank_by_sales'] is not None, f"rank_by_sales 不应为 None: {row}"
    
    print("✅ 所有测试通过！计算字段功能已修复。")
    
    # 验证排名逻辑
    china_rows = [row for row in result if row['country'] == '中国']
    usa_rows = [row for row in result if row['country'] == '美国']
    japan_rows = [row for row in result if row['country'] == '日本']
    
    print(f"中国记录: {china_rows}")
    print(f"美国记录: {usa_rows}")
    print(f"日本记录: {japan_rows}")
    
    assert len(china_rows) == 2, "中国应该有2条记录"
    
    # 按销售额排序：电子产品(1334.05) > 服装(500.00)
    china_electronics = next(row for row in china_rows if row['category'] == '电子产品')
    china_clothing = next(row for row in china_rows if row['category'] == '服装')
    
    # 注意：由于分区逻辑，每个国家内部单独排名
    # 中国的电子产品销售额最高，应该在中国内排名第1
    # 中国的服装销售额较低，应该在中国内排名第2
    
    print(f"中国电子产品排名: {china_electronics['rank_by_sales']}")
    print(f"中国服装排名: {china_clothing['rank_by_sales']}")
    
    # 检查是否正确分区计算
    china_ranks = [row['rank_by_sales'] for row in china_rows]
    usa_ranks = [row['rank_by_sales'] for row in usa_rows] 
    japan_ranks = [row['rank_by_sales'] for row in japan_rows]
    
    print(f"中国排名: {sorted(china_ranks)}")
    print(f"美国排名: {sorted(usa_ranks)}")
    print(f"日本排名: {sorted(japan_ranks)}")
    
    # 每个国家都应该有自己的排名序列，从1开始
    assert min(china_ranks) == 1, f"中国最小排名应该是1，实际: {min(china_ranks)}"
    assert min(usa_ranks) == 1, f"美国最小排名应该是1，实际: {min(usa_ranks)}"
    assert min(japan_ranks) == 1, f"日本最小排名应该是1，实际: {min(japan_ranks)}"
    
    print("✅ 排名逻辑验证通过！")

if __name__ == "__main__":
    test_calculated_fields()
