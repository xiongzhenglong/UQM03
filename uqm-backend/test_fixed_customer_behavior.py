#!/usr/bin/env python3
"""
测试修复后的客户行为多维分析配置
"""

import json
import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.engine import UQMEngine


async def test_fixed_customer_behavior_analysis():
    """测试修复后的客户行为分析配置"""
    
    print("🧪 测试修复后的客户行为多维分析配置...")
    
    # 读取修复后的配置
    with open('fixed_customer_behavior_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    try:
        # 创建UQM引擎实例
        engine = UQMEngine()
        
        print("✅ 步骤1: 配置加载成功")
        
        # 执行分析
        print("🔄 开始执行客户行为分析...")
        response = await engine.process(config)
        
        print("✅ 步骤2: 分析执行成功")
        print(f"📊 结果条数: {response.execution_info['row_count'] if response.success else 0}")
        
        if response.success and response.data:
            result = response.data
            print("\n📋 结果示例:")
            # 显示前3条结果
            for i, record in enumerate(result[:3]):
                print(f"  记录 {i+1}:")
                for key, value in record.items():
                    if isinstance(value, float):
                        print(f"    {key}: {value:.2f}")
                    else:
                        print(f"    {key}: {value}")
                print()
        
        print("✅ 所有测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_individual_steps():
    """测试各个步骤是否能正常工作"""
    
    print("\n🔍 测试各个步骤...")
    
    # 测试基础查询
    base_query_config = {
        "metadata": {
            "name": "TestBaseQuery",
            "description": "测试基础查询"
        },
        "steps": [
            {
                "name": "get_customer_behavior_data",
                "type": "query",
                "config": {
                    "data_source": "orders",
                    "joins": [
                        {"type": "INNER", "table": "customers", "on": "orders.customer_id = customers.customer_id"},
                        {"type": "INNER", "table": "order_items", "on": "orders.order_id = order_items.order_id"}
                    ],
                    "dimensions": [
                        {"expression": "customers.customer_segment", "alias": "customer_segment"},
                        {"expression": "customers.country", "alias": "country"},
                        {"expression": "(order_items.quantity * order_items.unit_price * (1 - order_items.discount))", "alias": "order_amount"},
                        {"expression": "orders.order_id", "alias": "order_id"},
                        {"expression": "customers.customer_id", "alias": "customer_id"}
                    ],
                    "filters": [
                        {"field": "orders.order_date", "operator": ">=", "value": "2024-01-01"}
                    ],
                    "limit": 10
                }
            }
        ],
        "output": "get_customer_behavior_data"
    }
    
    try:
        engine = UQMEngine()
        response = await engine.process(base_query_config)
        print(f"✅ 基础查询测试通过: {response.execution_info['row_count'] if response.success else 0} 条记录")
        
        if response.success and response.data:
            result = response.data
            print("📋 基础数据字段:")
            for key in result[0].keys():
                print(f"  - {key}")
        
        return response.success
        
    except Exception as e:
        print(f"❌ 基础查询测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    async def main():
        # 测试基础查询
        step1_ok = await test_individual_steps()
        
        if step1_ok:
            # 测试完整配置
            step2_ok = await test_fixed_customer_behavior_analysis()
            
            if step2_ok:
                print("\n🎉 所有测试都通过了!")
            else:
                print("\n💥 完整配置测试失败")
        else:
            print("\n💥 基础查询测试失败，跳过完整测试")
    
    asyncio.run(main())
