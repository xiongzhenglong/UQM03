#!/usr/bin/env python3
"""
模拟AI服务测试
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.routes import generate_uqm_schema
from src.api.models import AIGenerateRequest
import asyncio

async def test_mock():
    """测试模拟AI服务"""
    
    # 模拟请求
    request = AIGenerateRequest(
        query="查询所有用户信息",
        options={}
    )
    
    try:
        # 直接调用函数
        result = await generate_uqm_schema(request)
        print(f"返回结果类型: {type(result)}")
        print(f"返回结果: {result}")
        
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mock()) 