#!/usr/bin/env python3
"""
Setup and configuration script for UQM Schema Generator
"""

import os
import json
from pathlib import Path

def setup_environment():
    """Setup environment and configuration"""
    
    print("🚀 UQM Schema Generator Setup")
    print("=" * 50)
    
    # Check if OpenRouter API key is set
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        print("\nTo set up your API key, run:")
        print("PowerShell: $env:OPENROUTER_API_KEY='your_api_key_here'")
        print("Bash: export OPENROUTER_API_KEY='your_api_key_here'")
        print("\nGet your API key from: https://openrouter.ai/")
    else:
        print("✅ OPENROUTER_API_KEY found")
    
    # Create jsonResult directory
    result_dir = Path("jsonResult")
    if not result_dir.exists():
        result_dir.mkdir()
        print("✅ Created jsonResult directory")
    else:
        print("✅ jsonResult directory exists")
    
    # Check required files
    required_files = [
        "UQM_AI_Assistant_Guide.md",
        "数据库表结构简化描述.md", 
        "查询用例.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"✅ Found {file}")
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("\n🎉 Setup complete!")
    
    # Show usage examples
    print("\n📖 Usage Examples:")
    print("-" * 30)
    print("# Process first 5 queries:")
    print("python uqm_schema_generator.py range 1 5")
    print("\n# Process a single query (e.g., query #10):")
    print("python uqm_schema_generator.py single 10")
    print("\n# Process all queries (default: first 10):")
    print("python uqm_schema_generator.py")
    
    return True

def test_api_connection():
    """Test API connections"""
    print("\n🔧 Testing API Connections...")
    print("-" * 30)
    
    import requests
    
    # Test UQM API
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ UQM API (localhost:8000) is accessible")
        else:
            print(f"⚠️  UQM API returned status {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ UQM API (localhost:8000) is not accessible")
        print("   Make sure your UQM server is running")
    
    # Test OpenRouter API
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        try:
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            if response.status_code == 200:
                print("✅ OpenRouter API is accessible")
            else:
                print(f"❌ OpenRouter API error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ OpenRouter API connection failed: {e}")
    else:
        print("⚠️  Cannot test OpenRouter API - no API key set")

def show_query_preview():
    """Show preview of queries that will be processed"""
    try:
        from uqm_schema_generator import UQMSchemaGenerator
        
        # Create a temporary generator just to extract queries
        generator = UQMSchemaGenerator("dummy_key")
        queries = generator.extract_queries_from_file()
        
        print(f"\n📋 Found {len(queries)} queries in 查询用例.md")
        print("-" * 50)
        
        # Show first 10 queries
        for query in queries[:10]:
            print(f"{query['id']:3d}. {query['title'][:70]}...")
        
        if len(queries) > 10:
            print(f"     ... and {len(queries) - 10} more queries")
            
    except Exception as e:
        print(f"❌ Error reading queries: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_api_connection()
    elif len(sys.argv) > 1 and sys.argv[1] == "preview":
        show_query_preview()
    else:
        success = setup_environment()
        if success:
            test_api_connection()
            show_query_preview()
