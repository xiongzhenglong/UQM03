#!/usr/bin/env python3
"""
调试窗口函数的实现
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.steps.query_step import QueryStep

def test_window_function_parsing():
    """测试窗口函数解析"""
    
    # 创建测试数据
    test_data = [
        {'country': '中国', 'category': '电子产品', 'total_sales_amount': '1334.05'},
        {'country': '中国', 'category': '服装', 'total_sales_amount': '500.00'},
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
        ]
    }

    # 创建查询步骤实例
    query_step = QueryStep(config)

    # 测试窗口函数解析
    expression = 'ROW_NUMBER() OVER (PARTITION BY country ORDER BY total_sales_amount DESC)'
    current_row = {'country': '中国', 'category': '电子产品', 'total_sales_amount': '1334.05'}
    
    result = query_step._evaluate_window_function(expression, current_row, test_data)
    print(f"窗口函数结果: {result}")
    
    # 检查第二行
    current_row2 = {'country': '中国', 'category': '服装', 'total_sales_amount': '500.00'}
    result2 = query_step._evaluate_window_function(expression, current_row2, test_data)
    print(f"第二行窗口函数结果: {result2}")
    
    # 处理完整数据
    result = query_step._process_step_data(test_data)
    print('完整处理结果:')
    for row in result:
        print(f"  {row}")

if __name__ == "__main__":
    test_window_function_parsing()
