#!/usr/bin/env python3
"""
直接测试表达式计算功能
"""

import re

def test_expression_processing():
    """测试表达式处理"""
    
    # 原始表达式
    expression = "CAST(SUM(is_repurchase_customer) AS DECIMAL(10,4)) / CAST(COUNT(customer_id) AS DECIMAL(10,4))"
    
    print(f"原始表达式: {expression}")
    
    # 模拟数据
    rows = [
        {"customer_id": 1, "is_repurchase_customer": 1},
        {"customer_id": 2, "is_repurchase_customer": 1},
        {"customer_id": 3, "is_repurchase_customer": 1},
        {"customer_id": 7, "is_repurchase_customer": 0},
        {"customer_id": 8, "is_repurchase_customer": 0},
        {"customer_id": 9, "is_repurchase_customer": 0},
        {"customer_id": 10, "is_repurchase_customer": 0},
        {"customer_id": 11, "is_repurchase_customer": 0},
        {"customer_id": 12, "is_repurchase_customer": 0},
    ]
    
    # 手动处理步骤
    print(f"\n=== 手动处理步骤 ===")
    
    # 1. 计算SUM(is_repurchase_customer)
    sum_value = sum(row['is_repurchase_customer'] for row in rows)
    print(f"SUM(is_repurchase_customer) = {sum_value}")
    
    # 2. 计算COUNT(customer_id)
    count_value = len(rows)
    print(f"COUNT(customer_id) = {count_value}")
    
    # 3. 计算结果
    result = sum_value / count_value
    print(f"结果: {sum_value} / {count_value} = {result}")
    
    # 测试正则表达式替换
    print(f"\n=== 正则表达式测试 ===")
    
    result_expr = expression
    
    # 替换SUM
    sum_pattern = r'SUM\(([^)]+)\)'
    sum_matches = list(re.finditer(sum_pattern, result_expr, re.IGNORECASE))
    print(f"发现SUM匹配: {[match.group() for match in sum_matches]}")
    
    for match in reversed(sum_matches):
        start, end = match.span()
        field_expr = match.group(1).strip()
        print(f"SUM字段表达式: {field_expr}")
        print(f"替换范围: {start}-{end}")
        print(f"替换前: {result_expr}")
        result_expr = result_expr[:start] + str(sum_value) + result_expr[end:]
        print(f"替换后: {result_expr}")
    
    # 替换COUNT
    count_pattern = r'COUNT\(([^)]+)\)'
    count_matches = list(re.finditer(count_pattern, result_expr, re.IGNORECASE))
    print(f"发现COUNT匹配: {[match.group() for match in count_matches]}")
    
    for match in reversed(count_matches):
        start, end = match.span()
        field_expr = match.group(1).strip()
        print(f"COUNT字段表达式: {field_expr}")
        print(f"替换范围: {start}-{end}")
        print(f"替换前: {result_expr}")
        result_expr = result_expr[:start] + str(count_value) + result_expr[end:]
        print(f"替换后: {result_expr}")
    
    # 移除CAST函数 - 使用更智能的方法
    print(f"移除CAST前: {result_expr}")
    
    # 处理CAST函数 - 使用递归方法处理嵌套括号
    def remove_cast_functions(expr):
        while 'CAST(' in expr.upper():
            # 找到CAST的位置
            cast_start = expr.upper().find('CAST(')
            if cast_start == -1:
                break
                
            # 找到对应的闭合括号
            paren_count = 0
            cast_end = -1
            for i in range(cast_start + 5, len(expr)):  # 从CAST(后开始
                if expr[i] == '(':
                    paren_count += 1
                elif expr[i] == ')':
                    if paren_count == 0:
                        cast_end = i
                        break
                    paren_count -= 1
            
            if cast_end == -1:
                break
                
            # 提取CAST函数内容
            cast_content = expr[cast_start + 5:cast_end]  # 去掉CAST(
            
            # 找到AS关键字
            as_pos = cast_content.upper().rfind(' AS ')
            if as_pos != -1:
                # 提取AS前的表达式
                inner_expr = cast_content[:as_pos].strip()
                # 替换整个CAST函数
                expr = expr[:cast_start] + inner_expr + expr[cast_end + 1:]
            else:
                # 如果没有AS，就去掉CAST包装
                expr = expr[:cast_start] + cast_content + expr[cast_end + 1:]
        
        return expr
    
    result_expr = remove_cast_functions(result_expr)
    print(f"移除CAST后: {result_expr}")
    
    # 计算最终结果
    print(f"\n最终表达式: {result_expr}")
    try:
        final_result = eval(result_expr)
        print(f"计算结果: {final_result}")
    except Exception as e:
        print(f"计算失败: {e}")

if __name__ == "__main__":
    test_expression_processing()
