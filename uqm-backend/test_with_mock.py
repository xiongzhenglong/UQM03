#!/usr/bin/env python3
"""
使用模拟模式的测试脚本
"""

import os
import requests
import json

def test_with_mock():
    """使用模拟模式测试API"""
    
    # 设置模拟模式
    os.environ["AI_MOCK_MODE"] = "true"
    
    print("使用模拟模式测试API")
    print("=" * 30)
    
    # 测试请求
    test_data = {
        "query": "查询所有用户信息"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/generate",
            json=test_data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功")
            print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 检查响应结构
            if "uqm" in result:
                print("✅ 响应包含uqm字段")
                if "metadata" in result["uqm"]:
                    print("✅ uqm包含metadata字段")
                if "steps" in result["uqm"]:
                    print("✅ uqm包含steps字段")
            else:
                print("❌ 响应缺少uqm字段")
                
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_with_mock() 