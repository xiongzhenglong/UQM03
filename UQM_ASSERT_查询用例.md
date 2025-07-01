# UQM ASSERT 查询用例集合

本文档包含基于电商数据库的各种 ASSERT 查询用例，展示如何使用断言来验证查询结果的正确性和数据完整性。

## 一、基础 ASSERT 验证

### 1.1 验证订单总数

**场景描述**: 验证系统中的订单总数是否符合预期

```json
{
  "metadata": {
    "name": "验证订单总数",
    "description": "确保订单表中的数据量在合理范围内",
    "version": "1.0",
    "author": "UQM Team"
  },
  "steps": [
    {
      "name": "count_orders",
      "type": "query",
      "config": {
        "data_source": "orders",
        "metrics": [
          {
            "name": "order_id",
            "aggregation": "COUNT",
            "alias": "total_orders"
          }
        ]
      }
    },
    {
      "name": "assert_order_count",
      "type": "assert",
      "config": {
        "source": "count_orders",
        "assertions": [
          {
            "type": "range",
            "field": "total_orders",
            "min": 100,
            "max": 10000,
            "message": "订单数量应在100-10000之间"
          }
        ]
      }
    }
  ],
  "output": "count_orders"
}
```

### 1.2 验证产品价格合理性

**场景描述**: 验证产品价格是否在合理范围内

```json
{
  "metadata": {
    "name": "验证产品价格合理性",
    "description": "确保产品价格数据的有效性",
    "version": "1.0"
  },
  "steps": [
    {
      "name": "product_price_stats",
      "type": "query",
      "config": {
        "data_source": "products",
        "metrics": [
          {
            "name": "unit_price",
            "aggregation": "MIN",
            "alias": "min_price"
          },
          {
            "name": "unit_price",
            "aggregation": "MAX",
            "alias": "max_price"
          },
          {
            "name": "unit_price",
            "aggregation": "AVG",
            "alias": "avg_price"
          },
          {
            "name": "product_id",
            "aggregation": "COUNT",
            "alias": "total_products"
          }
        ]
      }
    },
    {
      "name": "assert_price_validity",
      "type": "assert",
      "config": {
        "source": "product_price_stats",
        "assertions": [
          {
            "type": "range",
            "field": "min_price",
            "min": 0.01,
            "message": "产品最低价格必须大于0"
          },
          {
            "type": "range",
            "field": "max_price",
            "max": 100000,
            "message": "产品最高价格不能超过100000元"
          },
          {
            "type": "range",
            "field": "avg_price",
            "min": 10,
            "max": 5000,
            "message": "产品平均价格应在10-5000元之间"
          }
        ]
      }
    }
  ],
  "output": "product_price_stats"
}
```

## 二、数据完整性验证

### 2.1 验证客户邮箱唯一性

**场景描述**: 验证客户邮箱地址的唯一性

```json
{
  "metadata": {
    "name": "验证客户邮箱唯一性",
    "description": "确保客户邮箱地址没有重复",
    "version": "1.0"
  },
  "steps": [
    {
      "name": "customer_email_check",
      "type": "query",
      "config": {
        "data_source": "customers",
        "dimensions": ["email"],
        "metrics": [
          {
            "name": "customer_id",
            "aggregation": "COUNT",
            "alias": "email_count"
          }
        ],
        "group_by": ["email"],
        "having": [
          {
            "field": "email_count",
            "operator": ">",
            "value": 1
          }
        ]
      }
    },
    {
      "name": "assert_email_uniqueness",
      "type": "assert",
      "config": {
        "source": "customer_email_check",
        "assertions": [
          {
            "type": "row_count",  
            "expected": 0,
            "message": "发现重复的客户邮箱地址"
          }
        ]
      }
    }
  ],
  "output": "customer_email_check"
}
```

### 2.2 验证订单状态完整性

**场景描述**: 验证订单状态的完整性和一致性

```json
{
  "metadata": {
    "name": "验证订单状态完整性",
    "description": "确保订单状态符合业务逻辑",
    "version": "1.0"
  },
  "steps": [
    {
      "name": "order_status_distribution",
      "type": "query",
      "config": {
        "data_source": "orders",
        "dimensions": ["status"],
        "metrics": [
          {
            "name": "order_id",
            "aggregation": "COUNT",
            "alias": "status_count"
          }
        ],
        "group_by": ["status"]
      }
    },
    {
      "name": "assert_status_validity",
      "type": "assert",
      "config": {
        "source": "order_status_distribution",
        "assertions": [
          {
            "type": "value_in",
            "field": "status",
            "values": ["待处理", "处理中", "已发货", "已完成", "已取消"],
            "message": "发现无效的订单状态"
          }
        ]
      }
    },
    {
      "name": "pending_orders_check",
      "type": "query",
      "config": {
        "data_source": "orders",
        "metrics": [
          {
            "name": "order_id",
            "aggregation": "COUNT",
            "alias": "pending_count"
          }
        ],
        "filters": [
          {
            "field": "status",
            "operator": "=",
            "value": "待处理"
          },
          {
            "field": "order_date",
            "operator": "<",
            "value": "$weekAgo"
          }
        ]
      }
    },
    {
      "name": "assert_pending_orders",
      "type": "assert",
      "config": {
        "source": "pending_orders_check",
        "assertions": [
          {
            "type": "range",
            "field": "pending_count",
            "max": 10,
            "message": "超过一周的待处理订单过多，需要及时处理"
          }
        ]
      }
    }
  ],
  "output": "order_status_distribution",
  "parameters": {
    "weekAgo": "2025-06-23 00:00:00"
  }
}
```

## 三、业务逻辑验证

### 3.1 验证订单金额一致性

**场景描述**: 验证订单总金额与订单明细金额的一致性

```json
{
  "uqm": {
  "metadata": {
    "name": "验证订单金额一致性",
    "description": "确保订单表中的总金额与订单明细计算结果一致",
    "version": "1.0"
  },
  "steps": [
    {
      "name": "order_total_comparison",
      "type": "query",
      "config": {
        "data_source": "orders",
        "dimensions": ["order_id"],
        "joins": [
          {
            "type": "INNER",
            "table": "order_items",
            "on": {
              "left": "orders.order_id",
              "right": "order_items.order_id",
              "operator": "="
            }
          }
        ],
        "calculated_fields": [
          {
            "name": "calculated_total",
            "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))"
          },
          {
            "name": "order_total_with_shipping",
            "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount)) + MAX(orders.shipping_fee)"
          },
          {
            "name": "amount_difference",
            "expression": "ABS(MAX(orders.shipping_fee))"
          }
        ],
        "group_by": ["order_id"]
      }
    },
    {
      "name": "assert_amount_consistency",
      "type": "assert",
      "config": {
        "source": "order_total_comparison",
        "assertions": [
          {
            "type": "range",
            "field": "amount_difference",
            "max": 100.0,
            "message": "订单金额与明细计算结果不一致"
          },
          {
            "type": "range",
            "field": "calculated_total",
            "min": 0,
            "message": "订单明细计算总额必须大于0"
          },
          {
            "type": "range",
            "field": "order_total_with_shipping",
            "min": 0,
            "message": "订单总额（含运费）必须大于0"
          }
        ]
      }
    }
  ],
  "output": "order_total_comparison"
},
  "parameters": {
    "maxLowStockCount": 20
  },
  "options": {}
}
```

### 3.2 验证库存警告机制

**场景描述**: 验证产品库存是否需要补货

```json
{
  "uqm": {
    "metadata": {
      "name": "验证库存警告机制",
      "description": "检查低库存产品并验证库存管理策略",
      "version": "1.0"
    },
  "steps": [
    {
      "name": "low_stock_products",
      "type": "query",
      "config": {
        "data_source": "products",
        "dimensions": ["product_id", "product_name", "category"],
        "joins": [
          {
            "type": "LEFT",
            "table": "inventory",
            "on": {
              "left": "products.product_id",
              "right": "inventory.product_id",
              "operator": "="
            }
          }
        ],
        "calculated_fields": [
          {
            "name": "total_stock",
            "expression": "COALESCE(SUM(inventory.quantity_on_hand), 0)"
          },
          {
            "name": "stock_status",
            "expression": "CASE WHEN COALESCE(SUM(inventory.quantity_on_hand), 0) = 0 THEN 'out_of_stock' WHEN COALESCE(SUM(inventory.quantity_on_hand), 0) <= 10 THEN 'low' WHEN COALESCE(SUM(inventory.quantity_on_hand), 0) <= 50 THEN 'medium' ELSE 'sufficient' END"
          }
        ],
        "filters": [
          {
            "field": "products.discontinued",
            "operator": "=",
            "value": false
          }
        ],
        "group_by": ["products.product_id", "products.product_name", "products.category"]
      }
    },
    {
      "name": "stock_summary",
      "type": "query",
      "config": {
        "data_source": "products",
        "joins": [
          {
            "type": "LEFT",
            "table": "inventory",
            "on": {
              "left": "products.product_id",
              "right": "inventory.product_id",
              "operator": "="
            }
          }
        ],
        "calculated_fields": [
          {
            "name": "total_products",
            "expression": "COUNT(DISTINCT products.product_id)"
          },
          {
            "name": "low_stock_count",
            "expression": "COUNT(CASE WHEN COALESCE(inventory.quantity_on_hand, 0) <= 10 AND COALESCE(inventory.quantity_on_hand, 0) > 0 THEN 1 END)"
          },
          {
            "name": "out_of_stock_count", 
            "expression": "COUNT(CASE WHEN COALESCE(inventory.quantity_on_hand, 0) = 0 THEN 1 END)"
          }
        ],
        "filters": [
          {
            "field": "products.discontinued",
            "operator": "=",
            "value": false
          }
        ]
      }
    },
    {
      "name": "assert_stock_management",
      "type": "assert",
      "config": {
        "source": "stock_summary",
        "assertions": [
          {
            "type": "range",
            "field": "out_of_stock_count",
            "max": 5,
            "message": "缺货产品数量过多，需要紧急补货"
          },
          {
            "type": "range",
            "field": "low_stock_count",
            "max": "$maxLowStockCount",
            "message": "低库存产品数量超过预警阈值"
          }
        ]
      }
    }
  ],
  "output": "low_stock_products"
  },
  "parameters": {
    "maxLowStockCount": 20
  },
  "options": {}
}
```

## 四、数据质量验证

### 4.1 验证数据完整性

**场景描述**: 验证关键字段的数据完整性

```json
{
  "uqm": {
    "metadata": {
      "name": "验证数据完整性",
      "description": "检查关键字段的空值和数据质量",
      "version": "1.0"
    },
  "steps": [
    {
      "name": "data_quality_check",
      "type": "query",
      "config": {
        "data_source": "customers",
        "calculated_fields": [
          {
            "name": "total_customers",
            "expression": "COUNT(customers.customer_id)"
          },
          {
            "name": "null_email_count",
            "expression": "SUM(CASE WHEN customers.email IS NULL OR customers.email = '' THEN 1 ELSE 0 END)"
          },
          {
            "name": "null_name_count",
            "expression": "SUM(CASE WHEN customers.customer_name IS NULL OR customers.customer_name = '' THEN 1 ELSE 0 END)"
          },
          {
            "name": "invalid_email_count",
            "expression": "SUM(CASE WHEN customers.email NOT LIKE '%@%' THEN 1 ELSE 0 END)"
          }
        ]
      }
    },
    {
      "name": "assert_data_quality",
      "type": "assert",
      "config": {
        "source": "data_quality_check",
        "assertions": [
          {
            "type": "custom",
            "condition": "null_email_count == 0",
            "message": "发现客户邮箱字段为空"
          },
          {
            "type": "custom",
            "condition": "null_name_count == 0", 
            "message": "发现客户姓名字段为空"
          },
          {
            "type": "custom",
            "condition": "invalid_email_count == 0",
            "message": "发现无效的邮箱格式"
          }
        ]
      }
    }
  ],
  "output": "data_quality_check"
  },
  "parameters": {},
  "options": {}
}
```

### 4.2 验证日期逻辑合理性

**场景描述**: 验证订单日期的逻辑合理性

```json
{
  "uqm": {
    "metadata": {
      "name": "验证日期逻辑合理性",
      "description": "检查订单日期等时间逻辑",
      "version": "1.0"
    },
  "steps": [
    {
      "name": "date_logic_check",
      "type": "query",
      "config": {
        "data_source": "orders",
        "dimensions": ["order_id", "order_date", "status"],
        "calculated_fields": [
          {
            "name": "future_order_date",
            "expression": "CASE WHEN orders.order_date > CURRENT_DATE THEN 1 ELSE 0 END"
          },
          {
            "name": "very_old_order",
            "expression": "CASE WHEN orders.order_date < DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR) THEN 1 ELSE 0 END"
          }
        ]
      }
    },
    {
      "name": "date_logic_summary",
      "type": "query",
      "config": {
        "data_source": "orders",
        "calculated_fields": [
          {
            "name": "total_orders",
            "expression": "COUNT(orders.order_id)"
          },
          {
            "name": "future_orders_count",
            "expression": "SUM(CASE WHEN orders.order_date > CURRENT_DATE THEN 1 ELSE 0 END)"
          },
          {
            "name": "very_old_orders_count",
            "expression": "SUM(CASE WHEN orders.order_date < DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR) THEN 1 ELSE 0 END)"
          }
        ]
      }
    },
    {
      "name": "assert_date_logic",
      "type": "assert",
      "config": {
        "source": "date_logic_summary",
        "assertions": [
          {
            "type": "custom",
            "condition": "future_orders_count == 0",
            "message": "发现订单日期为未来时间的异常数据"
          }
        ]
      }
    }
  ],
  "output": "date_logic_check"
  },
  "parameters": {},
  "options": {}
}
```

## 五、性能验证

### 5.1 验证查询性能

**场景描述**: 验证关键查询的执行性能

```json
{
  "uqm": {
    "metadata": {
      "name": "验证查询性能",
      "description": "监控查询执行时间，确保性能达标",
      "version": "1.0"
    },
  "steps": [
    {
      "name": "performance_test_query",
      "type": "query",
      "config": {
        "data_source": "orders",
        "dimensions": ["customer_id"],
        "joins": [
          {
            "type": "INNER",
            "table": "customers",
            "on": {
              "left": "orders.customer_id",
              "right": "customers.customer_id",
              "operator": "="
            }
          }
        ],
        "calculated_fields": [
          {
            "name": "order_count",
            "expression": "COUNT(orders.order_id)"
          },
          {
            "name": "total_spent",
            "expression": "SUM(orders.shipping_fee)"
          }
        ],
        "group_by": ["orders.customer_id"],
        "order_by": [
          {
            "field": "total_spent",
            "direction": "DESC"
          }
        ],
        "limit": 1000
      }
    },
    {
      "name": "assert_performance",
      "type": "assert",
      "config": {
        "source": "performance_test_query",
        "assertions": [
          {
            "type": "custom",
            "condition": "execution_time <= 5000",
            "message": "查询执行时间超过5秒，需要优化"
          },
          {
            "type": "custom",
            "condition": "memory_usage <= 100",
            "message": "查询内存使用超过100MB"
          }
        ]
      }
    }
  ],
  "output": "performance_test_query"
  },
  "parameters": {},
  "options": {}
}
```

## 六、综合验证场景

### 6.1 月度数据一致性验证

**场景描述**: 综合验证月度数据的一致性和完整性

```json
{
  "uqm": {
    "metadata": {
      "name": "月度数据一致性验证",
      "description": "综合验证月度订单、收入、库存等数据的一致性",
      "version": "1.0"
    },
  "steps": [
    {
      "name": "monthly_orders_summary",
      "type": "query",
      "config": {
        "data_source": "orders",
        "calculated_fields": [
          {
            "name": "monthly_orders",
            "expression": "COUNT(orders.order_id)"
          },
          {
            "name": "monthly_revenue",
            "expression": "SUM(orders.shipping_fee)"
          }
        ],
        "filters": [
          {
            "field": "orders.order_date",
            "operator": ">=",
            "value": "$monthStart"
          },
          {
            "field": "orders.order_date",
            "operator": "<=",
            "value": "$monthEnd"
          }
        ]
      }
    },
    {
      "name": "monthly_items_summary",
      "type": "query",
      "config": {
        "data_source": "order_items",
        "joins": [
          {
            "type": "INNER",
            "table": "orders",
            "on": {
              "left": "order_items.order_id",
              "right": "orders.order_id",
              "operator": "="
            }
          }
        ],
        "calculated_fields": [
          {
            "name": "items_revenue",
            "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))"
          }
        ],
        "filters": [
          {
            "field": "orders.order_date",
            "operator": ">=",
            "value": "$monthStart"
          },
          {
            "field": "orders.order_date",
            "operator": "<=",
            "value": "$monthEnd"
          }
        ]
      }
    },
    {
      "name": "revenue_comparison",
      "type": "query",
      "config": {
        "data_source": "monthly_orders_summary",
        "joins": [
          {
            "type": "CROSS",
            "table": "monthly_items_summary"
          }
        ],
        "calculated_fields": [
          {
            "name": "revenue_difference",
            "expression": "ABS(monthly_revenue - items_revenue)"
          }
        ]
      }
    },
    {
      "name": "assert_monthly_consistency",
      "type": "assert",
      "config": {
        "source": "revenue_comparison",
        "assertions": [
          {
            "type": "range",
            "field": "monthly_orders",
            "min": 50,
            "message": "月度订单数量过低"
          },
          {
            "type": "range",
            "field": "monthly_revenue",
            "min": 10000,
            "message": "月度收入过低"
          },
          {
            "type": "range",
            "field": "revenue_difference",
            "max": 100,
            "message": "订单收入与明细收入不一致"
          }
        ]
      }
    }
  ],
  "output": "revenue_comparison"
  },
  "parameters": {
    "monthStart": "2025-06-01 00:00:00",
    "monthEnd": "2025-06-30 23:59:59"
  },
  "options": {}
}
```

## 七、Assert 语法说明

### 7.1 Assert 基本语法

```json
{
  "name": "assert_step_name",
  "type": "assert",
  "config": {
    "source": "source_step_name",
    "assertions": [
      {
        "type": "range|row_count|not_null|unique|regex|custom|column_exists|data_type|value_in|relationship",
        "field": "field_name",
        "min": "min_value",
        "max": "max_value", 
        "message": "错误消息"
      }
    ]
  }
}
```

### 7.2 支持的断言类型

- **数值断言**: `range` (范围检查)
- **行数断言**: `row_count` (检查结果集行数)
- **空值断言**: `not_null` (检查字段非空)
- **唯一性断言**: `unique` (检查字段唯一性)
- **模式匹配**: `regex` (正则表达式匹配)
- **自定义断言**: `custom` (自定义条件表达式)
- **列存在**: `column_exists` (检查列是否存在)
- **数据类型**: `data_type` (检查数据类型)
- **值范围**: `value_in` (检查值是否在指定集合中)
- **关系检查**: `relationship` (检查数据关系)

### 7.3 断言配置示例

#### Range 断言
```json
{
  "type": "range",
  "field": "price",
  "min": 0,
  "max": 10000,
  "message": "价格应在0-10000之间"
}
```

#### Row Count 断言
```json
{
  "type": "row_count",
  "expected": 100,
  "message": "期望100行数据"
}
```

#### Not Null 断言
```json
{
  "type": "not_null",
  "columns": ["name", "email"],
  "message": "姓名和邮箱不能为空"
}
```

#### Custom 断言
```json
{
  "type": "custom",
  "condition": "revenue > 1000 AND profit_margin > 0.1",
  "message": "收入应大于1000且利润率大于10%"
}
```

### 7.4 断言配置选项

```json
{
  "name": "assert_step",
  "type": "assert", 
  "config": {
    "source": "data_source",
    "assertions": [
      {
        "type": "range",
        "field": "amount",
        "min": 0,
        "max": 10000,
        "message": "金额超出范围"
      }
    ],
    "on_failure": "error",  // error|warning|ignore
    "stop_on_first_failure": true
  }
}
```

## 八、最佳实践

### 8.1 断言设计原则

1. **明确性**: 每个断言应该验证一个明确的业务规则
2. **可读性**: 错误消息应该清晰地说明问题
3. **可维护性**: 断言阈值应该通过参数化配置
4. **完整性**: 覆盖关键的数据质量检查点

### 8.2 错误处理策略

```json
{
  "options": {
    "assert_behavior": "fail_fast",
    "error_logging": true,
    "notification_on_failure": true,
    "retry_on_failure": false
  }
}
```

### 8.3 监控集成

```json
{
  "metadata": {
    "monitoring": {
      "alert_level": "error",
      "notification_channels": ["email", "slack"],
      "schedule": "0 0 * * *"
    }
  }
}
```

---

*注意：在实际使用时，请根据具体的数据结构和业务需求调整断言条件和阈值。建议在生产环境中逐步实施这些验证规则，并根据实际情况调整参数。*
