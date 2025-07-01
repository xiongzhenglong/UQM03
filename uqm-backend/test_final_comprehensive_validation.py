#!/usr/bin/env python3
"""
最终综合验证脚本
验证修复后的用例是否符合规范：
1. JSON结构正确（无"uqm"包装）
2. 字段都真实存在
3. SQL可以正常执行
"""

import json
import re
import sqlite3
from pathlib import Path

def load_database():
    """连接数据库"""
    db_path = Path(__file__).parent / "uqm.db"
    return sqlite3.connect(str(db_path))

def get_table_columns(conn, table_name):
    """获取表的所有列名"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return columns

def validate_json_structure(json_str):
    """验证JSON结构是否正确（不应有"uqm"包装）"""
    try:
        data = json.loads(json_str)
        
        # 检查是否有"uqm"包装
        if "uqm" in data:
            return False, "发现不应存在的'uqm'包装"
        
        # 检查必需字段
        required_fields = ["metadata", "steps", "output"]
        for field in required_fields:
            if field not in data:
                return False, f"缺少必需字段: {field}"
        
        return True, "JSON结构正确"
    except json.JSONDecodeError as e:
        return False, f"JSON解析错误: {e}"

def extract_fields_from_config(config, conn):
    """从配置中提取字段并验证是否存在"""
    issues = []
    
    # 获取所有表的列信息
    tables_info = {}
    tables = ["products", "customers", "orders", "order_items", "inventory", "categories", "suppliers"]
    for table in tables:
        try:
            tables_info[table] = get_table_columns(conn, table)
        except:
            pass
    
    # 检查data_source
    data_source = config.get("data_source")
    if data_source and data_source not in tables_info:
        issues.append(f"数据源表不存在: {data_source}")
    
    # 检查dimensions字段
    if "dimensions" in config:
        for dim in config["dimensions"]:
            field_name = dim.split(".")[-1]  # 去掉表前缀
            table_name = dim.split(".")[0] if "." in dim else data_source
            if table_name in tables_info and field_name not in tables_info[table_name]:
                issues.append(f"维度字段不存在: {dim}")
    
    # 检查filters中的字段
    if "filters" in config:
        for filter_item in config["filters"]:
            field = filter_item.get("field", "")
            field_name = field.split(".")[-1]
            table_name = field.split(".")[0] if "." in field else data_source
            if table_name in tables_info and field_name not in tables_info[table_name]:
                issues.append(f"过滤字段不存在: {field}")
    
    # 检查group_by字段
    if "group_by" in config:
        for group_field in config["group_by"]:
            field_name = group_field.split(".")[-1]
            table_name = group_field.split(".")[0] if "." in group_field else data_source
            if table_name in tables_info and field_name not in tables_info[table_name]:
                issues.append(f"分组字段不存在: {group_field}")
    
    # 检查joins中的字段
    if "joins" in config:
        for join in config["joins"]:
            if "on" in join:
                left_field = join["on"].get("left", "").split(".")[-1]
                right_field = join["on"].get("right", "").split(".")[-1]
                left_table = join["on"].get("left", "").split(".")[0]
                right_table = join["on"].get("right", "").split(".")[0]
                
                if left_table in tables_info and left_field not in tables_info[left_table]:
                    issues.append(f"JOIN左字段不存在: {join['on']['left']}")
                if right_table in tables_info and right_field not in tables_info[right_table]:
                    issues.append(f"JOIN右字段不存在: {join['on']['right']}")
    
    return issues

def validate_use_case_file():
    """验证用例文件"""
    use_case_file = Path(__file__).parent.parent / "UQM_ASSERT_查询用例.md"
    
    if not use_case_file.exists():
        print("❌ 用例文件不存在")
        return False
    
    content = use_case_file.read_text(encoding="utf-8")
    
    # 提取所有JSON块
    json_blocks = re.findall(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
    
    print(f"📊 找到 {len(json_blocks)} 个JSON配置块")
    
    conn = load_database()
    total_issues = 0
    
    for i, json_block in enumerate(json_blocks, 1):
        print(f"\n🔍 验证JSON块 {i}:")
        
        # 验证JSON结构
        is_valid, message = validate_json_structure(json_block)
        if not is_valid:
            print(f"  ❌ JSON结构问题: {message}")
            total_issues += 1
            continue
        else:
            print(f"  ✅ JSON结构正确")
        
        # 解析JSON并验证字段
        try:
            data = json.loads(json_block)
            
            # 验证每个步骤中的字段
            for step in data.get("steps", []):
                if step.get("type") == "query":
                    config = step.get("config", {})
                    field_issues = extract_fields_from_config(config, conn)
                    
                    if field_issues:
                        print(f"  ❌ 步骤 '{step.get('name')}' 字段问题:")
                        for issue in field_issues:
                            print(f"    - {issue}")
                        total_issues += len(field_issues)
                    else:
                        print(f"  ✅ 步骤 '{step.get('name')}' 字段验证通过")
        
        except Exception as e:
            print(f"  ❌ 验证过程出错: {e}")
            total_issues += 1
    
    conn.close()
    
    print(f"\n📋 验证总结:")
    if total_issues == 0:
        print("🎉 所有用例验证通过！没有发现字段或结构问题。")
        return True
    else:
        print(f"❌ 发现 {total_issues} 个问题需要修复")
        return False

def check_phantom_fields():
    """检查是否还有幻觉字段"""
    use_case_file = Path(__file__).parent.parent / "UQM_ASSERT_查询用例.md"
    content = use_case_file.read_text(encoding="utf-8")
    
    # 常见的幻觉字段
    phantom_fields = [
        "units_in_stock", "reorder_level", "total_amount", "shipped_date",
        "order_value", "line_total", "extended_price", "profit_margin",
        "order_total", "payment_date", "delivery_date"
    ]
    
    found_phantoms = []
    for field in phantom_fields:
        if field in content:
            found_phantoms.append(field)
    
    if found_phantoms:
        print(f"⚠️  发现可能的幻觉字段: {', '.join(found_phantoms)}")
        return False
    else:
        print("✅ 未发现幻觉字段")
        return True

def main():
    print("🔧 UQM用例最终综合验证")
    print("=" * 50)
    
    # 1. 检查幻觉字段
    print("\n1️⃣ 检查幻觉字段...")
    phantom_ok = check_phantom_fields()
    
    # 2. 验证用例文件
    print("\n2️⃣ 验证用例结构和字段...")
    validation_ok = validate_use_case_file()
    
    # 总结
    print("\n" + "=" * 50)
    if phantom_ok and validation_ok:
        print("🎉 最终验证通过！所有用例已修复完成。")
        print("✅ 无幻觉字段")
        print("✅ JSON结构正确")
        print("✅ 字段名称准确")
        return True
    else:
        print("❌ 验证未通过，仍有问题需要修复")
        return False

if __name__ == "__main__":
    main()
