#!/usr/bin/env python3
"""
UQM后端启动脚本（支持AI功能）
帮助用户快速配置AI环境并启动服务
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"   当前版本: {sys.version}")
        return False
    print(f"✅ Python版本: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """检查依赖"""
    try:
        import fastapi
        import uvicorn
        import requests
        print("✅ 核心依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def setup_environment():
    """设置环境变量"""
    print("\n" + "=" * 50)
    print("AI环境配置")
    print("=" * 50)
    
    # 检查是否已有.env文件
    env_file = Path(".env")
    if env_file.exists():
        print("✅ 发现.env文件")
        load_existing_env = input("是否加载现有配置? (y/n): ").lower().strip()
        if load_existing_env == 'y':
            return True
    
    # 配置AI API密钥
    print("\n请配置OpenRouter API密钥:")
    print("1. 访问 https://openrouter.ai/")
    print("2. 注册账号并获取API密钥")
    print("3. 将API密钥粘贴到下方")
    
    api_key = getpass.getpass("OpenRouter API密钥: ").strip()
    if not api_key:
        print("❌ API密钥不能为空")
        return False
    
    # 配置其他参数
    api_base = input("AI API基础URL (默认: https://openrouter.ai/api/v1): ").strip()
    if not api_base:
        api_base = "https://openrouter.ai/api/v1"
    
    model = input("AI模型 (默认: anthropic/claude-3.5-sonnet): ").strip()
    if not model:
        model = "anthropic/claude-3.5-sonnet"
    
    max_tokens = input("最大Token数 (默认: 4000): ").strip()
    if not max_tokens:
        max_tokens = "4000"
    
    temperature = input("温度参数 (默认: 0.1): ").strip()
    if not temperature:
        temperature = "0.1"
    
    # 配置数据库
    print("\n数据库配置:")
    db_type = input("数据库类型 (postgresql/mysql/sqlite, 默认: sqlite): ").strip()
    if not db_type:
        db_type = "sqlite"
    
    if db_type == "sqlite":
        db_url = "sqlite:///./uqm.db"
    else:
        db_url = input(f"{db_type}连接URL: ").strip()
        if not db_url:
            print(f"❌ {db_type}连接URL不能为空")
            return False
    
    # 写入.env文件
    env_content = f"""# UQM后端配置
DEBUG=true
HOST=0.0.0.0
PORT=8000
SECRET_KEY=change-me-in-production

# 数据库配置
DEFAULT_DB_TYPE={db_type}
"""
    
    if db_type == "postgresql":
        env_content += f"DATABASE_URL={db_url}\n"
    elif db_type == "mysql":
        env_content += f"MYSQL_URL={db_url}\n"
    else:
        env_content += f"SQLITE_URL={db_url}\n"
    
    env_content += f"""
# Redis配置
REDIS_URL=redis://localhost:6379/0

# 缓存配置
CACHE_TYPE=memory
CACHE_DEFAULT_TIMEOUT=3600
CACHE_MAX_SIZE=1000

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json

# 查询配置
MAX_QUERY_TIMEOUT=300
MAX_CONCURRENT_QUERIES=10
QUERY_RESULT_LIMIT=10000

# 安全配置
ALLOWED_HOSTS=["localhost", "127.0.0.1"]
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
CORS_CREDENTIALS=true
CORS_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_HEADERS=["*"]

# 监控配置
ENABLE_METRICS=true
METRICS_PATH=/metrics

# AI配置
AI_API_BASE={api_base}
AI_API_KEY={api_key}
AI_MODEL={model}
AI_MAX_TOKENS={max_tokens}
AI_TEMPERATURE={temperature}
"""
    
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ 环境配置文件已创建: .env")
        return True
    except Exception as e:
        print(f"❌ 创建环境配置文件失败: {e}")
        return False

def check_guide_files():
    """检查指南文件"""
    print("\n" + "=" * 50)
    print("检查指南文件")
    print("=" * 50)
    
    files_to_check = [
        "UQM_JSON_SCHEMA_权威技术参考手册.md",
        "数据库表结构简化描述.md"
    ]
    
    missing_files = []
    for file in files_to_check:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (缺失)")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  缺少以下文件，AI功能可能受限:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n建议:")
        print("1. 从项目根目录复制这些文件到当前目录")
        print("2. 或者AI服务将使用默认的指南内容")
        
        continue_anyway = input("\n是否继续启动? (y/n): ").lower().strip()
        return continue_anyway == 'y'
    
    return True

def start_server():
    """启动服务器"""
    print("\n" + "=" * 50)
    print("启动UQM后端服务")
    print("=" * 50)
    
    try:
        # 启动命令
        cmd = [
            sys.executable, "-m", "uvicorn",
            "src.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        print("启动命令:", " ".join(cmd))
        print("\n服务将在以下地址启动:")
        print("  - 本地访问: http://localhost:8000")
        print("  - API文档: http://localhost:8000/docs")
        print("  - 健康检查: http://localhost:8000/api/v1/health")
        print("\n按 Ctrl+C 停止服务")
        print("-" * 50)
        
        # 启动服务
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"❌ 启动服务失败: {e}")

def main():
    """主函数"""
    print("UQM后端启动脚本 (支持AI功能)")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 设置环境
    if not setup_environment():
        return
    
    # 检查指南文件
    if not check_guide_files():
        return
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 