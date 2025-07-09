# UQM Assert 用例集

## 1. 表结构简要说明

- **departments**（部门表）：`department_id`, `name`, `location`
- **employees**（员工表）：`employee_id`, `first_name`, `last_name`, `job_title`, `salary`, `department_id`, `is_active`, `hire_date`, `phone_number`
- **products**（产品表）：`product_id`, `product_name`, `category`, `unit_price`, `supplier_id`, `discontinued`
- **orders**（订单主表）：`order_id`, `customer_id`, `employee_id`, `order_date`, `status`
- **order_items**（订单明细）：`order_item_id`, `order_id`, `product_id`, `quantity`, `unit_price`, `discount`
- **customers**（客户表）：`customer_id`, `customer_name`, `email`, `country`, `city`, `registration_date`, `customer_segment`

---

## 2. 典型 Assert 用例

### 用例1：验证活跃员工数量 (`row_count`)

**业务场景**：确保公司正常的运作，系统中的活跃员工数量（`is_active` = true）必须维持在一个健康的水平，例如至少多于10人。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "AssertActiveEmployeeCount",
      "description": "验证活跃员工数量至少为10人"
    },
    "steps": [
      {
        "name": "get_active_employees",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": [{"expression": "employee_id"}, {"expression": "first_name"}, {"expression": "last_name"}],
          "filters": [{"field": "is_active", "operator": "=", "value": true}]
        }
      },
      {
        "name": "assert_employee_count",
        "type": "assert",
        "config": {
          "source": "get_active_employees",
          "on_failure": "error",
          "assertions": [
            {
              "type": "row_count",
              "min": 10,
              "message": "活跃员工数量必须至少为10人"
            }
          ]
        }
      }
    ],
    "output": "get_active_employees"
  }
}
```

**预期输出（断言通过）：**
如果活跃员工数大于等于10，流程成功，输出员工数据。

**预期输出（断言失败）：**
如果活跃员工数小于10，流程将抛出`ExecutionError`。
```json
{
    "success": false,
    "error": {
        "code": "EXECUTION_ERROR",
        "message": "断言检查失败:\\n- 类型: row_count, 状态: FAILED, 消息: 活跃员工数量必须至少为10人, 详情: {'min': 10, 'actual': 9}"
    }
}
```

---

### 用例2：验证产品价格有效性 (`not_null`, `range`)

**业务场景**：所有上架销售的产品（`discontinued` = false）必须有合法的价格，即价格字段不能为空，且必须大于0。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "AssertProductPriceValidity",
      "description": "验证在售产品的价格非空且大于0"
    },
    "steps": [
      {
        "name": "get_active_products",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": [{"expression": "product_id"}, {"expression": "product_name"}, {"expression": "unit_price"}],
          "filters": [{"field": "discontinued", "operator": "=", "value": false}]
        }
      },
      {
        "name": "assert_price_validity",
        "type": "assert",
        "config": {
          "source": "get_active_products",
          "assertions": [
            {
              "type": "not_null",
              "columns": ["unit_price"],
              "message": "产品单价（unit_price）不能为空"
            },
            {
              "type": "range",
              "column": "unit_price",
              "min": 0.01,
              "message": "产品单价（unit_price）必须大于0"
            }
          ]
        }
      }
    ],
    "output": "get_active_products"
  }
}
```
**预期输出（断言失败）：**
如果存在价格为空或小于等于0的产品，将报告失败。
```json
{
    "success": false,
    "error": {
        "code": "EXECUTION_ERROR",
        "message": "断言检查失败:\\n- 类型: not_null, 状态: FAILED, 消息: 产品单价（unit_price）不能为空, 详情: {'column': 'unit_price', 'null_count': 1, 'sample_null_rows': [{'product_id': 101, 'product_name': '问题产品A', 'unit_price': null}]}\\n- 类型: range, 状态: FAILED, 消息: 产品单价（unit_price）必须大于0, 详情: {'column': 'unit_price', 'invalid_count': 1, 'sample_invalid_rows': [{'product_id': 102, 'product_name': '问题产品B', 'unit_price': 0}]}"
    }
}
```

---

### 用例3：验证客户邮箱唯一性 (`unique`)

**业务场景**：确保每个客户都有一个唯一的电子邮箱地址，这对于营销和客户关系管理至关重要。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "AssertCustomerEmailUniqueness",
      "description": "验证客户邮箱地址的唯一性"
    },
    "steps": [
      {
        "name": "get_all_customers",
        "type": "query",
        "config": {
          "data_source": "customers",
          "dimensions": [{"expression": "customer_id"}, {"expression": "email"}]
        }
      },
      {
        "name": "assert_email_uniqueness",
        "type": "assert",
        "config": {
          "source": "get_all_customers",
          "assertions": [
            {
              "type": "unique",
              "columns": ["email"],
              "message": "客户邮箱（email）必须是唯一的"
            }
          ]
        }
      }
    ],
    "output": "get_all_customers"
  }
}
```
**预期输出（断言失败）：**
如果存在重复的邮箱地址，将报告失败并显示重复项。
```json
{
    "success": false,
    "error": {
        "code": "EXECUTION_ERROR",
        "message": "断言检查失败:\\n- 类型: unique, 状态: FAILED, 消息: 客户邮箱（email）必须是唯一的, 详情: {'columns': ['email'], 'duplicate_count': 1, 'sample_duplicates': [{'email': 'duplicate@example.com', 'count': 2}]}"
    }
}
```

---

### 用例4：验证订单状态合法性 (`value_in`)

**业务场景**：订单状态必须是预定义集合中的一个，以保证订单流程的正确性。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "AssertOrderStatusValidity",
      "description": "验证订单状态是否在预期的枚举值内"
    },
    "steps": [
      {
        "name": "get_all_orders",
        "type": "query",
        "config": {
          "data_source": "orders",
          "dimensions": [{"expression": "order_id"}, {"expression": "status"}]
        }
      },
      {
        "name": "assert_order_status",
        "type": "assert",
        "config": {
          "source": "get_all_orders",
          "assertions": [
            {
              "type": "value_in",
              "column": "status",
              "allowed_values": ["待处理", "处理中", "已发货", "已完成", "已取消"],
              "message": "订单状态（status）值无效"
            }
          ]
        }
      }
    ],
    "output": "get_all_orders"
  }
}
```

**预期输出（断言失败）：**
如果存在非法状态值，将报告失败并显示非法值样本。
```json
{
    "success": false,
    "error": {
        "code": "EXECUTION_ERROR",
        "message": "断言检查失败:\\n- 类型: value_in, 状态: FAILED, 消息: 订单状态（status）值无效, 详情: {'column': 'status', 'invalid_count': 1, 'sample_invalid_values': ['已发货 ']}"
    }
}
```

---

### 用例5：验证员工电话号码格式 (`regex`)

**业务场景**：为确保联络畅通，需要对特定员工（ID为6）的电话号码（`phone_number`）进行格式校验，确保其符合中国大陆的11位手机号格式。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "AssertSpecificEmployeePhoneNumberFormat",
      "description": "验证指定员工(employee_id=6)的手机号码格式"
    },
    "steps": [
      {
        "name": "get_employees_with_phone",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": [{"expression": "employee_id"}, {"expression": "phone_number"}],
          "filters": [
            {"field": "phone_number", "operator": "is not null"},
            {"field": "employee_id", "operator": "=", "value": 6}
          ]
        }
      },
      {
        "name": "assert_phone_format",
        "type": "assert",
        "config": {
          "source": "get_employees_with_phone",
          "assertions": [
            {
              "type": "regex",
              "column": "phone_number",
              "pattern": "^1[3-9]\\d{9}$",
              "message": "电话号码（phone_number）必须是有效的11位手机号"
            }
          ]
        }
      }
    ],
    "output": "get_employees_with_phone"
  }
}
```
**预期输出（断言失败）：**
如果存在格式不匹配的电话号码，将报告失败并显示不匹配的样本。
```json
{
    "success": false,
    "error": {
        "code": "EXECUTION_ERROR",
        "message": "断言检查失败:\\n- 类型: regex, 状态: FAILED, 消息: 电话号码（phone_number）必须是有效的11位手机号, 详情: {'column': 'phone_number', 'pattern': '^1[3-9]\\d{9}$', 'mismatch_count': 1, 'sample_mismatched_rows': [{'employee_id': 10, 'phone_number': '12345'}]}"
    }
}
```

---

### 用例6：验证订单折扣合理性 (`custom`)

**业务场景**：为了控制成本，订单明细中的折扣率（`discount`）不能过高，例如不能超过50%。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "AssertOrderItemDiscountRate",
      "description": "验证订单折扣率是否低于50%"
    },
    "steps": [
      {
        "name": "get_order_items",
        "type": "query",
        "config": {
          "data_source": "order_items",
          "dimensions": [{"expression": "order_item_id"}, {"expression": "discount"}]
        }
      },
      {
        "name": "assert_discount_rate",
        "type": "assert",
        "config": {
          "source": "get_order_items",
          "assertions": [
            {
              "type": "custom",
              "expression": "discount < 0.5",
              "message": "订单折扣率（discount）必须小于50%"
            }
          ]
        }
      }
    ],
    "output": "get_order_items"
  }
}
```
**预期输出（断言失败）：**
如果存在折扣率大于或等于50%的订单项，将报告失败。
```json
{
    "success": false,
    "error": {
        "code": "EXECUTION_ERROR",
        "message": "断言检查失败:\\n- 类型: custom, 状态: FAILED, 消息: 订单折扣率（discount）必须小于50%, 详情: {'expression': \"discount < 0.5\", 'failed_count': 1, 'sample_failed_rows': [{'order_item_id': 25, 'discount': 0.6}]}"
    }
}
``` 