#!/usr/bin/env python3
"""
检查products和inventory表结构
"""

import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.engine import get_uqm_engine

async def check_products_and_inventory():
    """检查products和inventory表结构"""
    
    print("=== 检查products和inventory表结构 ===")
    
    try:
        engine = get_uqm_engine()
        connector_manager = engine.connector_manager
        connector = await connector_manager.get_default_connector()
        
        # 查看products表结构
        print("\n📋 Products表结构:")
        products_structure = await connector.execute_query("DESCRIBE products")
        for row in products_structure:
            print(f"  {row}")
        
        # 查看inventory表结构
        print("\n📋 Inventory表结构:")
        try:
            inventory_structure = await connector.execute_query("DESCRIBE inventory")
            for row in inventory_structure:
                print(f"  {row}")
        except Exception as e:
            print(f"  ❌ inventory表不存在或无法访问: {e}")
        
        # 查看warehouses表结构
        print("\n📋 Warehouses表结构:")
        try:
            warehouses_structure = await connector.execute_query("DESCRIBE warehouses")
            for row in warehouses_structure:
                print(f"  {row}")
        except Exception as e:
            print(f"  ❌ warehouses表不存在或无法访问: {e}")
            
        # 查看products表的示例数据
        print("\n📊 Products表示例数据:")
        products_data = await connector.execute_query("SELECT * FROM products LIMIT 3")
        for row in products_data:
            print(f"  {row}")
            
        # 查看所有表
        print("\n📋 所有表:")
        tables = await connector.execute_query("SHOW TABLES")
        for table in tables:
            print(f"  {table}")
    
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_products_and_inventory())
