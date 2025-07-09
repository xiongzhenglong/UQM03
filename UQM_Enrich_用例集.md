# UQM Enrich 用例集

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

## 2. 典型 Enrich 用例

### 2.1 员工信息丰富部门名称（基础用法，left join，lookup为表）

**业务场景**：为员工数据补充部门名称。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "EnrichEmployeeWithDepartment",
      "description": "为员工数据补充部门名称"
    },
    "steps": [
      {
        "name": "get_employees",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": [
            {"expression": "employee_id", "alias": "employee_id"},
            {"expression": "first_name", "alias": "first_name"},
            {"expression": "last_name", "alias": "last_name"},
            {"expression": "department_id", "alias": "department_id"}
          ],
          "filters": [
            {"field": "is_active", "operator": "=", "value": true}
          ]
        }
      },
      {
        "name": "enrich_with_department",
        "type": "enrich",
        "config": {
          "source": "get_employees",
          "lookup": {
            "table": "departments",
            "columns": ["department_id", "name"]
          },
          "on": {"left": "department_id", "right": "department_id"},
          "join_type": "left"
        }
      }
    ],
    "output": "enrich_with_department"
  }
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "employee_id": 1,
            "first_name": "张",
            "last_name": "伟",
            "department_id": 2,
            "name": "信息技术部"
        },
        {
            "employee_id": 2,
            "first_name": "王",
            "last_name": "芳",
            "department_id": 1,
            "name": "人力资源部"
        },
        {
            "employee_id": 3,
            "first_name": "李",
            "last_name": "强",
            "department_id": 2,
            "name": "信息技术部"
        }
    ],
    "metadata": {
        "name": "EnrichEmployeeWithDepartment",
        "description": "为员工数据补充部门名称",
        "version": "1.0",
        "author": "",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.03299975395202637,
        "row_count": 12,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_employees",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.002457141876220703,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "enrich_with_department",
            "step_type": "enrich",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.030542612075805664,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.2 订单明细丰富产品信息（inner join，lookup为对象，带where）

**业务场景**：为订单明细补充产品名称和类别，仅关联在售商品。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "EnrichOrderItemsWithProduct",
      "description": "订单明细补充产品信息，仅关联在售商品"
    },
    "steps": [
      {
        "name": "get_order_items",
        "type": "query",
        "config": {
          "data_source": "order_items",
          "dimensions": [
            {"expression": "order_id", "alias": "order_id"},
            {"expression": "product_id", "alias": "product_id"},
            {"expression": "quantity", "alias": "quantity"}
          ]
        }
      },
      {
        "name": "enrich_with_product",
        "type": "enrich",
        "config": {
          "source": "get_order_items",
          "lookup": {
            "table": "products",
            "columns": ["product_id", "product_name", "category"],
            "where": [
              {"field": "discontinued", "operator": "=", "value": false}
            ]
          },
          "on": "product_id",
          "join_type": "inner"
        }
      }
    ],
    "output": "enrich_with_product"
  }
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "order_id": 1,
            "product_id": 1,
            "quantity": 1,
            "product_name": "超高速SSD 1TB",
            "category": "电子产品"
        },
        {
            "order_id": 10,
            "product_id": 1,
            "quantity": 1,
            "product_name": "超高速SSD 1TB",
            "category": "电子产品"
        },
        {
            "order_id": 1,
            "product_id": 2,
            "quantity": 1,
            "product_name": "机械键盘",
            "category": "电子产品"
        }
    ],
    "metadata": {
        "name": "EnrichOrderItemsWithProduct",
        "description": "订单明细补充产品信息，仅关联在售商品",
        "version": "1.0",
        "author": "",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.02999711036682129,
        "row_count": 16,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_order_items",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 16,
            "execution_time": 0.003020763397216797,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "enrich_with_product",
            "step_type": "enrich",
            "status": "completed",
            "data": null,
            "row_count": 16,
            "execution_time": 0.02595067024230957,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.3 多字段关联：库存丰富产品与仓库信息（on为数组，right join）

**业务场景**：查询所有库存，补充产品名和仓库名，展示所有仓库-产品组合。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "EnrichInventoryWithProductWarehouse",
      "description": "库存数据补充产品名和仓库名"
    },
    "steps": [
      {
        "name": "get_inventory",
        "type": "query",
        "config": {
          "data_source": "inventory",
          "dimensions": [
            {"expression": "product_id", "alias": "product_id"},
            {"expression": "warehouse_id", "alias": "warehouse_id"},
            {"expression": "quantity_on_hand", "alias": "quantity"}
          ]
        }
      },
      {
        "name": "enrich_with_product_warehouse",
        "type": "enrich",
        "config": {
          "source": "get_inventory",
          "lookup": {
            "table": "products",
            "columns": ["product_id", "product_name"]
          },
          "on": {"left": "product_id", "right": "product_id"},
          "join_type": "left"
        }
      },
      {
        "name": "enrich_with_warehouse",
        "type": "enrich",
        "config": {
          "source": "enrich_with_product_warehouse",
          "lookup": {
            "table": "warehouses",
            "columns": ["warehouse_id", "warehouse_name"]
          },
          "on": {"left": "warehouse_id", "right": "warehouse_id"},
          "join_type": "left"
        }
      }
    ],
    "output": "enrich_with_warehouse"
  }
}
```
**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "product_id": 1,
            "warehouse_id": 1,
            "quantity": 100,
            "product_name": "超高速SSD 1TB",
            "warehouse_name": "华北仓"
        },
        {
            "product_id": 1,
            "warehouse_id": 2,
            "quantity": 50,
            "product_name": "超高速SSD 1TB",
            "warehouse_name": "华东仓"
        },
        {
            "product_id": 2,
            "warehouse_id": 1,
            "quantity": 200,
            "product_name": "机械键盘",
            "warehouse_name": "华北仓"
        }
    ],
    "metadata": {
        "name": "EnrichInventoryWithProductWarehouse",
        "description": "库存数据补充产品名和仓库名",
        "version": "1.0",
        "author": "",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.03999757766723633,
        "row_count": 20,
        "cache_hit": false,
        "steps_executed": 3
    },
    "step_results": [
        {
            "step_name": "get_inventory",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 20,
            "execution_time": 0.008000850677490234,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "enrich_with_product_warehouse",
            "step_type": "enrich",
            "status": "completed",
            "data": null,
            "row_count": 20,
            "execution_time": 0.003999471664428711,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "enrich_with_warehouse",
            "step_type": "enrich",
            "status": "completed",
            "data": null,
            "row_count": 20,
            "execution_time": 0.026993989944458008,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.4 lookup为前置步骤（步骤间数据丰富，full join）

**业务场景**：将两步查询结果（如活跃员工与VIP客户）做全连接，分析交集与并集。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "EnrichEmployeeWithVIPCustomer",
      "description": "员工与VIP客户信息全连接分析"
    },
    "steps": [
      {
        "name": "active_employees",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": [
            {"expression": "employee_id", "alias": "employee_id"},
            {"expression": "first_name", "alias": "first_name"}
          ],
          "filters": [
            {"field": "is_active", "operator": "=", "value": true}
          ]
        }
      },
      {
        "name": "vip_customers",
        "type": "query",
        "config": {
          "data_source": "customers",
          "dimensions": [
            {"expression": "customer_id", "alias": "customer_id"},
            {"expression": "customer_name", "alias": "customer_name"}
          ],
          "filters": [
            {"field": "customer_segment", "operator": "=", "value": "VIP"}
          ]
        }
      },
      {
        "name": "enrich_employee_with_vip_customer",
        "type": "enrich",
        "config": {
          "source": "active_employees",
          "lookup": "vip_customers",
          "on": {"left": "employee_id", "right": "customer_id"},
          "join_type": "full"
        }
      }
    ],
    "output": "enrich_employee_with_vip_customer"
  }
}
```
**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "employee_id": 1,
            "first_name": "张",
            "customer_id": 1.0,
            "customer_name": "孙悟空"
        },
        {
            "employee_id": 2,
            "first_name": "王",
            "customer_id": null,
            "customer_name": null
        },
        {
            "employee_id": 3,
            "first_name": "李",
            "customer_id": 3.0,
            "customer_name": "托尼·斯塔克"
        }
    ],
    "metadata": {
        "name": "EnrichEmployeeWithVIPCustomer",
        "description": "员工与VIP客户信息全连接分析",
        "version": "1.0",
        "author": "",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.037999629974365234,
        "row_count": 12,
        "cache_hit": false,
        "steps_executed": 3
    },
    "step_results": [
        {
            "step_name": "active_employees",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.028999805450439453,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "vip_customers",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 4,
            "execution_time": 0.003030538558959961,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "enrich_employee_with_vip_customer",
            "step_type": "enrich",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.00596928596496582,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.5 参数化lookup与多条件where（高级用法，lookup对象+参数）

**业务场景**：根据参数动态过滤供应商，为产品补充供应商信息。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "EnrichProductWithSupplierParam",
      "description": "产品补充供应商信息，支持国家参数过滤"
    },
    "parameters": [
      {"name": "supplier_country", "type": "string", "default": null}
    ],
    "steps": [
      {
        "name": "get_products",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": [
            {"expression": "product_id", "alias": "product_id"},
            {"expression": "product_name", "alias": "product_name"},
            {"expression": "supplier_id", "alias": "supplier_id"}
          ]
        }
      },
      {
        "name": "enrich_with_supplier",
        "type": "enrich",
        "config": {
          "source": "get_products",
          "lookup": {
            "table": "suppliers",
            "columns": ["supplier_id", "supplier_name", "country"],
            "where": [
              {
                "field": "country",
                "operator": "=",
                "value": "$supplier_country",
                "conditional": {
                  "type": "parameter_not_empty",
                  "parameter": "supplier_country",
                  "empty_values": [null, ""]
                }
              }
            ]
          },
          "on": {"left": "supplier_id", "right": "supplier_id"},
          "join_type": "left"
        }
      }
    ],
    "output": "enrich_with_supplier"
  },
  "parameters": {
    "supplier_country": "中国"
  }
}
```
**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "product_id": 1,
            "product_name": "超高速SSD 1TB",
            "supplier_id": 1,
            "supplier_name": "华南电子配件厂",
            "country": "中国"
        },
        {
            "product_id": 2,
            "product_name": "机械键盘",
            "supplier_id": 1,
            "supplier_name": "华南电子配件厂",
            "country": "中国"
        },
        {
            "product_id": 3,
            "product_name": "潮流印花T恤",
            "supplier_id": 2,
            "supplier_name": "长三角服装集团",
            "country": "中国"
        }
    ],
    "metadata": {
        "name": "EnrichProductWithSupplierParam",
        "description": "产品补充供应商信息，支持国家参数过滤",
        "version": "1.0",
        "author": "",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.02699899673461914,
        "row_count": 12,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_products",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.007999420166015625,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "enrich_with_supplier",
            "step_type": "enrich",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.018000364303588867,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.6 字段冲突与缺失key处理（边界用例，inner join）

**业务场景**：订单与员工信息合并，两个表都有employee_id，测试字段冲突自动处理。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "EnrichOrderWithEmployeeConflict",
      "description": "订单与员工信息合并，测试字段冲突与缺失key"
    },
    "steps": [
      {
        "name": "get_orders",
        "type": "query",
        "config": {
          "data_source": "orders",
          "dimensions": [
            {"expression": "order_id", "alias": "order_id"},
            {"expression": "employee_id", "alias": "employee_id"},
            {"expression": "order_date", "alias": "order_date"}
          ]
        }
      },
      {
        "name": "enrich_with_employee",
        "type": "enrich",
        "config": {
          "source": "get_orders",
          "lookup": {
            "table": "employees",
            "columns": ["employee_id", "first_name", "last_name"]
          },
          "on": "employee_id",
          "join_type": "inner"
        }
      }
    ],
    "output": "enrich_with_employee"
  }
}
```
**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "order_id": 1,
            "employee_id": 6,
            "order_date": "2024-01-20T10:30:00",
            "first_name": "杨",
            "last_name": "静"
        },
        {
            "order_id": 2,
            "employee_id": 6,
            "order_date": "2024-02-15T14:00:00",
            "first_name": "杨",
            "last_name": "静"
        },
        {
            "order_id": 3,
            "employee_id": 6,
            "order_date": "2024-02-28T18:45:00",
            "first_name": "杨",
            "last_name": "静"
        }
    ],
    "metadata": {
        "name": "EnrichOrderWithEmployeeConflict",
        "description": "订单与员工信息合并，测试字段冲突与缺失key",
        "version": "1.0",
        "author": "",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.02480459213256836,
        "row_count": 13,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_orders",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 13,
            "execution_time": 0.002053499221801758,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "enrich_with_employee",
            "step_type": "enrich",
            "status": "completed",
            "data": null,
            "row_count": 13,
            "execution_time": 0.0227510929107666,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

**说明**：如有字段冲突（如employee_id），系统会自动重命名（如employee_id_x, employee_id_y），如有缺失key，按join_type处理。

---

