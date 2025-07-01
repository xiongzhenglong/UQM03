#!/usr/bin/env python3
"""
测试API层面的断言失败响应
"""

import json
import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from src.main import app

def test_api_assertion_failure():
    """测试API层面的断言失败响应"""
    
    print("=== 测试API层面的断言失败响应 ===")
    
    # 创建测试客户端
    client = TestClient(app)
    
    # 构建会导致断言失败的请求
    request_data = {
        "uqm": {
            "metadata": {
                "name": "API_Assert_Test",
                "description": "测试API断言失败",
                "version": "1.0"
            },
            "steps": [
                {
                    "name": "get_order_count",
                    "type": "query",
                    "config": {
                        "data_source": "orders",
                        "metrics": [
                            {
                                "name": "order_id",
                                "aggregation": "COUNT",
                                "alias": "total_orders"
                            }
                        ]
                    }
                },
                {
                    "name": "assert_order_count",
                    "type": "assert",
                    "config": {
                        "source": "get_order_count",
                        "assertions": [
                            {
                                "type": "range",
                                "field": "total_orders",
                                "min": 100,
                                "max": 10000,
                                "on_failure": "error"  # 明确设置为 error
                            }
                        ]
                    }
                }
            ],
            "output": "assert_order_count"
        },
        "parameters": {},
        "options": {}
    }
    
    try:
        # 发送POST请求，添加正确的headers
        headers = {
            "Content-Type": "application/json",
            "Host": "localhost"
        }
        response = client.post("/execute", json=request_data, headers=headers)
        
        print(f"🔍 API响应分析:")
        print(f"  HTTP状态码: {response.status_code}")
        print(f"  响应头: {dict(response.headers)}")
        print(f"  响应体: {response.text}")
        
        if response.status_code == 200:
            print("❌ 问题确认: HTTP 200 但应该是错误状态")
            response_json = response.json()
            print(f"  success字段: {response_json.get('success')}")
            print(f"  error字段: {response_json.get('error')}")
            
        elif response.status_code >= 400:
            print("✅ 正确: HTTP错误状态码")
            if response.status_code == 500:
                print("✅ 正确: ExecutionError应该返回500")
            try:
                error_response = response.json()
                print(f"  错误响应: {json.dumps(error_response, indent=2, ensure_ascii=False)}")
            except:
                print(f"  无法解析错误响应JSON: {response.text}")
                
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_assertion_failure()
