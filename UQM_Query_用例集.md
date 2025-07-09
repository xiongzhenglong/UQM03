# UQM Query 用例集

## 1. 表结构简要说明

- **departments**（部门表）：`department_id`, `name`, `location`
- **employees**（员工表）：`employee_id`, `first_name`, `last_name`, `job_title`, `salary`, `department_id`, `is_active`, `hire_date`
- **products**（产品表）：`product_id`, `product_name`, `category`, `unit_price`, `supplier_id`, `discontinued`
- **orders**（订单主表）：`order_id`, `customer_id`, `employee_id`, `order_date`, `status`
- **order_items**（订单明细）：`order_item_id`, `order_id`, `product_id`, `quantity`, `unit_price`, `discount`
- **customers**（客户表）：`customer_id`, `customer_name`, `email`, `country`, `city`, `registration_date`, `customer_segment`
- **suppliers**（供应商表）：`supplier_id`, `supplier_name`, `country`
- **warehouses**（仓库表）：`warehouse_id`, `warehouse_name`, `location`
- **inventory**（库存表）：`inventory_id`, `product_id`, `warehouse_id`, `quantity_on_hand`

---

## 2. Query 用例

### 2.1 基础查询与计算字段

**业务场景**：查询所有在职员工的完整姓名、职位和所属部门名称。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "ActiveEmployeeInfo",
      "description": "查询在职员工基本信息",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "get_active_employees",
        "type": "query",
        "config": {
          "data_source": "employees",
          "joins": [
            {
              "type": "inner",
              "table": "departments",
              "on": "employees.department_id = departments.department_id"
            }
          ],
          "dimensions": [
            {
              "expression": "employees.job_title",
              "alias": "job_title"
            },
            {
              "expression": "departments.name",
              "alias": "department_name"
            }
          ],
          "calculated_fields": [
            {
              "expression": "CONCAT(employees.first_name, ' ', employees.last_name)",
              "alias": "full_name"
            }
          ],
          "filters": [
            {
              "field": "employees.is_active",
              "operator": "=",
              "value": true
            }
          ],
          "order_by": ["department_name", "full_name"]
        }
      }
    ],
    "output": "get_active_employees"
  }
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "job_title": "人事专员",
            "department_name": "人力资源部",
            "full_name": "刘 娜"
        },
        {
            "job_title": "HR经理",
            "department_name": "人力资源部",
            "full_name": "王 芳"
        },
        {
            "job_title": "高级软件工程师",
            "department_name": "信息技术部",
            "full_name": "Emily Jones"
        }
    ],
    "metadata": {
        "name": "ActiveEmployeeInfo",
        "description": "查询在职员工基本信息",
        "version": "1.0",
        "author": "",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.0069675445556640625,
        "row_count": 12,
        "cache_hit": false,
        "steps_executed": 1
    },
    "step_results": [
        {
            "step_name": "get_active_employees",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.004968404769897461,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.2 多表连接与聚合查询

**业务场景**：按客户统计其在2024年的总订单数和总消费金额。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "CustomerSpendingAnalysis",
      "description": "客户年度消费行为分析"
    },
    "steps": [
      {
        "name": "calculate_customer_spending",
        "type": "query",
        "config": {
          "data_source": "customers",
          "joins": [
            { "type": "inner", "table": "orders", "on": "customers.customer_id = orders.customer_id" },
            { "type": "inner", "table": "order_items", "on": "orders.order_id = order_items.order_id" }
          ],
          "dimensions": [
            { "expression": "customers.customer_name", "alias": "customer_name" }
          ],
          "calculated_fields": [
            {
              "expression": "COUNT(DISTINCT orders.order_id)",
              "alias": "total_orders"
            },
            {
              "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))",
              "alias": "total_spent"
            }
          ],
          "filters": [
            {
              "field": "YEAR(orders.order_date)",
              "operator": "=",
              "value": 2024
            }
          ],
          "group_by": ["customers.customer_name"],
          "order_by": [{"field": "total_spent", "direction": "desc"}]
        }
      }
    ],
    "output": "calculate_customer_spending"
  }
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "customer_name": "路飞",
            "total_orders": 1,
            "total_spent": "1570.3500"
        },
        {
            "customer_name": "élodie Dubois",
            "total_orders": 1,
            "total_spent": "1519.0500"
        },
        {
            "customer_name": "孙悟空",
            "total_orders": 2,
            "total_spent": "1134.0500"
        }
    ],
    "metadata": {
        "name": "CustomerSpendingAnalysis",
        "description": "客户年度消费行为分析",
        "version": "1.0",
        "author": "",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.01096487045288086,
        "row_count": 7,
        "cache_hit": false,
        "steps_executed": 1
    },
    "step_results": [
        {
            "step_name": "calculate_customer_spending",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 7,
            "execution_time": 0.01096487045288086,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.3 复杂嵌套过滤条件

**业务场景**：查询信息技术部的“软件工程师”或“高级软件工程师”，以及销售部的“销售经理”。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": { "name": "SpecificJobTitleQuery" },
    "steps": [
      {
        "name": "find_specific_employees",
        "type": "query",
        "config": {
          "data_source": "employees",
          "joins": [{ "type": "inner", "table": "departments", "on": "employees.department_id = departments.department_id" }],
          "dimensions": [
            "employees.first_name",
            "employees.last_name",
            "employees.job_title",
            "departments.name as department_name"
          ],
          "filters": [
            {
              "logical_operator": "OR",
              "conditions": [
                {
                  "logical_operator": "AND",
                  "conditions": [
                    { "field": "departments.name", "operator": "=", "value": "信息技术部" },
                    { "field": "employees.job_title", "operator": "IN", "value": ["软件工程师", "高级软件工程师"] }
                  ]
                },
                {
                  "logical_operator": "AND",
                  "conditions": [
                    { "field": "departments.name", "operator": "=", "value": "销售部" },
                    { "field": "employees.job_title", "operator": "=", "value": "销售经理" }
                  ]
                }
              ]
            }
          ]
        }
      }
    ],
    "output": "find_specific_employees"
  }
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "first_name": "张",
            "last_name": "伟",
            "job_title": "IT总监",
            "department_name": "信息技术部"
        },
        {
            "first_name": "王",
            "last_name": "芳",
            "job_title": "HR经理",
            "department_name": "人力资源部"
        },
        {
            "first_name": "李",
            "last_name": "强",
            "job_title": "软件工程师",
            "department_name": "信息技术部"
        },
        {
            "first_name": "刘",
            "last_name": "娜",
            "job_title": "人事专员",
            "department_name": "人力资源部"
        },
        {
            "first_name": "陈",
            "last_name": "军",
            "job_title": "销售总监",
            "department_name": "销售部"
        },
        {
            "first_name": "杨",
            "last_name": "静",
            "job_title": "销售代表",
            "department_name": "销售部"
        },
        {
            "first_name": "Ming",
            "last_name": "Li",
            "job_title": "高级财务分析师",
            "department_name": "财务部"
        },
        {
            "first_name": "Peter",
            "last_name": "Schmidt",
            "job_title": "欧洲区销售经理",
            "department_name": "欧洲销售部"
        },
        {
            "first_name": "Yuki",
            "last_name": "Tanaka",
            "job_title": "市场专员",
            "department_name": "市场营销部"
        },
        {
            "first_name": "Emily",
            "last_name": "Jones",
            "job_title": "高级软件工程师",
            "department_name": "信息技术部"
        },
        {
            "first_name": "Carlos",
            "last_name": "Garcia",
            "job_title": "运营经理",
            "department_name": "研发中心"
        },
        {
            "first_name": "Sophia",
            "last_name": "Müller",
            "job_title": "销售助理",
            "department_name": "欧洲销售部"
        }
    ],
    "metadata": {
        "name": "SpecificJobTitleQuery",
        "description": "",
        "version": "1.0",
        "author": "",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.0019989013671875,
        "row_count": 12,
        "cache_hit": false,
        "steps_executed": 1
    },
    "step_results": [
        {
            "step_name": "find_specific_employees",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.0019989013671875,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.4 参数化动态查询

**业务场景**：动态查询指定产品分类下，单价高于特定阈值的产品。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": { "name": "ParameterizedProductQuery" },
    "parameters": [
      { "name": "product_category", "type": "string", "default": "电子产品" },
      { "name": "min_unit_price", "type": "number", "default": 500 }
    ],
    "steps": [
      {
        "name": "get_products_by_param",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": ["product_name", "category", "unit_price"],
          "filters": [
            {
              "field": "category",
              "operator": "=",
              "value": "$product_category"
            },
            {
              "field": "unit_price",
              "operator": ">",
              "value": "$min_unit_price"
            }
          ],
          "order_by": [{"field": "unit_price", "direction": "desc"}]
        }
      }
    ],
    "output": "get_products_by_param"
  },
  "parameters": {
    "product_category": "电子产品",
    "min_unit_price": 600
  }
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "product_name": "蓝牙降噪耳机",
            "category": "电子产品",
            "unit_price": "1299.00"
        }
    ],
    "metadata": {
        "name": "ParameterizedProductQuery",
        "description": "",
        "version": "1.0",
        "author": "",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.005002498626708984,
        "row_count": 1,
        "cache_hit": false,
        "steps_executed": 1
    },
    "step_results": [
        {
            "step_name": "get_products_by_param",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 1,
            "execution_time": 0.005002498626708984,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.5 分组后筛选 (HAVING) 与排序

**业务场景**：按产品分类统计总销售额，并找出销售额超过1000元的分类，按销售额降序排列。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": { "name": "TopCategoryByRevenue" },
    "steps": [
      {
        "name": "calculate_category_revenue",
        "type": "query",
        "config": {
          "data_source": "products",
          "joins": [
            { "type": "inner", "table": "order_items", "on": "products.product_id = order_items.product_id" }
          ],
          "dimensions": [ "products.category" ],
          "calculated_fields": [
            {
              "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))",
              "alias": "total_revenue"
            }
          ],
          "group_by": [ "products.category" ],
          "having": [
            {
              "field": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))",
              "operator": ">",
              "value": 1000
            }
          ],
          "order_by": [{ "field": "total_revenue", "direction": "desc" }]
        }
      }
    ],
    "output": "calculate_category_revenue"
  }
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "category": "电子产品",
            "total_revenue": "5220.6000"
        },
        {
            "category": "家居用品",
            "total_revenue": "2318.0500"
        },
        {
            "category": "服装",
            "total_revenue": "1047.2000"
        },
        {
            "category": "图书",
            "total_revenue": "1032.0000"
        }
    ],
    "metadata": {
        "name": "TopCategoryByRevenue",
        "description": "",
        "version": "1.0",
        "author": "",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.0020661354064941406,
        "row_count": 4,
        "cache_hit": false,
        "steps_executed": 1
    },
    "step_results": [
        {
            "step_name": "calculate_category_revenue",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 4,
            "execution_time": 0.0020661354064941406,
            "cache_hit": false,
            "error": null
        }
    ]
}
```
---

### 2.6 窗口函数 (Window Functions)

**业务场景**：在每个部门内，根据员工的薪资进行排名。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": { "name": "EmployeeSalaryRanking" },
    "steps": [
      {
        "name": "rank_employee_salaries",
        "type": "query",
        "config": {
          "data_source": "employees",
          "joins": [{ "type": "inner", "table": "departments", "on": "employees.department_id = departments.department_id" }],
          "dimensions": [
            "employees.first_name",
            "employees.last_name",
            "departments.name as department_name",
            "employees.salary"
          ],
          "calculated_fields": [
            {
              "expression": "RANK() OVER (PARTITION BY departments.name ORDER BY salary DESC)",
              "alias": "salary_rank_in_department"
            }
          ],
          "filters": [{ "field": "employees.is_active", "operator": "=", "value": true }],
          "order_by": ["department_name", "salary_rank_in_department"]
        }
      }
    ],
    "output": "rank_employee_salaries"
  }
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "first_name": "王",
            "last_name": "芳",
            "department_name": "人力资源部",
            "salary": "25000.00",
            "salary_rank_in_department": 1
        },
        {
            "first_name": "刘",
            "last_name": "娜",
            "department_name": "人力资源部",
            "salary": "12000.00",
            "salary_rank_in_department": 2
        },
        {
            "first_name": "张",
            "last_name": "伟",
            "department_name": "信息技术部",
            "salary": "35000.00",
            "salary_rank_in_department": 1
        },
        {
            "first_name": "Emily",
            "last_name": "Jones",
            "department_name": "信息技术部",
            "salary": "22000.00",
            "salary_rank_in_department": 2
        },
        {
            "first_name": "李",
            "last_name": "强",
            "department_name": "信息技术部",
            "salary": "18000.00",
            "salary_rank_in_department": 3
        },
        {
            "first_name": "Yuki",
            "last_name": "Tanaka",
            "department_name": "市场营销部",
            "salary": "14000.00",
            "salary_rank_in_department": 1
        },
        {
            "first_name": "Peter",
            "last_name": "Schmidt",
            "department_name": "欧洲销售部",
            "salary": "42000.00",
            "salary_rank_in_department": 1
        },
        {
            "first_name": "Sophia",
            "last_name": "Müller",
            "department_name": "欧洲销售部",
            "salary": "16000.00",
            "salary_rank_in_department": 2
        },
        {
            "first_name": "Carlos",
            "last_name": "Garcia",
            "department_name": "研发中心",
            "salary": "31000.00",
            "salary_rank_in_department": 1
        },
        {
            "first_name": "Ming",
            "last_name": "Li",
            "department_name": "财务部",
            "salary": "28000.00",
            "salary_rank_in_department": 1
        },
        {
            "first_name": "陈",
            "last_name": "军",
            "department_name": "销售部",
            "salary": "38000.00",
            "salary_rank_in_department": 1
        },
        {
            "first_name": "杨",
            "last_name": "静",
            "department_name": "销售部",
            "salary": "15000.00",
            "salary_rank_in_department": 2
        }
    ],
    "metadata": {
        "name": "EmployeeSalaryRanking",
        "description": "",
        "version": "1.0",
        "author": "",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.0033600330352783203,
        "row_count": 12,
        "cache_hit": false,
        "steps_executed": 1
    },
    "step_results": [
        {
            "step_name": "rank_employee_salaries",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.0033600330352783203,
            "cache_hit": false,
            "error": null
        }
    ]
}
``` 