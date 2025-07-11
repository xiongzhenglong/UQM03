#!/usr/bin/env python3
"""
AI API 测试脚本
用于测试自然语言到UQM Schema的生成功能
"""

import os
import sys
import json
import requests
import time
from typing import Dict, Any

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ai_generate_api():
    """测试AI生成API"""
    
    # 配置
    API_BASE = "http://localhost:8000/api/v1"
    
    # 测试查询列表
    test_queries = [
        "查询所有用户信息",
        "统计每个用户的订单总金额",
        "查询最近7天的订单数量",
        "获取产品库存大于10的产品",
        "计算每个产品类别的平均价格"
    ]
    
    print("=" * 60)
    print("UQM AI API 测试")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n测试 {i}: {query}")
        print("-" * 40)
        
        try:
            # 测试生成Schema
            print("1. 测试生成Schema...")
            start_time = time.time()
            
            response = requests.post(
                f"{API_BASE}/generate",
                json={"query": query},
                timeout=30
            )
            
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # 直接返回schema，检查是否包含uqm字段
                if "uqm" in result:
                    print(f"✅ 生成成功 (耗时: {generation_time:.2f}s)")
                    
                    # 显示生成的Schema结构
                    schema = result
                    print(f"   Schema名称: {schema['uqm']['metadata']['name']}")
                    print(f"   步骤数: {len(schema['uqm']['steps'])}")
                    for j, step in enumerate(schema['uqm']['steps']):
                        print(f"   步骤{j+1}: {step['name']} ({step['type']})")
                    
                    # 测试生成并执行
                    print("\n2. 测试生成并执行...")
                    try:
                        exec_response = requests.post(
                            f"{API_BASE}/generate-and-execute",
                            json={"query": query},
                            timeout=60
                        )
                        
                        if exec_response.status_code == 200:
                            exec_result = exec_response.json()
                            if exec_result.get("success"):
                                print(f"✅ 执行成功")
                                print(f"   数据行数: {len(exec_result.get('data', []))}")
                                print(f"   执行时间: {exec_result.get('execution_info', {}).get('total_time', 0):.2f}s")
                            else:
                                print(f"❌ 执行失败: {exec_result.get('error', '未知错误')}")
                        else:
                            print(f"❌ 执行请求失败: {exec_response.status_code}")
                            
                    except Exception as e:
                        print(f"❌ 执行异常: {e}")
                    
                else:
                    print(f"❌ 生成失败: 响应格式不正确")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"   响应: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败: 请确保UQM后端服务正在运行")
            break
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 测试异常: {e}")
        
        print("\n" + "=" * 60)


def test_ai_service_directly():
    """直接测试AI服务"""
    
    print("\n" + "=" * 60)
    print("直接测试AI服务")
    print("=" * 60)
    
    try:
        from src.services.ai_service import get_ai_service
        
        # 获取AI服务实例
        ai_service = get_ai_service()
        print(f"✅ AI服务初始化成功")
        print(f"   模型: {ai_service.model}")
        print(f"   API Base: {ai_service.api_base}")
        
        # 测试生成
        test_query = "查询所有用户的订单总金额"
        print(f"\n测试查询: {test_query}")
        
        import asyncio
        schema = asyncio.run(ai_service.generate_uqm_schema(test_query))
        
        if schema:
            print("✅ 直接生成成功")
            print(f"   Schema: {json.dumps(schema, indent=2, ensure_ascii=False)}")
        else:
            print("❌ 直接生成失败")
            
    except Exception as e:
        print(f"❌ AI服务测试失败: {e}")


def check_environment():
    """检查环境配置"""
    
    print("=" * 60)
    print("环境配置检查")
    print("=" * 60)
    
    # 检查环境变量
    env_vars = [
        "AI_API_KEY",
        "AI_API_BASE", 
        "AI_MODEL",
        "AI_MAX_TOKENS",
        "AI_TEMPERATURE"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if var == "AI_API_KEY":
                # 隐藏API密钥
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: 未设置")
    
    # 检查文件
    files_to_check = [
        "UQM_JSON_SCHEMA_权威技术参考手册.md",
        "数据库表结构简化描述.md"
    ]
    
    print("\n文件检查:")
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file}: 存在")
        else:
            print(f"❌ {file}: 不存在")


def main():
    """主函数"""
    
    print("UQM AI API 测试工具")
    print("请确保UQM后端服务正在运行 (http://localhost:8000)")
    
    # 检查环境
    check_environment()
    
    # 测试AI服务
    test_ai_service_directly()
    
    # 测试API接口
    test_ai_generate_api()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main() 