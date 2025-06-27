"""
调试参数替换问题
"""

import sys
import os
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.engine import get_uqm_engine

def debug_parameter_substitution():
    """调试参数替换问题"""
    print("=" * 60)
    print("调试参数替换问题")
    print("=" * 60)
    
    engine = get_uqm_engine()
    
    # 简化的测试配置
    config = {
        "metadata": {
            "name": "DebugTest",
            "description": "调试测试",
            "version": "1.0"
        },
        "steps": [
            {
                "name": "test_query",
                "type": "query",
                "config": {
                    "data_source": "employees",
                    "dimensions": ["name", "department"],
                    "filters": [
                        {
                            "field": "department",
                            "operator": "IN",
                            "value": "$target_departments",
                            "conditional": {
                                "type": "parameter_not_empty",
                                "parameter": "target_departments",
                                "empty_values": [None, []]
                            }
                        },
                        {
                            "field": "job_title",
                            "operator": "IN",
                            "value": "$target_job_titles",
                            "conditional": {
                                "type": "parameter_not_empty",
                                "parameter": "target_job_titles",
                                "empty_values": [None, []]
                            }
                        }
                    ]
                }
            }
        ],
        "output": "test_query"
    }
    
    # 测试参数
    parameters = {
        "target_job_titles": ["软件工程师", "项目经理"]
    }
    
    try:
        # 解析配置
        parsed_data = engine.parser.parse(config)
        print("✅ 配置解析成功")
        
        # 查看原始数据
        print("\n📋 原始数据:")
        print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
        
        # 先处理条件过滤器
        print("\n🔍 处理条件过滤器...")
        after_conditional = engine._process_conditional_filters(parsed_data, parameters)
        
        print("\n📋 条件过滤器处理后:")
        print(json.dumps(after_conditional, indent=2, ensure_ascii=False))
        
        # 参数替换
        print("\n🔍 参数替换...")
        import copy
        processed_data = copy.deepcopy(after_conditional)
        
        data_str = json.dumps(processed_data)
        print(f"\n📋 参数替换前JSON长度: {len(data_str)}")
        print(f"📋 参数替换前JSON片段: {data_str[:200]}...")
        
        # 逐个替换参数
        for param_name, param_value in parameters.items():
            placeholder = f"${param_name}"
            print(f"\n🔄 替换参数: {param_name} = {param_value}")
            
            if isinstance(param_value, (list, dict)):
                replacement = json.dumps(param_value)
            else:
                replacement = json.dumps(param_value)
            
            print(f"   占位符: {placeholder}")
            print(f"   替换值: {replacement}")
            
            # 先处理带引号的占位符
            before_quote = data_str.count(f'"{placeholder}"')
            data_str = data_str.replace(f'"{placeholder}"', replacement)
            after_quote = data_str.count(f'"{placeholder}"')
            print(f"   带引号替换: {before_quote} -> {after_quote}")
            
            # 再处理不带引号的占位符
            before_no_quote = data_str.count(placeholder)
            data_str = data_str.replace(placeholder, replacement)
            after_no_quote = data_str.count(placeholder)
            print(f"   不带引号替换: {before_no_quote} -> {after_no_quote}")
        
        print(f"\n📋 参数替换后JSON长度: {len(data_str)}")
        print(f"📋 参数替换后JSON片段: {data_str[:200]}...")
        
        # 尝试解析JSON
        try:
            final_data = json.loads(data_str)
            print("✅ JSON解析成功")
            print("\n📋 最终数据:")
            print(json.dumps(final_data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"错误位置: {e.pos}")
            
            # 显示错误位置附近的内容
            start = max(0, e.pos - 50)
            end = min(len(data_str), e.pos + 50)
            print(f"错误附近内容: {data_str[start:end]}")
            
            # 保存出错的JSON到文件
            with open("debug_failed.json", "w", encoding="utf-8") as f:
                f.write(data_str)
            print("已保存出错的JSON到 debug_failed.json")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_parameter_substitution()
