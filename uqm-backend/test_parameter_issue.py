"""
测试参数化查询中的参数替换问题
"""

import sys
import os
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_parameter_replacement():
    """测试参数替换问题"""
    print("开始测试参数替换...")
    
    # 模拟用户的查询配置
    query_config = {
        "uqm": {
            "metadata": {
                "name": "ParameterizedSalaryPivotAnalysis",
                "description": "参数化的薪资透视分析",
                "version": "1.0",
                "author": "HR Analytics Team",
                "tags": ["hr_analysis", "salary_analysis", "pivot_table", "parameterized"]
            },
            "parameters": [
                {
                    "name": "target_departments",
                    "type": "array",
                    "description": "要分析的目标部门列表，为空则分析所有部门",
                    "required": False,
                    "default": []
                },
                {
                    "name": "target_job_titles", 
                    "type": "array",
                    "description": "要分析的目标职位列表，为空则分析所有职位",
                    "required": False,
                    "default": []
                },
                {
                    "name": "min_salary_threshold",
                    "type": "number",
                    "description": "最低薪资阈值，用于过滤薪资数据",
                    "required": False,
                    "default": 0
                },
                {
                    "name": "analysis_date_from",
                    "type": "string", 
                    "description": "分析起始日期（入职日期），格式：YYYY-MM-DD",
                    "required": False,
                    "default": None
                },
                {
                    "name": "analysis_date_to",
                    "type": "string",
                    "description": "分析结束日期（入职日期），格式：YYYY-MM-DD", 
                    "required": False,
                    "default": None
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
                                "field": "employees.salary",
                                "operator": ">=", 
                                "value": "$min_salary_threshold"
                            },
                            {
                                "field": "departments.name",
                                "operator": "IN",
                                "value": "$target_departments",
                                "condition": "IF(ARRAY_LENGTH($target_departments) > 0)"
                            },
                            {
                                "field": "employees.job_title",
                                "operator": "IN",
                                "value": "$target_job_titles", 
                                "condition": "IF(ARRAY_LENGTH($target_job_titles) > 0)"
                            },
                            {
                                "field": "employees.hire_date",
                                "operator": ">=",
                                "value": "$analysis_date_from",
                                "condition": "IF($analysis_date_from IS NOT NULL)"
                            },
                            {
                                "field": "employees.hire_date", 
                                "operator": "<=",
                                "value": "$analysis_date_to",
                                "condition": "IF($analysis_date_to IS NOT NULL)"
                            }
                        ]
                    }
                },
                {
                    "name": "pivot_filtered_salary_analysis",
                    "type": "pivot",
                    "config": {
                        "source": "get_filtered_employee_salary_data",
                        "index": "department_name",
                        "columns": "job_title",
                        "values": "salary",
                        "agg_func": "mean",
                        "fill_value": None,
                        "missing_strategy": "keep",
                        "sort_by": "department_name",
                        "sort_ascending": True
                    }
                }
            ],
            "output": "pivot_filtered_salary_analysis"
        },
        "parameters": {
            "target_departments": ["信息技术部", "销售部", "人力资源部"],
            "target_job_titles": [],
            "min_salary_threshold": 15000,
            "analysis_date_from": "2022-01-01",
            "analysis_date_to": None
        },
        "options": {
            "cache_enabled": True,
            "timeout": 300
        }
    }
    
    print("1. 测试原始配置的JSON序列化...")
    try:
        json_str = json.dumps(query_config, indent=2, ensure_ascii=False)
        print("✓ 原始配置JSON序列化成功")
        
        # 模拟参数替换过程
        print("\n2. 模拟参数替换过程...")
        parameters = query_config["parameters"]
        
        # 检查每个参数值
        for key, value in parameters.items():
            print(f"   参数 {key}: {value} (类型: {type(value)})")
            if value is None:
                print(f"     -> null 值可能导致问题")
            elif isinstance(value, list) and len(value) == 0:
                print(f"     -> 空数组可能导致问题")
        
        print("\n3. 测试可能的问题场景...")
        
        # 测试空数组的情况
        empty_array_json = json.dumps([], ensure_ascii=False)
        print(f"   空数组JSON: {empty_array_json}")
        
        # 测试null值的情况
        null_json = json.dumps(None, ensure_ascii=False)
        print(f"   null值JSON: {null_json}")
        
        # 测试中文字符串
        chinese_array_json = json.dumps(["信息技术部", "销售部", "人力资源部"], ensure_ascii=False)
        print(f"   中文数组JSON: {chinese_array_json}")
        
        return True
        
    except Exception as e:
        print(f"✗ JSON处理失败: {e}")
        import traceback
        print(f"错误详情:\n{traceback.format_exc()}")
        return False

def test_potential_fixes():
    """测试可能的修复方案"""
    print("\n" + "="*50)
    print("测试潜在修复方案")
    print("="*50)
    
    # 方案1: 检查条件过滤器的语法
    print("\n1. 检查条件过滤器语法...")
    
    problematic_filters = [
        {
            "field": "departments.name",
            "operator": "IN",
            "value": "$target_departments",
            "condition": "IF(ARRAY_LENGTH($target_departments) > 0)"
        },
        {
            "field": "employees.job_title",
            "operator": "IN",
            "value": "$target_job_titles", 
            "condition": "IF(ARRAY_LENGTH($target_job_titles) > 0)"
        },
        {
            "field": "employees.hire_date",
            "operator": ">=",
            "value": "$analysis_date_from",
            "condition": "IF($analysis_date_from IS NOT NULL)"
        },
        {
            "field": "employees.hire_date", 
            "operator": "<=",
            "value": "$analysis_date_to",
            "condition": "IF($analysis_date_to IS NOT NULL)"
        }
    ]
    
    for i, filter_config in enumerate(problematic_filters):
        try:
            json_str = json.dumps(filter_config, indent=2, ensure_ascii=False)
            print(f"   过滤器 {i+1}: ✓ JSON格式正确")
        except Exception as e:
            print(f"   过滤器 {i+1}: ✗ JSON格式错误 - {e}")
    
    # 方案2: 简化的过滤器配置
    print("\n2. 测试简化的过滤器配置...")
    
    simplified_filters = [
        {
            "field": "employees.is_active",
            "operator": "=",
            "value": True
        },
        {
            "field": "employees.salary",
            "operator": ">=", 
            "value": "$min_salary_threshold"
        }
        # 移除复杂的条件过滤器
    ]
    
    try:
        json_str = json.dumps(simplified_filters, indent=2, ensure_ascii=False)
        print("   ✓ 简化过滤器JSON格式正确")
        
        # 建议的修复方案
        print("\n📋 建议的修复方案:")
        print("   1. 移除复杂的条件过滤器（condition字段）")
        print("   2. 在query步骤中使用标准的参数替换")
        print("   3. 可能需要修改参数替换逻辑以支持条件过滤")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 简化过滤器也有问题: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("参数替换问题诊断测试")
    print("=" * 60)
    
    # 测试参数替换
    param_success = test_parameter_replacement()
    
    # 测试修复方案
    fix_success = test_potential_fixes()
    
    print("\n" + "=" * 60)
    print("诊断结果总结:")
    print(f"参数处理测试: {'通过' if param_success else '失败'}")
    print(f"修复方案测试: {'通过' if fix_success else '失败'}")
    print("=" * 60)
