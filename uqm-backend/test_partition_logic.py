#!/usr/bin/env python3
"""
详细调试窗口函数的分区逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.steps.query_step import QueryStep

def test_partition_logic():
    """测试分区逻辑"""
    
    # 创建测试数据
    test_data = [
        {'country': '中国', 'category': '电子产品', 'total_sales_amount': '1334.05'},
        {'country': '中国', 'category': '服装', 'total_sales_amount': '500.00'},
        {'country': '美国', 'category': '电子产品', 'total_sales_amount': '2000.00'},
        {'country': '美国', 'category': '图书', 'total_sales_amount': '800.00'},
    ]

    # 创建查询步骤实例
    query_step = QueryStep({
        'data_source': 'test',
        'dimensions': ['country'],
        'metrics': ['total_sales_amount']
    })

    # 手动测试分区逻辑
    expression = 'ROW_NUMBER() OVER (PARTITION BY country ORDER BY total_sales_amount DESC)'
    
    print("测试每一行的窗口函数计算：")
    for i, row in enumerate(test_data):
        result = query_step._evaluate_window_function(expression, row, test_data)
        print(f"行 {i}: {row} -> rank: {result}")

if __name__ == "__main__":
    test_partition_logic()
