#!/usr/bin/env python3
"""
检查数据库表结构
"""

import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.engine import get_uqm_engine

async def check_table_structure():
    """检查orders和order_items表结构"""
    
    print("=== 检查数据库表结构 ===")
    
    try:
        engine = get_uqm_engine()
        connector_manager = engine.connector_manager
        connector = await connector_manager.get_default_connector()
        
        # 查看orders表结构
        print("\n📋 Orders表结构:")
        orders_structure = await connector.execute_query("DESCRIBE orders")
        for row in orders_structure:
            print(f"  {row}")
        
        # 查看order_items表结构
        print("\n📋 Order_items表结构:")
        items_structure = await connector.execute_query("DESCRIBE order_items")
        for row in items_structure:
            print(f"  {row}")
            
        # 查看orders表的示例数据
        print("\n📊 Orders表示例数据:")
        orders_data = await connector.execute_query("SELECT * FROM orders LIMIT 3")
        for row in orders_data:
            print(f"  {row}")
            
        # 查看order_items表的示例数据
        print("\n📊 Order_items表示例数据:")
        items_data = await connector.execute_query("SELECT * FROM order_items LIMIT 3")
        for row in items_data:
            print(f"  {row}")
    
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_table_structure())
