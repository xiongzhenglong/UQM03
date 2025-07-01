"""
测试pivot步骤的column_prefix功能
"""

import pytest
import pandas as pd
from src.steps.pivot_step import PivotStep
from src.utils.exceptions import ValidationError, ExecutionError


class TestPivotColumnPrefix:
    """测试pivot步骤的column_prefix功能"""
    
    def setup_method(self):
        """设置测试数据"""
        self.sample_data = [
            {
                "department_name": "销售部",
                "job_title": "销售经理",
                "order_amount": 1000.0,
                "order_id": "ORD001",
                "customer_id": "CUST001"
            },
            {
                "department_name": "销售部",
                "job_title": "销售代表",
                "order_amount": 800.0,
                "order_id": "ORD002",
                "customer_id": "CUST002"
            },
            {
                "department_name": "销售部",
                "job_title": "销售经理",
                "order_amount": 1200.0,
                "order_id": "ORD003",
                "customer_id": "CUST003"
            },
            {
                "department_name": "技术部",
                "job_title": "技术总监",
                "order_amount": 1500.0,
                "order_id": "ORD004",
                "customer_id": "CUST004"
            },
            {
                "department_name": "技术部",
                "job_title": "工程师",
                "order_amount": 600.0,
                "order_id": "ORD005",
                "customer_id": "CUST005"
            }
        ]
    
    def test_pivot_with_column_prefix(self):
        """测试pivot步骤的column_prefix功能"""
        config = {
            "source": "test_data",
            "index": "department_name",
            "columns": "job_title",
            "values": "order_amount",
            "agg_func": "sum",
            "column_prefix": "销售额_",
            "fill_value": 0
        }
        
        step = PivotStep(config)
        
        # 模拟execute方法中的数据获取
        result = step._perform_pivot(self.sample_data)
        
        # 验证结果
        assert len(result) == 2  # 两个部门
        
        # 验证column_prefix是否生效
        for row in result:
            # 检查是否有带前缀的列
            has_prefix_columns = any(col.startswith("销售额_") for col in row.keys() if col != "department_name")
            assert has_prefix_columns, f"结果中没有找到带前缀的列: {list(row.keys())}"
        
        # 具体验证列名
        sales_dept = next(row for row in result if row["department_name"] == "销售部")
        expected_columns = ["销售额_销售经理", "销售额_销售代表"]
        
        for col in expected_columns:
            assert col in sales_dept, f"缺少列: {col}, 实际列: {list(sales_dept.keys())}"
        
        # 验证数值
        assert sales_dept["销售额_销售经理"] == 2200.0  # 1000 + 1200
        assert sales_dept["销售额_销售代表"] == 800.0
    
    def test_pivot_with_column_suffix(self):
        """测试pivot步骤的column_suffix功能"""
        config = {
            "source": "test_data",
            "index": "department_name",
            "columns": "job_title",
            "values": "order_amount",
            "agg_func": "sum",
            "column_suffix": "_金额",
            "fill_value": 0
        }
        
        step = PivotStep(config)
        result = step._perform_pivot(self.sample_data)
        
        # 验证结果
        assert len(result) == 2
        
        # 验证column_suffix是否生效
        for row in result:
            has_suffix_columns = any(col.endswith("_金额") for col in row.keys() if col != "department_name")
            assert has_suffix_columns, f"结果中没有找到带后缀的列: {list(row.keys())}"
    
    def test_pivot_with_prefix_and_suffix(self):
        """测试同时使用column_prefix和column_suffix"""
        config = {
            "source": "test_data",
            "index": "department_name",
            "columns": "job_title",
            "values": "order_amount",
            "agg_func": "sum",
            "column_prefix": "总_",
            "column_suffix": "_金额",
            "fill_value": 0
        }
        
        step = PivotStep(config)
        result = step._perform_pivot(self.sample_data)
        
        # 验证结果
        sales_dept = next(row for row in result if row["department_name"] == "销售部")
        
        # 验证前缀和后缀都存在
        expected_columns = ["总_销售经理_金额", "总_销售代表_金额"]
        for col in expected_columns:
            assert col in sales_dept, f"缺少列: {col}, 实际列: {list(sales_dept.keys())}"
    
    def test_pivot_count_with_prefix(self):
        """测试count聚合函数配合column_prefix"""
        config = {
            "source": "test_data",
            "index": "department_name",
            "columns": "job_title",
            "values": "order_id",
            "agg_func": "count",
            "column_prefix": "订单数_",
            "fill_value": 0
        }
        
        step = PivotStep(config)
        result = step._perform_pivot(self.sample_data)
        
        # 验证结果
        sales_dept = next(row for row in result if row["department_name"] == "销售部")
        
        # 验证列名和数值
        assert "订单数_销售经理" in sales_dept
        assert "订单数_销售代表" in sales_dept
        assert sales_dept["订单数_销售经理"] == 2  # 两个销售经理的订单
        assert sales_dept["订单数_销售代表"] == 1  # 一个销售代表的订单
    
    def test_no_prefix_suffix(self):
        """测试没有prefix和suffix的情况"""
        config = {
            "source": "test_data",
            "index": "department_name",
            "columns": "job_title",
            "values": "order_amount",
            "agg_func": "sum",
            "fill_value": 0
        }
        
        step = PivotStep(config)
        result = step._perform_pivot(self.sample_data)
        
        # 验证结果
        sales_dept = next(row for row in result if row["department_name"] == "销售部")
        
        # 验证原始列名
        expected_columns = ["销售经理", "销售代表"]
        for col in expected_columns:
            assert col in sales_dept, f"缺少列: {col}, 实际列: {list(sales_dept.keys())}"
    
    def test_multi_metric_scenario(self):
        """测试多指标场景（模拟实际业务用例）"""
        # 销售额pivot
        sales_config = {
            "source": "test_data",
            "index": "department_name", 
            "columns": "job_title",
            "values": "order_amount",
            "agg_func": "sum",
            "column_prefix": "销售额_",
            "fill_value": 0
        }
        
        # 订单数pivot
        count_config = {
            "source": "test_data",
            "index": "department_name",
            "columns": "job_title", 
            "values": "order_id",
            "agg_func": "count",
            "column_prefix": "订单数_",
            "fill_value": 0
        }
        
        sales_step = PivotStep(sales_config)
        count_step = PivotStep(count_config)
        
        sales_result = sales_step._perform_pivot(self.sample_data)
        count_result = count_step._perform_pivot(self.sample_data)
        
        # 验证两个结果的列名不冲突
        sales_cols = set()
        count_cols = set()
        
        for row in sales_result:
            sales_cols.update(col for col in row.keys() if col != "department_name")
        
        for row in count_result:
            count_cols.update(col for col in row.keys() if col != "department_name")
        
        # 验证没有重叠（除了index列）
        overlap = sales_cols.intersection(count_cols)
        assert not overlap, f"销售额和订单数的列名有重叠: {overlap}"
        
        # 验证前缀正确
        sales_prefix_cols = [col for col in sales_cols if col.startswith("销售额_")]
        count_prefix_cols = [col for col in count_cols if col.startswith("订单数_")]
        
        assert len(sales_prefix_cols) > 0, "销售额pivot结果没有正确的前缀"
        assert len(count_prefix_cols) > 0, "订单数pivot结果没有正确的前缀"


if __name__ == "__main__":
    # 运行测试
    test_instance = TestPivotColumnPrefix()
    test_instance.setup_method()
    
    print("🧪 开始测试pivot column_prefix功能...")
    
    try:
        test_instance.test_pivot_with_column_prefix()
        print("✅ test_pivot_with_column_prefix 通过")
        
        test_instance.test_pivot_with_column_suffix()
        print("✅ test_pivot_with_column_suffix 通过")
        
        test_instance.test_pivot_with_prefix_and_suffix()
        print("✅ test_pivot_with_prefix_and_suffix 通过")
        
        test_instance.test_pivot_count_with_prefix()
        print("✅ test_pivot_count_with_prefix 通过")
        
        test_instance.test_no_prefix_suffix()
        print("✅ test_no_prefix_suffix 通过")
        
        test_instance.test_multi_metric_scenario()
        print("✅ test_multi_metric_scenario 通过")
        
        print("\n🎉 所有测试通过！column_prefix功能正常工作")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
