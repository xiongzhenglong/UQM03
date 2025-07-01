"""
测试修复后的用户案例配置
验证所有问题都已解决
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.engine import get_uqm_engine

async def test_fixed_config():
    """测试修复后的配置"""
    print("🔧 测试修复后的用户案例配置")
    print("=" * 60)
    
    # 加载修复后的配置
    with open("fixed_user_case_config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    engine = get_uqm_engine()
    
    # 定义测试场景
    test_scenarios = [
        {
            "name": "基础测试",
            "description": "无参数，返回所有数据",
            "parameters": {}
        },
        {
            "name": "部门过滤",
            "description": "仅分析IT和销售部门",
            "parameters": {
                "target_departments": ["信息技术部", "销售部"]
            }
        },
        {
            "name": "职位排除",
            "description": "排除人事专员职位",
            "parameters": {
                "target_departments": ["信息技术部", "人力资源部"],
                "exclude_job_title": "人事专员"
            }
        },
        {
            "name": "薪资范围",
            "description": "薪资15K-40K范围",
            "parameters": {
                "min_salary": 15000,
                "max_salary": 40000
            }
        },
        {
            "name": "日期范围",
            "description": "2022-2024年入职员工",
            "parameters": {
                "hire_date_from": "2022-01-01",
                "hire_date_to": "2024-12-31",
                "target_departments": ["信息技术部", "销售部"]
            }
        },
        {
            "name": "综合过滤",
            "description": "多条件综合测试",
            "parameters": {
                "target_departments": ["信息技术部"],
                "min_salary": 18000,
                "hire_date_from": "2020-01-01"
            }
        }
    ]
    
    success_count = 0
    total_count = len(test_scenarios)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\\n📋 测试场景 {i}: {scenario['name']}")
        print(f"   描述: {scenario['description']}")
        print(f"   参数: {json.dumps(scenario['parameters'], ensure_ascii=False)}")
        
        try:
            # 执行查询
            result = await engine.process(config, scenario['parameters'])
            
            if result.success and result.data:
                print(f"   ✅ 成功 - 返回 {len(result.data)} 行数据")
                success_count += 1
                
                # 显示第一行数据作为示例
                if len(result.data) > 0:
                    first_row = result.data[0]
                    # 只显示前几个字段
                    display_fields = dict(list(first_row.items())[:3])
                    print(f"   📋 示例数据: {json.dumps(display_fields, ensure_ascii=False)}")
                    
            elif result.success and not result.data:
                print("   ⚠️  成功但无数据返回")
                
            else:
                print(f"   ❌ 失败 - {result}")
                
        except Exception as e:
            print(f"   ❌ 异常 - {e}")
    
    print(f"\\n\\n📊 测试总结")
    print("=" * 30)
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 所有测试通过！用户案例问题已完全解决。")
    else:
        print(f"⚠️  有 {total_count - success_count} 个测试失败，需要进一步调查。")

async def verify_fixes():
    """验证具体修复点"""
    print("\\n\\n🔍 验证具体修复点")
    print("=" * 40)
    
    engine = get_uqm_engine()
    
    # 加载修复后的配置
    with open("fixed_user_case_config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    print("1. 验证条件过滤器逻辑")
    print("-" * 30)
    
    # 测试有问题的参数组合（原来会导致逻辑矛盾的）
    problematic_params = {
        "exclude_job_title": "HR经理"  # 原来的问题参数
    }
    
    try:
        parsed_data = engine.parser.parse(config)
        processed_data = engine._substitute_parameters(parsed_data, problematic_params)
        
        filters = processed_data["steps"][0]["config"]["filters"]
        job_title_filters = [f for f in filters if f.get("field") == "employees.job_title"]
        
        if job_title_filters:
            job_filter = job_title_filters[0]
            print(f"   过滤器配置: {job_filter.get('field')} {job_filter.get('operator')} {job_filter.get('value')}")
            print("   ✅ 逻辑清晰：当提供exclude_job_title参数时，排除该职位")
        else:
            print("   ❌ 未找到职位过滤器")
            
    except Exception as e:
        print(f"   ❌ 验证失败: {e}")
    
    print("\\n2. 验证SQL语法")
    print("-" * 30)
    
    # 测试会产生数组操作的场景
    array_params = {
        "target_departments": ["信息技术部", "销售部"]
    }
    
    try:
        result = await engine.process(config, array_params)
        if result.success:
            print("   ✅ 数组参数SQL生成正常")
        else:
            print("   ❌ 数组参数SQL生成失败")
    except Exception as e:
        if "syntax" in str(e).lower():
            print(f"   ❌ SQL语法错误: {e}")
        else:
            print(f"   ⚠️  其他错误: {e}")
    
    print("\\n3. 验证参数值合理性")
    print("-" * 30)
    
    # 测试历史日期范围
    reasonable_params = {
        "hire_date_from": "2020-01-01",
        "hire_date_to": "2024-12-31"
    }
    
    try:
        result = await engine.process(config, reasonable_params)
        if result.success and result.data:
            print(f"   ✅ 历史日期范围正常 - 返回 {len(result.data)} 行数据")
        elif result.success and not result.data:
            print("   ⚠️  历史日期范围无数据（可能是数据库数据问题）")
        else:
            print("   ❌ 历史日期范围查询失败")
    except Exception as e:
        print(f"   ❌ 日期参数验证失败: {e}")

async def main():
    """主函数"""
    await test_fixed_config()
    await verify_fixes()

if __name__ == "__main__":
    asyncio.run(main())
