#!/usr/bin/env python
"""
测试只有calculated_fields的查询配置
验证修改后的ValidationError是否修复
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


async def test_calculated_fields_only():
    """测试只有calculated_fields的配置"""
    
    print("测试只有calculated_fields的查询配置...")
    
    # 测试配置：只有calculated_fields，没有dimensions和metrics
    config = {
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
        query_step = QueryStep(config)
        
        # 验证配置
        query_step.validate()
        
        print("✅ 验证通过！配置支持只有calculated_fields")
        return True
        
    except ValidationError as e:
        print(f"❌ 验证失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False


async def test_original_validation_still_works():
    """测试原始验证逻辑仍然有效"""
    
    print("\n测试原始验证逻辑...")
    
    # 测试配置：没有dimensions、metrics、calculated_fields
    config = {
        "data_source": "products"
    }
    
    try:
        query_step = QueryStep(config)
        query_step.validate()
        
        print("❌ 验证应该失败但却通过了")
        return False
        
    except ValidationError as e:
        if "至少需要指定" in str(e):
            print("✅ 原始验证逻辑正常工作")
            return True
        else:
            print(f"❌ 验证错误消息不正确: {e}")
            return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False


async def test_with_dimensions_and_metrics():
    """测试包含dimensions和metrics的配置仍然有效"""
    
    print("\n测试包含dimensions和metrics的配置...")
    
    config = {
        "data_source": "products",
        "dimensions": ["product_id", "product_name"],
        "metrics": [
            {
                "name": "product_id",
                "aggregation": "COUNT",
                "alias": "total_count"
            }
        ]
    }
    
    try:
        query_step = QueryStep(config)
        query_step.validate()
        
        print("✅ dimensions和metrics配置验证通过")
        return True
        
    except Exception as e:
        print(f"❌ dimensions和metrics配置验证失败: {e}")
        return False


async def main():
    """主测试函数"""
    
    print("开始测试calculated_fields修复...")
    print("=" * 50)
    
    # 运行所有测试
    test_results = []
    
    test_results.append(await test_calculated_fields_only())
    test_results.append(await test_original_validation_still_works())
    test_results.append(await test_with_dimensions_and_metrics())
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    
    if all(test_results):
        print("✅ 所有测试通过！calculated_fields修复成功")
        return True
    else:
        print("❌ 某些测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
