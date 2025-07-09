# UQM Pivot 用例集

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

## 2. 典型 Pivot 用例

### 2.1 产品销量按月透视分析（基础用法）

**业务场景**：分析各产品在不同月份的销量情况，将长表数据按月份列透视为宽表。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "ProductMonthlySalesAnalysis",
      "description": "产品销量按月透视分析",
      "version": "1.0",
      "author": "UQM Expert",
      "tags": ["pivot", "sales", "monthly", "product"]
    },
    "parameters": [],
    "steps": [
      {
        "name": "get_sales_data",
        "type": "query",
        "config": {
          "data_source": "orders",
          "joins": [
            {
              "type": "inner",
              "table": "order_items",
              "on": "orders.order_id = order_items.order_id"
            },
            {
              "type": "inner", 
              "table": "products",
              "on": "order_items.product_id = products.product_id"
            }
          ],
          "dimensions": [
            {
              "expression": "products.product_name",
              "alias": "product_name"
            },
            {
              "expression": "DATE_FORMAT(orders.order_date, '%Y-%m')",
              "alias": "order_month"
            }
          ],
          "calculated_fields": [
            {
              "expression": "SUM(order_items.quantity)",
              "alias": "total_quantity"
            }
          ],
          "group_by": [
            "products.product_name",
            "DATE_FORMAT(orders.order_date, '%Y-%m')"
          ],
          "filters": [
            {
              "field": "orders.status",
              "operator": "IN",
              "value": ["已完成", "已发货"]
            }
          ]
        }
      },
      {
        "name": "pivot_monthly_sales",
        "type": "pivot",
        "config": {
          "source": "get_sales_data",
          "index": "product_name",
          "columns": "order_month",
          "values": "total_quantity",
          "agg_func": "sum",
          "fill_value": 0
        }
      }
    ],
    "output": "pivot_monthly_sales"
  },
  "parameters": {},
  "options": {}
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "product_name": "日式和风床品四件套",
            "2024-01": 0.0,
            "2024-02": 0.0,
            "2024-05": 0.0,
            "2024-07": 1.0,
            "2024-11": 0.0,
            "2024-12": 0.0,
            "2025-03": 0.0
        },
        {
            "product_name": "智能升降学习桌",
            "2024-01": 0.0,
            "2024-02": 0.0,
            "2024-05": 0.0,
            "2024-07": 0.0,
            "2024-11": 1.0,
            "2024-12": 0.0,
            "2025-03": 0.0
        },
        {
            "product_name": "机械键盘",
            "2024-01": 1.0,
            "2024-02": 0.0,
            "2024-05": 0.0,
            "2024-07": 0.0,
            "2024-11": 0.0,
            "2024-12": 0.0,
            "2025-03": 0.0
        },
        {
            "product_name": "潮流印花T恤",
            "2024-01": 0.0,
            "2024-02": 2.0,
            "2024-05": 0.0,
            "2024-07": 0.0,
            "2024-11": 0.0,
            "2024-12": 5.0,
            "2025-03": 0.0
        },
        {
            "product_name": "蓝牙降噪耳机",
            "2024-01": 0.0,
            "2024-02": 0.0,
            "2024-05": 1.0,
            "2024-07": 0.0,
            "2024-11": 0.0,
            "2024-12": 0.0,
            "2025-03": 0.0
        },
        {
            "product_name": "超高速SSD 1TB",
            "2024-01": 1.0,
            "2024-02": 0.0,
            "2024-05": 0.0,
            "2024-07": 0.0,
            "2024-11": 0.0,
            "2024-12": 0.0,
            "2025-03": 1.0
        },
        {
            "product_name": "高精度光学鼠标",
            "2024-01": 0.0,
            "2024-02": 0.0,
            "2024-05": 2.0,
            "2024-07": 0.0,
            "2024-11": 0.0,
            "2024-12": 0.0,
            "2025-03": 0.0
        }
    ],
    "metadata": {
        "name": "ProductMonthlySalesAnalysis",
        "description": "产品销量按月透视分析",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "pivot",
            "sales",
            "monthly",
            "product"
        ]
    },
    "execution_info": {
        "total_time": 1.244013786315918,
        "row_count": 7,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_sales_data",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 9,
            "execution_time": 1.002580165863037,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "pivot_monthly_sales",
            "step_type": "pivot",
            "status": "completed",
            "data": null,
            "row_count": 7,
            "execution_time": 0.23743033409118652,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.2 部门员工薪资统计透视（多聚合函数）

**业务场景**：按部门和职位透视员工薪资，同时计算平均值、最大值、最小值和员工数量。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "DepartmentSalaryStatsPivot",
      "description": "部门员工薪资多维度统计透视",
      "version": "1.0",
      "author": "UQM Expert",
      "tags": ["pivot", "salary", "department", "statistics"]
    },
    "parameters": [
      {
        "name": "target_department_names",
        "type": "array",
        "default": null,
        "description": "指定要分析的部门名称列表，为空则分析所有部门"
      }
    ],
    "steps": [
      {
        "name": "get_employee_salary_data",
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
              "expression": "departments.name",
              "alias": "department_name"
            },
            {
              "expression": "employees.job_title",
              "alias": "job_title"
            },
            {
              "expression": "employees.salary",
              "alias": "salary"
            }
          ],
          "filters": [
            {
              "field": "employees.is_active",
              "operator": "=",
              "value": true
            },
            {
              "field": "departments.name",
              "operator": "IN",
              "value": "$target_department_names",
              "conditional": {
                "type": "parameter_not_empty",
                "parameter": "target_department_names",
                "empty_values": [null, []]
              }
            }
          ]
        }
      },
      {
        "name": "pivot_salary_stats",
        "type": "pivot",
        "config": {
          "source": "get_employee_salary_data",
          "index": "department_name",
          "columns": "job_title",
          "values": "salary",
          "agg_func": {
            "salary_avg": "mean",
            "salary_max": "max",
            "salary_min": "min",
            "employee_count": "count"
          },
          "fill_value": null,
          "column_prefix": "stats_"
        }
      }
    ],
    "output": "pivot_salary_stats"
  },
  "parameters": {
    "target_department_names": ["信息技术部", "人力资源部"]
  },
  "options": {}
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "department_name": "人力资源部",
            "stats_salary_avg_HR经理": 25000.0,
            "stats_salary_avg_IT总监": null,
            "stats_salary_avg_人事专员": 12000.0,
            "stats_salary_avg_软件工程师": null,
            "stats_salary_avg_高级软件工程师": null,
            "stats_salary_max_HR经理": 25000.0,
            "stats_salary_max_IT总监": null,
            "stats_salary_max_人事专员": 12000.0,
            "stats_salary_max_软件工程师": null,
            "stats_salary_max_高级软件工程师": null,
            "stats_salary_min_HR经理": 25000.0,
            "stats_salary_min_IT总监": null,
            "stats_salary_min_人事专员": 12000.0,
            "stats_salary_min_软件工程师": null,
            "stats_salary_min_高级软件工程师": null,
            "stats_employee_count_HR经理": 1.0,
            "stats_employee_count_IT总监": null,
            "stats_employee_count_人事专员": 1.0,
            "stats_employee_count_软件工程师": null,
            "stats_employee_count_高级软件工程师": null
        },
        {
            "department_name": "信息技术部",
            "stats_salary_avg_HR经理": null,
            "stats_salary_avg_IT总监": 35000.0,
            "stats_salary_avg_人事专员": null,
            "stats_salary_avg_软件工程师": 18000.0,
            "stats_salary_avg_高级软件工程师": 22000.0,
            "stats_salary_max_HR经理": null,
            "stats_salary_max_IT总监": 35000.0,
            "stats_salary_max_人事专员": null,
            "stats_salary_max_软件工程师": 18000.0,
            "stats_salary_max_高级软件工程师": 22000.0,
            "stats_salary_min_HR经理": null,
            "stats_salary_min_IT总监": 35000.0,
            "stats_salary_min_人事专员": null,
            "stats_salary_min_软件工程师": 18000.0,
            "stats_salary_min_高级软件工程师": 22000.0,
            "stats_employee_count_HR经理": null,
            "stats_employee_count_IT总监": 1.0,
            "stats_employee_count_人事专员": null,
            "stats_employee_count_软件工程师": 1.0,
            "stats_employee_count_高级软件工程师": 1.0
        }
    ],
    "metadata": {
        "name": "DepartmentSalaryStatsPivot",
        "description": "部门员工薪资多维度统计透视",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "pivot",
            "salary",
            "department",
            "statistics"
        ]
    },
    "execution_info": {
        "total_time": 0.05668783187866211,
        "row_count": 2,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_employee_salary_data",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 5,
            "execution_time": 0.020029544830322266,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "pivot_salary_stats",
            "step_type": "pivot",
            "status": "completed",
            "data": null,
            "row_count": 2,
            "execution_time": 0.03469109535217285,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.3 客户订单金额和数量双指标透视（多值字段）

**业务场景**：按客户分层和国家透视订单总金额和订单数量，实现多值字段的透视分析。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "CustomerOrderMetricsPivot",
      "description": "客户订单金额和数量双指标透视分析",
      "version": "1.0",
      "author": "UQM Expert",
      "tags": ["pivot", "customer", "orders", "metrics"]
    },
    "parameters": [
      {
        "name": "analysis_year",
        "type": "string",
        "default": "2024",
        "description": "分析年份"
      }
    ],
    "steps": [
      {
        "name": "get_customer_order_metrics",
        "type": "query",
        "config": {
          "data_source": "customers",
          "joins": [
            {
              "type": "left",
              "table": "orders",
              "on": "customers.customer_id = orders.customer_id"
            },
            {
              "type": "left",
              "table": "order_items",
              "on": "orders.order_id = order_items.order_id"
            }
          ],
          "dimensions": [
            {
              "expression": "customers.customer_segment",
              "alias": "customer_segment"
            },
            {
              "expression": "customers.country",
              "alias": "country"
            }
          ],
          "calculated_fields": [
            {
              "expression": "COALESCE(SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount)), 0)",
              "alias": "total_amount"
            },
            {
              "expression": "COUNT(DISTINCT orders.order_id)",
              "alias": "order_count"
            }
          ],
          "filters": [
            {
              "field": "YEAR(orders.order_date)",
              "operator": "=",
              "value": "$analysis_year"
            }
          ],
          "group_by": [
            "customers.customer_segment",
            "customers.country"
          ]
        }
      },
      {
        "name": "pivot_customer_metrics",
        "type": "pivot",
        "config": {
          "source": "get_customer_order_metrics",
          "index": "customer_segment",
          "columns": "country",
          "values": ["total_amount", "order_count"],
          "agg_func": "sum",
          "fill_value": 0
        }
      }
    ],
    "output": "pivot_customer_metrics"
  },
  "parameters": {
    "analysis_year": "2024"
  },
  "options": {}
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "customer_segment": "VIP",
            "order_count_中国": 2,
            "order_count_德国": 0,
            "order_count_意大利": 0,
            "order_count_日本": 0,
            "order_count_法国": 1,
            "order_count_美国": 1,
            "total_amount_中国": 1134.05,
            "total_amount_德国": 0.0,
            "total_amount_意大利": 0.0,
            "total_amount_日本": 0.0,
            "total_amount_法国": 1519.05,
            "total_amount_美国": 599.0
        },
        {
            "customer_segment": "新客户",
            "order_count_中国": 0,
            "order_count_德国": 1,
            "order_count_意大利": 0,
            "order_count_日本": 0,
            "order_count_法国": 0,
            "order_count_美国": 0,
            "total_amount_中国": 0.0,
            "total_amount_德国": 799.0,
            "total_amount_意大利": 0.0,
            "total_amount_日本": 0.0,
            "total_amount_法国": 0.0,
            "total_amount_美国": 0.0
        },
        {
            "customer_segment": "普通",
            "order_count_中国": 1,
            "order_count_德国": 0,
            "order_count_意大利": 1,
            "order_count_日本": 1,
            "order_count_法国": 0,
            "order_count_美国": 0,
            "total_amount_中国": 232.2,
            "total_amount_德国": 0.0,
            "total_amount_意大利": 516.0,
            "total_amount_日本": 1570.35,
            "total_amount_法国": 0.0,
            "total_amount_美国": 0.0
        }
    ],
    "metadata": {
        "name": "CustomerOrderMetricsPivot",
        "description": "客户订单金额和数量双指标透视分析",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "pivot",
            "customer",
            "orders",
            "metrics"
        ]
    },
    "execution_info": {
        "total_time": 0.055039405822753906,
        "row_count": 3,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_customer_order_metrics",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 7,
            "execution_time": 0.00995635986328125,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "pivot_customer_metrics",
            "step_type": "pivot",
            "status": "completed",
            "data": null,
            "row_count": 3,
            "execution_time": 0.045083045959472656,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.4 供应商产品分类库存透视（复杂索引）

**业务场景**：按供应商名称和国家作为复合索引，按产品分类透视库存数量，实现多级索引透视。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "SupplierCategoryInventoryPivot",
      "description": "供应商产品分类库存复合索引透视分析",
      "version": "1.0",
      "author": "UQM Expert",
      "tags": ["pivot", "supplier", "inventory", "category", "complex_index"]
    },
    "parameters": [
      {
        "name": "min_inventory_threshold",
        "type": "number",
        "default": 0,
        "description": "最小库存阈值，只显示库存量大于此值的记录"
      }
    ],
    "steps": [
      {
        "name": "get_supplier_inventory_data",
        "type": "query",
        "config": {
          "data_source": "suppliers",
          "joins": [
            {
              "type": "inner",
              "table": "products",
              "on": "suppliers.supplier_id = products.supplier_id"
            },
            {
              "type": "inner",
              "table": "inventory",
              "on": "products.product_id = inventory.product_id"
            }
          ],
          "dimensions": [
            {
              "expression": "suppliers.supplier_name",
              "alias": "supplier_name"
            },
            {
              "expression": "suppliers.country",
              "alias": "supplier_country"
            },
            {
              "expression": "products.category",
              "alias": "product_category"
            }
          ],
          "calculated_fields": [
            {
              "expression": "SUM(inventory.quantity_on_hand)",
              "alias": "total_inventory"
            }
          ],
          "group_by": [
            "suppliers.supplier_name",
            "suppliers.country",
            "products.category"
          ],
          "filters": [
            {
              "field": "products.discontinued",
              "operator": "=",
              "value": false
            }
          ],
          "having": [
            {
              "field": "SUM(inventory.quantity_on_hand)",
              "operator": ">",
              "value": "$min_inventory_threshold"
            }
          ]
        }
      },
      {
        "name": "pivot_supplier_inventory",
        "type": "pivot",
        "config": {
          "source": "get_supplier_inventory_data",
          "index": ["supplier_name", "supplier_country"],
          "columns": "product_category",
          "values": "total_inventory",
          "agg_func": "sum",
          "fill_value": 0
        }
      }
    ],
    "output": "pivot_supplier_inventory"
  },
  "parameters": {
    "min_inventory_threshold": 10
  },
  "options": {}
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "supplier_name": "京都纺织株式会社",
            "supplier_country": "日本",
            "图书": 0.0,
            "家居用品": 220.0,
            "服装": 0.0,
            "电子产品": 0.0
        },
        {
            "supplier_name": "华南电子配件厂",
            "supplier_country": "中国",
            "图书": 0.0,
            "家居用品": 0.0,
            "服装": 0.0,
            "电子产品": 500.0
        },
        {
            "supplier_name": "珠三角智能制造",
            "supplier_country": "中国",
            "图书": 800.0,
            "家居用品": 50.0,
            "服装": 0.0,
            "电子产品": 0.0
        },
        {
            "supplier_name": "硅谷创新科技",
            "supplier_country": "美国",
            "图书": 0.0,
            "家居用品": 0.0,
            "服装": 0.0,
            "电子产品": 120.0
        },
        {
            "supplier_name": "长三角服装集团",
            "supplier_country": "中国",
            "图书": 0.0,
            "家居用品": 0.0,
            "服装": 1050.0,
            "电子产品": 0.0
        },
        {
            "supplier_name": "黑森林精密仪器",
            "supplier_country": "德国",
            "图书": 0.0,
            "家居用品": 0.0,
            "服装": 0.0,
            "电子产品": 630.0
        }
    ],
    "metadata": {
        "name": "SupplierCategoryInventoryPivot",
        "description": "供应商产品分类库存复合索引透视分析",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "pivot",
            "supplier",
            "inventory",
            "category",
            "complex_index"
        ]
    },
    "execution_info": {
        "total_time": 0.041176795959472656,
        "row_count": 6,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_supplier_inventory_data",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 7,
            "execution_time": 0.024184226989746094,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "pivot_supplier_inventory",
            "step_type": "pivot",
            "status": "completed",
            "data": null,
            "row_count": 6,
            "execution_time": 0.015995025634765625,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.5 员工入职季度分析透视（列前缀功能）

**业务场景**：按部门透视员工在不同季度的入职人数，使用列前缀便于识别和后续处理。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "EmployeeHiringQuarterPivot",
      "description": "员工入职季度分析透视，使用列前缀功能",
      "version": "1.0",
      "author": "UQM Expert",
      "tags": ["pivot", "employee", "hiring", "quarter", "column_prefix"]
    },
    "parameters": [
      {
        "name": "analysis_years",
        "type": "array",
        "default": ["2023", "2024"],
        "description": "分析年份列表"
      }
    ],
    "steps": [
      {
        "name": "get_hiring_data",
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
              "expression": "departments.name",
              "alias": "department_name"
            },
            {
              "expression": "CONCAT(YEAR(employees.hire_date), '-Q', QUARTER(employees.hire_date))",
              "alias": "hire_quarter"
            }
          ],
          "calculated_fields": [
            {
              "expression": "COUNT(*)",
              "alias": "hire_count"
            }
          ],
          "filters": [
            {
              "field": "YEAR(employees.hire_date)",
              "operator": "IN",
              "value": "$analysis_years"
            }
          ],
          "group_by": [
            "departments.name",
            "CONCAT(YEAR(employees.hire_date), '-Q', QUARTER(employees.hire_date))"
          ]
        }
      },
      {
        "name": "pivot_hiring_quarters",
        "type": "pivot",
        "config": {
          "source": "get_hiring_data",
          "index": "department_name",
          "columns": "hire_quarter",
          "values": "hire_count",
          "agg_func": "sum",
          "fill_value": 0,
          "column_prefix": "quarter_"
        }
      }
    ],
    "output": "pivot_hiring_quarters"
  },
  "parameters": {
    "analysis_years": ["2023", "2024"]
  },
  "options": {}
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "department_name": "人力资源部",
            "quarter_2023-Q1": 0,
            "quarter_2023-Q2": 1,
            "quarter_2024-Q1": 0,
            "quarter_2024-Q2": 0
        },
        {
            "department_name": "信息技术部",
            "quarter_2023-Q1": 0,
            "quarter_2023-Q2": 0,
            "quarter_2024-Q1": 0,
            "quarter_2024-Q2": 1
        },
        {
            "department_name": "市场营销部",
            "quarter_2023-Q1": 0,
            "quarter_2023-Q2": 0,
            "quarter_2024-Q1": 1,
            "quarter_2024-Q2": 0
        },
        {
            "department_name": "销售部",
            "quarter_2023-Q1": 1,
            "quarter_2023-Q2": 0,
            "quarter_2024-Q1": 0,
            "quarter_2024-Q2": 0
        }
    ],
    "metadata": {
        "name": "EmployeeHiringQuarterPivot",
        "description": "员工入职季度分析透视，使用列前缀功能",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "pivot",
            "employee",
            "hiring",
            "quarter",
            "column_prefix"
        ]
    },
    "execution_info": {
        "total_time": 0.02496194839477539,
        "row_count": 4,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_hiring_data",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 4,
            "execution_time": 0.013046503067016602,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "pivot_hiring_quarters",
            "step_type": "pivot",
            "status": "completed",
            "data": null,
            "row_count": 4,
            "execution_time": 0.010949850082397461,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.6 动态产品销售透视分析（高级参数化用法）

**业务场景**：支持动态指定透视的索引字段、列字段和值字段，实现灵活的产品销售数据透视分析。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "DynamicProductSalesPivot",
      "description": "动态产品销售透视分析，支持参数化配置透视字段",
      "version": "1.0",
      "author": "UQM Expert",
      "tags": ["pivot", "dynamic", "parameterized", "sales", "advanced"]
    },
    "parameters": [
      {
        "name": "pivot_index_field",
        "type": "string",
        "default": "product_name",
        "description": "透视索引字段：product_name, category, supplier_name"
      },
      {
        "name": "pivot_column_field",
        "type": "string", 
        "default": "order_month",
        "description": "透视列字段：order_month, customer_segment, country"
      },
      {
        "name": "pivot_value_field",
        "type": "string",
        "default": "total_amount",
        "description": "透视值字段：total_amount, total_quantity, avg_price"
      },
      {
        "name": "pivot_agg_function",
        "type": "string",
        "default": "sum",
        "description": "聚合函数：sum, avg, count, max, min"
      },
      {
        "name": "date_range_start",
        "type": "string",
        "default": "2024-01-01",
        "description": "分析开始日期"
      },
      {
        "name": "date_range_end", 
        "type": "string",
        "default": "2024-12-31",
        "description": "分析结束日期"
      }
    ],
    "steps": [
      {
        "name": "get_dynamic_sales_data",
        "type": "query",
        "config": {
          "data_source": "orders",
          "joins": [
            {
              "type": "inner",
              "table": "order_items",
              "on": "orders.order_id = order_items.order_id"
            },
            {
              "type": "inner",
              "table": "products",
              "on": "order_items.product_id = products.product_id"
            },
            {
              "type": "inner",
              "table": "customers",
              "on": "orders.customer_id = customers.customer_id"
            },
            {
              "type": "left",
              "table": "suppliers",
              "on": "products.supplier_id = suppliers.supplier_id"
            }
          ],
          "dimensions": [
            {
              "expression": "products.product_name",
              "alias": "product_name"
            },
            {
              "expression": "products.category",
              "alias": "category"
            },
            {
              "expression": "COALESCE(suppliers.supplier_name, '未知供应商')",
              "alias": "supplier_name"
            },
            {
              "expression": "DATE_FORMAT(orders.order_date, '%Y-%m')",
              "alias": "order_month"
            },
            {
              "expression": "customers.customer_segment",
              "alias": "customer_segment"
            },
            {
              "expression": "customers.country",
              "alias": "country"
            }
          ],
          "calculated_fields": [
            {
              "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))",
              "alias": "total_amount"
            },
            {
              "expression": "SUM(order_items.quantity)",
              "alias": "total_quantity"
            },
            {
              "expression": "AVG(order_items.unit_price)",
              "alias": "avg_price"
            }
          ],
          "filters": [
            {
              "field": "orders.order_date",
              "operator": ">=",
              "value": "$date_range_start"
            },
            {
              "field": "orders.order_date",
              "operator": "<=",
              "value": "$date_range_end"
            },
            {
              "field": "orders.status",
              "operator": "IN",
              "value": ["已完成", "已发货"]
            }
          ],
          "group_by": [
            "products.product_name",
            "products.category",
            "suppliers.supplier_name",
            "DATE_FORMAT(orders.order_date, '%Y-%m')",
            "customers.customer_segment",
            "customers.country"
          ]
        }
      },
      {
        "name": "dynamic_sales_pivot",
        "type": "pivot",
        "config": {
          "source": "get_dynamic_sales_data",
          "index": "$pivot_index_field",
          "columns": "$pivot_column_field",
          "values": "$pivot_value_field",
          "agg_func": "$pivot_agg_function",
          "fill_value": 0
        }
      }
    ],
    "output": "dynamic_sales_pivot"
  },
  "parameters": {
    "pivot_index_field": "category",
    "pivot_column_field": "customer_segment", 
    "pivot_value_field": "total_amount",
    "pivot_agg_function": "sum",
    "date_range_start": "2024-01-01",
    "date_range_end": "2024-06-30"
  },
  "options": {}
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "category": "服装",
            "VIP": 0.0,
            "普通": 232.2
        },
        {
            "category": "电子产品",
            "VIP": 835.05,
            "普通": 1570.3500000000001
        }
    ],
    "metadata": {
        "name": "DynamicProductSalesPivot",
        "description": "动态产品销售透视分析，支持参数化配置透视字段",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "pivot",
            "dynamic",
            "parameterized",
            "sales",
            "advanced"
        ]
    },
    "execution_info": {
        "total_time": 0.011020660400390625,
        "row_count": 2,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_dynamic_sales_data",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 5,
            "execution_time": 0.004029989242553711,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "dynamic_sales_pivot",
            "step_type": "pivot",
            "status": "completed",
            "data": null,
            "row_count": 2,
            "execution_time": 0.005991935729980469,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

## 3. Pivot 使用要点总结

### 3.1 基本配置参数

- **source**: 源数据步骤名称
- **index**: 透视索引字段（行），支持字符串或字符串数组
- **columns**: 透视列字段，支持字符串或字符串数组  
- **values**: 透视值字段，支持字符串或字符串数组
- **agg_func**: 聚合函数，支持 sum、mean、count、min、max、std、var、first、last
- **fill_value**: 填充空值，默认为0或null
- **column_prefix**: 列前缀，便于识别透视后的列

### 3.2 高级功能

1. **多聚合函数**: 支持对不同值字段使用不同聚合函数
2. **多级索引**: index 可以是数组，实现复合索引透视
3. **多值字段**: values 可以是数组，同时透视多个值字段
4. **参数化配置**: 透视字段支持参数化，实现动态透视
5. **列前缀**: 通过 column_prefix 为透视后的列添加前缀

### 3.3 使用建议

1. 数据预处理时确保字段类型正确
2. 合理使用 fill_value 处理空值
3. 大数据量时考虑在源数据步骤中预先聚合
4. 使用列前缀避免列名冲突
5. 参数化配置提高查询的灵活性和复用性 