"""
测试季度销售趋势分析场景
验证多个pivot步骤使用column_prefix的完整流程
"""
import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.steps.query_step import QueryStep
from src.steps.pivot_step import PivotStep
from src.steps.union_step import UnionStep

@pytest.fixture
def quarterly_sales_data():
    """模拟季度销售聚合数据"""
    return pd.DataFrame([
        {"product_category": "电子产品", "quarter": "Q1", "total_sales_amount": 150000, "total_quantity": 500, "order_count": 125},
        {"product_category": "电子产品", "quarter": "Q2", "total_sales_amount": 180000, "total_quantity": 600, "order_count": 150},
        {"product_category": "电子产品", "quarter": "Q3", "total_sales_amount": 220000, "total_quantity": 750, "order_count": 175},
        {"product_category": "电子产品", "quarter": "Q4", "total_sales_amount": 280000, "total_quantity": 950, "order_count": 225},
        {"product_category": "服装", "quarter": "Q1", "total_sales_amount": 80000, "total_quantity": 400, "order_count": 100},
        {"product_category": "服装", "quarter": "Q2", "total_sales_amount": 95000, "total_quantity": 480, "order_count": 120},
        {"product_category": "服装", "quarter": "Q3", "total_sales_amount": 110000, "total_quantity": 550, "order_count": 140},
        {"product_category": "服装", "quarter": "Q4", "total_sales_amount": 130000, "total_quantity": 650, "order_count": 160},
        {"product_category": "家居用品", "quarter": "Q1", "total_sales_amount": 60000, "total_quantity": 300, "order_count": 75},
        {"product_category": "家居用品", "quarter": "Q2", "total_sales_amount": 72000, "total_quantity": 360, "order_count": 90},
        {"product_category": "家居用品", "quarter": "Q3", "total_sales_amount": 85000, "total_quantity": 425, "order_count": 105},
        {"product_category": "家居用品", "quarter": "Q4", "total_sales_amount": 98000, "total_quantity": 490, "order_count": 120},
    ])

def test_quarterly_pivot_q1_sales(quarterly_sales_data):
    """测试Q1销售额pivot - 应该有销售额_前缀"""
    pivot_step = PivotStep()
    
    config = {
        "source": "quarterly_data",
        "index_columns": ["product_category"],
        "pivot_column": "quarter",
        "value_columns": ["total_sales_amount"],
        "filters": [{"field": "quarter", "operator": "=", "value": "Q1"}],
        "column_prefix": "销售额_"
    }
    
    # 过滤Q1数据
    q1_data = quarterly_sales_data[quarterly_sales_data["quarter"] == "Q1"]
    
    result = pivot_step._perform_pivot(q1_data, config)
    
    # 验证结果结构
    assert isinstance(result, list)
    assert len(result) == 3  # 3个产品类别
    
    # 验证列名包含prefix
    for row in result:
        assert "销售额_Q1" in row
        assert row["销售额_Q1"] > 0

def test_quarterly_pivot_q2_quantity(quarterly_sales_data):
    """测试Q2销售量pivot - 应该有数量_前缀"""
    pivot_step = PivotStep()
    
    config = {
        "source": "quarterly_data",
        "index_columns": ["product_category"],
        "pivot_column": "quarter",
        "value_columns": ["total_quantity"],
        "filters": [{"field": "quarter", "operator": "=", "value": "Q2"}],
        "column_prefix": "数量_"
    }
    
    # 过滤Q2数据
    q2_data = quarterly_sales_data[quarterly_sales_data["quarter"] == "Q2"]
    
    result = pivot_step._perform_pivot(q2_data, config)
    
    # 验证结果结构
    assert isinstance(result, list)
    assert len(result) == 3  # 3个产品类别
    
    # 验证列名包含prefix
    for row in result:
        assert "数量_Q2" in row
        assert row["数量_Q2"] > 0

def test_quarterly_pivot_q3_orders(quarterly_sales_data):
    """测试Q3订单数pivot - 应该有订单_前缀"""
    pivot_step = PivotStep()
    
    config = {
        "source": "quarterly_data",
        "index_columns": ["product_category"],
        "pivot_column": "quarter",
        "value_columns": ["order_count"],
        "filters": [{"field": "quarter", "operator": "=", "value": "Q3"}],
        "column_prefix": "订单_"
    }
    
    # 过滤Q3数据
    q3_data = quarterly_sales_data[quarterly_sales_data["quarter"] == "Q3"]
    
    result = pivot_step._perform_pivot(q3_data, config)
    
    # 验证结果结构
    assert isinstance(result, list)
    assert len(result) == 3  # 3个产品类别
    
    # 验证列名包含prefix
    for row in result:
        assert "订单_Q3" in row
        assert row["订单_Q3"] > 0

def test_quarterly_pivot_q4_complete(quarterly_sales_data):
    """测试Q4完整数据pivot - 应该有季度_前缀"""
    pivot_step = PivotStep()
    
    config = {
        "source": "quarterly_data",
        "index_columns": ["product_category"],
        "pivot_column": "quarter",
        "value_columns": ["total_sales_amount", "total_quantity", "order_count"],
        "filters": [{"field": "quarter", "operator": "=", "value": "Q4"}],
        "column_prefix": "季度_"
    }
    
    # 过滤Q4数据
    q4_data = quarterly_sales_data[quarterly_sales_data["quarter"] == "Q4"]
    
    result = pivot_step._perform_pivot(q4_data, config)
    
    # 验证结果结构
    assert isinstance(result, list)
    assert len(result) == 3  # 3个产品类别
    
    # 验证所有列名都包含prefix
    for row in result:
        assert "季度_Q4_total_sales_amount" in row
        assert "季度_Q4_total_quantity" in row
        assert "季度_Q4_order_count" in row
        assert row["季度_Q4_total_sales_amount"] > 0
        assert row["季度_Q4_total_quantity"] > 0
        assert row["季度_Q4_order_count"] > 0

def test_union_quarterly_results(quarterly_sales_data):
    """测试Union步骤合并所有季度结果"""
    pivot_step = PivotStep()
    union_step = UnionStep()
    
    # 准备4个pivot结果
    q1_config = {
        "source": "quarterly_data",
        "index_columns": ["product_category"],
        "pivot_column": "quarter",
        "value_columns": ["total_sales_amount"],
        "filters": [{"field": "quarter", "operator": "=", "value": "Q1"}],
        "column_prefix": "销售额_"
    }
    
    q2_config = {
        "source": "quarterly_data",
        "index_columns": ["product_category"],
        "pivot_column": "quarter",
        "value_columns": ["total_quantity"],
        "filters": [{"field": "quarter", "operator": "=", "value": "Q2"}],
        "column_prefix": "数量_"
    }
    
    q3_config = {
        "source": "quarterly_data",
        "index_columns": ["product_category"],
        "pivot_column": "quarter",
        "value_columns": ["order_count"],
        "filters": [{"field": "quarter", "operator": "=", "value": "Q3"}],
        "column_prefix": "订单_"
    }
    
    q4_config = {
        "source": "quarterly_data",
        "index_columns": ["product_category"],
        "pivot_column": "quarter",
        "value_columns": ["total_sales_amount", "total_quantity", "order_count"],
        "filters": [{"field": "quarter", "operator": "=", "value": "Q4"}],
        "column_prefix": "季度_"
    }
    
    # 执行各个pivot
    q1_data = quarterly_sales_data[quarterly_sales_data["quarter"] == "Q1"]
    q2_data = quarterly_sales_data[quarterly_sales_data["quarter"] == "Q2"]
    q3_data = quarterly_sales_data[quarterly_sales_data["quarter"] == "Q3"]
    q4_data = quarterly_sales_data[quarterly_sales_data["quarter"] == "Q4"]
    
    q1_result = pivot_step._perform_pivot(q1_data, q1_config)
    q2_result = pivot_step._perform_pivot(q2_data, q2_config)
    q3_result = pivot_step._perform_pivot(q3_data, q3_config)
    q4_result = pivot_step._perform_pivot(q4_data, q4_config)
    
    # 模拟Union配置
    union_config = {
        "sources": ["pivot_q1_sales", "pivot_q2_quantity", "pivot_q3_orders", "pivot_q4_complete"],
        "join_type": "LEFT"
    }
    
    # 创建数据上下文
    context = {
        "pivot_q1_sales": pd.DataFrame(q1_result),
        "pivot_q2_quantity": pd.DataFrame(q2_result),
        "pivot_q3_orders": pd.DataFrame(q3_result),
        "pivot_q4_complete": pd.DataFrame(q4_result)
    }
    
    result = union_step._perform_union(context, union_config)
    
    # 验证合并结果
    assert isinstance(result, list)
    assert len(result) == 3  # 3个产品类别
    
    # 验证每一行都包含所有前缀的列
    for row in result:
        # Q1销售额
        assert "销售额_Q1" in row
        # Q2数量
        assert "数量_Q2" in row
        # Q3订单数
        assert "订单_Q3" in row
        # Q4完整数据
        assert "季度_Q4_total_sales_amount" in row
        assert "季度_Q4_total_quantity" in row
        assert "季度_Q4_order_count" in row
        
        # 验证数据非空
        assert row["销售额_Q1"] is not None
        assert row["数量_Q2"] is not None
        assert row["订单_Q3"] is not None

def test_column_prefix_with_suffix():
    """测试同时使用column_prefix和column_suffix"""
    pivot_step = PivotStep()
    
    data = pd.DataFrame([
        {"category": "A", "quarter": "Q1", "sales": 1000},
        {"category": "B", "quarter": "Q1", "sales": 2000},
    ])
    
    config = {
        "index_columns": ["category"],
        "pivot_column": "quarter",
        "value_columns": ["sales"],
        "column_prefix": "前缀_",
        "column_suffix": "_后缀"
    }
    
    result = pivot_step._perform_pivot(data, config)
    
    # 验证前缀和后缀都应用了
    for row in result:
        assert "前缀_Q1_sales_后缀" in row

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
