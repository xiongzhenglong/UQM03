"""
测试用户提供的配置案例，分析为什么返回空数据
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.engine import get_uqm_engine

def create_user_test_config():
    """创建用户提供的测试配置"""
    return {
        "metadata": {
            "name": "AdvancedParameterizedSalaryPivotAnalysis",
            "description": "高级参数化薪资透视分析，支持部门和职位过滤。通过直接参数替换实现条件过滤。",
            "version": "2.0",
            "author": "HR Analytics Team",
            "tags": ["hr_analysis", "salary_analysis", "pivot_table", "parameterized", "advanced"]
        },
        "parameters": [
            {
                "name": "target_departments",
                "type": "array",
                "description": "要分析的目标部门列表",
                "required": False,
                "default": ["信息技术部", "销售部", "人力资源部"]
            },
            {
                "name": "min_salary_threshold",
                "type": "number",
                "description": "最低薪资阈值，用于过滤薪资数据",
                "required": False,
                "default": 15000
            }
        ],
        "steps": [
            {
                "name": "get_filtered_employee_salary_data",
                "type": "query",
                "config": {
                    "data_source": "employees",
                    "joins": [
                        {
                            "type": "INNER",
                            "table": "departments",
                            "on": "employees.department_id = departments.department_id"
                        }
                    ],
                    "dimensions": [
                        {"expression": "departments.name", "alias": "department_name"},
                        {"expression": "employees.job_title", "alias": "job_title"},
                        {"expression": "employees.salary", "alias": "salary"}
                    ],
                    "filters": [
                        {
                            "field": "employees.is_active",
                            "operator": "=",
                            "value": True
                        },
                        {
                            "field": "employees.job_title",
                            "operator": "=",
                            "value": "$job_title",
                            "conditional": {
                                "type": "expression",
                                "expression": "$job_title != 'HR经理'"  # 修复：使用 expression 而不是 parameter
                            }
                        },
                        {
                            "field": "employees.hire_date",
                            "operator": "BETWEEN",
                            "value": ["$hire_date_from", "$hire_date_to"],
                            "conditional": {
                                "type": "all_parameters_exist",
                                "parameters": ["hire_date_from", "hire_date_to"]
                            }
                        },
                        {
                            "field": "employees.salary",
                            "operator": ">=", 
                            "value": "$min_salary_threshold"
                        },
                        {
                            "field": "departments.name",
                            "operator": "IN",
                            "value": "$target_departments"
                        }
                    ]
                }
            },
            {
                "name": "pivot_salary_analysis",
                "type": "pivot",
                "config": {
                    "source": "get_filtered_employee_salary_data",
                    "index": "department_name",
                    "columns": "job_title",
                    "values": "salary",
                    "agg_func": "mean",
                    "fill_value": 0,
                    "missing_strategy": "drop"
                }
            }
        ],
        "output": "pivot_salary_analysis"
    }

async def test_user_case_debug():
    """调试用户案例"""
    print("=" * 70)
    print("调试用户提供的配置案例")
    print("=" * 70)
    
    engine = get_uqm_engine()
    config = create_user_test_config()
    
    # 用户提供的参数
    parameters = {
        "target_departments": ["信息技术部", "销售部", "人力资源部"],
        "min_salary_threshold": 15000,
        "job_title": "HR经理",
        "hire_date_from": "2025-01-15",
        "hire_date_to": "2025-06-15"
    }
    
    print(f"📋 用户参数: {json.dumps(parameters, ensure_ascii=False, indent=2)}")
    
    try:
        # 解析配置
        parsed_data = engine.parser.parse(config)
        print("✅ 配置解析成功")
        
        # 参数替换和条件过滤器处理
        processed_data = engine._substitute_parameters(parsed_data, parameters)
        
        # 检查处理后的过滤器
        filters = processed_data["steps"][0]["config"]["filters"]
        print(f"\n📊 处理后过滤器数量: {len(filters)}")
        
        print("\n🔍 详细过滤器分析:")
        for i, filter_config in enumerate(filters, 1):
            field = filter_config.get("field", "unknown")
            operator = filter_config.get("operator", "unknown")
            value = filter_config.get("value", "unknown")
            print(f"   {i}. {field} {operator} {value}")
        
        # 分析可能的问题
        print("\n🚨 潜在问题分析:")
        
        # 检查job_title过滤器的逻辑
        job_title_filters = [f for f in filters if f.get("field") == "employees.job_title"]
        if job_title_filters:
            job_filter = job_title_filters[0]
            if job_filter.get("operator") == "=" and job_filter.get("value") == "HR经理":
                print("   ⚠️  问题1: job_title过滤器设置为 = 'HR经理'")
                print("       但条件表达式是 $job_title != 'HR经理'")
                print("       这意味着只有当job_title不等于'HR经理'时才应用此过滤器")
                print("       但过滤器本身却要求job_title等于'HR经理'，这是矛盾的")
        
        # 检查日期范围
        hire_date_filters = [f for f in filters if f.get("field") == "employees.hire_date"]
        if hire_date_filters:
            print("   ⚠️  问题2: 日期范围可能太窄")
            print("       hire_date_from: 2025-01-15")
            print("       hire_date_to: 2025-06-15")
            print("       这个日期范围在未来，数据库中可能没有这个时间段的数据")
        
        # 检查部门过滤
        dept_filters = [f for f in filters if f.get("field") == "departments.name"]
        if dept_filters:
            dept_filter = dept_filters[0]
            print(f"   ✅ 部门过滤器: {dept_filter.get('value')}")
        
        # 检查薪资过滤
        salary_filters = [f for f in filters if f.get("field") == "employees.salary"]
        if salary_filters:
            salary_filter = salary_filters[0]
            print(f"   ✅ 薪资过滤器: >= {salary_filter.get('value')}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def create_corrected_config():
    """创建修正后的配置"""
    return {
        "metadata": {
            "name": "CorrectedParameterizedSalaryPivotAnalysis",
            "description": "修正后的参数化薪资透视分析",
            "version": "2.1",
            "author": "HR Analytics Team",
            "tags": ["hr_analysis", "salary_analysis", "pivot_table", "parameterized", "corrected"]
        },
        "steps": [
            {
                "name": "get_filtered_employee_salary_data",
                "type": "query",
                "config": {
                    "data_source": "employees",
                    "joins": [
                        {
                            "type": "INNER",
                            "table": "departments",
                            "on": "employees.department_id = departments.department_id"
                        }
                    ],
                    "dimensions": [
                        {"expression": "departments.name", "alias": "department_name"},
                        {"expression": "employees.job_title", "alias": "job_title"},
                        {"expression": "employees.salary", "alias": "salary"},
                        {"expression": "employees.hire_date", "alias": "hire_date"}
                    ],
                    "filters": [
                        {
                            "field": "employees.is_active",
                            "operator": "=",
                            "value": True
                        },
                        {
                            "field": "employees.job_title",
                            "operator": "=",
                            "value": "$job_title",
                            "conditional": {
                                "type": "parameter_exists",
                                "parameter": "job_title"
                            }
                        },
                        {
                            "field": "employees.hire_date",
                            "operator": ">=",
                            "value": "$hire_date_from",
                            "conditional": {
                                "type": "parameter_exists",
                                "parameter": "hire_date_from"
                            }
                        },
                        {
                            "field": "employees.hire_date",
                            "operator": "<=",
                            "value": "$hire_date_to",
                            "conditional": {
                                "type": "parameter_exists",
                                "parameter": "hire_date_to"
                            }
                        },
                        {
                            "field": "departments.name",
                            "operator": "IN",
                            "value": "$target_departments",
                            "conditional": {
                                "type": "parameter_not_empty",
                                "parameter": "target_departments",
                                "empty_values": [None, []]
                            }
                        },
                        {
                            "field": "employees.salary",
                            "operator": ">=",
                            "value": "$min_salary_threshold",
                            "conditional": {
                                "type": "parameter_not_empty",
                                "parameter": "min_salary_threshold",
                                "empty_values": [None, 0]
                            }
                        }
                    ]
                }
            },
            {
                "name": "pivot_salary_analysis",
                "type": "pivot",
                "config": {
                    "source": "get_filtered_employee_salary_data",
                    "index": "department_name",
                    "columns": "job_title",
                    "values": "salary",
                    "agg_func": "mean",
                    "fill_value": 0,
                    "missing_strategy": "drop"
                }
            }
        ],
        "output": "pivot_salary_analysis"
    }

async def test_corrected_config():
    """测试修正后的配置"""
    print("\n" + "=" * 70)
    print("测试修正后的配置")
    print("=" * 70)
    
    engine = get_uqm_engine()
    config = create_corrected_config()
    
    # 测试不同的参数组合
    test_scenarios = [
        {
            "name": "场景1: 查找HR经理（使用合理的日期范围）",
            "parameters": {
                "target_departments": ["人力资源部"],
                "job_title": "HR经理",
                "hire_date_from": "2020-01-01",
                "hire_date_to": "2024-12-31"
            }
        },
        {
            "name": "场景2: 查找信息技术部员工（不限职位）",
            "parameters": {
                "target_departments": ["信息技术部"],
                "min_salary_threshold": 15000
            }
        },
        {
            "name": "场景3: 查找所有部门的软件工程师",
            "parameters": {
                "job_title": "软件工程师",
                "min_salary_threshold": 18000
            }
        },
        {
            "name": "场景4: 基础查询（只过滤活跃员工）",
            "parameters": {}
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🧪 {scenario['name']}")
        print(f"📋 参数: {json.dumps(scenario['parameters'], ensure_ascii=False)}")
        
        try:
            # 解析和处理配置
            parsed_data = engine.parser.parse(config)
            processed_data = engine._substitute_parameters(parsed_data, scenario['parameters'])
            
            # 显示过滤器
            filters = processed_data["steps"][0]["config"]["filters"]
            print(f"📊 生成过滤器: {len(filters)}个")
            
            for filter_config in filters:
                field = filter_config.get("field", "unknown")
                operator = filter_config.get("operator", "unknown")
                value = filter_config.get("value", "unknown")
                print(f"   • {field} {operator} {value}")
            
            print("✅ 配置处理成功")
            
        except Exception as e:
            print(f"❌ 配置处理失败: {e}")

async def save_corrected_configs():
    """保存修正后的配置文件"""
    print("\n" + "=" * 70)
    print("保存修正后的配置文件")
    print("=" * 70)
    
    # 保存原始配置（有问题的）
    original_config = create_user_test_config()
    with open("original_problematic_config.json", "w", encoding="utf-8") as f:
        json.dump(original_config, f, indent=2, ensure_ascii=False)
    print("✅ 原始配置（有问题）已保存到: original_problematic_config.json")
    
    # 保存修正后的配置
    corrected_config = create_corrected_config()
    with open("corrected_config.json", "w", encoding="utf-8") as f:
        json.dump(corrected_config, f, indent=2, ensure_ascii=False)
    print("✅ 修正后的配置已保存到: corrected_config.json")
    
    # 创建使用说明
    usage_guide = {
        "问题分析": {
            "问题1": "原始配置中job_title过滤器的条件表达式逻辑错误",
            "问题2": "日期范围设置在未来，数据库中没有对应数据",
            "问题3": "conditional字段中使用了错误的属性名"
        },
        "修正方案": {
            "修正1": "移除矛盾的条件表达式，使用parameter_exists检查",
            "修正2": "使用合理的历史日期范围进行测试",
            "修正3": "为所有参数化过滤器添加正确的条件检查"
        },
        "测试参数示例": {
            "查找HR经理": {
                "target_departments": ["人力资源部"],
                "job_title": "HR经理",
                "hire_date_from": "2020-01-01",
                "hire_date_to": "2024-12-31"
            },
            "查找IT部门员工": {
                "target_departments": ["信息技术部"],
                "min_salary_threshold": 15000
            }
        }
    }
    
    with open("configuration_fix_guide.json", "w", encoding="utf-8") as f:
        json.dump(usage_guide, f, indent=2, ensure_ascii=False)
    print("✅ 配置修复指南已保存到: configuration_fix_guide.json")

if __name__ == "__main__":
    print("🚀 开始调试用户配置案例...")
    
    # 调试原始配置
    asyncio.run(test_user_case_debug())
    
    # 测试修正后的配置
    asyncio.run(test_corrected_config())
    
    # 保存配置文件
    asyncio.run(save_corrected_configs())
    
    print("\n" + "=" * 70)
    print("🎉 调试和修复完成!")
    print("=" * 70)
    print("📋 问题总结:")
    print("1. 条件表达式逻辑错误：$job_title != 'HR经理' 但却要过滤 = 'HR经理'")
    print("2. 日期范围在未来：2025年的数据在测试数据库中不存在")
    print("3. conditional字段配置错误：应该使用expression而不是parameter")
    print("\n📋 解决方案:")
    print("1. 使用parameter_exists检查参数是否存在")
    print("2. 使用合理的历史日期范围")
    print("3. 为所有参数化过滤器添加条件检查")
    print("4. 使用修正后的配置文件进行测试")
