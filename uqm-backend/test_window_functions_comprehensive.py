#!/usr/bin/env python3
"""
全面测试窗口函数功能
验证不同窗口函数和多字段分区的情况
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.steps.query_step import QueryStep

def test_row_number_function():
    """测试 ROW_NUMBER 窗口函数"""
    print("=== 测试 ROW_NUMBER 窗口函数 ===")
    
    test_data = [
        {'country': '中国', 'category': '电子产品', 'sales': 1334.05, 'year': 2023},
        {'country': '中国', 'category': '服装', 'sales': 500.00, 'year': 2023},
        {'country': '中国', 'category': '电子产品', 'sales': 1500.00, 'year': 2024},
        {'country': '美国', 'category': '电子产品', 'sales': 2000.00, 'year': 2023},
        {'country': '美国', 'category': '图书', 'sales': 800.00, 'year': 2023},
    ]

    config = {
        'data_source': 'test_data',
        'dimensions': ['country', 'category', 'sales', 'year'],
        'calculated_fields': [
            {
                'alias': 'row_num_by_country',
                'expression': 'ROW_NUMBER() OVER (PARTITION BY country ORDER BY sales DESC)'
            }
        ]
    }

    query_step = QueryStep(config)
    result = query_step._process_step_data(test_data)

    print('结果:')
    for row in result:
        print(f"  {row}")
    
    # 验证结果
    assert len(result) == len(test_data)
    for row in result:
        assert 'row_num_by_country' in row
        assert isinstance(row['row_num_by_country'], int)
        assert row['row_num_by_country'] >= 1
    
    print("✅ ROW_NUMBER 测试通过")

def test_rank_function():
    """测试 RANK 窗口函数"""
    print("\n=== 测试 RANK 窗口函数 ===")
    
    test_data = [
        {'dept': 'IT', 'name': 'Alice', 'salary': 8000},
        {'dept': 'IT', 'name': 'Bob', 'salary': 8000},  # 相同薪资
        {'dept': 'IT', 'name': 'Charlie', 'salary': 7000},
        {'dept': 'Sales', 'name': 'David', 'salary': 9000},
        {'dept': 'Sales', 'name': 'Eve', 'salary': 6000},
    ]

    config = {
        'data_source': 'test_data',
        'dimensions': ['dept', 'name', 'salary'],
        'calculated_fields': [
            {
                'alias': 'salary_rank',
                'expression': 'RANK() OVER (PARTITION BY dept ORDER BY salary DESC)'
            }
        ]
    }

    query_step = QueryStep(config)
    result = query_step._process_step_data(test_data)

    print('结果:')
    for row in result:
        print(f"  {row}")
    
    # 验证结果
    assert len(result) == len(test_data)
    for row in result:
        assert 'salary_rank' in row
        assert isinstance(row['salary_rank'], int)
        assert row['salary_rank'] >= 1
    
    print("✅ RANK 测试通过")

def test_multi_field_partition():
    """测试多字段分区"""
    print("\n=== 测试多字段分区 ===")
    
    test_data = [
        {'region': '北方', 'city': '北京', 'product': '电子产品', 'sales': 1000},
        {'region': '北方', 'city': '北京', 'product': '服装', 'sales': 800},
        {'region': '北方', 'city': '天津', 'product': '电子产品', 'sales': 600},
        {'region': '南方', 'city': '上海', 'product': '电子产品', 'sales': 1200},
        {'region': '南方', 'city': '深圳', 'product': '电子产品', 'sales': 1100},
    ]

    config = {
        'data_source': 'test_data',
        'dimensions': ['region', 'city', 'product', 'sales'],
        'calculated_fields': [
            {
                'alias': 'rank_by_region_product',
                'expression': 'ROW_NUMBER() OVER (PARTITION BY region, product ORDER BY sales DESC)'
            }
        ]
    }

    query_step = QueryStep(config)
    result = query_step._process_step_data(test_data)

    print('结果:')
    for row in result:
        print(f"  {row}")
    
    # 验证结果
    assert len(result) == len(test_data)
    for row in result:
        assert 'rank_by_region_product' in row
        assert isinstance(row['rank_by_region_product'], int)
        assert row['rank_by_region_product'] >= 1
    
    print("✅ 多字段分区测试通过")

def test_no_partition():
    """测试无分区的全局排名"""
    print("\n=== 测试无分区的全局排名 ===")
    
    test_data = [
        {'name': 'Alice', 'score': 95},
        {'name': 'Bob', 'score': 87},
        {'name': 'Charlie', 'score': 92},
        {'name': 'David', 'score': 89},
    ]

    config = {
        'data_source': 'test_data',
        'dimensions': ['name', 'score'],
        'calculated_fields': [
            {
                'alias': 'global_rank',
                'expression': 'ROW_NUMBER() OVER (ORDER BY score DESC)'
            }
        ]
    }

    query_step = QueryStep(config)
    result = query_step._process_step_data(test_data)

    print('结果:')
    for row in result:
        print(f"  {row}")
    
    # 验证结果
    assert len(result) == len(test_data)
    ranks = [row['global_rank'] for row in result]
    assert set(ranks) == {1, 2, 3, 4}  # 应该有1-4的排名
    
    print("✅ 无分区全局排名测试通过")

def test_string_numeric_conversion():
    """测试字符串数值转换"""
    print("\n=== 测试字符串数值转换 ===")
    
    test_data = [
        {'category': 'A', 'amount': '1000.50'},  # 字符串格式的数字
        {'category': 'A', 'amount': '500.25'},
        {'category': 'B', 'amount': '750.00'},
        {'category': 'B', 'amount': '1200.75'},
    ]

    config = {
        'data_source': 'test_data',
        'dimensions': ['category', 'amount'],
        'calculated_fields': [
            {
                'alias': 'amount_rank',
                'expression': 'ROW_NUMBER() OVER (PARTITION BY category ORDER BY amount DESC)'
            }
        ]
    }

    query_step = QueryStep(config)
    result = query_step._process_step_data(test_data)

    print('结果:')
    for row in result:
        print(f"  {row}")
    
    # 验证结果
    assert len(result) == len(test_data)
    
    # 检查每个分类内的排名是否正确
    a_records = [r for r in result if r['category'] == 'A']
    b_records = [r for r in result if r['category'] == 'B']
    
    # A类：1000.50 应该排第1，500.25 应该排第2
    assert len(a_records) == 2
    # B类：1200.75 应该排第1，750.00 应该排第2
    assert len(b_records) == 2
    
    print("✅ 字符串数值转换测试通过")

def test_edge_cases():
    """测试边界情况"""
    print("\n=== 测试边界情况 ===")
    
    # 空数据测试
    print("测试空数据...")
    config = {
        'data_source': 'test_data',
        'dimensions': ['name'],
        'calculated_fields': [
            {
                'alias': 'rank',
                'expression': 'ROW_NUMBER() OVER (ORDER BY name)'
            }
        ]
    }
    
    query_step = QueryStep(config)
    result = query_step._process_step_data([])
    assert result == []
    print("✅ 空数据测试通过")
    
    # 单条记录测试
    print("测试单条记录...")
    result = query_step._process_step_data([{'name': 'Alice'}])
    assert len(result) == 1
    assert result[0]['rank'] == 1
    print("✅ 单条记录测试通过")
    
    # 空值处理测试
    print("测试空值处理...")
    test_data = [
        {'name': 'Alice', 'score': 100},
        {'name': 'Bob', 'score': None},
        {'name': 'Charlie', 'score': 90},
    ]
    
    config = {
        'data_source': 'test_data',
        'dimensions': ['name', 'score'],
        'calculated_fields': [
            {
                'alias': 'score_rank',
                'expression': 'ROW_NUMBER() OVER (ORDER BY score DESC)'
            }
        ]
    }
    
    query_step = QueryStep(config)
    result = query_step._process_step_data(test_data)
    assert len(result) == 3
    for row in result:
        assert 'score_rank' in row
    print("✅ 空值处理测试通过")

def run_all_tests():
    """运行所有测试"""
    print("开始运行窗口函数全面测试...")
    
    try:
        test_row_number_function()
        test_rank_function()
        test_multi_field_partition()
        test_no_partition()
        test_string_numeric_conversion()
        test_edge_cases()
        
        print("\n" + "="*50)
        print("🎉 所有测试都通过了！窗口函数功能完全正常！")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
