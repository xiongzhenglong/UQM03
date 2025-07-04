# UQM 完整 JSON Schema 语法参考文档

## 📖 概述

UQM (统一查询模型) 是一个基于 JSON 的查询描述语言，提供声明式的数据查询和分析功能。它类似于 SQL 但使用 JSON 格式，支持多步骤数据处理管道，包括查询、丰富、透视、联合等操作。

本文档提供了 UQM 的完整语法规则和使用示例，旨在帮助开发者和 AI 系统正确构建 UQM 查询。

## 🏗️ 顶层架构

### 1. API 请求结构

```json
{
  "uqm": {
    "metadata": { /* 元数据 */ },
    "steps": [ /* 步骤管道 */ ],
    "output": "step_name"
  },
  "parameters": { /* 运行时参数 */ },
  "options": { /* 执行选项 */ }
}
```

### 2. 核心组件说明

| 组件 | 必需 | 说明 |
|------|------|------|
| `uqm` | ✅ | UQM 核心配置对象 |
| `parameters` | ❌ | 运行时参数键值对 |
| `options` | ❌ | 执行选项配置 |

## 📋 UQM 核心语法

### 1. metadata (元数据) - 必需

```json
{
  "metadata": {
    "name": "string",           // 必需：查询名称
    "description": "string",    // 推荐：查询描述
    "version": "string",        // 可选：版本号，默认"1.0"
    "author": "string",         // 可选：作者
    "tags": ["string"]          // 可选：标签数组
  }
}
```

**示例：**
```json
{
  "metadata": {
    "name": "员工薪资分析",
    "description": "按部门统计员工平均薪资和人数",
    "version": "1.0",
    "author": "HR Team",
    "tags": ["hr", "salary", "analysis"]
  }
}
```

### 2. steps (步骤管道) - 必需

Steps 是 UQM 的核心，定义了数据处理的步骤序列。每个步骤都有特定的类型和配置。

```json
{
  "steps": [
    {
      "name": "string",      // 必需：步骤名称（唯一标识）
      "type": "string",      // 必需：步骤类型
      "config": {           // 必需：步骤配置
        // 具体配置根据步骤类型而定
      }
    }
  ]
}
```

### 3. output (输出步骤) - 可选

```json
{
  "output": "step_name"  // 指定哪个步骤的结果作为最终输出
}
```

如果未指定，默认使用最后一个步骤的结果。

## 🔧 步骤类型详解

### 1. query 步骤 - 数据查询

用于从数据库表或前置步骤结果中查询数据。

```json
{
  "name": "step_name",
  "type": "query",
  "config": {
    "data_source": "string",              // 必需：数据源（表名或步骤名）
    "dimensions": [                       // 可选：维度字段
      "field_name",                       // 简单字段
      {
        "expression": "SQL_expression",   // 表达式
        "alias": "alias_name"             // 别名
      }
    ],
    "metrics": [                          // 可选：指标字段
      {
        "name": "field_name",             // 聚合字段名
        "aggregation": "function",        // 聚合函数
        "alias": "alias_name"             // 别名
      },
      {
        "expression": "SQL_expression",   // 自定义表达式
        "alias": "alias_name"
      }
    ],
    // ⚠️ 重要限制：metrics 中定义的聚合结果字段不能在同一步骤的 filters 中直接使用
    // 如需根据聚合结果过滤，请使用 having 条件或多步骤查询
    "calculated_fields": [                // 可选：计算字段
      {
        "alias": "field_name",
        "expression": "SQL_expression"
      }
    ],
    // ⚠️ 重要限制：calculated_fields 中定义的字段别名不能在同一步骤的 filters 中直接使用
    // 如需根据计算字段过滤，请使用多步骤查询：先计算字段，再在下一步骤中过滤
    "filters": [                          // 可选：过滤条件
      {
        "field": "field_name",
        "operator": "operator",
        "value": "value",
        "conditional": {                  // 可选：条件逻辑
          "type": "expression",
          "expression": "boolean_expression"
        }
      }
    ],
    // ⚠️ filters 字段限制说明：
    // 1. field 只能引用 data_source 中的原始字段、dimensions 中的字段或别名
    // 2. 不能直接引用 calculated_fields 中定义的字段别名
    // 3. 不能引用 metrics 中定义的聚合结果字段
    // 4. 如需根据计算字段或聚合结果过滤，请使用多步骤查询
    "joins": [                            // 可选：表连接
      {
        "type": "JOIN_TYPE",              // INNER/LEFT/RIGHT/FULL
        "table": "table_name",
        "on": "join_condition"
      }
    ],
    "group_by": ["field_name"],           // 可选：分组字段
    "having": [                           // 可选：HAVING条件
      {
        "field": "field_name",
        "operator": "operator",
        "value": "value"
      }
    ],
    // ✅ having 是对聚合结果进行过滤的正确方式
    // 可以在 having 中使用 metrics 中定义的聚合字段别名
    "order_by": [                         // 可选：排序
      {
        "field": "field_name",
        "direction": "ASC|DESC"
      }
    ],
    "limit": 100,                         // 可选：限制结果数
    "offset": 0                           // 可选：偏移量
  }
}
```

**支持的聚合函数：**
- `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`
- `COUNT_DISTINCT`, `STDDEV`, `VARIANCE`

**支持的操作符：**
- 比较：`=`, `!=`, `<`, `<=`, `>`, `>=`
- 逻辑：`AND`, `OR`, `NOT`
- 集合：`IN`, `NOT IN`
- 模式：`LIKE`, `NOT LIKE`
- 区间：`BETWEEN`, `NOT BETWEEN`
- 空值：`IS NULL`, `IS NOT NULL`

**重要注意事项：**
- `group_by` 中的字段名必须是 `dimensions` 中定义的字段名或别名
- 如果使用了 `joins`，确保分组字段在连接后的结果集中存在
- 表别名必须与 `data_source` 和 `joins` 中定义的保持一致
- **⚠️ 表别名规则**：在 `metrics` 中使用 `name` 字段时，必须包含正确的表别名前缀（如 `oi.quantity` 而不是 `quantity`）
- **⚠️ 表别名规则**：使用表别名时，所有字段引用都必须使用完整的表别名前缀
- **⚠️ 核心限制**：在 `calculated_fields` 中定义的字段别名**不能**在同一步骤的 `filters` 中直接使用
- **⚠️ 核心限制**：在 `metrics` 中定义的聚合结果字段**不能**在同一步骤的 `filters` 中直接使用
- **⚠️ 输出规则**：作为最终输出的步骤必须明确定义 `dimensions`、`metrics` 或 `calculated_fields`，不能只有 `filters` 而没有字段定义
- **解决方案**：如需根据计算字段或聚合结果过滤，必须使用多步骤查询：先计算/聚合，再在下一步骤中过滤

**字段引用限制示例：**

❌ **错误：直接在 filters 中引用 calculated_fields**
```json
{
  "type": "query",
  "config": {
    "data_source": "sales_data",
    "calculated_fields": [
      {
        "alias": "sales_rank",
        "expression": "ROW_NUMBER() OVER (ORDER BY total_sales DESC)"
      }
    ],
    "filters": [
      {
        "field": "sales_rank",  // ❌ 错误：不能直接引用同一步骤的计算字段
        "operator": "=",
        "value": 1
      }
    ]
  }
}
```

❌ **错误：直接在 filters 中引用 metrics**
```json
{
  "type": "query",
  "config": {
    "data_source": "sales_data",
    "metrics": [
      {
        "name": "total_sales",
        "aggregation": "SUM",
        "alias": "sum_sales"
      }
    ],
    "filters": [
      {
        "field": "sum_sales",  // ❌ 错误：不能在 filters 中引用聚合结果
        "operator": ">",
        "value": 1000
      }
    ],
    "group_by": ["product_category"]
  }
}
```

✅ **正确：使用多步骤查询**
```json
{
  "steps": [
    {
      "name": "calculate_rankings",
      "type": "query",
      "config": {
        "data_source": "sales_data",
        "calculated_fields": [
          {
            "alias": "sales_rank",
            "expression": "ROW_NUMBER() OVER (ORDER BY total_sales DESC)"
          }
        ]
      }
    },
    {
      "name": "filter_top_results",
      "type": "query",
      "config": {
        "data_source": "calculate_rankings",
        "filters": [
          {
            "field": "sales_rank",  // ✅ 正确：引用前一步骤的字段
            "operator": "=",
            "value": 1
          }
        ]
      }
    }
  ]
}
```

✅ **正确：对聚合结果使用 having 条件**
```json
{
  "type": "query",
  "config": {
    "data_source": "sales_data",
    "metrics": [
      {
        "name": "total_sales",
        "aggregation": "SUM",
        "alias": "sum_sales"
      }
    ],
    "group_by": ["product_category"],
    "having": [
      {
        "field": "sum_sales",  // ✅ 正确：在 having 中使用聚合结果
        "operator": ">",
        "value": 1000
      }
    ]
  }
}
```

**示例：**
```json
{
  "name": "get_employee_salary_stats",
  "type": "query",
  "config": {
    "data_source": "employees",
    "dimensions": [
      "department_id",
      {
        "expression": "CASE WHEN salary > 10000 THEN '高薪' ELSE '普通' END",
        "alias": "salary_level"
      }
    ],
    "metrics": [
      {
        "name": "salary",
        "aggregation": "AVG",
        "alias": "avg_salary"
      },
      {
        "name": "employee_id",
        "aggregation": "COUNT",
        "alias": "employee_count"
      }
    ],
    "joins": [
      {
        "type": "INNER",
        "table": "departments",
        "on": "employees.department_id = departments.department_id"
      }
    ],
    "filters": [
      {
        "field": "employees.is_active",
        "operator": "=",
        "value": true
      },
      {
        "field": "employees.salary",
        "operator": ">",
        "value": 5000
      }
    ],
    "group_by": ["department_id", "salary_level"],
    "order_by": [
      {
        "field": "avg_salary",
        "direction": "DESC"
      }
    ]
  }
}
```

**自连接查询示例：**
```json
{
  "name": "get_employee_with_manager",
  "type": "query",
  "config": {
    "data_source": "employees e",
    "dimensions": [
      "e.first_name AS employee_first_name",
      "e.last_name AS employee_last_name",
      "m.first_name AS manager_first_name",
      "m.last_name AS manager_last_name"
    ],
    "joins": [
      {
        "type": "LEFT",
        "table": "employees m",
        "on": "e.manager_id = m.employee_id"
      }
    ],
    "filters": [
      {
        "field": "e.is_active",
        "operator": "=",
        "value": true
      }
    ]
  }
}
```

### 2. enrich 步骤 - 数据丰富

用于通过查找表丰富数据，类似于 SQL 的 JOIN 操作。

```json
{
  "name": "step_name",
  "type": "enrich",
  "config": {
    "source": "source_step_name",         // 必需：源步骤名称
    "lookup": {                           // 必需：查找表配置
      "table": "table_name",              // 查找表名
      "columns": [                        // 要获取的列
        "column_name",
        "column_name AS alias"
      ]
    },
    "on": {                              // 必需：连接条件
      "left": "left_field",              // 左侧字段
      "right": "right_field",            // 右侧字段
      "operator": "="                    // 可选：连接操作符，默认"="
    },
    "join_type": "left"                  // 可选：连接类型，默认"left"
  }
}
```

**支持的连接类型：**
- `left` (默认)
- `inner`
- `right`
- `full`

**示例：**
```json
{
  "name": "enrich_employee_with_department",
  "type": "enrich",
  "config": {
    "source": "get_employees",
    "lookup": {
      "table": "departments",
      "columns": [
        "department_id",
        "name AS department_name",
        "location AS office_location"
      ]
    },
    "on": {
      "left": "department_id",
      "right": "department_id"
    },
    "join_type": "left"
  }
}
```

### 3. pivot 步骤 - 数据透视

用于将行数据转换为列数据，创建透视表。

```json
{
  "name": "step_name",
  "type": "pivot",
  "config": {
    "source": "source_step_name",        // 必需：源步骤名称
    "index": "field_name",               // 必需：行索引字段
    "columns": "field_name",             // 必需：列字段
    "values": "field_name",              // 必需：值字段
    "agg_func": "function",              // 可选：聚合函数，默认"sum"
    "column_prefix": "prefix_",          // 可选：列名前缀
    "fill_value": 0                      // 可选：填充值，默认null
  }
}
```

**支持的聚合函数：**
- `sum`, `avg`, `count`, `min`, `max`
- `count_distinct`, `first`, `last`

**示例：**
```json
{
  "name": "pivot_sales_by_quarter",
  "type": "pivot",
  "config": {
    "source": "get_quarterly_sales",
    "index": "product_category",
    "columns": "quarter",
    "values": "total_sales",
    "agg_func": "sum",
    "column_prefix": "Q",
    "fill_value": 0
  }
}
```

### 4. unpivot 步骤 - 反透视

用于将列数据转换为行数据，是 pivot 的逆操作。

```json
{
  "name": "step_name",
  "type": "unpivot",
  "config": {
    "source": "source_step_name",        // 必需：源步骤名称
    "id_vars": ["field_name"],           // 必需：保持不变的列
    "value_vars": ["field_name"],        // 必需：要转换的列
    "var_name": "variable_name",         // 可选：变量名列，默认"variable"
    "value_name": "value_name"           // 可选：值名列，默认"value"
  }
}
```

**示例：**
```json
{
  "name": "unpivot_quarterly_sales",
  "type": "unpivot",
  "config": {
    "source": "pivot_sales_by_quarter",
    "id_vars": ["product_category"],
    "value_vars": ["Q1", "Q2", "Q3", "Q4"],
    "var_name": "quarter",
    "value_name": "sales_amount"
  }
}
```

### 5. union 步骤 - 数据联合

用于合并多个数据源的结果。

```json
{
  "name": "step_name",
  "type": "union",
  "config": {
    "sources": [                         // 必需：源步骤名称数组
      "source_step_1",
      "source_step_2"
    ],
    "union_type": "all",                 // 可选：联合类型，"all"或"distinct"
    "column_mapping": {                  // 可选：列映射
      "source_step_1": {
        "old_column": "new_column"
      },
      "source_step_2": {
        "old_column": "new_column"
      }
    }
  }
}
```

**示例：**
```json
{
  "name": "union_all_sales",
  "type": "union",
  "config": {
    "sources": [
      "online_sales",
      "offline_sales"
    ],
    "union_type": "all",
    "column_mapping": {
      "online_sales": {
        "web_order_id": "order_id",
        "customer_email": "customer_info"
      },
      "offline_sales": {
        "store_order_id": "order_id",
        "customer_phone": "customer_info"
      }
    }
  }
}
```

### 6. assert 步骤 - 数据断言

用于验证数据质量和业务规则。

```json
{
  "name": "step_name",
  "type": "assert",
  "config": {
    "source": "source_step_name",        // 必需：源步骤名称
    "assertions": [                      // 必需：断言规则数组
      {
        "type": "row_count",             // 行数断言
        "expected": 100,                 // 期望的行数（可选）
        "min": 1,                        // 最小行数（可选）
        "max": 1000,                     // 最大行数（可选）
        "message": "数据行数不符合预期"    // 错误消息
      },
      {
        "type": "range",                 // 数值范围断言
        "field": "salary",               // 要检查的字段
        "min": 0,                        // 最小值（可选）
        "max": 100000,                   // 最大值（可选）
        "message": "薪资超出合理范围"      // 错误消息
      },
      {
        "type": "unique",                // 唯一性断言
        "field": "employee_id",          // 要检查的字段
        "message": "员工ID必须唯一"       // 错误消息
      },
      {
        "type": "not_null",              // 非空断言
        "field": "email",                // 要检查的字段
        "message": "邮箱不能为空"          // 错误消息
      },
      {
        "type": "value_in",              // 值在指定集合中断言
        "field": "status",               // 要检查的字段
        "values": ["active", "inactive", "pending"],  // 允许的值
        "message": "状态值无效"           // 错误消息
      },
      {
        "type": "custom",                // 自定义表达式断言
        "expression": "revenue > 1000 AND profit_margin > 0.1",  // 自定义条件表达式
        "message": "收入和利润率不符合要求"  // 错误消息
      }
    ]
  }
}
```

**支持的断言类型：**
- `row_count`: 检查结果集行数
- `range`: 检查数值字段的范围
- `unique`: 检查字段值的唯一性
- `not_null`: 检查字段非空
- `value_in`: 检查字段值是否在指定集合中
- `custom`: 自定义条件表达式断言

**断言字段说明：**
- `field`: 要检查的字段名（适用于 range、unique、not_null、value_in 类型）
- `expected`: 期望的精确值（适用于 row_count 类型）
- `min`/`max`: 最小值/最大值（适用于 row_count、range 类型）
- `values`: 允许的值列表（适用于 value_in 类型）
- `expression`: 自定义条件表达式（适用于 custom 类型）
- `message`: 断言失败时的错误消息（所有类型必需）

**示例：**
```json
{
  "name": "validate_employee_data",
  "type": "assert",
  "config": {
    "source": "get_employees",
    "assertions": [
      {
        "type": "row_count",
        "min": 1,
        "max": 10000,
        "message": "员工数据应在合理范围内"
      },
      {
        "type": "range",
        "field": "salary",
        "min": 3000,
        "max": 50000,
        "message": "薪资应在3000-50000之间"
      },
      {
        "type": "unique",
        "field": "email",
        "message": "员工邮箱必须唯一"
      },
      {
        "type": "not_null",
        "field": "employee_name",
        "message": "员工姓名不能为空"
      },
      {
        "type": "value_in",
        "field": "department",
        "values": ["IT", "HR", "Sales", "Finance"],
        "message": "部门名称必须是有效值"
      },
      {
        "type": "custom",
        "expression": "salary > 0 AND hire_date <= CURRENT_DATE",
        "message": "薪资必须大于0且入职日期不能是未来时间"
      }
    ]
  }
}
```

## 📝 参数系统

### 1. 参数定义

在 UQM 中可以定义参数，用于运行时动态赋值。

```json
{
  "parameters": [
    {
      "name": "parameter_name",          // 必需：参数名称
      "type": "data_type",               // 必需：数据类型
      "default": "default_value",        // 可选：默认值
      "required": true,                  // 可选：是否必需，默认false
      "description": "parameter_desc"    // 可选：参数描述
    }
  ]
}
```

**支持的数据类型：**
- `string`: 字符串
- `number`: 数值
- `boolean`: 布尔值
- `array`: 数组
- `object`: 对象
- `date`: 日期

### 2. 参数使用

在查询中使用参数有两种语法格式：

**格式1：使用 `$parameter_name` 语法**
```json
{
  "filters": [
    {
      "field": "department_id",
      "operator": "=",
      "value": "$department_id"
    }
  ]
}
```

**格式2：使用 `${parameter_name}` 语法**
```json
{
  "filters": [
    {
      "field": "department_id",
      "operator": "=",
      "value": "${department_id}"
    }
  ]
}
```

**注意：**
- 两种格式都支持，可以在同一个查询中混合使用
- `${parameter_name}` 格式更明确，建议在复杂表达式中使用
- `$parameter_name` 格式更简洁，适合简单的参数引用

**混合使用示例：**
```json
{
  "calculated_fields": [
    {
      "alias": "salary_category",
      "expression": "CASE WHEN salary > ${high_threshold} THEN 'High' WHEN salary > $medium_threshold THEN 'Medium' ELSE 'Low' END"
    }
  ],
  "filters": [
    {
      "field": "department_id",
      "operator": "=",
      "value": "$department_id"
    },
    {
      "field": "salary_range",
      "operator": "BETWEEN",
      "value": "${salary_range}"
    }
  ]
}
```

### 3. 条件参数

支持基于参数值的条件逻辑。

```json
{
  "filters": [
    {
      "field": "salary",
      "operator": ">",
      "value": "$min_salary",
      "conditional": {
        "type": "expression",
        "expression": "$min_salary != null && $min_salary > 0"
      }
    }
  ]
}
```

## ⚙️ 执行选项

### 1. options 配置

```json
{
  "options": {
    "cache_enabled": true,               // 是否启用缓存
    "cache_ttl": 3600,                   // 缓存TTL(秒)
    "timeout": 300,                      // 查询超时时间(秒)
    "max_rows": 10000,                   // 最大返回行数
    "explain": false,                    // 是否返回执行计划
    "debug": false                       // 是否启用调试模式
  }
}
```

## 🔄 高级特性

### 1. 窗口函数

在 query 步骤中使用窗口函数：

```json
{
  "calculated_fields": [
    {
      "alias": "rank",
      "expression": "ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC)"
    },
    {
      "alias": "salary_percentile",
      "expression": "PERCENT_RANK() OVER (ORDER BY salary)"
    }
  ]
}
```

### 2. 复杂表达式

支持复杂的 SQL 表达式：

```json
{
  "calculated_fields": [
    {
      "alias": "age_group",
      "expression": "CASE WHEN DATEDIFF(CURRENT_DATE, birth_date) / 365 < 30 THEN '青年' WHEN DATEDIFF(CURRENT_DATE, birth_date) / 365 < 50 THEN '中年' ELSE '老年' END"
    }
  ]
}
```

### 3. 多表连接

支持复杂的多表连接：

```json
{
  "joins": [
    {
      "type": "INNER",
      "table": "departments",
      "on": "employees.department_id = departments.department_id"
    },
    {
      "type": "LEFT",
      "table": "managers",
      "on": "employees.manager_id = managers.employee_id"
    }
  ]
}
```

**表别名注意事项：**
- 当使用表别名时，`data_source` 必须包含别名定义（如 `"employees e"`）
- 所有字段引用必须使用正确的表别名前缀
- 自连接必须使用不同的别名来区分同一张表的不同实例

## 📊 完整示例

### 示例1：员工薪资分析

```json
{
  "uqm": {
    "metadata": {
      "name": "部门薪资分析",
      "description": "分析各部门的薪资情况，包括平均薪资、最高薪资、最低薪资和员工数量",
      "version": "1.0",
      "author": "HR Team"
    },
    "steps": [
      {
        "name": "get_employee_salary_data",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": [
            "department_id",
            "departments.name AS department_name"
          ],
          "metrics": [
            {
              "name": "salary",
              "aggregation": "AVG",
              "alias": "avg_salary"
            },
            {
              "name": "salary",
              "aggregation": "MAX",
              "alias": "max_salary"
            },
            {
              "name": "salary",
              "aggregation": "MIN",
              "alias": "min_salary"
            },
            {
              "name": "employee_id",
              "aggregation": "COUNT",
              "alias": "employee_count"
            }
          ],
          "joins": [
            {
              "type": "INNER",
              "table": "departments",
              "on": "employees.department_id = departments.department_id"
            }
          ],
          "filters": [
            {
              "field": "employees.is_active",
              "operator": "=",
              "value": true
            }
          ],
          "group_by": ["department_id", "departments.name"],
          "order_by": [
            {
              "field": "avg_salary",
              "direction": "DESC"
            }
          ]
        }
      },
      {
        "name": "validate_results",
        "type": "assert",
        "config": {
          "source": "get_employee_salary_data",
          "assertions": [
            {
              "type": "row_count",
              "condition": ">",
              "value": 0,
              "message": "应该有薪资数据"
            },
            {
              "type": "column_values",
              "column": "avg_salary",
              "condition": ">",
              "value": 0,
              "message": "平均薪资应该大于0"
            }
          ]
        }
      }
    ],
    "output": "validate_results"
  },
  "parameters": {},
  "options": {
    "cache_enabled": true,
    "timeout": 300
  }
}
```

### 示例2：销售透视分析

```json
{
  "uqm": {
    "metadata": {
      "name": "季度销售透视分析",
      "description": "按产品类别和季度分析销售数据",
      "version": "1.0",
      "author": "Sales Team"
    },
    "steps": [
      {
        "name": "get_sales_data",
        "type": "query",
        "config": {
          "data_source": "order_items",
          "dimensions": [
            "products.category",
            {
              "expression": "CASE WHEN MONTH(orders.order_date) IN (1,2,3) THEN 'Q1' WHEN MONTH(orders.order_date) IN (4,5,6) THEN 'Q2' WHEN MONTH(orders.order_date) IN (7,8,9) THEN 'Q3' ELSE 'Q4' END",
              "alias": "quarter"
            }
          ],
          "metrics": [
            {
              "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))",
              "alias": "total_sales"
            }
          ],
          "joins": [
            {
              "type": "INNER",
              "table": "orders",
              "on": "order_items.order_id = orders.order_id"
            },
            {
              "type": "INNER",
              "table": "products",
              "on": "order_items.product_id = products.product_id"
            }
          ],
          "filters": [
            {
              "field": "YEAR(orders.order_date)",
              "operator": "=",
              "value": "$year"
            },
            {
              "field": "orders.status",
              "operator": "=",
              "value": "已完成"
            }
          ],
          "group_by": ["products.category", "quarter"]
        }
      },
      {
        "name": "pivot_sales_by_quarter",
        "type": "pivot",
        "config": {
          "source": "get_sales_data",
          "index": "category",
          "columns": "quarter",
          "values": "total_sales",
          "agg_func": "sum",
          "column_prefix": "销售额_",
          "fill_value": 0
        }
      }
    ],
    "output": "pivot_sales_by_quarter"
  },
  "parameters": {
    "year": 2024
  },
  "options": {
    "cache_enabled": true
  }
}
```

## 🚨 最佳实践

### 1. 命名规范
- 步骤名称使用有意义的描述性名称
- 字段别名使用清晰的命名
- 参数名称使用下划线分隔

### 2. 性能优化
- 合理使用索引字段进行过滤
- 避免不必要的大数据集连接
- 适当使用 LIMIT 限制结果集大小

### 3. 错误处理
- 添加适当的断言验证数据质量
- 提供清晰的错误消息
- 使用条件过滤避免空值错误
- 确保所有字段引用使用正确的表别名或字段名
- 验证 `group_by` 中的字段在 `dimensions` 中已定义

### 4. 计算字段和过滤器的使用
- **重要规则**：不能在同一个查询步骤的 `filters` 中直接使用 `calculated_fields` 中定义的别名
- **解决方案**：使用多步骤查询来处理基于计算字段的过滤
  - 第一步：定义计算字段
  - 第二步：使用计算字段进行过滤
- **示例场景**：需要根据排名、百分比等计算结果进行过滤时

### 5. 表别名和字段引用
- 当使用表别名时，所有字段引用必须使用完整的表别名前缀
- 在 `metrics` 的 `name` 字段中，必须包含表别名（如 `"name": "oi.quantity"`）
- 在 `dimensions` 中可以使用 `"p.category"` 或 `{"expression": "p.category", "alias": "category"}`
- 确保表别名在整个查询中保持一致

### 6. 多步骤查询的字段延续关系
- **重要概念**：步骤之间存在字段延续关系，前一步骤的输出字段可以被后续步骤引用
- **输出步骤规则**：`output` 指定的最终输出步骤必须明确定义要输出的字段
- **字段定义要求**：最终输出步骤应包含 `dimensions`、`metrics` 或 `calculated_fields` 来明确字段结构
- **⚠️ 常见错误**：最终输出步骤只有 `filters` 而缺少字段定义，导致输出结果不明确
- **实践建议**：确保最终输出步骤包含所有需要的字段，避免字段丢失

**❌ 错误：最终输出步骤缺少字段定义**
```json
{
  "steps": [
    {
      "name": "calculate_data",
      "type": "query",
      "config": {
        "data_source": "sales_data",
        "dimensions": ["category"],
        "calculated_fields": [
          {
            "alias": "category_rank",
            "expression": "ROW_NUMBER() OVER (ORDER BY total_sales DESC)"
          }
        ]
      }
    },
    {
      "name": "filter_results",
      "type": "query",
      "config": {
        "data_source": "calculate_data",
        "filters": [
          {
            "field": "category_rank",
            "operator": "<=",
            "value": 5
          }
        ]
        // ❌ 错误：没有定义输出字段，不知道输出什么
      }
    }
  ],
  "output": "filter_results"
}
```

**✅ 正确：最终输出步骤包含完整字段定义**
```json
{
  "steps": [
    {
      "name": "calculate_data",
      "type": "query",
      "config": {
        "data_source": "sales_data",
        "dimensions": ["category"],
        "metrics": [
          {
            "name": "total_sales",
            "aggregation": "SUM",
            "alias": "total_sales"
          }
        ],
        "calculated_fields": [
          {
            "alias": "category_rank",
            "expression": "ROW_NUMBER() OVER (ORDER BY total_sales DESC)"
          }
        ]
      }
    },
    {
      "name": "filter_results",
      "type": "query",
      "config": {
        "data_source": "calculate_data",
        "dimensions": ["category"],
        "metrics": [
          {
            "name": "total_sales",
            "aggregation": "SUM",
            "alias": "total_sales"
          }
        ],
        "calculated_fields": [
          {
            "alias": "category_rank",
            "expression": "category_rank"
          }
        ],
        "filters": [
          {
            "field": "category_rank",
            "operator": "<=",
            "value": 5
          }
        ]
        // ✅ 正确：明确定义了输出的所有字段
      }
    }
  ],
  "output": "filter_results"
}
```

**错误示例：**
```json
{
  "name": "wrong_example",
  "type": "query",
  "config": {
    "data_source": "sales_data",
    "calculated_fields": [
      {
        "alias": "sales_rank",
        "expression": "ROW_NUMBER() OVER (ORDER BY total_sales DESC)"
      }
    ],
    "filters": [
      {
        "field": "sales_rank",  // 错误：不能直接引用计算字段
        "operator": "=",
        "value": 1
      }
    ]
  }
}
```

**正确示例：**
```json
{
  "steps": [
    {
      "name": "calculate_rankings",
      "type": "query",
      "config": {
        "data_source": "sales_data",
        "dimensions": [
          "product_category"
        ],
        "metrics": [
          {
            "name": "total_sales",
            "aggregation": "SUM",
            "alias": "total_sales"
          }
        ],
        "calculated_fields": [
          {
            "alias": "sales_rank",
            "expression": "ROW_NUMBER() OVER (ORDER BY total_sales DESC)"
          }
        ],
        "group_by": ["product_category"]
      }
    },
    {
      "name": "filter_top_results",
      "type": "query",
      "config": {
        "data_source": "calculate_rankings",
        "dimensions": [
          "product_category"
        ],
        "metrics": [
          {
            "name": "total_sales",
            "aggregation": "SUM",
            "alias": "total_sales"
          }
        ],
        "calculated_fields": [
          {
            "alias": "sales_rank",
            "expression": "sales_rank"
          }
        ],
        "filters": [
          {
            "field": "sales_rank",  // ✅ 正确：引用前一步骤的字段
            "operator": "<=",
            "value": 5
          }
        ],
        "order_by": [
          {
            "field": "sales_rank",
            "direction": "ASC"
          }
        ]
      }
    }
  ],
  "output": "filter_top_results"  // ✅ 最终输出步骤包含完整字段定义
}
```

**表别名和最终输出步骤示例：**
```json
{
  "steps": [
    {
      "name": "get_sales_by_category",
      "type": "query",
      "config": {
        "data_source": "order_items oi",
        "dimensions": ["p.category"],
        "metrics": [
          {
            "name": "oi.quantity",  // ✅ 正确：使用表别名前缀
            "aggregation": "SUM",
            "alias": "total_quantity"
          }
        ],
        "joins": [
          {
            "type": "INNER",
            "table": "products p",
            "on": "oi.product_id = p.product_id"
          }
        ],
        "group_by": ["p.category"]
      }
    },
    {
      "name": "final_output",
      "type": "query",
      "config": {
        "data_source": "get_sales_by_category",
        "dimensions": ["category"],  // ✅ 正确：最终输出步骤明确定义字段
        "metrics": [
          {
            "name": "total_quantity",
            "aggregation": "SUM",
            "alias": "total_quantity"
          }
        ],
        "calculated_fields": [
          {
            "alias": "category_rank",
            "expression": "ROW_NUMBER() OVER (ORDER BY total_quantity DESC)"
          }
        ]
      }
    }
  ],
  "output": "final_output"  // ✅ 最终输出步骤包含完整字段定义
}
```

## 🔍 调试技巧

### 1. 启用调试模式
```json
{
  "options": {
    "debug": true,
    "explain": true
  }
}
```

### 2. 分步测试
逐步构建查询，先测试基础步骤，再添加复杂逻辑。

### 3. 数据验证
使用 assert 步骤验证每个关键步骤的数据质量。

### 4. 常见错误处理
- **"Unknown column"错误**：检查字段名是否正确，表别名是否一致
- **"GROUP BY"错误**：确保分组字段在 `dimensions` 中定义
- **连接错误**：验证连接条件中的字段在相关表中存在

---

**注意：** 本文档基于 UQM 当前版本编写，具体语法可能随版本更新而变化。建议结合实际使用场景和系统文档进行开发。
