#!/usr/bin/env python3
"""
调试数据类型处理问题
"""

import json
import asyncio
import sys
import os
from decimal import Decimal

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_type_handling():
    """测试数据类型处理"""
    
    print("=== 测试数据类型处理 ===")
    
    # 模拟实际数据
    test_data = [
        {
            'min_price': Decimal('89.00'),  # MySQL返回的是Decimal类型
            'max_price': Decimal('1599.00'),
            'avg_price': Decimal('609.083333'),
            'total_products': 12
        }
    ]
    
    # 模拟断言
    assertion = {
        "type": "range",
        "field": "min_price",
        "min": 1000,
        "message": "产品最低价格必须大于1000"
    }
    
    print(f"📊 测试数据:")
    for record in test_data:
        for key, value in record.items():
            print(f"  {key}: {value} (类型: {type(value)})")
    
    print(f"\n🔍 断言逻辑测试:")
    field_name = assertion.get("field")
    min_value = assertion.get("min")
    
    for i, record in enumerate(test_data):
        if field_name in record:
            value = record[field_name]
            print(f"  原始值: {value} (类型: {type(value)})")
            print(f"  isinstance(value, (int, float)): {isinstance(value, (int, float))}")
            print(f"  isinstance(value, Decimal): {isinstance(value, Decimal)}")
            
            # 测试类型转换
            if isinstance(value, (int, float)):
                print(f"  ✅ 会进入断言逻辑")
                if min_value is not None and value < min_value:
                    print(f"  ❌ 应该失败: {value} < {min_value}")
                else:
                    print(f"  ✅ 通过检查: {value} >= {min_value}")
            else:
                print(f"  ❌ 不会进入断言逻辑 - 类型检查失败")
                print(f"  问题: Decimal类型不在 (int, float) 中")
                
                # 测试转换
                try:
                    float_value = float(value)
                    print(f"  转换后: {float_value} (类型: {type(float_value)})")
                    if min_value is not None and float_value < min_value:
                        print(f"  ❌ 转换后应该失败: {float_value} < {min_value}")
                    else:
                        print(f"  ✅ 转换后通过: {float_value} >= {min_value}")
                except:
                    print(f"  ❌ 无法转换为float")

if __name__ == "__main__":
    test_type_handling()
