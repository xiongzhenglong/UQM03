#!/usr/bin/env python3
"""
UQM AI API 使用示例
展示如何使用新的直接返回schema的API
"""

import requests
import json

def generate_schema(query):
    """生成UQM Schema"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/generate",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()  # 直接返回schema
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def generate_and_execute(query):
    """生成并执行查询"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/generate-and-execute",
            json={"query": query},
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def main():
    """主函数"""
    print("UQM AI API 使用示例")
    print("=" * 50)
    
    # 示例查询
    queries = [
        "查询所有用户信息",
        "统计每个用户的订单总金额",
        "查询最近7天的订单数量"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n示例 {i}: {query}")
        print("-" * 30)
        
        # 生成Schema
        print("1. 生成Schema...")
        schema = generate_schema(query)
        
        if schema:
            print("✅ Schema生成成功")
            print(f"   名称: {schema['uqm']['metadata']['name']}")
            print(f"   描述: {schema['uqm']['metadata']['description']}")
            print(f"   步骤数: {len(schema['uqm']['steps'])}")
            
            # 显示Schema结构
            print("\n   生成的Schema:")
            print(json.dumps(schema, indent=4, ensure_ascii=False))
            
            # 生成并执行
            print("\n2. 生成并执行...")
            result = generate_and_execute(query)
            
            if result and result.get("success"):
                print("✅ 执行成功")
                data = result.get("data", [])
                print(f"   数据行数: {len(data)}")
                if data:
                    print("   前3行数据:")
                    for j, row in enumerate(data[:3]):
                        print(f"     {j+1}: {row}")
            else:
                print("❌ 执行失败")
        else:
            print("❌ Schema生成失败")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 