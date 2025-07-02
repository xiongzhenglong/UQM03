#!/usr/bin/env python
"""
测试用户原始的库存警告配置
"""

import sys
import json
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.steps.query_step import QueryStep
from src.utils.exceptions import ValidationError, ExecutionError


async def test_user_stock_config():
    """测试用户的库存警告配置"""
    
    print("测试用户的原始库存警告配置...")
    
    # 用户的原始配置
    stock_summary_config = {
        "data_source": "products",
        "joins": [
            {
                "type": "LEFT",
                "table": "inventory",
                "on": {
                    "left": "products.product_id",
                    "right": "inventory.product_id",
                    "operator": "="
                }
            }
        ],
        "calculated_fields": [
            {
                "name": "total_products",
                "expression": "COUNT(DISTINCT products.product_id)"
            },
            {
                "name": "low_stock_count",
                "expression": "COUNT(CASE WHEN COALESCE(inventory.quantity_on_hand, 0) <= 10 AND COALESCE(inventory.quantity_on_hand, 0) > 0 THEN 1 END)"
            },
            {
                "name": "out_of_stock_count", 
                "expression": "COUNT(CASE WHEN COALESCE(inventory.quantity_on_hand, 0) = 0 THEN 1 END)"
            }
        ],
        "filters": [
            {
                "field": "products.discontinued",
                "operator": "=",
                "value": False
            }
        ]
    }
    
    try:
        # 创建查询步骤
        query_step = QueryStep(stock_summary_config)
        
        # 验证配置
        query_step.validate()
        
        print("✅ 用户的库存警告配置验证通过！")
        print("配置详情:")
        print(f"  - 数据源: {stock_summary_config['data_source']}")
        print(f"  - JOIN表: {stock_summary_config['joins'][0]['table']}")
        print(f"  - 计算字段数量: {len(stock_summary_config['calculated_fields'])}")
        print("  - 计算字段列表:")
        for field in stock_summary_config['calculated_fields']:
            print(f"    * {field['name']}")
        
        return True
        
    except ValidationError as e:
        print(f"❌ 验证失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False


async def main():
    """主测试函数"""
    
    print("验证用户原始配置修复...")
    print("=" * 50)
    
    success = await test_user_stock_config()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 修复成功！用户的配置现在可以正常工作了")
        print("\n现在用户可以使用只有 calculated_fields 的查询配置，")
        print("而不需要强制添加 dimensions 或 metrics。")
    else:
        print("❌ 修复失败")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
