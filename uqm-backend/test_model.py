#!/usr/bin/env python3
"""
模型测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.models import AIGenerateResponse

def test_model():
    """测试AIGenerateResponse模型"""
    
    print("测试AIGenerateResponse模型")
    print("=" * 30)
    
    # 测试数据
    test_data = {
        "uqm": {
            "metadata": {
                "name": "测试查询",
                "description": "这是一个测试查询"
            },
            "steps": [
                {
                    "name": "step1",
                    "type": "query",
                    "config": {
                        "data_source": "users",
                        "dimensions": ["id", "name"]
                    }
                }
            ],
            "output": "step1"
        },
        "parameters": {},
        "options": {
            "cache_enabled": True
        }
    }
    
    try:
        # 创建模型实例
        response = AIGenerateResponse(**test_data)
        print("✅ 模型创建成功")
        
        # 转换为字典
        response_dict = response.dict()
        print(f"✅ 转换为字典成功")
        print(f"字典内容: {response_dict}")
        
        # 转换为JSON
        import json
        response_json = response.json()
        print(f"✅ 转换为JSON成功")
        print(f"JSON内容: {response_json}")
        
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model() 