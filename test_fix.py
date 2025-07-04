#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的查询步骤
验证聚合函数问题是否解决
"""

import json
import sys
import traceback
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent
uqm_backend_path = project_root / "uqm-backend"
sys.path.insert(0, str(uqm_backend_path))

try:
    # 直接导入并测试QueryStep
    from src.steps.query_step import QueryStep
    
    def test_case_when_with_aggregates():
        """测试CASE WHEN表达式中的聚合函数处理"""
        print("=" * 60)
        print("测试：CASE WHEN表达式中的聚合函数处理")
        print("=" * 60)
        
        # 创建测试用的QueryStep实例
        config = {
            "data_source": "test_data",
            "dimensions": ["customer_id"],
            "calculated_fields": [
                {
                    "alias": "is_repeat_purchaser",
                    "expression": "CASE WHEN SUM(coc.total_orders) > 1 THEN 1 ELSE 0 END"
                }
            ]
        }
        
        query_step = QueryStep(config)
        
        # 创建测试数据
        test_data = [
            {"customer_id": "C001", "coc_total_orders": 3},
            {"customer_id": "C002", "coc_total_orders": 1}, 
            {"customer_id": "C003", "coc_total_orders": 5}
        ]
        
        print("测试数据:")
        for row in test_data:
            print(f"  {row}")
        
        try:
            # 测试 _evaluate_condition_with_aggregates 方法
            print("\n测试聚合条件评估:")
            
            for row in test_data:
                # 测试条件 "SUM(coc.total_orders) > 1"
                condition = "SUM(coc.total_orders) > 1"
                result = query_step._evaluate_condition_with_aggregates(condition, row)
                expected = row["coc_total_orders"] > 1
                
                print(f"  客户 {row['customer_id']}: SUM={row['coc_total_orders']}, 条件='{condition}', 结果={result}, 期望={expected}")
                
                if result == expected:
                    print(f"    ✅ 正确")
                else:
                    print(f"    ❌ 错误")
                    return False
            
            # 测试 CASE WHEN 表达式
            print("\n测试CASE WHEN表达式:")
            
            for row in test_data:
                expression = "CASE WHEN SUM(coc.total_orders) > 1 THEN 1 ELSE 0 END"
                result = query_step._evaluate_case_when_expression(expression, row)
                expected = 1 if row["coc_total_orders"] > 1 else 0
                
                print(f"  客户 {row['customer_id']}: 表达式结果={result}, 期望={expected}")
                
                if result == expected:
                    print(f"    ✅ 正确")
                else:
                    print(f"    ❌ 错误")
                    return False
            
            print("\n✅ 所有聚合函数测试通过！")
            return True
            
        except Exception as e:
            print(f"\n❌ 测试过程中出错：{e}")
            traceback.print_exc()
            return False

    def test_expression_with_aggregates():
        """测试包含聚合函数的表达式处理"""
        print("\n" + "=" * 60)
        print("测试：包含聚合函数的表达式处理")
        print("=" * 60)
        
        config = {
            "data_source": "test_data",
            "calculated_fields": [
                {
                    "alias": "avg_rate",
                    "expression": "AVG(crpf.is_repeat_purchaser)"
                }
            ]
        }
        
        query_step = QueryStep(config)
        
        # 测试数据
        test_data = [
            {"crpf_is_repeat_purchaser": 0.75},
            {"crpf_is_repeat_purchaser": 0.80},
            {"crpf_is_repeat_purchaser": 0.65}
        ]
        
        print("测试数据:")
        for i, row in enumerate(test_data):
            print(f"  行 {i+1}: {row}")
        
        try:
            print("\n测试聚合表达式评估:")
            
            for i, row in enumerate(test_data):
                expression = "AVG(crpf.is_repeat_purchaser)"
                result = query_step._evaluate_expression_with_aggregates(expression, row)
                expected = row["crpf_is_repeat_purchaser"]  # 应该找到对应的字段值
                
                print(f"  行 {i+1}: 表达式='{expression}', 结果={result}, 期望={expected}")
                
                if result == expected:
                    print(f"    ✅ 正确")
                else:
                    print(f"    ❌ 错误")
                    return False
            
            print("\n✅ 聚合表达式测试通过！")
            return True
            
        except Exception as e:
            print(f"\n❌ 聚合表达式测试出错：{e}")
            traceback.print_exc()
            return False

    def test_basic_functionality():
        """测试基本功能"""
        print("\n" + "=" * 60)
        print("测试：基本功能验证")
        print("=" * 60)
        
        try:
            # 测试1：验证QueryStep可以正常创建
            config = {
                "data_source": "orders",
                "dimensions": ["customer_id"],
                "metrics": [
                    {
                        "name": "order_id",
                        "aggregation": "COUNT",
                        "alias": "total_orders"
                    }
                ]
            }
            
            query_step = QueryStep(config)
            query_step.validate()
            print("✅ QueryStep创建和验证成功")
            
            # 测试2：验证表达式解析器可以处理聚合函数
            test_row = {"coc_total_orders": 3}
            condition = "SUM(coc.total_orders) > 1"
            
            result = query_step._evaluate_condition_with_aggregates(condition, test_row)
            print(f"✅ 聚合条件评估成功: {condition} = {result}")
            
            # 测试3：验证CASE WHEN表达式解析
            case_expression = "CASE WHEN SUM(coc.total_orders) > 1 THEN 1 ELSE 0 END"
            case_result = query_step._evaluate_case_when_expression(case_expression, test_row)
            print(f"✅ CASE WHEN表达式评估成功: {case_expression} = {case_result}")
            
            return True
            
        except Exception as e:
            print(f"❌ 基本功能测试失败：{e}")
            traceback.print_exc()
            return False

    def main():
        """主测试函数"""
        print("开始测试修复后的QueryStep...")
        print(f"项目路径：{project_root}")
        print(f"UQM后端路径：{uqm_backend_path}")
        
        # 测试1：基本功能
        test1_success = test_basic_functionality()
        
        # 测试2：CASE WHEN与聚合函数
        test2_success = test_case_when_with_aggregates()
        
        # 测试3：聚合表达式处理
        test3_success = test_expression_with_aggregates()
        
        # 总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print(f"基本功能测试：{'✅ 通过' if test1_success else '❌ 失败'}")
        print(f"CASE WHEN聚合测试：{'✅ 通过' if test2_success else '❌ 失败'}")
        print(f"聚合表达式测试：{'✅ 通过' if test3_success else '❌ 失败'}")
        
        all_success = test1_success and test2_success and test3_success
        
        if all_success:
            print("\n🎉 所有测试通过！聚合函数问题已成功修复！")
            print("\n修复要点：")
            print("1. ✅ _evaluate_condition_with_aggregates 方法正确处理聚合函数")
            print("2. ✅ _evaluate_expression_with_aggregates 方法正确处理聚合表达式") 
            print("3. ✅ CASE WHEN表达式能正确调用聚合函数评估")
            print("4. ✅ 字段名变体匹配（支持前缀别名）")
        else:
            print("\n⚠️  部分测试失败，需要进一步检查")
            
        return all_success

    if __name__ == "__main__":
        success = main()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"❌ 导入错误：{e}")
    print("请确保QueryStep模块可用")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"❌ 未知错误：{e}")
    traceback.print_exc()
    sys.exit(1)
