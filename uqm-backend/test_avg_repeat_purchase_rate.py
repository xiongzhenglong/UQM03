import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.steps.query_step import QueryStep

# 模拟 customer_repeat_purchase_flag 步骤的输出
customer_repeat_purchase_flag_data = [
    {"coc.customer_id": 1, "coc_total_orders": 3.0, "cfod_first_order_date": "2024-01-20T10:30:00", "is_repeat_purchaser": 1},
    {"coc.customer_id": 2, "coc_total_orders": 2.0, "cfod_first_order_date": "2024-02-15T14:00:00", "is_repeat_purchaser": 1},
    {"coc.customer_id": 3, "coc_total_orders": 1.0, "cfod_first_order_date": "2024-03-10T09:00:00", "is_repeat_purchaser": 0},
]

# average_repeat_purchase_rate 步骤配置
avg_step_config = {
    "data_source": "customer_repeat_purchase_flag crpf",
    "metrics": [
        {
            "name": "crpf.is_repeat_purchaser",
            "aggregation": "AVG",
            "alias": "average_repeat_purchase_rate"
        }
    ],
    "calculated_fields": [
        {
            "alias": "average_repeat_purchase_rate",
            "expression": "AVG(crpf.is_repeat_purchaser)"
        }
    ]
}

def test_avg_repeat_purchase_rate():
    step = QueryStep(avg_step_config)
    # 直接调用本地处理逻辑
    result = step._process_step_data(customer_repeat_purchase_flag_data)
    print("本地聚合结果:", result)
    assert result and result[0]["average_repeat_purchase_rate"] == (1+1+0)/3, "平均复购率计算错误"

if __name__ == "__main__":
    test_avg_repeat_purchase_rate()
    print("✅ 本地聚合AVG(crpf.is_repeat_purchaser)测试通过") 