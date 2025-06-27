#!/usr/bin/env python3
"""
测试NULLIF函数处理
"""

def test_nullif_expression():
    """测试NULLIF表达式处理"""
    
    # 模拟query_step中的_evaluate_complex_aggregate_expression方法
    def evaluate_test_expression(expression, sum_val, count_val):
        import re
        
        result_expr = expression
        
        # 替换SUM
        result_expr = result_expr.replace('SUM(is_repurchase_customer_flag)', str(sum_val))
        result_expr = result_expr.replace('SUM(is_any_order_customer_flag)', str(count_val))
        
        # 移除CAST函数
        def remove_cast_functions(expr):
            while 'CAST(' in expr.upper():
                cast_start = expr.upper().find('CAST(')
                if cast_start == -1:
                    break
                    
                paren_count = 0
                cast_end = -1
                for i in range(cast_start + 5, len(expr)):
                    if expr[i] == '(':
                        paren_count += 1
                    elif expr[i] == ')':
                        if paren_count == 0:
                            cast_end = i
                            break
                        paren_count -= 1
                
                if cast_end == -1:
                    break
                    
                cast_content = expr[cast_start + 5:cast_end]
                as_pos = cast_content.upper().rfind(' AS ')
                if as_pos != -1:
                    inner_expr = cast_content[:as_pos].strip()
                    expr = expr[:cast_start] + inner_expr + expr[cast_end + 1:]
                else:
                    expr = expr[:cast_start] + cast_content + expr[cast_end + 1:]
            
            return expr
        
        result_expr = remove_cast_functions(result_expr)
        
        # 处理NULLIF函数
        def handle_nullif(expr):
            while 'NULLIF(' in expr.upper():
                nullif_start = expr.upper().find('NULLIF(')
                if nullif_start == -1:
                    break
                    
                paren_count = 0
                nullif_end = -1
                for i in range(nullif_start + 7, len(expr)):
                    if expr[i] == '(':
                        paren_count += 1
                    elif expr[i] == ')':
                        if paren_count == 0:
                            nullif_end = i
                            break
                        paren_count -= 1
                
                if nullif_end == -1:
                    break
                    
                nullif_content = expr[nullif_start + 7:nullif_end]
                params = nullif_content.split(',')
                if len(params) == 2:
                    expr1 = params[0].strip()
                    expr2 = params[1].strip()
                    
                    if expr2 == '0':
                        safe_expr = f"(None if {expr1} == 0 else {expr1})"
                        expr = expr[:nullif_start] + safe_expr + expr[nullif_end + 1:]
                    else:
                        safe_expr = f"(None if {expr1} == {expr2} else {expr1})"
                        expr = expr[:nullif_start] + safe_expr + expr[nullif_end + 1:]
                else:
                    break
            
            return expr
        
        result_expr = handle_nullif(result_expr)
        
        print(f"原始表达式: {expression}")
        print(f"最终表达式: {result_expr}")
        
        try:
            result = eval(result_expr)
            print(f"计算结果: {result}")
            return result
        except Exception as e:
            print(f"计算失败: {e}")
            return None
    
    # 测试用例1: 正常除法
    print("=== 测试用例1: 正常除法 ===")
    expr1 = "CAST(SUM(is_repurchase_customer_flag) AS DECIMAL(10, 4)) / NULLIF(CAST(SUM(is_any_order_customer_flag) AS DECIMAL(10, 4)), 0)"
    result1 = evaluate_test_expression(expr1, 3, 9)
    print(f"期望结果: 0.3333, 实际结果: {result1}")
    
    # 测试用例2: 除零保护 
    print("\n=== 测试用例2: 除零保护 ===")
    expr2 = "CAST(SUM(is_repurchase_customer_flag) AS DECIMAL(10, 4)) / NULLIF(CAST(SUM(is_any_order_customer_flag) AS DECIMAL(10, 4)), 0)"
    result2 = evaluate_test_expression(expr2, 3, 0)
    print(f"期望结果: None (避免除零), 实际结果: {result2}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_nullif_expression()
