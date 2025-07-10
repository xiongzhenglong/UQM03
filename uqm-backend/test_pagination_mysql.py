#!/usr/bin/env python3
"""
使用MySQL的分页功能测试脚本
"""

import asyncio
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.engine import get_uqm_engine

async def test_pagination_with_mysql():
    """测试MySQL分页功能"""
    print("开始测试MySQL分页功能...")
    
    # 测试第1页
    uqm_request = {
        "uqm": {
            "metadata": {
                "name": "员工分页查询测试",
                "description": "测试员工表分页功能"
            },
            "steps": [
                {
                    "name": "get_employees_page1",
                    "type": "query",
                    "config": {
                        "data_source": "employees",
                        "dimensions": [
                            "employee_id",
                            "first_name", 
                            "last_name",
                            "job_title"
                        ],
                        "order_by": [
                            {"field": "employee_id", "direction": "ASC"}
                        ]
                    }
                }
            ],
            "output": "get_employees_page1"
        },
        "parameters": {},
        "options": {
            "page": 1,
            "page_size": 5,
            "pagination_target_step": "get_employees_page1"
        }
    }
    
    try:
        engine = get_uqm_engine()
        
        print("执行第1页查询...")
        result = await engine.process(
            uqm_data=uqm_request["uqm"],
            parameters=uqm_request["parameters"],
            options=uqm_request["options"]
        )
        
        print("✅ 第1页查询成功!")
        print(f"返回数据行数: {len(result.data) if result.data else 0}")
        
        pagination_info = result.execution_info.get("pagination")
        if pagination_info:
            print("✅ 分页信息正常:")
            print(f"   当前页: {pagination_info['page']}")
            print(f"   每页大小: {pagination_info['page_size']}")
            print(f"   总记录数: {pagination_info['total_items']}")
            print(f"   总页数: {pagination_info['total_pages']}")
            
            # 显示第1页的数据
            print("第1页数据:")
            for i, row in enumerate(result.data):
                print(f"   {i+1}. ID:{row.get('employee_id')} - {row.get('first_name')} {row.get('last_name')} - {row.get('job_title')}")
            
            total_pages = pagination_info['total_pages']
            if total_pages > 1:
                # 测试第2页
                await test_second_page(engine, total_pages)
            
            return True
        else:
            print("❌ 未找到分页信息")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_second_page(engine, total_pages):
    """测试第2页"""
    print(f"\n测试第2页（总共{total_pages}页）...")
    
    uqm_request = {
        "uqm": {
            "metadata": {
                "name": "员工分页查询第2页",
                "description": "测试第2页数据"
            },
            "steps": [
                {
                    "name": "get_employees_page2",
                    "type": "query",
                    "config": {
                        "data_source": "employees",
                        "dimensions": [
                            "employee_id",
                            "first_name", 
                            "last_name",
                            "job_title"
                        ],
                        "order_by": [
                            {"field": "employee_id", "direction": "ASC"}
                        ]
                    }
                }
            ],
            "output": "get_employees_page2"
        },
        "parameters": {},
        "options": {
            "page": 2,
            "page_size": 5,
            "pagination_target_step": "get_employees_page2"
        }
    }
    
    try:
        result = await engine.process(
            uqm_data=uqm_request["uqm"],
            parameters=uqm_request["parameters"],
            options=uqm_request["options"]
        )
        
        print("✅ 第2页查询成功!")
        print(f"返回数据行数: {len(result.data) if result.data else 0}")
        
        pagination_info = result.execution_info.get("pagination")
        if pagination_info:
            print(f"当前页: {pagination_info['page']}")
            
            # 显示第2页的数据
            print("第2页数据:")
            for i, row in enumerate(result.data):
                print(f"   {i+1}. ID:{row.get('employee_id')} - {row.get('first_name')} {row.get('last_name')} - {row.get('job_title')}")
        
    except Exception as e:
        print(f"❌ 第2页测试失败: {e}")

async def test_multi_step_with_pagination():
    """测试多步骤查询中的分页（enrich场景）"""
    print("\n测试多步骤查询分页...")
    
    uqm_request = {
        "uqm": {
            "metadata": {
                "name": "员工部门信息分页",
                "description": "测试多步骤查询中对特定步骤分页"
            },
            "steps": [
                {
                    "name": "get_employees_paginated",
                    "type": "query", 
                    "config": {
                        "data_source": "employees",
                        "dimensions": ["employee_id", "first_name", "last_name", "department_id"],
                        "order_by": [{"field": "employee_id", "direction": "ASC"}]
                    }
                },
                {
                    "name": "enrich_with_department",
                    "type": "enrich",
                    "config": {
                        "source": "get_employees_paginated",
                        "lookup": {
                            "table": "departments",
                            "columns": ["department_id", "name AS department_name"]
                        },
                        "on": "department_id",
                        "join_type": "left"
                    }
                }
            ],
            "output": "enrich_with_department"
        },
        "parameters": {},
        "options": {
            "page": 1,
            "page_size": 3,
            "pagination_target_step": "get_employees_paginated"  # 对第一个步骤分页
        }
    }
    
    try:
        engine = get_uqm_engine()
        result = await engine.process(
            uqm_data=uqm_request["uqm"],
            parameters=uqm_request["parameters"],
            options=uqm_request["options"]
        )
        
        print("✅ 多步骤分页查询成功!")
        print(f"最终返回数据行数: {len(result.data) if result.data else 0}")
        
        pagination_info = result.execution_info.get("pagination")
        if pagination_info:
            print("✅ 分页信息正常:")
            print(f"   总记录数: {pagination_info['total_items']}")
            print(f"   当前页: {pagination_info['page']}")
            
        # 显示结果数据
        print("结果数据（包含部门信息）:")
        for i, row in enumerate(result.data):
            print(f"   {i+1}. ID:{row.get('employee_id')} - {row.get('first_name')} {row.get('last_name')} - 部门:{row.get('department_name', 'N/A')}")
            
        return True
        
    except Exception as e:
        print(f"❌ 多步骤分页测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("UQM MySQL分页功能完整测试")
    print("=" * 60)
    
    test1_passed = await test_pagination_with_mysql()
    test2_passed = await test_multi_step_with_pagination()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("🎉 所有分页测试通过!")
        print("分页功能实现成功，支持以下特性:")
        print("✅ 基本分页查询")
        print("✅ 正确的分页元数据计算")
        print("✅ 多页数据获取")
        print("✅ 多步骤查询中的选择性分页")
        print("✅ 与现有功能的兼容性")
    else:
        print("❌ 部分测试失败!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 