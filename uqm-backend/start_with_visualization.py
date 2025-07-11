#!/usr/bin/env python3
"""
启动包含AI可视化功能的UQM后端服务
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import requests
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_env_vars():
    """检查环境变量配置"""
    required_vars = [
        "AI_API_BASE",
        "AI_API_KEY", 
        "AI_MODEL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("请设置以下环境变量:")
        for var in missing_vars:
            if var == "AI_API_BASE":
                print(f"  {var}=https://openrouter.ai/api/v1")
            elif var == "AI_MODEL":
                print(f"  {var}=anthropic/claude-3.5-sonnet")
            else:
                print(f"  {var}=your_value_here")
        return False
    
    print("✅ 环境变量检查通过")
    return True

def test_visualization_api():
    """测试可视化API"""
    print("\n🧪 测试可视化API...")
    
    try:
        import requests
        import json
        
        # 测试数据
        test_data = [
            {"name": "张三", "age": 25, "salary": 8000, "department": "技术部"},
            {"name": "李四", "age": 30, "salary": 12000, "department": "销售部"},
        ]
        
        response = requests.post(
            "http://localhost:8000/api/v1/generate-visualization",
            json={
                "data": test_data,
                "query": "生成一个按部门统计平均薪资的柱状图",
                "visualization_type": "auto"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 可视化API测试成功")
                print(f"   生成类型: {result.get('visualization_type')}")
                return True
            else:
                print(f"❌ 可视化API返回错误: {result.get('error')}")
                return False
        else:
            print(f"❌ 可视化API请求失败: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务，请确保服务已启动")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 启动UQM后端服务（包含AI可视化功能）")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查环境变量
    if not check_env_vars():
        sys.exit(1)
    
    # 切换到后端目录
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print(f"\n📁 工作目录: {os.getcwd()}")
    
    # 启动服务
    print("\n🌐 启动后端服务...")
    print("服务地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        # 启动uvicorn服务器
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "src.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 