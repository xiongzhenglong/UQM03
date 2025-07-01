"""
测试销售业绩多指标分析的完整流程
模拟用户实际遇到的问题场景
"""

import pytest
import pandas as pd
from src.steps.pivot_step import PivotStep
from src.steps.enrich_step import EnrichStep


class TestSalesMultiMetricsScenario:
    """测试销售业绩多指标分析场景"""
    
    def setup_method(self):
        """设置测试数据，模拟实际的销售数据"""
        self.sales_data = [
            {
                "department_name": "欧洲销售部",
                "job_title": "欧洲区销售经理",
                "order_amount": 1570.35,
                "order_id": "ORD001",
                "customer_id": "CUST001"
            },
            {
                "department_name": "欧洲销售部",
                "job_title": "欧洲区销售经理", 
                "order_amount": 0.0,  # 第二个订单
                "order_id": "ORD002",
                "customer_id": "CUST002"
            },
            {
                "department_name": "销售部",
                "job_title": "销售代表",
                "order_amount": 1634.05,
                "order_id": "ORD003", 
                "customer_id": "CUST003"
            },
            {
                "department_name": "销售部",
                "job_title": "销售代表",
                "order_amount": 0.0,  # 第二个订单
                "order_id": "ORD004",
                "customer_id": "CUST004"
            },
            {
                "department_name": "销售部",
                "job_title": "销售代表",
                "order_amount": 0.0,  # 第三个订单  
                "order_id": "ORD005",
                "customer_id": "CUST005"
            }
        ]
    
    def test_sales_amount_pivot_with_prefix(self):
        """测试销售额pivot，验证column_prefix是否正常工作"""
        config = {
            "source": "get_sales_data",
            "index": "department_name",
            "columns": "job_title", 
            "values": "order_amount",
            "agg_func": "sum",
            "column_prefix": "销售额_",
            "fill_value": 0
        }
        
        step = PivotStep(config)
        result = step._perform_pivot(self.sales_data)
        
        print("📊 销售额pivot结果:")
        for row in result:
            print(f"  {row}")
        
        # 验证结果结构
        assert len(result) == 2, f"应该有2个部门，实际有{len(result)}个"
        
        # 验证列名包含正确的前缀
        for row in result:
            for col_name in row.keys():
                if col_name != "department_name":
                    assert col_name.startswith("销售额_"), f"列名 '{col_name}' 应该以 '销售额_' 开头"
        
        # 验证具体数值
        欧洲销售部 = next(row for row in result if row["department_name"] == "欧洲销售部")
        销售部 = next(row for row in result if row["department_name"] == "销售部")
        
        assert "销售额_欧洲区销售经理" in 欧洲销售部, f"缺少 '销售额_欧洲区销售经理' 列: {list(欧洲销售部.keys())}"
        assert "销售额_销售代表" in 销售部, f"缺少 '销售额_销售代表' 列: {list(销售部.keys())}"
        
        # 验证数值正确性
        assert 欧洲销售部["销售额_欧洲区销售经理"] == 1570.35
        assert 销售部["销售额_销售代表"] == 1634.05
    
    def test_order_count_pivot_with_prefix(self):
        """测试订单数pivot，验证column_prefix是否正常工作"""
        config = {
            "source": "get_sales_data",
            "index": "department_name",
            "columns": "job_title",
            "values": "order_id", 
            "agg_func": "count",
            "column_prefix": "订单数_",
            "fill_value": 0
        }
        
        step = PivotStep(config)
        result = step._perform_pivot(self.sales_data)
        
        print("📊 订单数pivot结果:")
        for row in result:
            print(f"  {row}")
        
        # 验证列名包含正确的前缀
        for row in result:
            for col_name in row.keys():
                if col_name != "department_name":
                    assert col_name.startswith("订单数_"), f"列名 '{col_name}' 应该以 '订单数_' 开头"
        
        # 验证具体数值
        欧洲销售部 = next(row for row in result if row["department_name"] == "欧洲销售部")
        销售部 = next(row for row in result if row["department_name"] == "销售部")
        
        assert 欧洲销售部["订单数_欧洲区销售经理"] == 2  # 2个订单
        assert 销售部["订单数_销售代表"] == 3  # 3个订单
    
    def test_customer_count_pivot_with_prefix(self):
        """测试客户数pivot，验证column_prefix是否正常工作"""
        config = {
            "source": "get_sales_data",
            "index": "department_name",
            "columns": "job_title",
            "values": "customer_id",
            "agg_func": "count", 
            "column_prefix": "客户数_",
            "fill_value": 0
        }
        
        step = PivotStep(config)
        result = step._perform_pivot(self.sales_data)
        
        print("📊 客户数pivot结果:")
        for row in result:
            print(f"  {row}")
        
        # 验证列名包含正确的前缀  
        for row in result:
            for col_name in row.keys():
                if col_name != "department_name":
                    assert col_name.startswith("客户数_"), f"列名 '{col_name}' 应该以 '客户数_' 开头"
    
    def test_multi_metrics_combination(self):
        """测试多指标组合，验证前缀是否能正确区分不同指标"""
        
        # 1. 销售额pivot
        sales_config = {
            "source": "get_sales_data",
            "index": "department_name",
            "columns": "job_title",
            "values": "order_amount",
            "agg_func": "sum",
            "column_prefix": "销售额_", 
            "fill_value": 0
        }
        
        # 2. 订单数pivot
        order_config = {
            "source": "get_sales_data", 
            "index": "department_name",
            "columns": "job_title",
            "values": "order_id",
            "agg_func": "count",
            "column_prefix": "订单数_",
            "fill_value": 0
        }
        
        # 3. 客户数pivot
        customer_config = {
            "source": "get_sales_data",
            "index": "department_name", 
            "columns": "job_title",
            "values": "customer_id",
            "agg_func": "count",
            "column_prefix": "客户数_",
            "fill_value": 0
        }
        
        # 执行所有pivot
        sales_step = PivotStep(sales_config)
        order_step = PivotStep(order_config)
        customer_step = PivotStep(customer_config)
        
        sales_result = sales_step._perform_pivot(self.sales_data)
        order_result = order_step._perform_pivot(self.sales_data)
        customer_result = customer_step._perform_pivot(self.sales_data)
        
        print("\n🔍 多指标分析结果:")
        print("销售额结果:", sales_result[0])
        print("订单数结果:", order_result[0])
        print("客户数结果:", customer_result[0])
        
        # 验证每个结果的列名前缀都正确
        for row in sales_result:
            sales_cols = [col for col in row.keys() if col != "department_name"]
            for col in sales_cols:
                assert col.startswith("销售额_"), f"销售额列名错误: {col}"
        
        for row in order_result:
            order_cols = [col for col in row.keys() if col != "department_name"]
            for col in order_cols:
                assert col.startswith("订单数_"), f"订单数列名错误: {col}"
        
        for row in customer_result:
            customer_cols = [col for col in row.keys() if col != "department_name"] 
            for col in customer_cols:
                assert col.startswith("客户数_"), f"客户数列名错误: {col}"
        
        # 验证列名不会冲突
        all_sales_cols = set()
        all_order_cols = set()
        all_customer_cols = set()
        
        for row in sales_result:
            all_sales_cols.update(col for col in row.keys() if col != "department_name")
        for row in order_result:
            all_order_cols.update(col for col in row.keys() if col != "department_name")
        for row in customer_result:
            all_customer_cols.update(col for col in row.keys() if col != "department_name")
        
        # 确保三个指标的列名没有重叠
        assert not all_sales_cols.intersection(all_order_cols), "销售额和订单数列名重叠"
        assert not all_sales_cols.intersection(all_customer_cols), "销售额和客户数列名重叠"
        assert not all_order_cols.intersection(all_customer_cols), "订单数和客户数列名重叠"
        
        print("✅ 多指标列名前缀验证通过，没有冲突")
    
    def test_expected_vs_actual_result_format(self):
        """对比期望结果和实际结果格式"""
        
        # 用户期望的结果格式
        expected_format = {
            "department_name": "欧洲销售部",
            "销售额_欧洲区销售经理": 1570.35,
            "销售额_销售代表": 0.0,
            "订单数_欧洲区销售经理": 2,
            "订单数_销售代表": 0,
            "客户数_欧洲区销售经理": 2,
            "客户数_销售代表": 0
        }
        
        # 用户实际得到的错误格式
        actual_wrong_format = {
            "department_name": "欧洲销售部",
            "欧洲区销售经理": 1570.35,        # ❌ 没有前缀
            "销售代表": 0.0,                # ❌ 没有前缀
            "欧洲区销售经理_1": 2,           # ❌ 错误的后缀
            "销售代表_1": 0,                # ❌ 错误的后缀
            "欧洲区销售经理_2": 2,           # ❌ 错误的后缀
            "销售代表_2": 0                 # ❌ 错误的后缀
        }
        
        print("期望格式:", expected_format)
        print("错误格式:", actual_wrong_format)
        
        # 使用修复后的代码测试
        sales_config = {
            "source": "get_sales_data",
            "index": "department_name",
            "columns": "job_title",
            "values": "order_amount",
            "agg_func": "sum",
            "column_prefix": "销售额_",
            "fill_value": 0
        }
        
        step = PivotStep(sales_config)
        result = step._perform_pivot(self.sales_data)
        
        # 检查结果是否符合期望格式
        欧洲销售部 = next(row for row in result if row["department_name"] == "欧洲销售部")
        
        # 验证列名格式正确
        for col_name in 欧洲销售部.keys():
            if col_name != "department_name":
                assert col_name.startswith("销售额_"), f"列名格式错误: {col_name}"
                assert not col_name.endswith("_1") and not col_name.endswith("_2"), f"不应该有数字后缀: {col_name}"
        
        print("✅ 修复后的结果格式正确")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestSalesMultiMetricsScenario() 
    test_instance.setup_method()
    
    print("🧪 开始测试销售业绩多指标分析场景...")
    
    try:
        test_instance.test_sales_amount_pivot_with_prefix()
        print("✅ test_sales_amount_pivot_with_prefix 通过")
        
        test_instance.test_order_count_pivot_with_prefix()
        print("✅ test_order_count_pivot_with_prefix 通过")
        
        test_instance.test_customer_count_pivot_with_prefix()
        print("✅ test_customer_count_pivot_with_prefix 通过")
        
        test_instance.test_multi_metrics_combination()
        print("✅ test_multi_metrics_combination 通过")
        
        test_instance.test_expected_vs_actual_result_format()
        print("✅ test_expected_vs_actual_result_format 通过")
        
        print("\n🎉 所有测试通过！销售业绩多指标分析的column_prefix功能正常工作")
        print("\n🔧 修复总结:")
        print("   - 在pivot_step.py的_perform_pivot方法中添加了_format_pivot_result调用")
        print("   - 这确保了column_prefix和column_suffix能够正确应用")
        print("   - 解决了用户遇到的列名冲突和前缀丢失问题")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
