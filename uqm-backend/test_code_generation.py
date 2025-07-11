#!/usr/bin/env python3
"""
测试代码生成功能
"""

import requests
import json
import time

# API配置
BASE_URL = "http://localhost:8000/api/v1"

def test_visualization_with_code_generation():
    """测试可视化代码生成功能"""
    
    # 模拟数据
    test_data = [
        {"name": "张三", "age": 25, "salary": 8000, "department": "技术部", "status": "active"},
        {"name": "李四", "age": 30, "salary": 12000, "department": "销售部", "status": "active"},
        {"name": "王五", "age": 28, "salary": 10000, "department": "技术部", "status": "inactive"},
        {"name": "赵六", "age": 35, "salary": 15000, "department": "管理部", "status": "active"},
        {"name": "钱七", "age": 27, "salary": 9000, "department": "技术部", "status": "active"},
        {"name": "孙八", "age": 32, "salary": 11000, "department": "销售部", "status": "active"},
        {"name": "周九", "age": 29, "salary": 9500, "department": "技术部", "status": "inactive"},
        {"name": "吴十", "age": 33, "salary": 13000, "department": "管理部", "status": "active"},
    ]
    
    print("=" * 60)
    print("测试可视化代码生成功能")
    print("=" * 60)
    
    # 测试1: 表格可视化
    print("\n1. 测试表格可视化代码生成")
    print("-" * 40)
    
    request_data = {
        "data": test_data,
        "query": "创建一个包含所有员工信息的表格，支持按部门筛选和按薪资排序",
        "visualization_type": "table",
        "options": {}
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-visualization",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 表格可视化代码生成成功")
                print(f"   可视化类型: {result.get('visualization_type')}")
                config = result.get('config', {})
                if 'columns' in config:
                    print(f"   生成的列数: {len(config['columns'])}")
                    for col in config['columns']:
                        print(f"     - {col.get('title', 'N/A')} ({col.get('dataIndex', 'N/A')})")
            else:
                print(f"❌ 表格生成失败: {result.get('error')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 测试2: 图表可视化
    print("\n2. 测试图表可视化代码生成")
    print("-" * 40)
    
    request_data = {
        "data": test_data,
        "query": "生成一个按部门统计平均薪资的柱状图，并显示每个部门的员工数量",
        "visualization_type": "chart",
        "options": {}
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-visualization",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 图表可视化代码生成成功")
                print(f"   可视化类型: {result.get('visualization_type')}")
                config = result.get('config', {})
                if 'series' in config:
                    print(f"   生成的系列数: {len(config['series'])}")
                    for series in config['series']:
                        print(f"     - {series.get('name', 'N/A')} ({series.get('type', 'N/A')})")
            else:
                print(f"❌ 图表生成失败: {result.get('error')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 测试3: 自动选择可视化类型
    print("\n3. 测试自动选择可视化类型")
    print("-" * 40)
    
    request_data = {
        "data": test_data,
        "query": "分析员工薪资分布情况",
        "visualization_type": "auto",
        "options": {}
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-visualization",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 自动选择可视化类型成功")
                print(f"   选择的类型: {result.get('visualization_type')}")
                config = result.get('config', {})
                if 'title' in config:
                    print(f"   图表标题: {config['title'].get('text', 'N/A')}")
            else:
                print(f"❌ 自动选择失败: {result.get('error')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_data_analysis():
    """测试数据分析功能"""
    print("\n" + "=" * 60)
    print("测试数据分析功能")
    print("=" * 60)
    
    # 导入数据分析器
    try:
        from src.services.data_analyzer import get_data_analyzer
        
        # 测试数据
        test_data = [
            {"name": "张三", "age": 25, "salary": 8000, "department": "技术部", "status": True},
            {"name": "李四", "age": 30, "salary": 12000, "department": "销售部", "status": True},
            {"name": "王五", "age": 28, "salary": 10000, "department": "技术部", "status": False},
        ]
        
        analyzer = get_data_analyzer()
        analysis = analyzer.analyze_data(test_data)
        
        print("✅ 数据分析成功")
        print(f"   总行数: {analysis.total_rows}")
        print(f"   总列数: {analysis.total_columns}")
        print(f"   数值列: {analysis.numeric_columns}")
        print(f"   字符串列: {analysis.string_columns}")
        print(f"   布尔列: {analysis.boolean_columns}")
        
        # 生成处理代码
        ts_code = analyzer.generate_processing_code(analysis, 'typescript')
        print(f"\n✅ TypeScript代码生成成功 ({len(ts_code)} 字符)")
        
        py_code = analyzer.generate_processing_code(analysis, 'python')
        print(f"✅ Python代码生成成功 ({len(py_code)} 字符)")
        
        # 保存代码到文件
        with open('generated_typescript_code.ts', 'w', encoding='utf-8') as f:
            f.write(ts_code)
        
        with open('generated_python_code.py', 'w', encoding='utf-8') as f:
            f.write(py_code)
        
        print("✅ 代码已保存到文件")
        
    except ImportError as e:
        print(f"❌ 无法导入数据分析器: {e}")
    except Exception as e:
        print(f"❌ 数据分析测试失败: {e}")

def test_complex_data():
    """测试复杂数据"""
    print("\n" + "=" * 60)
    print("测试复杂数据可视化")
    print("=" * 60)
    
    # 复杂的测试数据
    complex_data = [
        {
            "id": 1,
            "name": "产品A",
            "category": "电子产品",
            "price": 999.99,
            "stock": 50,
            "sales": 120,
            "rating": 4.5,
            "created_at": "2024-01-15",
            "is_active": True
        },
        {
            "id": 2,
            "name": "产品B",
            "category": "服装",
            "price": 299.99,
            "stock": 100,
            "sales": 85,
            "rating": 4.2,
            "created_at": "2024-01-20",
            "is_active": True
        },
        {
            "id": 3,
            "name": "产品C",
            "category": "电子产品",
            "price": 1499.99,
            "stock": 25,
            "sales": 45,
            "rating": 4.8,
            "created_at": "2024-01-25",
            "is_active": False
        },
        {
            "id": 4,
            "name": "产品D",
            "category": "家居",
            "price": 199.99,
            "stock": 200,
            "sales": 150,
            "rating": 4.0,
            "created_at": "2024-01-30",
            "is_active": True
        }
    ]
    
    # 测试复杂数据的可视化
    request_data = {
        "data": complex_data,
        "query": "创建一个产品分析仪表板，包含按类别统计的平均价格、总库存和总销量",
        "visualization_type": "auto",
        "options": {}
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-visualization",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 复杂数据可视化生成成功")
                print(f"   可视化类型: {result.get('visualization_type')}")
                config = result.get('config', {})
                
                # 分析生成的配置
                if result.get('visualization_type') == 'table':
                    if 'columns' in config:
                        print(f"   生成的列数: {len(config['columns'])}")
                elif result.get('visualization_type') == 'chart':
                    if 'series' in config:
                        print(f"   生成的系列数: {len(config['series'])}")
                        for series in config['series']:
                            print(f"     - {series.get('name', 'N/A')} ({series.get('type', 'N/A')})")
            else:
                print(f"❌ 复杂数据可视化失败: {result.get('error')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("开始测试代码生成功能...")
    
    # 测试可视化代码生成
    test_visualization_with_code_generation()
    
    # 测试数据分析
    test_data_analysis()
    
    # 测试复杂数据
    test_complex_data()
    
    print("\n测试完成!")
    print("\n生成的文件:")
    print("- generated_typescript_code.ts: TypeScript数据处理代码")
    print("- generated_python_code.py: Python数据处理代码") 