# UQM Unpivot 用例集

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

## 2. 典型 Unpivot 用例

### 2.1 员工基本信息宽转长（基础用法，真实字段）

**业务场景**：将员工表中的基本信息字段（薪水、职位、入职日期）转换为长表结构，便于后续分析。

**UQM 配置：**
```json
{
    "uqm": {
      "metadata": {
        "name": "ZhangWeiEmployeeInfoUnpivot",
        "description": "查询员工张伟的薪水、职位、入职日期信息，并进行宽表转长表处理。",
        "version": "1.0",
        "author": "UQM Expert",
        "tags": [
          "employee",
          "unpivot",
          "zhangwei"
        ]
      },
      "parameters": [],
      "steps": [
        {
          "name": "get_zhangwei_employee_data",
          "type": "query",
          "config": {
            "data_source": "employees",
            "dimensions": [
              {
                "expression": "employees.employee_id",
                "alias": "employee_id"
              },
              {
                "expression": "employees.first_name",
                "alias": "first_name"
              },
              {
                "expression": "employees.last_name",
                "alias": "last_name"
              }
            ],
            "calculated_fields": [
              {
                "expression": "employees.salary",
                "alias": "salary"
              },
              {
                "expression": "employees.job_title",
                "alias": "job_title"
              },
              {
                "expression": "employees.hire_date",
                "alias": "hire_date"
              }
            ],
            "filters": [
              {
                "field": "employees.first_name",
                "operator": "=",
                "value": "张"
              },
              {
                "field": "employees.last_name",
                "operator": "=",
                "value": "伟"
              }
            ],
            "group_by": [
              "employees.employee_id",
              "employees.first_name",
              "employees.last_name"
            ]
          }
        },
        {
          "name": "unpivot_zhangwei_info",
          "type": "unpivot",
          "config": {
            "source": "get_zhangwei_employee_data",
            "id_vars": [
              "employee_id",
              "first_name",
              "last_name"
            ],
            "value_vars": [
              "salary",
              "job_title",
              "hire_date"
            ],
            "var_name": "attribute",
            "value_name": "value"
          }
        }
      ],
      "output": "unpivot_zhangwei_info"
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
            "employee_id": 1,
            "first_name": "张",
            "last_name": "伟",
            "attribute": "salary",
            "value": "35000.00"
        },
        {
            "employee_id": 1,
            "first_name": "张",
            "last_name": "伟",
            "attribute": "job_title",
            "value": "IT总监"
        },
        {
            "employee_id": 1,
            "first_name": "张",
            "last_name": "伟",
            "attribute": "hire_date",
            "value": "2022-01-10"
        }
    ],
    "metadata": {
        "name": "ZhangWeiEmployeeInfoUnpivot",
        "description": "查询员工张伟的薪水、职位、入职日期信息，并进行宽表转长表处理。",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "employee",
            "unpivot",
            "zhangwei"
        ]
    },
    "execution_info": {
        "total_time": 0.0069828033447265625,
        "row_count": 3,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_zhangwei_employee_data",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 1,
            "execution_time": 0.0029845237731933594,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "unpivot_zhangwei_info",
            "step_type": "unpivot",
            "status": "completed",
            "data": null,
            "row_count": 3,
            "execution_time": 0.003998279571533203,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.2 产品多价格字段转长表（自定义字段名）

**业务场景**：产品 机械键盘 多属性宽转长（单价、类别、是否下架）。。

**UQM 配置：**
```json
{
    "uqm": {
      "metadata": {
        "name": "UnpivotProductAttributes",
        "description": "将产品表中的多属性（单价、类别、是否下架）进行宽表转长表处理，并按产品名称分组聚合。",
        "version": "1.0",
        "author": "UQM Expert",
        "tags": [
          "unpivot",
          "product",
          "aggregation",
          "attributes"
        ]
      },
      "parameters": [
        {
          "name": "target_product_name",
          "type": "string",
          "default": null,
          "description": "指定要查询的产品名称，可选。"
        }
      ],
      "steps": [
        {
          "name": "get_product_data",
          "type": "query",
          "config": {
            "data_source": "products",
            "dimensions": [
              {
                "expression": "product_name",
                "alias": "product_name"
              },
              {
                "expression": "unit_price",
                "alias": "unit_price"
              },
              {
                "expression": "category",
                "alias": "category"
              },
              {
                "expression": "discontinued",
                "alias": "discontinued"
              }
            ],
            "filters": [
              {
                "field": "product_name",
                "operator": "=",
                "value": "$target_product_name",
                "conditional": {
                  "type": "parameter_not_empty",
                  "parameter": "target_product_name",
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
          "name": "unpivot_product_attributes",
          "type": "unpivot",
          "config": {
            "source": "get_product_data",
            "id_vars": [
              "product_name"
            ],
            "value_vars": [
              "unit_price",
              "category",
              "discontinued"
            ],
            "var_name": "attribute_name",
            "value_name": "attribute_value"
          }
        }
      ],
      "output": "unpivot_product_attributes"
    },
    "parameters": {
      "target_product_name": "机械键盘"
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
            "product_name": "机械键盘",
            "attribute_name": "unit_price",
            "attribute_value": "380.00"
        },
        {
            "product_name": "机械键盘",
            "attribute_name": "category",
            "attribute_value": "电子产品"
        },
        {
            "product_name": "机械键盘",
            "attribute_name": "discontinued",
            "attribute_value": 0
        }
    ],
    "metadata": {
        "name": "UnpivotProductAttributes",
        "description": "将产品表中的多属性（单价、类别、是否下架）进行宽表转长表处理，并按产品名称分组聚合。",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "unpivot",
            "product",
            "aggregation",
            "attributes"
        ]
    },
    "execution_info": {
        "total_time": 0.0020058155059814453,
        "row_count": 3,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_product_data",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 1,
            "execution_time": 0.0010044574737548828,
            "cache_hit": true,
            "error": null
        },
        {
            "step_name": "unpivot_product_attributes",
            "step_type": "unpivot",
            "status": "completed",
            "data": null,
            "row_count": 3,
            "execution_time": 0.0,
            "cache_hit": true,
            "error": null
        }
    ]
}
```

---

### 2.3 订单明细多数量字段转长表（边界用法：部分字段缺失）

**业务场景**：将订单明细表中的数量、成交单价、折扣率等字段宽转长，便于后续分析。

**UQM 配置：**
```json
{
    "uqm": {
      "metadata": {
        "name": "UnpivotOrderItemDetails",
        "description": "将订单明细表中特定order_item_id的字段宽转长",
        "version": "1.0",
        "author": "UQM Expert",
        "tags": [
          "unpivot",
          "order_items",
          "details"
        ]
      },
      "parameters": [
        {
          "name": "target_order_item_id",
          "type": "number",
          "default": 1,
          "description": "目标订单明细ID"
        }
      ],
      "steps": [
        {
          "name": "filter_order_item",
          "type": "query",
          "config": {
            "data_source": "order_items",
            "filters": [
              {
                "field": "order_item_id",
                "operator": "=",
                "value": "$target_order_item_id"
              }
            ],
            "dimensions": [
              {
                "expression": "order_item_id",
                "alias": "order_item_id"
              },
              {
                "expression": "quantity",
                "alias": "quantity"
              },
              {
                "expression": "unit_price",
                "alias": "unit_price"
              },
              {
                "expression": "discount",
                "alias": "discount"
              }
            ]
          }
        },
        {
          "name": "unpivot_item_details",
          "type": "unpivot",
          "config": {
            "source": "filter_order_item",
            "id_vars": [
              "order_item_id"
            ],
            "value_vars": [
              "quantity",
              "unit_price",
              "discount"
            ],
            "var_name": "detail_type",
            "value_name": "detail_value"
          }
        }
      ],
      "output": "unpivot_item_details"
    },
    "parameters": {
      "target_order_item_id": 1
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
            "order_item_id": 1,
            "detail_type": "quantity",
            "detail_value": 1
        },
        {
            "order_item_id": 1,
            "detail_type": "unit_price",
            "detail_value": "499.00"
        },
        {
            "order_item_id": 1,
            "detail_type": "discount",
            "detail_value": "0.05"
        }
    ],
    "metadata": {
        "name": "UnpivotOrderItemDetails",
        "description": "将订单明细表中特定order_item_id的字段宽转长",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "unpivot",
            "order_items",
            "details"
        ]
    },
    "execution_info": {
        "total_time": 0.007001638412475586,
        "row_count": 3,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "filter_order_item",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 1,
            "execution_time": 0.004006862640380859,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "unpivot_item_details",
            "step_type": "unpivot",
            "status": "completed",
            "data": null,
            "row_count": 3,
            "execution_time": 0.0029947757720947266,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.4 库存多仓库数量转长表（高级用法：动态value_vars参数化）

**业务场景**：库存表有多个仓库的库存字段，支持通过参数动态指定需要unpivot的仓库字段。

**UQM 配置：**
```json
{
  "uqm": {
    "metadata": {
      "name": "UnpivotInventoryAttributesParam",
      "description": "库存多属性宽转长，支持动态 value_vars 参数化"
    },
    "parameters": [
      {
        "name": "inventory_fields",
        "type": "array",
        "description": "需要转换的库存属性字段名"
      }
    ],
    "steps": [
      {
        "name": "get_inventory_attributes",
        "type": "query",
        "config": {
          "data_source": "inventory",
          "dimensions": [
            {"expression": "inventory_id", "alias": "inventory_id"},
            {"expression": "product_id", "alias": "product_id"},
            {"expression": "warehouse_id", "alias": "warehouse_id"},
            {"expression": "quantity_on_hand", "alias": "quantity_on_hand"},
            {"expression": "last_updated", "alias": "last_updated"}
          ]
        }
      },
      {
        "name": "unpivot_inventory_attributes",
        "type": "unpivot",
        "config": {
          "source": "get_inventory_attributes",
          "id_vars": ["inventory_id", "product_id", "warehouse_id"],
          "value_vars": "$inventory_fields",
          "var_name": "attribute",
          "value_name": "value"
        }
      }
    ],
    "output": "unpivot_inventory_attributes"
  },
  "parameters": {
    "inventory_fields": ["quantity_on_hand", "last_updated"]
  }
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "inventory_id": 1,
            "product_id": 1,
            "warehouse_id": 1,
            "attribute": "quantity_on_hand",
            "value": 100
        },
        {
            "inventory_id": 1,
            "product_id": 1,
            "warehouse_id": 1,
            "attribute": "last_updated",
            "value": {}
        }
    ],
    "metadata": {
        "name": "UnpivotInventoryAttributesParam",
        "description": "库存多属性宽转长，支持动态 value_vars 参数化",
        "version": "1.0",
        "author": "",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.0040323734283447266,
        "row_count": 20,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_inventory_attributes",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 20,
            "execution_time": 0.0,
            "cache_hit": true,
            "error": null
        },
        {
            "step_name": "unpivot_inventory_attributes",
            "step_type": "unpivot",
            "status": "completed",
            "data": null,
            "row_count": 20,
            "execution_time": 0.003008127212524414,
            
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.5 客户多联系方式转长表（自定义var_name/value_name）

**业务场景**：将客户表中的邮箱、国家、城市、客户分层等属性宽转长，自定义字段名。

**UQM 配置：**
```json
{
    "uqm": {
      "metadata": {
        "name": "客户属性宽转长",
        "description": "将客户表中的邮箱、国家、城市、客户分层等属性宽转长，并自定义字段名。",
        "version": "1.0",
        "author": "UQM Expert",
        "tags": ["customer", "unpivot", "attribute"]
      },
      "parameters": [
        {
          "name": "customer_ids",
          "type": "array",
          "default": null,
          "description": "指定要处理的客户ID列表，如果为空则处理所有客户。"
        }
      ],
      "steps": [
        {
          "name": "select_customer_attributes",
          "type": "query",
          "config": {
            "data_source": "customers",
            "dimensions": [
              {"expression": "customer_id", "alias": "customer_id"},
              {"expression": "customer_name", "alias": "customer_name"},
              {"expression": "email", "alias": "email"},
              {"expression": "country", "alias": "country"},
              {"expression": "city", "alias": "city"},
              {"expression": "registration_date", "alias": "registration_date"},
              {"expression": "customer_segment", "alias": "customer_segment"}
            ],
            "filters": [
              {
                "field": "customer_id",
                "operator": "IN",
                "value": "$customer_ids",
                "conditional": {
                  "type": "parameter_not_empty",
                  "parameter": "customer_ids",
                  "empty_values": [null, []]
                }
              }
            ]
          }
        },
        {
          "name": "unpivot_customer_attributes",
          "type": "unpivot",
          "config": {
            "source": "select_customer_attributes",
            "id_vars": ["customer_id", "customer_name", "registration_date"],
            "value_vars": ["email", "country", "city", "customer_segment"],
            "var_name": "attribute_name",
            "value_name": "attribute_value"
          }
        }
      ],
      "output": "unpivot_customer_attributes"
    },
    "parameters": {
      "customer_ids": [1]
    },
    "options": {"cache_enabled":false}
}
```

**预期输出示例：**
```json
{
    "success": true,
    "data": [
        {
            "customer_id": 1,
            "customer_name": "孙悟空",
            "registration_date": "2023-01-15",
            "attribute_name": "email",
            "attribute_value": "sun.wukong@test.com"
        },
        {
            "customer_id": 1,
            "customer_name": "孙悟空",
            "registration_date": "2023-01-15",
            "attribute_name": "country",
            "attribute_value": "中国"
        },
        {
            "customer_id": 1,
            "customer_name": "孙悟空",
            "registration_date": "2023-01-15",
            "attribute_name": "city",
            "attribute_value": "北京"
        },
        {
            "customer_id": 1,
            "customer_name": "孙悟空",
            "registration_date": "2023-01-15",
            "attribute_name": "customer_segment",
            "attribute_value": "VIP"
        }
    ],
    "metadata": {
        "name": "客户属性宽转长",
        "description": "将客户表中的邮箱、国家、城市、客户分层等属性宽转长，并自定义字段名。",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "customer",
            "unpivot",
            "attribute"
        ]
    },
    "execution_info": {
        "total_time": 0.005126953125,
        "row_count": 4,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "select_customer_attributes",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 1,
            "execution_time": 0.0022373199462890625,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "unpivot_customer_attributes",
            "step_type": "unpivot",
            "status": "completed",
            "data": null,
            "row_count": 4,
            "execution_time": 0.0028896331787109375,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

### 2.6 供应商多地区联系人转长表（高级用法：多id_vars+多value_vars）

**业务场景**：供应商表有多个地区联系人字段，需保留供应商ID和名称，转换所有联系人为长表。

**UQM 配置：**
```json
{
    "uqm": {
      "metadata": {
        "name": "UnpivotSupplierContacts",
        "description": "将供应商表中的多个地区联系人字段转换为长表格式",
        "version": "1.0",
        "author": "UQM Expert",
        "tags": [
          "unpivot",
          "supplier",
          "contact"
        ]
      },
      "steps": [
        {
          "name": "get_supplier_data",
          "type": "query",
          "config": {
            "data_source": "suppliers",
            "dimensions": [
              {
                "expression": "supplier_id",
                "alias": "supplier_id"
              },
              {
                "expression": "supplier_name",
                "alias": "supplier_name"
              },
              {
                "expression": "contact_person",
                "alias": "contact_person_default"
              },
              {
                "expression": "phone",
                "alias": "phone_default"
              }
            ]
          }
        },
        {
          "name": "unpivot_contacts",
          "type": "unpivot",
          "config": {
            "source": "get_supplier_data",
            "id_vars": [
              "supplier_id",
              "supplier_name"
            ],
            "value_vars": [
              "contact_person_default",
              "phone_default"
            ],
            "var_name": "contact_type",
            "value_name": "contact_info"
          }
        }
      ],
      "output": "unpivot_contacts"
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
            "supplier_id": 1,
            "supplier_name": "华南电子配件厂",
            "contact_type": "contact_person_default",
            "contact_info": "王经理"
        },
        {
            "supplier_id": 2,
            "supplier_name": "长三角服装集团",
            "contact_type": "contact_person_default",
            "contact_info": "李总"
        },
        {
            "supplier_id": 3,
            "supplier_name": "硅谷创新科技",
            "contact_type": "contact_person_default",
            "contact_info": "Mr. Smith"
        },   
        {
            "supplier_id": 1,
            "supplier_name": "华南电子配件厂",
            "contact_type": "phone_default",
            "contact_info": "0755-88888888"
        },
        {
            "supplier_id": 3,
            "supplier_name": "硅谷创新科技",
            "contact_type": "phone_default",
            "contact_info": "1-800-555-0100"
        },
      
    ],
    "metadata": {
        "name": "UnpivotSupplierContacts",
        "description": "将供应商表中的多个地区联系人字段转换为长表格式",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "unpivot",
            "supplier",
            "contact"
        ]
    },
    "execution_info": {
        "total_time": 0.0059909820556640625,
        "row_count": 14,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "get_supplier_data",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 7,
            "execution_time": 0.002991914749145508,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "unpivot_contacts",
            "step_type": "unpivot",
            "status": "completed",
            "data": null,
            "row_count": 14,
            "execution_time": 0.0029990673065185547,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

--- 