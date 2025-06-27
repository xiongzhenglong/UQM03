"""
分析和实现条件过滤器功能
目标：当参数未提供时，自动忽略相关的过滤器
"""

import sys
import os
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_conditional_filtering_need():
    """分析条件过滤的需求"""
    print("=" * 60)
    print("条件过滤器需求分析")
    print("=" * 60)
    
    print("\n🎯 场景示例:")
    print("1. 模板定义了4个参数：target_departments, target_job_titles, min_salary, max_salary")
    print("2. 用户只传入了2个参数：target_departments, min_salary")
    print("3. 期望结果：自动忽略 target_job_titles 和 max_salary 相关的过滤器")
    
    print("\n📋 当前问题:")
    print("- 未传入的参数会使用默认值（如 null, [], 0）")
    print("- 空值参数仍然会生成过滤器，可能导致错误的查询结果")
    print("- 需要手动处理每个参数的存在性检查")
    
    print("\n💡 解决方案思路:")
    print("1. 在过滤器中添加条件字段（conditional）")
    print("2. 参数替换时检查参数是否存在且有效")
    print("3. 无效参数的过滤器自动跳过")
    print("4. 支持多种条件表达式")
    
    return True

def design_conditional_filter_syntax():
    """设计条件过滤器语法"""
    print("\n" + "=" * 60)
    print("条件过滤器语法设计")
    print("=" * 60)
    
    print("\n📝 语法设计:")
    
    # 基础条件语法
    basic_syntax = {
        "field": "departments.name",
        "operator": "IN",
        "value": "$target_departments",
        "conditional": {
            "type": "parameter_exists",
            "parameter": "target_departments"
        }
    }
    
    print("1. 基础条件 - 参数存在检查:")
    print(json.dumps(basic_syntax, indent=2, ensure_ascii=False))
    
    # 高级条件语法
    advanced_syntax = {
        "field": "employees.salary",
        "operator": ">=",
        "value": "$min_salary",
        "conditional": {
            "type": "parameter_not_empty",
            "parameter": "min_salary",
            "empty_values": [None, 0, ""]
        }
    }
    
    print("\n2. 高级条件 - 参数非空检查:")
    print(json.dumps(advanced_syntax, indent=2, ensure_ascii=False))
    
    # 复合条件语法
    complex_syntax = {
        "field": "employees.hire_date",
        "operator": "BETWEEN",
        "value": ["$start_date", "$end_date"],
        "conditional": {
            "type": "all_parameters_exist",
            "parameters": ["start_date", "end_date"]
        }
    }
    
    print("\n3. 复合条件 - 多参数检查:")
    print(json.dumps(complex_syntax, indent=2, ensure_ascii=False))
    
    # 表达式条件语法
    expression_syntax = {
        "field": "products.category",
        "operator": "=",
        "value": "$category",
        "conditional": {
            "type": "expression",
            "expression": "$category != null && $category != '' && $category != 'all'"
        }
    }
    
    print("\n4. 表达式条件 - 自定义逻辑:")
    print(json.dumps(expression_syntax, indent=2, ensure_ascii=False))
    
    return True

def create_enhanced_parameterized_example():
    """创建增强的参数化查询示例"""
    print("\n" + "=" * 60)
    print("增强参数化查询示例")
    print("=" * 60)
    
    enhanced_config = {
        "uqm": {
            "metadata": {
                "name": "FlexibleParameterizedSalaryAnalysis",
                "description": "灵活的参数化薪资分析，支持条件过滤器，未提供的参数自动忽略相关过滤器。",
                "version": "3.0",
                "author": "HR Analytics Team",
                "tags": ["hr_analysis", "salary_analysis", "pivot_table", "conditional_filtering"]
            },
            "parameters": [
                {
                    "name": "target_departments",
                    "type": "array",
                    "description": "要分析的目标部门列表，为空或未提供时分析所有部门",
                    "required": False,
                    "default": None
                },
                {
                    "name": "target_job_titles",
                    "type": "array", 
                    "description": "要分析的目标职位列表，为空或未提供时分析所有职位",
                    "required": False,
                    "default": None
                },
                {
                    "name": "min_salary",
                    "type": "number",
                    "description": "最低薪资阈值，未提供时不限制最低薪资",
                    "required": False,
                    "default": None
                },
                {
                    "name": "max_salary",
                    "type": "number",
                    "description": "最高薪资阈值，未提供时不限制最高薪资",
                    "required": False,
                    "default": None
                },
                {
                    "name": "hire_date_from",
                    "type": "string",
                    "description": "入职日期起始，格式 YYYY-MM-DD，未提供时不限制",
                    "required": False,
                    "default": None
                },
                {
                    "name": "hire_date_to",
                    "type": "string",
                    "description": "入职日期结束，格式 YYYY-MM-DD，未提供时不限制",
                    "required": False,
                    "default": None
                }
            ],
            "steps": [
                {
                    "name": "get_filtered_employee_data",
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
                                "field": "employees.job_title",
                                "operator": "IN",
                                "value": "$target_job_titles",
                                "conditional": {
                                    "type": "parameter_not_empty",
                                    "parameter": "target_job_titles",
                                    "empty_values": [None, []]
                                }
                            },
                            {
                                "field": "employees.salary",
                                "operator": ">=",
                                "value": "$min_salary",
                                "conditional": {
                                    "type": "parameter_not_empty",
                                    "parameter": "min_salary",
                                    "empty_values": [None, 0]
                                }
                            },
                            {
                                "field": "employees.salary",
                                "operator": "<=",
                                "value": "$max_salary",
                                "conditional": {
                                    "type": "parameter_not_empty",
                                    "parameter": "max_salary",
                                    "empty_values": [None, 0]
                                }
                            },
                            {
                                "field": "employees.hire_date",
                                "operator": ">=",
                                "value": "$hire_date_from",
                                "conditional": {
                                    "type": "parameter_not_empty",
                                    "parameter": "hire_date_from",
                                    "empty_values": [None, ""]
                                }
                            },
                            {
                                "field": "employees.hire_date",
                                "operator": "<=",
                                "value": "$hire_date_to",
                                "conditional": {
                                    "type": "parameter_not_empty",
                                    "parameter": "hire_date_to",
                                    "empty_values": [None, ""]
                                }
                            }
                        ]
                    }
                },
                {
                    "name": "pivot_salary_analysis",
                    "type": "pivot",
                    "config": {
                        "source": "get_filtered_employee_data",
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
    }
    
    print("增强的参数化配置：")
    print(json.dumps(enhanced_config, indent=2, ensure_ascii=False))
    
    # 测试场景
    test_scenarios = [
        {
            "name": "只传入部门参数",
            "parameters": {
                "target_departments": ["信息技术部", "销售部"]
            },
            "expected": "只应用部门过滤器，其他过滤器被忽略"
        },
        {
            "name": "传入部门和薪资范围",
            "parameters": {
                "target_departments": ["信息技术部"],
                "min_salary": 15000,
                "max_salary": 50000
            },
            "expected": "应用部门和薪资范围过滤器"
        },
        {
            "name": "只传入时间范围",
            "parameters": {
                "hire_date_from": "2022-01-01",
                "hire_date_to": "2024-12-31"
            },
            "expected": "只应用时间范围过滤器"
        },
        {
            "name": "传入所有参数",
            "parameters": {
                "target_departments": ["信息技术部"],
                "target_job_titles": ["软件工程师", "IT总监"],
                "min_salary": 20000,
                "max_salary": 40000,
                "hire_date_from": "2022-01-01",
                "hire_date_to": "2024-12-31"
            },
            "expected": "应用所有过滤器"
        }
    ]
    
    print("\n📋 测试场景:")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print(f"   参数: {json.dumps(scenario['parameters'], ensure_ascii=False)}")
        print(f"   期望: {scenario['expected']}")
    
    return enhanced_config

if __name__ == "__main__":
    print("🚀 开始分析条件过滤器功能需求...")
    
    # 分析需求
    analyze_conditional_filtering_need()
    
    # 设计语法
    design_conditional_filter_syntax()
    
    # 创建示例
    enhanced_config = create_enhanced_parameterized_example()
    
    print("\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    print("✅ 需求分析完成")
    print("✅ 语法设计完成")
    print("✅ 示例配置完成")
    print("\n📋 下一步:")
    print("1. 修改参数替换逻辑以支持条件过滤器")
    print("2. 在 query_step.py 中实现条件判断")
    print("3. 添加测试验证功能")
    print("4. 更新文档示例")
