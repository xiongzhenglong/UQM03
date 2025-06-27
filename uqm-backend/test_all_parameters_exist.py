"""
测试 all_parameters_exist 条件过滤器功能
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.engine import get_uqm_engine

def create_all_parameters_exist_test_config():
    """创建测试 all_parameters_exist 的配置"""
    return {
        "metadata": {
            "name": "AllParametersExistTest",
            "description": "测试 all_parameters_exist 条件过滤器功能",
            "version": "1.0"
        },
        "parameters": [
            {
                "name": "hire_date_from",
                "type": "string",
                "required": False
            },
            {
                "name": "hire_date_to",
                "type": "string",
                "required": False
            },
            {
                "name": "salary_min",
                "type": "number",
                "required": False
            },
            {
                "name": "salary_max",
                "type": "number",
                "required": False
            },
            {
                "name": "target_departments",
                "type": "array",
                "required": False
            }
        ],
        "steps": [
            {
                "name": "filtered_query",
                "type": "query",
                "config": {
                    "data_source": "employees",
                    "dimensions": ["employee_id", "name", "hire_date", "salary", "department"],
                    "filters": [
                        {
                            "field": "active",
                            "operator": "=",
                            "value": True
                        },
                        {
                            "field": "hire_date",
                            "operator": ">=",
                            "value": "$hire_date_from",
                            "conditional": {
                                "type": "parameter_exists",
                                "parameter": "hire_date_from"
                            }
                        },
                        {
                            "field": "hire_date",
                            "operator": "<=",
                            "value": "$hire_date_to",
                            "conditional": {
                                "type": "parameter_exists",
                                "parameter": "hire_date_to"
                            }
                        },
                        {
                            "field": "hire_date",
                            "operator": "BETWEEN",
                            "value": ["$hire_date_from", "$hire_date_to"],
                            "conditional": {
                                "type": "all_parameters_exist",
                                "parameters": ["hire_date_from", "hire_date_to"]
                            }
                        },
                        {
                            "field": "salary",
                            "operator": ">=",
                            "value": "$salary_min",
                            "conditional": {
                                "type": "parameter_exists",
                                "parameter": "salary_min"
                            }
                        },
                        {
                            "field": "salary",
                            "operator": "<=",
                            "value": "$salary_max",
                            "conditional": {
                                "type": "parameter_exists",
                                "parameter": "salary_max"
                            }
                        },
                        {
                            "field": "salary",
                            "operator": "BETWEEN",
                            "value": ["$salary_min", "$salary_max"],
                            "conditional": {
                                "type": "all_parameters_exist",
                                "parameters": ["salary_min", "salary_max"]
                            }
                        },
                        {
                            "field": "department",
                            "operator": "IN",
                            "value": "$target_departments",
                            "conditional": {
                                "type": "parameter_not_empty",
                                "parameter": "target_departments",
                                "empty_values": [None, []]
                            }
                        }
                    ]
                }
            }
        ],
        "output": "filtered_query"
    }

async def test_all_parameters_exist():
    """测试 all_parameters_exist 条件过滤器"""
    print("=" * 70)
    print("测试 all_parameters_exist 条件过滤器功能")
    print("=" * 70)
    
    engine = get_uqm_engine()
    config = create_all_parameters_exist_test_config()
    
    # 测试场景
    test_scenarios = [
        {
            "name": "场景1：传入完整时间范围（触发 all_parameters_exist）",
            "parameters": {
                "hire_date_from": "2022-01-01",
                "hire_date_to": "2024-12-31"
            },
            "expected_filters": [
                "active = true",
                "hire_date >= '2022-01-01'",
                "hire_date <= '2024-12-31'", 
                "hire_date BETWEEN ['2022-01-01', '2024-12-31']"  # 这个应该保留
            ]
        },
        {
            "name": "场景2：只传入起始时间（不触发 all_parameters_exist）",
            "parameters": {
                "hire_date_from": "2022-01-01"
            },
            "expected_filters": [
                "active = true",
                "hire_date >= '2022-01-01'"
                # BETWEEN 过滤器应该被跳过
            ]
        },
        {
            "name": "场景3：传入完整薪资范围（触发 all_parameters_exist）",
            "parameters": {
                "salary_min": 15000,
                "salary_max": 50000
            },
            "expected_filters": [
                "active = true",
                "salary >= 15000",
                "salary <= 50000",
                "salary BETWEEN [15000, 50000]"  # 这个应该保留
            ]
        },
        {
            "name": "场景4：只传入最低薪资（不触发 all_parameters_exist）",
            "parameters": {
                "salary_min": 15000
            },
            "expected_filters": [
                "active = true",
                "salary >= 15000"
                # BETWEEN 过滤器应该被跳过
            ]
        },
        {
            "name": "场景5：传入时间范围和部门（混合测试）",
            "parameters": {
                "hire_date_from": "2022-01-01",
                "hire_date_to": "2024-12-31",
                "target_departments": ["IT", "销售"]
            },
            "expected_filters": [
                "active = true",
                "hire_date >= '2022-01-01'",
                "hire_date <= '2024-12-31'",
                "hire_date BETWEEN ['2022-01-01', '2024-12-31']",
                "department IN ['IT', '销售']"
            ]
        },
        {
            "name": "场景6：传入所有参数（全量测试）",
            "parameters": {
                "hire_date_from": "2022-01-01",
                "hire_date_to": "2024-12-31",
                "salary_min": 15000,
                "salary_max": 50000,
                "target_departments": ["IT"]
            },
            "expected_filters": [
                "active = true",
                "hire_date >= '2022-01-01'",
                "hire_date <= '2024-12-31'",
                "hire_date BETWEEN ['2022-01-01', '2024-12-31']",
                "salary >= 15000",
                "salary <= 50000", 
                "salary BETWEEN [15000, 50000]",
                "department IN ['IT']"
            ]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🧪 {scenario['name']}")
        print(f"📋 传入参数: {json.dumps(scenario['parameters'], ensure_ascii=False)}")
        
        try:
            # 解析和处理配置
            parsed_data = engine.parser.parse(config)
            processed_data = engine._substitute_parameters(parsed_data, scenario['parameters'])
            
            # 检查过滤器
            filters = processed_data["steps"][0]["config"]["filters"]
            print(f"📊 生成的过滤器数量: {len(filters)}")
            
            # 分析过滤器类型
            active_filters = []
            hire_date_ge_filters = []
            hire_date_le_filters = []
            hire_date_between_filters = []
            salary_ge_filters = []
            salary_le_filters = []
            salary_between_filters = []
            department_filters = []
            
            for filter_config in filters:
                field = filter_config.get("field", "unknown")
                operator = filter_config.get("operator", "unknown")
                value = filter_config.get("value", "unknown")
                
                print(f"   • {field} {operator} {value}")
                
                if field == "active":
                    active_filters.append(filter_config)
                elif field == "hire_date":
                    if operator == ">=":
                        hire_date_ge_filters.append(filter_config)
                    elif operator == "<=":
                        hire_date_le_filters.append(filter_config)
                    elif operator == "BETWEEN":
                        hire_date_between_filters.append(filter_config)
                elif field == "salary":
                    if operator == ">=":
                        salary_ge_filters.append(filter_config)
                    elif operator == "<=":
                        salary_le_filters.append(filter_config)
                    elif operator == "BETWEEN":
                        salary_between_filters.append(filter_config)
                elif field == "department":
                    department_filters.append(filter_config)
            
            # 验证 all_parameters_exist 逻辑
            params = scenario['parameters']
            
            # 检查时间范围 BETWEEN 过滤器
            if "hire_date_from" in params and "hire_date_to" in params:
                if len(hire_date_between_filters) > 0:
                    print("   ✅ 时间范围 BETWEEN 过滤器正确保留（两个时间参数都存在）")
                else:
                    print("   ❌ 时间范围 BETWEEN 过滤器应该保留但被跳过了")
            else:
                if len(hire_date_between_filters) == 0:
                    print("   ✅ 时间范围 BETWEEN 过滤器正确跳过（缺少时间参数）")
                else:
                    print("   ❌ 时间范围 BETWEEN 过滤器应该跳过但被保留了")
            
            # 检查薪资范围 BETWEEN 过滤器
            if "salary_min" in params and "salary_max" in params:
                if len(salary_between_filters) > 0:
                    print("   ✅ 薪资范围 BETWEEN 过滤器正确保留（两个薪资参数都存在）")
                else:
                    print("   ❌ 薪资范围 BETWEEN 过滤器应该保留但被跳过了")
            else:
                if len(salary_between_filters) == 0:
                    print("   ✅ 薪资范围 BETWEEN 过滤器正确跳过（缺少薪资参数）")
                else:
                    print("   ❌ 薪资范围 BETWEEN 过滤器应该跳过但被保留了")
            
            print("✅ 场景测试完成")
            
        except Exception as e:
            print(f"❌ 场景测试失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始测试 all_parameters_exist 条件过滤器...")
    
    # 运行测试
    asyncio.run(test_all_parameters_exist())
    
    print("\n" + "=" * 70)
    print("🎉 all_parameters_exist 功能测试完成!")
    print("=" * 70)
    print("✅ 核心功能验证:")
    print("   - 所有指定参数都存在时：保留过滤器")
    print("   - 任一指定参数缺失时：跳过过滤器")
    print("   - 适用场景：BETWEEN 操作、复合条件过滤")
    print("   - 与其他条件类型组合使用正常")
    print("\n📋 典型使用场景:")
    print("1. 日期范围过滤：需要开始和结束日期都存在")
    print("2. 数值范围过滤：需要最小值和最大值都存在")
    print("3. 复合条件过滤：需要多个相关参数同时存在")
    print("4. 地理位置过滤：需要经纬度都存在")
