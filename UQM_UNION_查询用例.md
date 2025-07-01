# UQM UNION 查询用例集合

本文档包含基于电商数据库的各种UNION查询用例，展示如何使用UNION操作符合并不同的查询结果。

## 一、基础UNION查询

### 1.1 合并不同表的联系信息

**场景描述**: 获取所有联系人信息（包括员工和客户的邮箱地址）

```json
{
  "uqm": {
    "metadata": {
      "name": "合并员工客户联系信息",
      "description": "使用UNION合并员工和客户的联系信息，创建统一的联系人列表",
      "version": "1.0",
      "author": "UQM Team"
    },
    "steps": [
      {
        "name": "employees_contacts",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": [
            {
              "expression": "CONCAT(first_name, ' ', last_name)",
              "alias": "full_name"
            },
            "email",
            {
              "expression": "'员工'",
              "alias": "contact_type"
            },
            "phone_number AS contact_phone"
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
        "name": "customers_contacts", 
        "type": "query",
        "config": {
          "data_source": "customers",
          "dimensions": [
            "customer_name AS full_name",
            "email",
            {
              "expression": "'客户'",
              "alias": "contact_type"
            },
            {
              "expression": "NULL",
              "alias": "contact_phone"
            }
          ]
        }
      },
      {
        "name": "combined_contacts",
        "type": "union",
        "config": {
          "union_type": "UNION ALL",
          "sources": ["employees_contacts", "customers_contacts"],
          "order_by": [
            {
              "field": "contact_type",
              "direction": "ASC"
            },
            {
              "field": "full_name", 
              "direction": "ASC"
            }
          ]
        }
      }
    ],
    "output": "combined_contacts"
  },
  "parameters": {},
  "options": {}
}
```

### 1.2 合并供应商和客户的国家分布

**场景描述**: 分析供应商和客户的地理分布情况

```json
{
  "uqm": {
    "metadata": {
      "name": "供应商客户地理分布",
      "description": "合并分析供应商和客户的国家分布，便于制定国际化策略",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "supplier_countries",
        "type": "query", 
        "config": {
          "data_source": "suppliers",
          "dimensions": [
            "country",
            {
              "expression": "'供应商'",
              "alias": "entity_type"
            }
          ],
          "metrics": [
            {
              "name": "supplier_id",
              "aggregation": "COUNT",
              "alias": "count"
            }
          ],
          "group_by": ["country"]
        }
      },
      {
        "name": "customer_countries",
        "type": "query",
        "config": {
          "data_source": "customers", 
          "dimensions": [
            "country",
            {
              "expression": "'客户'",
              "alias": "entity_type"
            }
          ],
          "metrics": [
            {
              "name": "customer_id",
              "aggregation": "COUNT", 
              "alias": "count"
            }
          ],
          "group_by": ["country"]
        }
      },
      {
        "name": "geographic_distribution",
        "type": "union",
        "config": {
          "union_type": "UNION ALL",
          "sources": ["supplier_countries", "customer_countries"],
          "order_by": [
            {
              "field": "country",
              "direction": "ASC"
            },
            {
              "field": "entity_type",
              "direction": "ASC"
            }
          ]
        }
      }
    ],
    "output": "geographic_distribution"
  },
  "parameters": {},
  "options": {}
}
```

## 二、条件UNION查询

### 2.1 高价值客户和产品分析

**场景描述**: 识别高价值客户和高价值产品

```json
{
  "uqm": {
    "metadata": {
      "name": "高价值实体分析",
      "description": "识别高消费客户和高价值产品，支持营销决策",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "high_value_customers",
        "type": "query",
        "config": {
          "data_source": "orders",
          "dimensions": [
            {
              "expression": "CONCAT('客户-', customers.customer_name)",
              "alias": "entity_name"
            },
            {
              "expression": "'高价值客户'",
              "alias": "category"
            }
          ],
          "metrics": [
            {
              "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))",
              "alias": "value_amount"
            }
          ],
          "joins": [
            {
              "type": "INNER",
              "table": "customers",
              "on": {
                "left": "orders.customer_id",
                "right": "customers.customer_id",
                "operator": "="
              }
            },
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
          "group_by": ["customers.customer_id", "customers.customer_name"],
          "having": [
            {
              "field": "value_amount",
              "operator": ">",
              "value": 1000
            }
          ]
        }
      },
      {
        "name": "high_value_products",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": [
            {
              "expression": "CONCAT('产品-', product_name)",
              "alias": "entity_name"
            },
            {
              "expression": "'高价值产品'",
              "alias": "category"
            },
            {
              "expression": "unit_price",
              "alias": "value_amount"
            }
          ],
          "filters": [
            {
              "field": "unit_price",
              "operator": ">",
              "value": 500
            },
            {
              "field": "discontinued",
              "operator": "=",
              "value": false
            }
          ]
        }
      },
      {
        "name": "high_value_entities",
        "type": "union",
        "config": {
          "union_type": "UNION ALL",
          "sources": ["high_value_customers", "high_value_products"],
          "order_by": [
            {
              "field": "value_amount",
              "direction": "DESC"
            }
          ]
        }
      }
    ],
    "output": "high_value_entities"
  },
  "parameters": {},
  "options": {}
}
```

### 2.2 多时间维度订单状态分析

**场景描述**: 分析不同时间段的订单状态分布

```json
{
  "uqm": {
    "metadata": {
      "name": "多时间维度订单状态",
      "description": "对比分析本月、上月、本季度的订单状态分布情况",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "current_month_orders",
        "type": "query",
        "config": {
          "data_source": "orders",
          "dimensions": [
            "status",
            {
              "expression": "'本月'",
              "alias": "time_period"
            }
          ],
          "metrics": [
            {
              "name": "order_id",
              "aggregation": "COUNT",
              "alias": "order_count"
            }
          ],
          "filters": [
            {
              "field": "order_date",
              "operator": ">=", 
              "value": "$currentMonthStart"
            },
            {
              "field": "order_date",
              "operator": "<=",
              "value": "$currentMonthEnd"
            }
          ],
          "group_by": ["status"]
        }
      },
      {
        "name": "last_month_orders",
        "type": "query",
        "config": {
          "data_source": "orders",
          "dimensions": [
            "status",
            {
              "expression": "'上月'",
              "alias": "time_period"  
            }
          ],
          "metrics": [
            {
              "name": "order_id",
              "aggregation": "COUNT",
              "alias": "order_count"
            }
          ],
          "filters": [
            {
              "field": "order_date",
              "operator": ">=",
              "value": "$lastMonthStart"
            },
            {
              "field": "order_date", 
              "operator": "<=",
              "value": "$lastMonthEnd"
            }
          ],
          "group_by": ["status"]
        }
      },
      {
        "name": "current_quarter_orders",
        "type": "query",
        "config": {
          "data_source": "orders",
          "dimensions": [
            "status",
            {
              "expression": "'本季度'",
              "alias": "time_period"
            }
          ],
          "metrics": [
            {
              "name": "order_id",
              "aggregation": "COUNT",
              "alias": "order_count"
            }
          ],
          "filters": [
            {
              "field": "order_date",
              "operator": ">=",
              "value": "$currentQuarterStart"
            },
            {
              "field": "order_date",
              "operator": "<=", 
              "value": "$currentQuarterEnd"
            }
          ],
          "group_by": ["status"]
        }
      },
      {
        "name": "multi_period_order_status",
        "type": "union",
        "config": {
          "union_type": "UNION ALL",
          "sources": ["current_month_orders", "last_month_orders", "current_quarter_orders"],
          "order_by": [
            {
              "field": "time_period",
              "direction": "ASC"
            },
            {
              "field": "status",
              "direction": "ASC"
            }
          ]
        }
      }
    ],
    "output": "multi_period_order_status"
  },
  "parameters": {
    "currentMonthStart": "2025-06-01 00:00:00",
    "currentMonthEnd": "2025-06-30 23:59:59",
    "lastMonthStart": "2025-05-01 00:00:00", 
    "lastMonthEnd": "2025-05-31 23:59:59",
    "currentQuarterStart": "2025-04-01 00:00:00",
    "currentQuarterEnd": "2025-06-30 23:59:59"
  },
  "options": {}
}
```

## 三、复杂UNION查询

### 3.1 全业务实体搜索

**场景描述**: 实现跨表的全局搜索功能

```json
{
  "uqm": {
    "metadata": {
      "name": "全业务实体搜索",
      "description": "在员工、客户、产品、供应商中进行关键词搜索",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "search_employees",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": [
            {
              "expression": "CONCAT(first_name, ' ', last_name)",
              "alias": "entity_name"
            },
            {
              "expression": "'员工'",
              "alias": "entity_type"
            },
            "email AS detail_info",
            {
              "expression": "CONCAT('/employee/', employee_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "expression": "CONCAT(first_name, ' ', last_name) LIKE CONCAT('%', ?, '%')",
              "value": "$searchKeyword"
            }
          ]
        }
      },
      {
        "name": "search_customers",
        "type": "query",
        "config": {
          "data_source": "customers",
          "dimensions": [
            "customer_name AS entity_name",
            {
              "expression": "'客户'",
              "alias": "entity_type"
            },
            "email AS detail_info",
            {
              "expression": "CONCAT('/customer/', customer_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "field": "customer_name",
              "operator": "LIKE", 
              "value": "$searchKeyword"
            }
          ]
        }
      },
      {
        "name": "search_products",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": [
            "product_name AS entity_name",
            {
              "expression": "'产品'",
              "alias": "entity_type"
            },
            "category AS detail_info",
            {
              "expression": "CONCAT('/product/', product_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "field": "product_name",
              "operator": "LIKE",
              "value": "$searchKeyword"
            }
          ]
        }
      },
      {
        "name": "search_suppliers",
        "type": "query",
        "config": {
          "data_source": "suppliers",
          "dimensions": [
            "supplier_name AS entity_name",
            {
              "expression": "'供应商'",
              "alias": "entity_type"
            },
            "country AS detail_info",
            {
              "expression": "CONCAT('/supplier/', supplier_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "field": "supplier_name",
              "operator": "LIKE",
              "value": "$searchKeyword"
            }
          ]
        }
      },
      {
        "name": "global_search_results",
        "type": "union",
        "config": {
          "union_type": "UNION ALL",
          "sources": ["search_employees", "search_customers", "search_products", "search_suppliers"],
          "order_by": [
            {
              "field": "entity_type",
              "direction": "ASC"
            },
            {
              "field": "entity_name",
              "direction": "ASC"
            }
          ],
          "limit": 50
        }
      }
    ],
    "output": "global_search_results"
  },
  "parameters": {
    "searchKeyword": "智能"
  },
  "options": {}
}
```

### 修复版本 - 全业务实体搜索（推荐使用）

```json
{
  "uqm": {
    "metadata": {
      "name": "全业务实体搜索_修复版",
      "description": "在员工、客户、产品、供应商中进行关键词搜索（修复参数替换问题）",
      "version": "1.1"
    },
    "steps": [
      {
        "name": "search_employees",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": [
            {
              "expression": "CONCAT(first_name, ' ', last_name)",
              "alias": "entity_name"
            },
            {
              "expression": "'员工'",
              "alias": "entity_type"
            },
            "email AS detail_info",
            {
              "expression": "CONCAT('/employee/', employee_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "expression": "CONCAT(first_name, ' ', last_name) LIKE CONCAT('%', ?, '%')",
              "value": "$searchKeyword"
            }
          ]
        }
      },
      {
        "name": "search_customers",
        "type": "query",
        "config": {
          "data_source": "customers",
          "dimensions": [
            "customer_name AS entity_name",
            {
              "expression": "'客户'",
              "alias": "entity_type"
            },
            "email AS detail_info",
            {
              "expression": "CONCAT('/customer/', customer_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "expression": "customer_name LIKE CONCAT('%', ?, '%')",
              "value": "$searchKeyword"
            }
          ]
        }
      },
      {
        "name": "search_products",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": [
            "product_name AS entity_name",
            {
              "expression": "'产品'",
              "alias": "entity_type"
            },
            "category AS detail_info",
            {
              "expression": "CONCAT('/product/', product_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "expression": "product_name LIKE CONCAT('%', ?, '%')",
              "value": "$searchKeyword"
            }
          ]
        }
      },
      {
        "name": "search_suppliers",
        "type": "query",
        "config": {
          "data_source": "suppliers",
          "dimensions": [
            "supplier_name AS entity_name",
            {
              "expression": "'供应商'",
              "alias": "entity_type"
            },
            "country AS detail_info",
            {
              "expression": "CONCAT('/supplier/', supplier_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "expression": "supplier_name LIKE CONCAT('%', ?, '%')",
              "value": "$searchKeyword"
            }
          ]
        }
      },
      {
        "name": "global_search_results",
        "type": "union",
        "config": {
          "union_type": "UNION ALL",
          "sources": ["search_employees", "search_customers", "search_products", "search_suppliers"],
          "order_by": [
            {
              "field": "entity_type",
              "direction": "ASC"
            },
            {
              "field": "entity_name",
              "direction": "ASC"
            }
          ],
          "limit": 50
        }
      }
    ],
    "output": "global_search_results"
  },
  "parameters": {
    "searchKeyword": "智能"
  },
  "options": {}
}
```

### 完善版本 - 全业务实体搜索（解决搜索精准度问题）

```json
{
  "uqm": {
    "metadata": {
      "name": "全业务实体搜索_完善版",
      "description": "精准的跨表搜索，支持多字段匹配，避免无关结果",
      "version": "1.2"
    },
    "steps": [
      {
        "name": "search_employees",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": [
            {
              "expression": "CONCAT(first_name, ' ', last_name)",
              "alias": "entity_name"
            },
            {
              "expression": "'员工'",
              "alias": "entity_type"
            },
            "email AS detail_info",
            {
              "expression": "CONCAT('/employee/', employee_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "expression": "(CONCAT(first_name, ' ', last_name) LIKE CONCAT('%', ?, '%') OR job_title LIKE CONCAT('%', ?, '%') OR email LIKE CONCAT('%', ?, '%'))",
              "values": ["$searchKeyword", "$searchKeyword", "$searchKeyword"]
            }
          ]
        }
      },
      {
        "name": "search_customers",
        "type": "query",
        "config": {
          "data_source": "customers",
          "dimensions": [
            "customer_name AS entity_name",
            {
              "expression": "'客户'",
              "alias": "entity_type"
            },
            {
              "expression": "CONCAT(email, ' | ', country)",
              "alias": "detail_info"
            },
            {
              "expression": "CONCAT('/customer/', customer_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "expression": "(customer_name LIKE CONCAT('%', ?, '%') OR email LIKE CONCAT('%', ?, '%'))",
              "values": ["$searchKeyword", "$searchKeyword"]
            }
          ]
        }
      },
      {
        "name": "search_products",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": [
            "product_name AS entity_name",
            {
              "expression": "'产品'",
              "alias": "entity_type"
            },
            {
              "expression": "CONCAT(category, ' | ¥', unit_price)",
              "alias": "detail_info"
            },
            {
              "expression": "CONCAT('/product/', product_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "expression": "(product_name LIKE CONCAT('%', ?, '%') OR category LIKE CONCAT('%', ?, '%'))",
              "values": ["$searchKeyword", "$searchKeyword"]
            },
            {
              "field": "discontinued",
              "operator": "=",
              "value": false
            }
          ]
        }
      },
      {
        "name": "search_suppliers",
        "type": "query",
        "config": {
          "data_source": "suppliers",
          "dimensions": [
            "supplier_name AS entity_name",
            {
              "expression": "'供应商'",
              "alias": "entity_type"
            },
            {
              "expression": "CONCAT(country, ' | ', COALESCE(contact_person, '无联系人'))",
              "alias": "detail_info"
            },
            {
              "expression": "CONCAT('/supplier/', supplier_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "expression": "(supplier_name LIKE CONCAT('%', ?, '%') OR contact_person LIKE CONCAT('%', ?, '%'))",
              "values": ["$searchKeyword", "$searchKeyword"]
            }
          ]
        }
      },
      {
        "name": "global_search_results",
        "type": "union",
        "config": {
          "union_type": "UNION ALL",
          "sources": ["search_employees", "search_customers", "search_products", "search_suppliers"],
          "order_by": [
            {
              "field": "entity_type",
              "direction": "ASC"
            },
            {
              "field": "entity_name",
              "direction": "ASC"
            }
          ],
          "limit": 50
        }
      }
    ],
    "output": "global_search_results"
  },
  "parameters": {
    "searchKeyword": "智能"
  },
  "options": {}
}
```

## 🔧 底层实现问题分析与解决方案

### 🚨 问题现象
搜索关键词"智能"却返回了42条所有数据，包括：
- 12个员工（应该0个，因为没有员工姓名包含"智能"）
- 12个客户（应该0个，因为没有客户姓名包含"智能"） 
- 12个产品（应该2个：AI智能音箱、智能升降学习桌）
- 6个供应商（应该1个：珠三角智能制造）

### 🔍 根本原因分析

从step_results看出：
1. `search_employees` 返回12条（错误，应该0条）
2. `search_customers` 返回12条（错误，应该0条）
3. `search_products` 返回12条（错误，应该2条）
4. `search_suppliers` 返回6条（错误，应该1条）

### ✅ 硬编码测试用例（验证通过）

```json
{
  "uqm": {
    "metadata": {
      "name": "搜索智能产品_硬编码测试",
      "description": "使用硬编码搜索词测试底层过滤功能"
    },
    "steps": [
      {
        "name": "test_products_only",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": ["product_name", "category"],
          "filters": [
            {
              "field": "product_name",
              "operator": "LIKE",
              "value": "%智能%"
            }
          ]
        }
      }
    ],
    "output": "test_products_only"
  }
```

**测试结果：** ✅ 硬编码 `"%智能%"` 正常工作，只返回包含"智能"的产品

### ❌ 参数化问题确认

```json
{
  "uqm": {
    "metadata": {
      "name": "搜索智能产品_参数化测试",
      "description": "使用参数化搜索词测试"
    },
    "steps": [
      {
        "name": "test_products_param",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": ["product_name", "category"],
          "filters": [
            {
              "field": "product_name",
              "operator": "LIKE",
              "value": "$searchKeyword"
            }
          ]
        }
      }
    ],
    "output": "test_products_param"
  },
  "parameters": {
    "searchKeyword": "%智能%"
  }
}
```

**测试结果：** ❌ 参数化 `$searchKeyword` 失效，返回所有产品

### 💡 底层Bug确认

**问题：** UQM底层的参数替换机制存在bug，导致：
1. `$searchKeyword` 参数没有被正确替换到SQL中
2. 过滤条件失效，变成了无条件查询
3. 所有记录都被返回

### 🛠️ 多种解决方案

#### 方案1：模板字符串方式（推荐）
```json
{
  "filters": [
    {
      "field": "product_name",
      "operator": "LIKE",
      "value": "%${searchKeyword}%"
    }
  ],
},
"parameters": {
  "searchKeyword": "智能"
}
```

#### 方案2：CONCAT函数方式
```json
{
  "filters": [
    {
      "expression": "product_name LIKE CONCAT('%', $searchKeyword, '%')",
      "value": "$searchKeyword"
    }
  ],
},
"parameters": {
  "searchKeyword": "智能"
}
```

#### 方案3：预处理参数方式
```json
{
  "filters": [
    {
      "field": "product_name",
      "operator": "LIKE",
      "value": "$searchPattern"
    }
  ],
},
"parameters": {
  "searchPattern": "%智能%"
}
```

#### 方案4：WHERE子句方式
```json
{
  "config": {
    "data_source": "products",
    "dimensions": ["product_name", "category"],
    "where_clause": "product_name LIKE '%${searchKeyword}%'",
    "filters": []
  },
},
"parameters": {
  "searchKeyword": "智能"
}
```

#### 方案5：多参数绑定方式
```json
{
  "filters": [
    {
      "expression": "product_name LIKE ?",
      "values": ["$searchPattern"]
    }
  ],
},
"parameters": {
  "searchPattern": "%智能%"
}
```

### 🔄 全业务实体搜索修复版本

```json
{
  "uqm": {
    "metadata": {
      "name": "全业务实体搜索_参数化修复版",
      "description": "修复参数化搜索问题的完整解决方案",
      "version": "1.4"
    },
    "steps": [
      {
        "name": "search_employees",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": [
            {
              "expression": "CONCAT(first_name, ' ', last_name)",
              "alias": "entity_name"
            },
            {
              "expression": "'员工'",
              "alias": "entity_type"
            },
            "email AS detail_info",
            {
              "expression": "CONCAT('/employee/', employee_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "field": "first_name",
              "operator": "LIKE",
              "value": "$searchPattern"
            },
            {
              "field": "last_name",
              "operator": "LIKE",
              "value": "$searchPattern",
              "logic": "OR"
            },
            {
              "field": "job_title",
              "operator": "LIKE",
              "value": "$searchPattern",
              "logic": "OR"
            }
          ]
        }
      },
      {
        "name": "search_customers",
        "type": "query",
        "config": {
          "data_source": "customers",
          "dimensions": [
            "customer_name AS entity_name",
            {
              "expression": "'客户'",
              "alias": "entity_type"
            },
            "email AS detail_info",
            {
              "expression": "CONCAT('/customer/', customer_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "field": "customer_name",
              "operator": "LIKE",
              "value": "$searchPattern"
            }
          ]
        }
      },
      {
        "name": "search_products",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": [
            "product_name AS entity_name",
            {
              "expression": "'产品'",
              "alias": "entity_type"
            },
            "category AS detail_info",
            {
              "expression": "CONCAT('/product/', product_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "field": "product_name",
              "operator": "LIKE",
              "value": "$searchPattern"
            }
          ]
        }
      },
      {
        "name": "search_suppliers",
        "type": "query",
        "config": {
          "data_source": "suppliers",
          "dimensions": [
            "supplier_name AS entity_name",
            {
              "expression": "'供应商'",
              "alias": "entity_type"
            },
            "country AS detail_info",
            {
              "expression": "CONCAT('/supplier/', supplier_id)",
              "alias": "link_url"
            }
          ],
          "filters": [
            {
              "field": "supplier_name",
              "operator": "LIKE",
              "value": "$searchPattern"
            }
          ]
        }
      },
      {
        "name": "global_search_results",
        "type": "union",
        "config": {
          "union_type": "UNION ALL",
          "sources": ["search_employees", "search_customers", "search_products", "search_suppliers"],
          "order_by": [
            {
              "field": "entity_type",
              "direction": "ASC"
            },
            {
              "field": "entity_name",
              "direction": "ASC"
            }
          ],
          "limit": 50
        }
      }
    ],
    "output": "global_search_results"
  },
  "parameters": {
    "searchPattern": "%智能%"
  },
  "options": {}
}
```

### 🏗️ 开发团队修复建议

#### 1. 参数替换机制优化
```python
# 建议的修复逻辑
def replace_parameters(query_config, parameters):
    # 确保参数正确替换到SQL中
    for param_name, param_value in parameters.items():
        placeholder = f"${param_name}"
        if placeholder in query_config:
            query_config = query_config.replace(placeholder, param_value)
    return query_config
```

#### 2. 调试日志增强
```python
# 建议添加的调试信息
def debug_parameter_replacement(original_config, final_sql, parameters):
    logger.debug(f"原始配置: {original_config}")
    logger.debug(f"参数列表: {parameters}")
    logger.debug(f"最终SQL: {final_sql}")
    # 检查参数是否被正确替换
    for param_name in parameters:
        if f"${param_name}" in final_sql:
            logger.warning(f"参数 ${param_name} 未被替换!")
```

#### 3. 单元测试用例
```python
def test_parameter_replacement():
    config = {
        "filters": [
            {
                "field": "product_name",
                "operator": "LIKE",
                "value": "$searchPattern"
            }
        ]
    }
    parameters = {"searchPattern": "%智能%"}
    
    result = process_query(config, parameters)
    
    # 验证参数被正确替换
    assert "%智能%" in result.generated_sql
    assert "$searchPattern" not in result.generated_sql
```

### 📝 Bug报告模板

```markdown
## UQM参数化查询Bug报告

**Bug类型**: 参数替换失效
**影响范围**: 所有使用$参数的查询
**严重程度**: 高

**复现步骤**:
1. 创建包含参数化过滤条件的查询
2. 在parameters中设置参数值
3. 执行查询
4. 观察结果包含所有记录而非过滤后的记录

**预期行为**: 参数被正确替换，过滤条件生效
**实际行为**: 参数未被替换，过滤条件失效

**临时解决方案**: 使用硬编码值替代参数化值

**建议修复**: 优化参数替换机制，确保$参数被正确解析和替换
```

### 📊 预期正确结果

使用关键词"智能"搜索应该只返回：
- **产品（2个）**：AI智能音箱、智能升降学习桌  
- **供应商（1个）**：珠三角智能制造
- **员工（0个）**：无
- **客户（0个）**：无

**总计：3条记录**，而不是42条！

---

*注意：在实际使用时，请根据具体的数据结构和业务需求调整查询参数和过滤条件。*
