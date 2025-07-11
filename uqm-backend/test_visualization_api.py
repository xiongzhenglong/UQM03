#!/usr/bin/env python3
"""
测试AI可视化生成API
"""

import requests
import json
import time

# API配置
BASE_URL = "http://localhost:8000/api/v1"

def test_generate_visualization():
    """测试生成可视化代码"""
    
    # 模拟数据
    test_data = [
        {"name": "张三", "age": 25, "salary": 8000, "department": "技术部"},
        {"name": "李四", "age": 30, "salary": 12000, "department": "销售部"},
        {"name": "王五", "age": 28, "salary": 10000, "department": "技术部"},
        {"name": "赵六", "age": 35, "salary": 15000, "department": "管理部"},
        {"name": "钱七", "age": 27, "salary": 9000, "department": "技术部"},
    ]
    
    # 测试请求
    request_data = {
        "data": test_data,
        "query": "生成一个按部门统计平均薪资的柱状图",
        "visualization_type": "auto",
        "options": {}
    }
    
    print("测试数据:")
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
    print("\n请求参数:")
    print(json.dumps(request_data, ensure_ascii=False, indent=2))
    
    try:
        # 发送请求
        response = requests.post(
            f"{BASE_URL}/generate-visualization",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("响应结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 验证响应结构
            if result.get("success") and result.get("config"):
                print("\n✅ 可视化生成成功!")
                print(f"可视化类型: {result.get('visualization_type')}")
            else:
                print("\n❌ 响应格式不正确")
        else:
            print(f"请求失败: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_table_visualization():
    """测试表格可视化"""
    
    test_data = [
        {"id": 1, "name": "产品A", "price": 100, "stock": 50},
        {"id": 2, "name": "产品B", "price": 200, "stock": 30},
        {"id": 3, "name": "产品C", "price": 150, "stock": 40},
    ]
    
    request_data = {
        "data": test_data,
        "query": "创建一个产品信息表格，包含排序和筛选功能",
        "visualization_type": "table",
        "options": {}
    }
    
    print("\n" + "="*50)
    print("测试表格可视化")
    print("="*50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-visualization",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("表格配置:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"表格生成失败: {response.text}")
            
    except Exception as e:
        print(f"表格测试失败: {e}")

def test_chart_visualization():
    """测试图表可视化"""
    
    test_data = [
        {"month": "1月", "sales": 1000, "profit": 200},
        {"month": "2月", "sales": 1200, "profit": 250},
        {"month": "3月", "sales": 800, "profit": 150},
        {"month": "4月", "sales": 1500, "profit": 300},
    ]
    
    request_data = {
        "data": test_data,
        "query": "生成一个显示月度销售额和利润的折线图",
        "visualization_type": "chart",
        "options": {}
    }
    
    print("\n" + "="*50)
    print("测试图表可视化")
    print("="*50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-visualization",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("图表配置:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"图表生成失败: {response.text}")
            
    except Exception as e:
        print(f"图表测试失败: {e}")

if __name__ == "__main__":
    print("开始测试AI可视化生成API...")
    print("="*50)
    
    # 测试基本功能
    test_generate_visualization()
    
    # 测试表格可视化
    test_table_visualization()
    
    # 测试图表可视化
    test_chart_visualization()
    
    print("\n测试完成!") 