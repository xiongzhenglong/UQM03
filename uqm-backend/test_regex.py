#!/usr/bin/env python3
"""
测试正则表达式
"""
import re

over_clause = 'PARTITION BY country ORDER BY total_sales_amount DESC'
print(f"OVER子句: '{over_clause}'")

# 测试不同的正则表达式
patterns = [
    r'PARTITION\s+BY\s+([^O]+?)(?:\s+ORDER\s+BY|$)',
    r'PARTITION\s+BY\s+([^O]+?)(?:\s+ORDER|$)',
    r'PARTITION\s+BY\s+(\w+)',
    r'PARTITION\s+BY\s+([a-zA-Z_][a-zA-Z0-9_]*)',
    r'PARTITION\s+BY\s+(.+?)\s+ORDER\s+BY'
]

for i, pattern in enumerate(patterns):
    match = re.search(pattern, over_clause, re.IGNORECASE)
    if match:
        print(f"模式 {i+1}: '{pattern}' -> 匹配: '{match.group(1)}'")
    else:
        print(f"模式 {i+1}: '{pattern}' -> 无匹配")

print("\n测试 ORDER BY 解析:")
order_pattern = r'ORDER\s+BY\s+(.+?)$'
order_match = re.search(order_pattern, over_clause, re.IGNORECASE)
if order_match:
    print(f"ORDER BY 匹配: '{order_match.group(1)}'")
else:
    print("ORDER BY 无匹配")
