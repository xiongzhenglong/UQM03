# UQM Union 用例集

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

## 2. 典型 Union 用例

### 2.1 员工与客户基本信息合并（UNION，基础用法）

**业务场景**：将员工和客户的姓名信息合并，去除重复。

**UQM 配置：**
```json
{
    "uqm": {
      "metadata": {
        "name": "MergeEmployeeAndCustomerNames",
        "description": "合并员工和客户的姓名信息，并去除重复项",
        "version": "1.0",
        "author": "UQM Expert",
        "tags": [
          "union",
          "deduplication",
          "names"
        ]
      },
      "parameters": [],
      "steps": [
        {
          "name": "get_employee_names",
          "type": "query",
          "config": {
            "data_source": "employees",
            "dimensions": [
              {
                "expression": "CONCAT(first_name, ' ', last_name)",
                "alias": "full_name"
              }
            ],
            "filters": [
              {
                "field": "is_active",
                "operator": "=",
                "value": true
              }
            ]
          }
        },
        {
          "name": "get_customer_names",
          "type": "query",
          "config": {
            "data_source": "customers",
            "dimensions": [
              {
                "expression": "customer_name",
                "alias": "full_name"
              }
            ]
          }
        },
        {
          "name": "union_names",
          "type": "union",
          "config": {
            "sources": [
              "get_employee_names",
              "get_customer_names"
            ],
            "mode": "union",
            "add_source_column": false,
            "remove_duplicates": true
          }
        }
      ],
      "output": "union_names"
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
            "full_name": "张 伟"
        },       
        {
            "full_name": "Ming Li"
        },
        {
            "full_name": "Peter Schmidt"
        },      
        {
            "full_name": "孙悟空"
        }       
    ],
    "metadata": {
        "name": "MergeEmployeeAndCustomerNames",
        "description": "合并员工和客户的姓名信息，并去除重复项",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "union",
            "deduplication",
            "names"
        ]
    },
    "execution_info": {
        "total_time": 0.005997419357299805,
        "row_count": 24,
        "cache_hit": false,
        "steps_executed": 3
    },
    "step_results": [
        {
            "step_name": "get_employee_names",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.003998994827270508,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "get_customer_names",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.001998424530029297,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "union_names",
            "step_type": "union",
            "status": "completed",
            "data": null,
            "row_count": 24,
            "execution_time": 0.0,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.2 订单与订单明细合并（UNION ALL，保留重复）

**业务场景**：将订单主表和订单明细表的订单ID合并，保留所有重复项。

**UQM 配置：**
```json
{
    "uqm": {
      "metadata": {
        "name": "UnionOrderIDs",
        "description": "合并订单主表和订单明细表的订单ID，保留所有重复项。",
        "version": "1.0",
        "author": "UQM Expert",
        "tags": [
          "orders",
          "order_items",
          "union"
        ]
      },
      "parameters": [],
      "steps": [
        {
          "name": "get_order_ids",
          "type": "query",
          "config": {
            "data_source": "orders",
            "dimensions": [
              {
                "expression": "order_id",
                "alias": "order_id"
              }
            ]
          }
        },
        {
          "name": "get_order_item_ids",
          "type": "query",
          "config": {
            "data_source": "order_items",
            "dimensions": [
              {
                "expression": "order_id",
                "alias": "order_id"
              }
            ]
          }
        },
        {
          "name": "union_order_ids",
          "type": "union",
          "config": {
            "sources": [
              "get_order_ids",
              "get_order_item_ids"
            ],
            "mode": "union_all",
            "add_source_column": true,
            "source_column": "data_source"
          }
        }
      ],
      "output": "union_order_ids"
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
            "order_id": 1,
            "data_source": "get_order_ids"
        },
        {
            "order_id": 4,
            "data_source": "get_order_ids"
        },       
        {
            "order_id": 1,
            "data_source": "get_order_item_ids"
        }
    ],
    "metadata": {
        "name": "UnionOrderIDs",
        "description": "合并订单主表和订单明细表的订单ID，保留所有重复项。",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "orders",
            "order_items",
            "union"
        ]
    },
    "execution_info": {
        "total_time": 0.043970346450805664,
        "row_count": 29,
        "cache_hit": false,
        "steps_executed": 3
    },
    "step_results": [
        {
            "step_name": "get_order_ids",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 13,
            "execution_time": 0.038001298904418945,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "get_order_item_ids",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 16,
            "execution_time": 0.004999399185180664,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "union_order_ids",
            "step_type": "union",
            "status": "completed",
            "data": null,
            "row_count": 29,
            "execution_time": 0.0,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.3 产品与已下架产品交集（INTERSECT，交集用法）

**业务场景**：找出所有既在产品表又在已下架产品列表中的产品ID。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "IntersectDiscontinuedProducts",
      "description": "产品与已下架产品ID交集"
    },
    "steps": [
      {
        "name": "get_all_products",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": [
            {"expression": "product_id", "alias": "product_id"}
          ]
        }
      },
      {
        "name": "get_discontinued_products",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": [
            {"expression": "product_id", "alias": "product_id"}
          ],
          "filters": [
            {"field": "discontinued", "operator": "=", "value": true}
          ]
        }
      },
      {
        "name": "intersect_products",
        "type": "union",
        "config": {
          "sources": ["get_all_products", "get_discontinued_products"],
          "mode": "intersect"
        }
      }
    ],
    "output": "intersect_products"
  }
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {"product_id": 3},
        {"product_id": 5}
    ],
    "metadata": {
        "name": "IntersectDiscontinuedProducts",
        "description": "产品与已下架产品ID交集"
    },
    "execution_info": {
        "total_time": 0.01,
        "row_count": 2,
        "steps_executed": 3
    },
    "step_results": [
        {"step_name": "get_all_products", "step_type": "query", "status": "completed"},
        {"step_name": "get_discontinued_products", "step_type": "query", "status": "completed"},
        {"step_name": "intersect_products", "step_type": "union", "status": "completed"}
    ]
}
```

---

### 2.4 活跃员工与离职员工差集（EXCEPT，差集用法）

**业务场景**：找出既是客户又是供应商的公司名称。

**UQM 配置：**
```json
{
    "uqm": {
      "metadata": {
        "name": "FindCompaniesThatAreBothCustomersAndSuppliers",
        "description": "找出既是客户又是供应商的公司名称",
        "version": "1.0",
        "author": "UQM Expert",
        "tags": [
          "customer",
          "supplier",
          "company",
          "intersect"
        ]
      },
      "parameters": [],
      "steps": [
        {
          "name": "get_customer_company_names",
          "type": "query",
          "config": {
            "data_source": "customers",
            "dimensions": [
              {
                "expression": "customer_name",
                "alias": "company_name"
              }
            ]
          }
        },
        {
          "name": "get_supplier_company_names",
          "type": "query",
          "config": {
            "data_source": "suppliers",
            "dimensions": [
              {
                "expression": "supplier_name",
                "alias": "company_name"
              }
            ]
          }
        },
        {
          "name": "intersect_company_names",
          "type": "union",
          "config": {
            "sources": [
              "get_customer_company_names",
              "get_supplier_company_names"
            ],
            "mode": "intersect"
          }
        }
      ],
      "output": "intersect_company_names"
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
            "company_name": "路飞"
        }
    ],
    "metadata": {
        "name": "FindCompaniesThatAreBothCustomersAndSuppliers",
        "description": "找出既是客户又是供应商的公司名称",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "customer",
            "supplier",
            "company",
            "intersect"
        ]
    },
    "execution_info": {
        "total_time": 0.006799459457397461,
        "row_count": 1,
        "cache_hit": false,
        "steps_executed": 3
    },
    "step_results": [
        {
            "step_name": "get_customer_company_names",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.004038095474243164,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "get_supplier_company_names",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 7,
            "execution_time": 0.0017435550689697266,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "intersect_company_names",
            "step_type": "union",
            "status": "completed",
            "data": null,
            "row_count": 1,
            "execution_time": 0.0010178089141845703,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.5 多表字段补齐与对齐（字段缺失补齐/对齐）

**业务场景**：合并员工和供应商的ID与姓名信息，字段名不同，自动补齐缺失字段。

**UQM 配置：**
```json
{
    "uqm": {
      "metadata": {
        "name": "CombineEmployeeAndSupplierInfo",
        "description": "合并员工和供应商的ID与姓名信息，并补齐缺失字段",
        "version": "1.0",
        "author": "UQM Expert",
        "tags": [
          "union",
          "employee",
          "supplier",
          "combine"
        ]
      },
      "parameters": [],
      "steps": [
        {
          "name": "get_employee_info",
          "type": "query",
          "config": {
            "data_source": "employees",
            "dimensions": [
              {
                "expression": "employee_id",
                "alias": "id"
              },
              {
                "expression": "CONCAT(first_name, ' ', last_name)",
                "alias": "name"
              },
              {
                "expression": "'employee'",
                "alias": "type"
              }
            ]
          }
        },
        {
          "name": "get_supplier_info",
          "type": "query",
          "config": {
            "data_source": "suppliers",
            "dimensions": [
              {
                "expression": "supplier_id",
                "alias": "id"
              },
              {
                "expression": "supplier_name",
                "alias": "name"
              },
              {
                "expression": "'supplier'",
                "alias": "type"
              }
            ]
          }
        },
        {
          "name": "union_employee_supplier",
          "type": "union",
          "config": {
            "sources": [
              "get_employee_info",
              "get_supplier_info"
            ],
            "mode": "union_all",
            "add_source_column": true,
            "source_column": "source_type",
            "remove_duplicates": false
          }
        }
      ],
      "output": "union_employee_supplier"
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
            "type": "employee",
            "name": "张 伟",
            "id": 1,
            "source_type": "get_employee_info"
        },
        {
            "type": "employee",
            "name": "王 芳",
            "id": 2,
            "source_type": "get_employee_info"
        },
        {
            "type": "employee",
            "name": "李 强",
            "id": 3,
            "source_type": "get_employee_info"
        }
    ],
    "metadata": {
        "name": "CombineEmployeeAndSupplierInfo",
        "description": "合并员工和供应商的ID与姓名信息，并补齐缺失字段",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "union",
            "employee",
            "supplier",
            "combine"
        ]
    },
    "execution_info": {
        "total_time": 0.010998725891113281,
        "row_count": 19,
        "cache_hit": false,
        "steps_executed": 3
    },
    "step_results": [
        {
            "step_name": "get_employee_info",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.007997989654541016,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "get_supplier_info",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 7,
            "execution_time": 0.0019991397857666016,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "union_employee_supplier",
            "step_type": "union",
            "status": "completed",
            "data": null,
            "row_count": 19,
            "execution_time": 0.0,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.6 源标识字段添加与参数化（add_source_column + 参数化）

**业务场景**：合并指定国家的客户和供应商，输出时标记来源。

**UQM 配置：**
```json
{
    "uqm": {
      "metadata": {
        "name": "UnionCustomersAndSuppliersByCountry",
        "description": "合并指定国家的客户和供应商，并标记来源",
        "version": "1.0",
        "author": "UQM Expert",
        "tags": [
          "union",
          "customer",
          "supplier",
          "country",
          "parameterized"
        ]
      },
      "parameters": [
        {
          "name": "target_country",
          "type": "string",
          "required": true,
          "description": "需要合并的客户和供应商所在的国家"
        }
      ],
      "steps": [
        {
          "name": "get_customer_data",
          "type": "query",
          "config": {
            "data_source": "customers",
            "dimensions": [
              {
                "expression": "customer_name",
                "alias": "company_name"
              },
              {
                "expression": "country",
                "alias": "country"
              }
            ],
            "filters": [
              {
                "field": "country",
                "operator": "=",
                "value": "$target_country",
                "conditional": {
                  "type": "parameter_not_empty",
                  "parameter": "target_country",
                  "empty_values": [
                    null,
                    ""
                  ]
                }
              }
            ]
          }
        },
        {
          "name": "get_supplier_data",
          "type": "query",
          "config": {
            "data_source": "suppliers",
            "dimensions": [
              {
                "expression": "supplier_name",
                "alias": "company_name"
              },
              {
                "expression": "country",
                "alias": "country"
              }
            ],
            "filters": [
              {
                "field": "country",
                "operator": "=",
                "value": "$target_country",
                "conditional": {
                  "type": "parameter_not_empty",
                  "parameter": "target_country",
                  "empty_values": [
                    null,
                    ""
                  ]
                }
              }
            ]
          }
        },
        {
          "name": "union_company_data",
          "type": "union",
          "config": {
            "sources": [
              "get_customer_data",
              "get_supplier_data"
            ],
            "mode": "union_all",
            "add_source_column": true,
            "source_column": "entity_type",
            "remove_duplicates": false
          }
        }
      ],
      "output": "union_company_data"
    },
    "parameters": {
      "target_country": "中国"
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
            "country": "中国",
            "company_name": "孙悟空",
            "entity_type": "get_customer_data"
        },        
        {
            "country": "中国",
            "company_name": "长三角服装集团",
            "entity_type": "get_supplier_data"
        },
        {
            "country": "中国",
            "company_name": "珠三角智能制造",
            "entity_type": "get_supplier_data"
        }
    ],
    "metadata": {
        "name": "UnionCustomersAndSuppliersByCountry",
        "description": "合并指定国家的客户和供应商，并标记来源",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "union",
            "customer",
            "supplier",
            "country",
            "parameterized"
        ]
    },
    "execution_info": {
        "total_time": 0.0049970149993896484,
        "row_count": 6,
        "cache_hit": false,
        "steps_executed": 3
    },
    "step_results": [
        {
            "step_name": "get_customer_data",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 2,
            "execution_time": 0.002033233642578125,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "get_supplier_data",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 4,
            "execution_time": 0.001997709274291992,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "union_company_data",
            "step_type": "union",
            "status": "completed",
            "data": null,
            "row_count": 6,
            "execution_time": 0.0,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

--- 