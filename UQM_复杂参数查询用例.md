# UQM 复杂参数查询用例测试

本文档包含了用于测试 UQM 框架对复杂查询条件支持情况的测试用例，主要涉及嵌套的 AND、OR、IN、NOT IN、BETWEEN 等复杂条件组合。

## 1. 嵌套 AND/OR 条件查询

### 1.1 复杂员工筛选查询
**场景**: 查询满足以下条件的员工：
- (薪资 > 20000 AND 部门是信息技术部) OR (薪资 > 30000 AND 部门是销售部)
- AND 入职日期在 2022年之后

```json
{
  "uqm": {
    "metadata": {
      "name": "复杂员工筛选查询",
      "description": "测试嵌套AND/OR条件的员工筛选",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "complex_employee_filter",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": [
            "employees.employee_id",
            "employees.first_name",
            "employees.last_name",
            "employees.salary",
            "employees.hire_date",
            "departments.name AS department_name"
          ],
          "joins": [
            {
              "type": "INNER",
              "table": "departments",
              "on": {
                "left": "employees.department_id",
                "right": "departments.department_id",
                "operator": "="
              }
            }
          ],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "logic": "OR",
                  "conditions": [
                    {
                      "logic": "AND",
                      "conditions": [
                        {
                          "field": "employees.salary",
                          "operator": ">",
                          "value": "$minItSalary"
                        },
                        {
                          "field": "departments.name",
                          "operator": "=",
                          "value": "$itDepartment"
                        }
                      ]
                    },
                    {
                      "logic": "AND",
                      "conditions": [
                        {
                          "field": "employees.salary",
                          "operator": ">",
                          "value": "$minSalesSalary"
                        },
                        {
                          "field": "departments.name",
                          "operator": "=",
                          "value": "$salesDepartment"
                        }
                      ]
                    }
                  ]
                },
                {
                  "field": "employees.hire_date",
                  "operator": ">",
                  "value": "$hireAfterDate"
                }
              ]
            }
          ]
        }
      }
    ],
    "output": "complex_employee_filter"
  },
  "parameters": {
    "minItSalary": 20000,
    "itDepartment": "信息技术部",
    "minSalesSalary": 30000,
    "salesDepartment": "销售部",
    "hireAfterDate": "2022-01-01"
  },
  "options": {}
}
```

### 1.2 多条件客户分析查询
**场景**: 查询满足以下条件的客户：
- (国家是中国 AND 客户分层是VIP) OR (国家是美国 AND 注册日期在2023年后)
- AND 不在指定城市列表中

```json
{
  "uqm": {
    "metadata": {
      "name": "多条件客户分析查询",
      "description": "测试复杂客户筛选条件",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "complex_customer_analysis",
        "type": "query",
        "config": {
          "data_source": "customers",
          "dimensions": [
            "customer_id",
            "customer_name",
            "email",
            "country",
            "city",
            "registration_date",
            "customer_segment"
          ],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "logic": "OR",
                  "conditions": [
                    {
                      "logic": "AND",
                      "conditions": [
                        {
                          "field": "country",
                          "operator": "=",
                          "value": "$targetCountry1"
                        },
                        {
                          "field": "customer_segment",
                          "operator": "=",
                          "value": "$vipSegment"
                        }
                      ]
                    },
                    {
                      "logic": "AND",
                      "conditions": [
                        {
                          "field": "country",
                          "operator": "=",
                          "value": "$targetCountry2"
                        },
                        {
                          "field": "registration_date",
                          "operator": ">",
                          "value": "$registrationAfter"
                        }
                      ]
                    }
                  ]
                },
                {
                  "field": "city",
                  "operator": "NOT IN",
                  "value": "$excludedCities"
                }
              ]
            }
          ]
        }
      }
    ],
    "output": "complex_customer_analysis"
  },
  "parameters": {
    "targetCountry1": "中国",
    "vipSegment": "VIP",
    "targetCountry2": "美国",
    "registrationAfter": "2023-01-01",
    "excludedCities": ["北京", "上海", "纽约", "洛杉矶"]
  },
  "options": {}
}
```

## 2. 复杂范围和列表条件

### 2.1 订单状态和金额范围查询
**场景**: 查询满足以下条件的订单：
- 订单状态在指定列表中 AND (订单金额在某个范围 OR 运费为0)

## 方案1：使用JOIN聚合替代子查询
```json
{
  "uqm": {
    "metadata": {
      "name": "订单状态和金额范围查询-JOIN方案",
      "description": "使用JOIN和聚合函数替代子查询",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "complex_order_filter",
        "type": "query",
        "config": {
          "data_source": "orders",
          "dimensions": [
            "orders.order_id",
            "orders.customer_id",
            "orders.order_date",
            "orders.status",
            "orders.shipping_fee",
            "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount)) AS total_amount"
          ],
          "joins": [
            {
              "type": "LEFT",
              "table": "order_items",
              "on": {
                "left": "orders.order_id",
                "right": "order_items.order_id",
                "operator": "="
              }
            }
          ],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "field": "orders.status",
                  "operator": "IN",
                  "value": "$allowedStatuses"
                },
                {
                  "logic": "OR",
                  "conditions": [
                    {
                      "field": "orders.shipping_fee",
                      "operator": "=",
                      "value": "$freeShipping"
                    }
                  ]
                }
              ]
            }
          ],
          "group_by": [
            "orders.order_id",
            "orders.customer_id", 
            "orders.order_date",
            "orders.status",
            "orders.shipping_fee"
          ],
          "having": [
            {
              "field": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))",
              "operator": "BETWEEN",
              "value": {
                "min": "$minAmount",
                "max": "$maxAmount"
              }
            }
          ]
        }
      }
    ],
    "output": "complex_order_filter"
  },
  "parameters": {
    "allowedStatuses": ["已完成", "已发货", "处理中"],
    "minAmount": 500,
    "maxAmount": 2000,
    "freeShipping": 0
  },
  "options": {}
}
```

## 方案2：使用子查询替代计算字段
```json
{
  "uqm": {
    "metadata": {
      "name": "订单状态和金额范围查询-子查询方案",
      "description": "直接在WHERE条件中使用子查询",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "complex_order_filter",
        "type": "query",
        "config": {
          "data_source": "orders",
          "dimensions": [
            "orders.order_id",
            "orders.customer_id",
            "orders.order_date",
            "orders.status",
            "orders.shipping_fee"
          ],
          "calculated_fields": [
            {
              "name": "order_total",
              "expression": "(SELECT SUM(quantity * unit_price * (1 - discount)) FROM order_items WHERE order_items.order_id = orders.order_id)",
              "alias": "total_amount"
            }
          ],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "field": "orders.status",
                  "operator": "IN",
                  "value": "$allowedStatuses"
                },
                {
                  "logic": "OR",
                  "conditions": [
                    {
                      "field": "(SELECT SUM(quantity * unit_price * (1 - discount)) FROM order_items WHERE order_items.order_id = orders.order_id)",
                      "operator": "BETWEEN",
                      "value": {
                        "min": "$minAmount",
                        "max": "$maxAmount"
                      }
                    },
                    {
                      "field": "orders.shipping_fee",
                      "operator": "=",
                      "value": "$freeShipping"
                    }
                  ]
                }
              ]
            }
          ]
        }
      }
    ],
    "output": "complex_order_filter"
  },
  "parameters": {
    "allowedStatuses": ["已完成", "已发货", "处理中"],
    "minAmount": 500,
    "maxAmount": 2000,
    "freeShipping": 0
  },
  "options": {}
}
```

## 方案3：原始结构使用HAVING版本
```json
{
  "uqm": {
    "metadata": {
      "name": "订单状态和金额范围查询-HAVING版本",
      "description": "保持原有结构，使用HAVING替代WHERE条件",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "complex_order_filter",
        "type": "query",
        "config": {
          "data_source": "orders",
          "dimensions": [
            "orders.order_id",
            "orders.customer_id",
            "orders.order_date",
            "orders.status",
            "orders.shipping_fee"
          ],
          "calculated_fields": [
            {
              "name": "order_total",
              "expression": "(SELECT SUM(quantity * unit_price * (1 - discount)) FROM order_items WHERE order_items.order_id = orders.order_id)",
              "alias": "total_amount"
            }
          ],
          "joins": [
            {
              "type": "LEFT",
              "table": "order_items",
              "on": {
                "left": "orders.order_id",
                "right": "order_items.order_id",
                "operator": "="
              }
            }
          ],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "field": "orders.status",
                  "operator": "IN",
                  "value": "$allowedStatuses"
                },
                {
                  "field": "orders.shipping_fee",
                  "operator": "=",
                  "value": "$freeShipping"
                }
              ]
            }
          ],
          "group_by": [
            "orders.order_id",
            "orders.customer_id",
            "orders.order_date", 
            "orders.status",
            "orders.shipping_fee"
          ],
          "having": [
            {
              "field": "(SELECT SUM(quantity * unit_price * (1 - discount)) FROM order_items WHERE order_items.order_id = orders.order_id)",
              "operator": "BETWEEN",
              "value": {
                "min": "$minAmount",
                "max": "$maxAmount"
              }
            }
          ]
        }
      }
    ],
    "output": "complex_order_filter"
  },
  "parameters": {
    "allowedStatuses": ["已完成", "已发货", "处理中"],
    "minAmount": 500,
    "maxAmount": 2000,
    "freeShipping": 0
  },
  "options": {}
}
```

## 方案4：使用EXISTS子查询保持逻辑完整性
```json
{
  "uqm": {
    "metadata": {
      "name": "订单状态和金额范围查询-EXISTS方案",
      "description": "使用EXISTS子查询保持原始逻辑结构",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "complex_order_filter",
        "type": "query",
        "config": {
          "data_source": "orders",
          "dimensions": [
            "orders.order_id",
            "orders.customer_id",
            "orders.order_date",
            "orders.status",
            "orders.shipping_fee"
          ],
          "calculated_fields": [
            {
              "name": "order_total",
              "expression": "(SELECT SUM(quantity * unit_price * (1 - discount)) FROM order_items WHERE order_items.order_id = orders.order_id)",
              "alias": "total_amount"
            }
          ],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "field": "orders.status",
                  "operator": "IN",
                  "value": "$allowedStatuses"
                },
                {
                  "logic": "OR",
                  "conditions": [
                    {
                      "field": "EXISTS",
                      "operator": "=",
                      "value": "(SELECT 1 FROM order_items oi WHERE oi.order_id = orders.order_id HAVING SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) BETWEEN $minAmount AND $maxAmount)"
                    },
                    {
                      "field": "orders.shipping_fee",
                      "operator": "=",
                      "value": "$freeShipping"
                    }
                  ]
                }
              ]
            }
          ]
        }
      }
    ],
    "output": "complex_order_filter"
  },
  "parameters": {
    "allowedStatuses": ["已完成", "已发货", "处理中"],
    "minAmount": 500,
    "maxAmount": 2000,
    "freeShipping": 0
  },
  "options": {}
}
```

## 方案5：分步查询方案（推荐）
```json
{
  "uqm": {
    "metadata": {
      "name": "订单状态和金额范围查询-分步方案",
      "description": "使用两个步骤分别处理不同条件，逻辑清晰且性能较好",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "orders_with_amount",
        "type": "query",
        "config": {
          "data_source": "orders",
          "dimensions": [
            "orders.order_id",
            "orders.customer_id",
            "orders.order_date",
            "orders.status",
            "orders.shipping_fee",
            "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount)) AS total_amount"
          ],
          "joins": [
            {
              "type": "LEFT",
              "table": "order_items",
              "on": {
                "left": "orders.order_id",
                "right": "order_items.order_id",
                "operator": "="
              }
            }
          ],
          "filters": [
            {
              "field": "orders.status",
              "operator": "IN",
              "value": "$allowedStatuses"
            }
          ],
          "group_by": [
            "orders.order_id",
            "orders.customer_id",
            "orders.order_date",
            "orders.status",
            "orders.shipping_fee"
          ]
        }
      },
      {
        "name": "final_filtered_orders",
        "type": "query",
        "config": {
          "data_source": "{{orders_with_amount}}",
          "dimensions": [
            "order_id",
            "customer_id",
            "order_date",
            "status",
            "shipping_fee",
            "total_amount"
          ],
          "filters": [
            {
              "logic": "OR",
              "conditions": [
                {
                  "field": "total_amount",
                  "operator": "BETWEEN",
                  "value": {
                    "min": "$minAmount",
                    "max": "$maxAmount"
                  }
                },
                {
                  "field": "shipping_fee",
                  "operator": "=",
                  "value": "$freeShipping"
                }
              ]
            }
          ]
        }
      }
    ],
    "output": "final_filtered_orders"
  },
  "parameters": {
    "allowedStatuses": ["已完成", "已发货", "处理中"],
    "minAmount": 500,
    "maxAmount": 2000,
    "freeShipping": 0
  },
  "options": {}
}
```

## 方案总结对比：

### 🌟 **方案5（最推荐）**: 分步查询
- **优势**: 逻辑清晰，性能好，易于调试和维护
- **逻辑**: 第一步处理状态筛选和金额计算，第二步处理复杂的OR条件
- **适用**: 几乎所有UQM框架都支持

### ✅ **方案2**: 直接子查询
- **优势**: 完全保持原始逻辑结构
- **缺点**: 子查询可能执行多次，性能稍差

### ✅ **方案4**: EXISTS + HAVING
- **优势**: 保持逻辑结构，EXISTS通常性能较好
- **缺点**: 语法复杂，需要框架支持EXISTS

### ❌ **方案1 & 方案3**: HAVING分离
- **问题**: 破坏了原始的逻辑结构
- **不推荐**: 改变了业务含义

### 2.2 产品库存和供应商复合查询
**场景**: 查询满足以下条件的产品：
- (产品未下架 AND 库存量 > 指定值) OR (产品类别在指定列表 AND 供应商国家不在排除列表)

```json
{
  "uqm": {
    "metadata": {
      "name": "产品库存和供应商复合查询",
      "description": "测试复杂的产品和库存条件",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "complex_product_inventory",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": [
            "products.product_id",
            "products.product_name",
            "products.category",
            "products.unit_price",
            "products.discontinued",
            "suppliers.supplier_name",
            "suppliers.country AS supplier_country",
            "SUM(inventory.quantity_on_hand) AS total_inventory"
          ],
          "joins": [
            {
              "type": "LEFT",
              "table": "suppliers",
              "on": {
                "left": "products.supplier_id",
                "right": "suppliers.supplier_id",
                "operator": "="
              }
            },
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
          "filters": [
            {
              "logic": "OR",
              "conditions": [
                {
                  "logic": "AND",
                  "conditions": [
                    {
                      "field": "products.discontinued",
                      "operator": "=",
                      "value": "$activeProduct"
                    },
                    {
                      "field": "inventory.quantity_on_hand",
                      "operator": ">",
                      "value": "$minInventory"
                    }
                  ]
                },
                {
                  "logic": "AND",
                  "conditions": [
                    {
                      "field": "products.category",
                      "operator": "IN",
                      "value": "$targetCategories"
                    },
                    {
                      "field": "suppliers.country",
                      "operator": "NOT IN",
                      "value": "$excludedCountries"
                    }
                  ]
                }
              ]
            }
          ],
          "group_by": [
            "products.product_id",
            "products.product_name",
            "products.category",
            "products.unit_price",
            "products.discontinued",
            "suppliers.supplier_name",
            "suppliers.country"
          ]
        }
      }
    ],
    "output": "complex_product_inventory"
  },
  "parameters": {
    "activeProduct": false,
    "minInventory": 50,
    "targetCategories": ["电子产品", "家居用品"],
    "excludedCountries": ["未知国家", "测试国家"]
  },
  "options": {}
}
```

## 3. 时间范围和多表关联复合查询

### 3.1 销售业绩复合分析
**场景**: 查询满足以下条件的销售数据：
- (订单日期在指定季度 AND 客户是VIP) OR (订单金额 > 指定值 AND 负责员工部门是销售部)
- AND 产品不在停产列表中

```json
{
  "uqm": {
    "metadata": {
      "name": "销售业绩复合分析",
      "description": "测试时间范围和多表关联的复杂查询",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "complex_sales_analysis",
        "type": "query",
        "config": {
          "data_source": "orders",
          "dimensions": [
            "orders.order_id",
            "orders.order_date",
            "customers.customer_name",
            "customers.customer_segment",
            {
              "expression": "CONCAT(employees.first_name, ' ', employees.last_name)",
              "alias": "employee_name"
            },
            "departments.name AS employee_department",
            "products.product_name",
            "products.category"
          ],
          "calculated_fields": [
            {
              "name": "order_total",
              "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))",
              "alias": "total_amount"
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
              "type": "LEFT",
              "table": "employees",
              "on": {
                "left": "orders.employee_id",
                "right": "employees.employee_id",
                "operator": "="
              }
            },
            {
              "type": "LEFT",
              "table": "departments",
              "on": {
                "left": "employees.department_id",
                "right": "departments.department_id",
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
            },
            {
              "type": "INNER",
              "table": "products",
              "on": {
                "left": "order_items.product_id",
                "right": "products.product_id",
                "operator": "="
              }
            }
          ],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "logic": "OR",
                  "conditions": [
                    {
                      "logic": "AND",
                      "conditions": [
                        {
                          "field": "orders.order_date",
                          "operator": "BETWEEN",
                          "value": {
                            "min": "$quarterStartDate",
                            "max": "$quarterEndDate"
                          }
                        },
                        {
                          "field": "customers.customer_segment",
                          "operator": "=",
                          "value": "$vipSegment"
                        }
                      ]
                    },
                    {
                      "logic": "AND",
                      "conditions": [
                        {
                          "field": "total_amount",
                          "operator": ">",
                          "value": "$minOrderAmount"
                        },
                        {
                          "field": "departments.name",
                          "operator": "IN",
                          "value": "$salesDepartments"
                        }
                      ]
                    }
                  ]
                },
                {
                  "field": "products.discontinued",
                  "operator": "=",
                  "value": "$activeOnly"
                }
              ]
            }
          ],
          "group_by": [
            "orders.order_id",
            "orders.order_date",
            "customers.customer_name",
            "customers.customer_segment",
            "employees.first_name",
            "employees.last_name",
            "departments.name",
            "products.product_name",
            "products.category"
          ]
        }
      }
    ],
    "output": "complex_sales_analysis"
  },
  "parameters": {
    "quarterStartDate": "2024-01-01",
    "quarterEndDate": "2024-03-31",
    "vipSegment": "VIP",
    "minOrderAmount": 1000,
    "salesDepartments": ["销售部", "欧洲销售部"],
    "activeOnly": false
  },
  "options": {}
}
```

## 4. 嵌套子查询与复杂条件

### 4.1 高价值客户与产品偏好分析
**场景**: 查询满足以下条件的客户购买行为：
- 客户历史总消费 > 指定金额 AND (购买过高价产品 OR 购买次数 > 指定次数)
- AND 最近一次购买在指定时间内

```json
{
  "uqm": {
    "metadata": {
      "name": "高价值客户与产品偏好分析",
      "description": "测试子查询和复杂条件组合",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "high_value_customer_analysis",
        "type": "query",
        "config": {
          "data_source": "customers",
          "dimensions": [
            "customers.customer_id",
            "customers.customer_name",
            "customers.customer_segment"
          ],
          "calculated_fields": [
            {
              "name": "total_spent",
              "expression": "(SELECT SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) FROM orders o JOIN order_items oi ON o.order_id = oi.order_id WHERE o.customer_id = customers.customer_id)",
              "alias": "customer_total_spent"
            },
            {
              "name": "order_count",
              "expression": "(SELECT COUNT(*) FROM orders WHERE customer_id = customers.customer_id)",
              "alias": "total_orders"
            },
            {
              "name": "max_product_price",
              "expression": "(SELECT MAX(oi.unit_price) FROM orders o JOIN order_items oi ON o.order_id = oi.order_id WHERE o.customer_id = customers.customer_id)",
              "alias": "highest_product_price"
            },
            {
              "name": "last_order_date",
              "expression": "(SELECT MAX(order_date) FROM orders WHERE customer_id = customers.customer_id)",
              "alias": "last_purchase_date"
            }
          ],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "field": "customer_total_spent",
                  "operator": ">",
                  "value": "$minTotalSpent"
                },
                {
                  "logic": "OR",
                  "conditions": [
                    {
                      "field": "highest_product_price",
                      "operator": ">",
                      "value": "$highPriceThreshold"
                    },
                    {
                      "field": "total_orders",
                      "operator": ">",
                      "value": "$minOrderCount"
                    }
                  ]
                },
                {
                  "field": "last_purchase_date",
                  "operator": ">=",
                  "value": "$recentPurchaseDate"
                }
              ]
            }
          ]
        }
      }
    ],
    "output": "high_value_customer_analysis"
  },
  "parameters": {
    "minTotalSpent": 2000,
    "highPriceThreshold": 500,
    "minOrderCount": 3,
    "recentPurchaseDate": "2024-01-01"
  },
  "options": {}
}
```

### 4.2 库存警报和供应商风险评估
**场景**: 查询需要关注的产品和供应商：
- (库存量 < 安全库存 AND 最近30天有销售) OR (供应商只供应1个产品 AND 该产品销量 > 指定值)
- AND 产品价格在指定范围内

```json
{
  "uqm": {
    "metadata": {
      "name": "库存警报和供应商风险评估",
      "description": "测试复杂的库存和供应商风险条件",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "inventory_supplier_risk_analysis",
        "type": "query",
        "config": {
          "data_source": "products",
          "dimensions": [
            "products.product_id",
            "products.product_name",
            "products.category",
            "products.unit_price",
            "suppliers.supplier_name",
            "suppliers.country AS supplier_country"
          ],
          "calculated_fields": [
            {
              "name": "current_inventory",
              "expression": "(SELECT SUM(quantity_on_hand) FROM inventory WHERE product_id = products.product_id)",
              "alias": "total_inventory"
            },
            {
              "name": "recent_sales",
              "expression": "(SELECT SUM(oi.quantity) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE oi.product_id = products.product_id AND o.order_date >= DATE_SUB(NOW(), INTERVAL 30 DAY))",
              "alias": "sales_last_30_days"
            },
            {
              "name": "supplier_product_count",
              "expression": "(SELECT COUNT(*) FROM products p WHERE p.supplier_id = products.supplier_id)",
              "alias": "supplier_total_products"
            },
            {
              "name": "product_total_sales",
              "expression": "(SELECT SUM(oi.quantity) FROM order_items oi WHERE oi.product_id = products.product_id)",
              "alias": "total_product_sales"
            }
          ],
          "joins": [
            {
              "type": "LEFT",
              "table": "suppliers",
              "on": {
                "left": "products.supplier_id",
                "right": "suppliers.supplier_id",
                "operator": "="
              }
            }
          ],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "logic": "OR",
                  "conditions": [
                    {
                      "logic": "AND",
                      "conditions": [
                        {
                          "field": "total_inventory",
                          "operator": "<",
                          "value": "$safetyStock"
                        },
                        {
                          "field": "sales_last_30_days",
                          "operator": ">",
                          "value": "$minRecentSales"
                        }
                      ]
                    },
                    {
                      "logic": "AND",
                      "conditions": [
                        {
                          "field": "supplier_total_products",
                          "operator": "=",
                          "value": "$singleProductSupplier"
                        },
                        {
                          "field": "total_product_sales",
                          "operator": ">",
                          "value": "$highSalesThreshold"
                        }
                      ]
                    }
                  ]
                },
                {
                  "field": "products.unit_price",
                  "operator": "BETWEEN",
                  "value": {
                    "min": "$minPrice",
                    "max": "$maxPrice"
                  }
                }
              ]
            }
          ]
        }
      }
    ],
    "output": "inventory_supplier_risk_analysis"
  },
  "parameters": {
    "safetyStock": 20,
    "minRecentSales": 1,
    "singleProductSupplier": 1,
    "highSalesThreshold": 10,
    "minPrice": 10,
    "maxPrice": 1000
  },
  "options": {}
}
```

## 5. 多步骤复杂查询

### 5.1 分层条件筛选查询
**场景**: 先筛选出符合条件的客户，再基于这些客户查询其订单详情

```json
{
  "uqm": {
    "metadata": {
      "name": "分层条件筛选查询",
      "description": "测试多步骤查询和条件传递",
      "version": "1.0"
    },
    "steps": [
      {
        "name": "qualified_customers",
        "type": "query",
        "config": {
          "data_source": "customers",
          "dimensions": [
            "customer_id"
          ],
          "calculated_fields": [
            {
              "name": "total_orders",
              "expression": "(SELECT COUNT(*) FROM orders WHERE customer_id = customers.customer_id)",
              "alias": "order_count"
            },
            {
              "name": "total_spent",
              "expression": "(SELECT SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) FROM orders o JOIN order_items oi ON o.order_id = oi.order_id WHERE o.customer_id = customers.customer_id)",
              "alias": "customer_total_spent"
            }
          ],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "logic": "OR",
                  "conditions": [
                    {
                      "field": "customers.customer_segment",
                      "operator": "=",
                      "value": "$vipSegment"
                    },
                    {
                      "logic": "AND",
                      "conditions": [
                        {
                          "field": "order_count",
                          "operator": ">=",
                          "value": "$minOrders"
                        },
                        {
                          "field": "customer_total_spent",
                          "operator": ">",
                          "value": "$minSpent"
                        }
                      ]
                    }
                  ]
                },
                {
                  "field": "customers.registration_date",
                  "operator": ">=",
                  "value": "$registrationAfter"
                }
              ]
            }
          ]
        }
      },
      {
        "name": "qualified_customer_orders",
        "type": "query",
        "config": {
          "data_source": "orders",
          "dimensions": [
            "orders.order_id",
            "orders.customer_id",
            "orders.order_date",
            "orders.status",
            "customers.customer_name",
            "customers.customer_segment"
          ],
          "calculated_fields": [
            {
              "name": "order_value",
              "expression": "(SELECT SUM(quantity * unit_price * (1 - discount)) FROM order_items WHERE order_id = orders.order_id)",
              "alias": "total_order_value"
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
            }
          ],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "field": "orders.customer_id",
                  "operator": "IN",
                  "value": "{{qualified_customers.customer_id}}"
                },
                {
                  "logic": "OR",
                  "conditions": [
                    {
                      "field": "orders.status",
                      "operator": "IN",
                      "value": "$completedStatuses"
                    },
                    {
                      "logic": "AND",
                      "conditions": [
                        {
                          "field": "total_order_value",
                          "operator": ">",
                          "value": "$highValueThreshold"
                        },
                        {
                          "field": "orders.status",
                          "operator": "!=",
                          "value": "$cancelledStatus"
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      }
    ],
    "output": "qualified_customer_orders"
  },
  "parameters": {
    "vipSegment": "VIP",
    "minOrders": 2,
    "minSpent": 1000,
    "registrationAfter": "2023-01-01",
    "completedStatuses": ["已完成", "已发货"],
    "highValueThreshold": 800,
    "cancelledStatus": "已取消"
  },
  "options": {}
}
```

## 测试要点说明

1. **嵌套逻辑**: 测试 AND/OR 的嵌套组合是否正确执行
2. **操作符支持**: 验证 IN, NOT IN, BETWEEN, IS NULL 等操作符
3. **参数传递**: 确认复杂参数（数组、对象）的正确传递
4. **计算字段**: 测试在复杂条件中使用计算字段
5. **多表关联**: 验证复杂 JOIN 条件下的筛选逻辑
6. **子查询**: 测试子查询在复杂条件中的表现
7. **步骤间数据传递**: 验证多步骤查询中数据的正确传递

这些测试用例覆盖了大部分复杂查询场景，可以有效验证 UQM 框架对复杂参数查询的支持程度。
