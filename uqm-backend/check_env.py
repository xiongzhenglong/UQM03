#!/usr/bin/env python3
"""
环境检查脚本
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_environment():
    """检查环境配置"""
    
    print("=" * 50)
    print("环境配置检查")
    print("=" * 50)
    
    # 检查AI相关环境变量
    ai_vars = [
        "AI_API_KEY",
        "AI_API_BASE", 
        "AI_MODEL",
        "AI_MAX_TOKENS",
        "AI_TEMPERATURE"
    ]
    
    for var in ai_vars:
        value = os.getenv(var)
        if value:
            if var == "AI_API_KEY":
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: 未设置")
    
    # 检查配置文件
    print("\n配置文件检查:")
    config_files = [
        ".env",
        "UQM_JSON_SCHEMA_权威技术参考手册.md",
        "数据库表结构简化描述.md"
    ]
    
    for file in config_files:
        if os.path.exists(file):
            print(f"✅ {file}: 存在")
        else:
            print(f"❌ {file}: 不存在")
    
    # 尝试导入AI服务
    print("\nAI服务检查:")
    try:
        from src.services.ai_service import get_ai_service
        ai_service = get_ai_service()
        print(f"✅ AI服务初始化成功")
        print(f"   模型: {ai_service.model}")
        print(f"   API Base: {ai_service.api_base}")
    except Exception as e:
        print(f"❌ AI服务初始化失败: {e}")
    
    # 尝试导入API模型
    print("\nAPI模型检查:")
    try:
        from src.api.models import AIGenerateResponse
        print(f"✅ AIGenerateResponse模型导入成功")
        
        # 测试模型实例化
        test_data = {
            "uqm": {
                "metadata": {"name": "test"},
                "steps": [{"name": "step1", "type": "query", "config": {}}],
                "output": "step1"
            },
            "parameters": {},
            "options": {}
        }
        
        response = AIGenerateResponse(**test_data)
        print(f"✅ AIGenerateResponse实例化成功")
        print(f"   响应数据: {response.dict()}")
        
    except Exception as e:
        print(f"❌ API模型检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_environment() 