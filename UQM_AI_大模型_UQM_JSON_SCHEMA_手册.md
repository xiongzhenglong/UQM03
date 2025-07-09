# UQM JSON Schema 技术手册（AI专用高质量版）

> 本手册专为大模型AI生成和推理UQM JSON Schema而设计，内容详尽，涵盖所有功能点、边界条件和常见陷阱，风格高度结构化，便于API自动化生成。

---

## 1. UQM JSON Schema 总体结构

```jsonc
{
  "uqm": {
    "metadata": { /* 查询元信息，详见下方 */ },
    "parameters": [ /* 动态参数定义，详见下方 */ ],
    "steps": [ /* 步骤列表，详见下方 */ ],
    "output": "step_name" // 指定输出步骤名，若省略则默认最后一个步骤
  },
  "parameters": { /* 参数实际值，详见下方 */ },
  "options": { /* 执行选项，详见下方，可选 */ }
}
```

---

## 2. metadata 元数据

```jsonc
"metadata": {
  "name": "查询名称",
  "description": "查询描述",
  "version": "1.0",
  "author": "作者",
  "tags": ["标签1", "标签2"]
}
```

- 建议所有查询都填写 name、description、author，便于追踪和管理。

---

## 3. parameters 动态参数

```jsonc
"parameters": [
  {
    "name": "参数名",
    "type": "string|number|boolean|date|enum|array|object",
    "default": "默认值",
    "required": true,
    "description": "参数说明"
  }
  // ... 可定义多个参数
]
```
- 参数引用格式：`$参数名`，如`"value": "$min_salary"`。不要用`${}`。
- **参数只能在 config 字段（如 filters、dimensions、metrics 等）中引用，不能在 metadata、steps.name、output 等结构字段中引用。**
- **参数类型要与实际传入值严格匹配，否则会校验失败。**

---

## 4. steps 步骤列表

每个步骤为一个对象，必须包含 `name`、`type`、`config` 字段。支持的 type 及其 config 结构如下：

### 4.1 QueryStep（type: "query"）

```jsonc
{
  "name": "get_salary_data",
  "type": "query",
  "config": {
    "data_source": "employees",
    "joins": [
      {
        "type": "INNER",
        "table": "departments",
        "on": "employees.department_id = departments.department_id"
      }
    ],
    "dimensions": [
      { "expression": "departments.name", "alias": "department_name" },
      { "expression": "employees.job_title", "alias": "job_title" },
      { "expression": "employees.salary", "alias": "salary" }
    ],
    "filters": [
      { "field": "employees.is_active", "operator": "=", "value": true },
      {
        "field": "departments.name",
        "operator": "IN",
        "value": "$target_departments",
        "conditional": {
          "type": "parameter_not_empty",
          "parameter": "target_departments",
          "empty_values": [null, []]
        }
      },
      {
        "field": "employees.salary",
        "operator": ">=",
        "value": "$min_salary",
        "conditional": {
          "type": "parameter_not_empty",
          "parameter": "min_salary",
          "empty_values": [null, 0]
        }
      }
    ]
  }
}
```

- `dimensions` 必须用 `{ "expression": "...", "alias": "..." }` 格式，不能直接用字符串。
- `filters` 支持参数化和 conditional 条件过滤，参数引用用 `$参数名`。

---

### 4.2 PivotStep（type: "pivot"）

```jsonc
{
  "name": "pivot_salary",
  "type": "pivot",
  "config": {
    "source": "get_salary_data",
    "index": "department_name",
    "columns": "job_title",
    "values": "salary",
    "agg_func": "mean",
    "fill_value": 0
  }
}
```

- `index`、`columns`、`values` 必须是上一步 alias 字段名。
- `agg_func` 常用 "mean"、"sum"、"count" 等。

---

### 4.3 EnrichStep（type: "enrich"）

```jsonc
{
  "name": "enrich_with_department",
  "type": "enrich",
  "config": {
    "source": "get_salary_data",
    "lookup": {
      "table": "departments",
      "columns": ["department_id", "name"],
      "where": [
        { "field": "is_active", "operator": "=", "value": true }
      ]
    },
    "on": { "left": "department_id", "right": "department_id" },
    "join_type": "left"
  }
}
```
- `source`：主数据源（上一步骤名，必填）
- `lookup`：查找表，可以是字符串（引用前面步骤）或对象（数据库表配置，含 table, columns, where 等）
- `on`：关联条件（字符串、对象或数组，必填）
- `join_type`：连接类型（left/right/inner/full，默认 left）

---

### 4.4 AssertStep（type: "assert"）

```jsonc
{
  "name": "assert_salary_range",
  "type": "assert",
  "config": {
    "source": "get_salary_data",
    "assertions": [
      { "type": "range", "field": "salary", "min": 1000, "max": 100000, "message": "薪资必须在合理区间" },
      { "type": "not_null", "columns": ["department_id", "salary"] }
    ],
    "on_failure": "error"
  }
}
```
- `source`：被断言的数据来源（上一步骤名，必填）
- `assertions`：断言列表（数组，必填），每个断言对象需包含 type 及其相关参数，详见第8节断言类型说明
- `on_failure`：断言失败时的处理方式（error/warning/ignore，默认 error）

---

### 4.5 UnionStep（type: "union"）

```jsonc
{
  "name": "union_sales_and_orders",
  "type": "union",
  "config": {
    "sources": ["sales_data", "order_data"],
    "mode": "union_all",
    "add_source_column": true,
    "source_column": "data_source",
    "remove_duplicates": false
  }
}
```
- `sources`：数据源步骤名列表（数组，至少2个，必填）
- **mode**：合并模式（union/union_all/intersect/except，默认 union）
- `add_source_column`：是否添加来源标识列（布尔，默认 false）
- `source_column`：来源列名（字符串，默认 "_source"）
- `remove_duplicates`：是否去重（布尔，默认 false，仅对 union 有效）

---

### 4.6 UnpivotStep（type: "unpivot"）

```jsonc
{
  "name": "unpivot_monthly_sales",
  "type": "unpivot",
  "config": {
    "source": "pivot_monthly_sales",
    "id_vars": ["department_name"],
    "value_vars": ["Jan", "Feb", "Mar"],
    "var_name": "month",
    "value_name": "sales"
  }
}
```
- `source`：数据来源（上一步骤名，必填）
- `id_vars`：保留为行的字段（字符串或数组，必填）
- `value_vars`：需要转为列的字段（字符串或数组，必填）
- `var_name`：新生成的变量列名（字符串，默认 "variable"）
- `value_name`：新生成的值列名（字符串，默认 "value"）

---

## 5. 参数声明与引用

### 5.1 参数声明

```jsonc
"parameters": [
  { "name": "target_departments", "type": "array", "default": null },
  { "name": "min_salary", "type": "number", "default": null }
]
```

### 5.2 参数实际值

```jsonc
"parameters": {
  "target_departments": ["信息技术部", "销售部"],
  "min_salary": 15000
}
```

### 5.3 参数引用

- 在 filters、dimensions 等 config 里，引用参数用 `$参数名`，如 `"value": "$min_salary"`。

---

## 6. 完整标准示例

```jsonc
{
  "uqm": {
    "metadata": {
      "name": "ParametricSalaryPivot",
      "description": "参数化部门、职位、薪资范围的薪资透视"
    },
    "parameters": [
      { "name": "target_departments", "type": "array", "default": null },
      { "name": "min_salary", "type": "number", "default": null }
    ],
    "steps": [
      {
        "name": "get_param_salary_data",
        "type": "query",
        "config": {
          "data_source": "employees",
          "joins": [
            {
              "type": "INNER",
              "table": "departments",
              "on": "employees.department_id = departments.department_id"
            }
          ],
          "dimensions": [
            { "expression": "departments.name", "alias": "department_name" },
            { "expression": "employees.job_title", "alias": "job_title" },
            { "expression": "employees.salary", "alias": "salary" }
          ],
          "filters": [
            { "field": "employees.is_active", "operator": "=", "value": true },
            {
              "field": "departments.name",
              "operator": "IN",
              "value": "$target_departments",
              "conditional": {
                "type": "parameter_not_empty",
                "parameter": "target_departments",
                "empty_values": [null, []]
              }
            },
            {
              "field": "employees.salary",
              "operator": ">=",
              "value": "$min_salary",
              "conditional": {
                "type": "parameter_not_empty",
                "parameter": "min_salary",
                "empty_values": [null, 0]
              }
            }
          ]
        }
      },
      {
        "name": "pivot_param_salary",
        "type": "pivot",
        "config": {
          "source": "get_param_salary_data",
          "index": "department_name",
          "columns": "job_title",
          "values": "salary",
          "agg_func": "mean",
          "fill_value": 0
        }
      }
    ],
    "output": "pivot_param_salary"
  },
  "parameters": {
    "target_departments": ["信息技术部", "销售部"],
    "min_salary": 15000
  }
}
```

---

## 7. 常见错误与修正建议

- **不要直接用 "表.字段" 作为 pivot 字段名**，要用 alias。
- **dimensions 必须用对象格式**，不能直接字符串。
- **参数引用要用 $，不能用 ${} 或其他格式**。
- **parameters 必须在 uqm 下声明，且类型、默认值要写清楚**。
- **filters 支持 conditional 字段，用于参数可选过滤**。

---

如需更详细的字段说明和更多用例，可参考《UQM_Pivot_用例集.md》中的标准格式。

---

## 8. 断言（assertions）类型与用法

- **每个 assertion 必须指定 type，常见类型及参数如下：**
  - row_count: { expected, min, max, message }
  - not_null: { columns, message }
  - unique: { columns, message }
  - range: { field, min, max, message }
  - regex: { field, pattern, message }
  - custom: { expression, message }
  - column_exists: { columns, message }
  - data_type: { columns, types, message }
  - value_in: { field, values, message }
  - relationship: { left_field, right_field, type, message }
- **断言字段必须是 source 步骤的输出字段。**
- **on_failure 推荐 error，生产环境不建议用 ignore。**

---

## 9. union 步骤注意事项

- **sources 必须是前置步骤名，不能参数化。**
- **所有 sources 的输出字段结构必须兼容。**
- **mode 支持 union（去重并集）、union_all（保留重复并集）、intersect（交集）、except（差集），具体用法详见下方示例和说明。**
- **add_source_column/source_column 可选，便于追踪来源。**
- **remove_duplicates 仅对 union 有效。**

---


**场景：找出既是客户又是供应商的公司名称**

```jsonc
{
  "uqm": {
    "metadata": {
      "name": "IntersectCustomerSupplierNames",
      "description": "找出既是客户又是供应商的公司名称",
      "version": "1.0",
      "author": "UQM Expert",
      "tags": [
        "intersect",
        "customer",
        "supplier",
        "company"
      ]
    },
    "steps": [
      {
        "name": "get_customer_names",
        "type": "query",
        "config": {
          "data_source": "customers",
          "dimensions": [
            {"expression": "customer_name", "alias": "company_name"}
          ]
        }
      },
      {
        "name": "get_supplier_names",
        "type": "query",
        "config": {
          "data_source": "suppliers",
          "dimensions": [
            {"expression": "supplier_name", "alias": "company_name"}
          ]
        }
      },
      {
        "name": "intersect_company_names",
        "type": "union",
        "config": {
          "sources": ["get_customer_names", "get_supplier_names"],
          "mode": "intersect"
        }
      }
    ],
    "output": "intersect_company_names"
  }
}
```

**预期输出示例：**
```jsonc
{
    "success": true,
    "data": [
        {"company_name": "长三角服装集团"},
        {"company_name": "华南电子配件厂"}
    ],
    "metadata": {
        "name": "IntersectCustomerSupplierNames",
        "description": "找出既是客户又是供应商的公司名称",
        "version": "1.0",
        "author": "UQM Expert",
        "created_at": null,
        "updated_at": null,
        "tags": [
            "intersect",
            "customer",
            "supplier",
            "company"
        ]
    },
    "execution_info": {
        "total_time": 0.01,
        "row_count": 2,
        "steps_executed": 3
    },
    "step_results": [
        {
            "step_name": "get_customer_names",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.003,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "get_supplier_names",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 8,
            "execution_time": 0.002,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "intersect_company_names",
            "step_type": "union",
            "status": "completed",
            "data": null,
            "row_count": 2,
            "execution_time": 0.001,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

---

## 10. 典型用例示例（API请求结构）

### 10.1 复杂嵌套过滤条件
```jsonc
{
  "uqm": {
    "metadata": {"name": "复杂员工筛选查询"},
    "steps": [
      {
        "name": "complex_employee_filter",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": ["employee_id", "salary"],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "logic": "OR",
                  "conditions": [
                    {"field": "salary", "operator": ">", "value": "$minSalary"},
                    {"field": "department_id", "operator": "=", "value": "$deptId"}
                  ]
                },
                {"field": "hire_date", "operator": ">", "value": "$hireAfter"}
              ]
            }
          ]
        }
      }
    ],
    "output": "complex_employee_filter"
  },
  "parameters": {"minSalary": 20000, "deptId": 1, "hireAfter": "2022-01-01"},
  "options": {}
}
```

### 10.2 断言用例
```jsonc
{
  "metadata": {"name": "验证订单总数"},
  "steps": [
    {
      "name": "count_orders",
      "type": "query",
      "config": {
        "data_source": "orders",
        "metrics": [
          {"name": "order_id", "aggregation": "COUNT", "alias": "total_orders"}
        ]
      }
    },
    {
      "name": "assert_order_count",
      "type": "assert",
      "config": {
        "source": "count_orders",
        "assertions": [
          {"type": "range", "field": "total_orders", "min": 100, "max": 10000, "message": "订单数量应在100-10000之间"}
        ]
      }
    }
  ],
  "output": "count_orders"
}
```

---

## 11. 常见错误与陷阱总结

- filter 字段不能引用本 step 的 metrics/calculated_fields 别名。
- group_by 字段也不能引用本 step 的 metrics/calculated_fields/dimensions 的别名。
- having 字段才可用于聚合/计算字段过滤。
- 如需基于计算字段分组，需增加一个 step 先生成该字段，或直接在 group_by 里写表达式。
- 大模型生成时应自动判断并修正 group_by 字段为本 step 计算字段别名的情况。
- 参数类型、字段名、步骤名、输出名均需严格匹配。
- steps、output、sources 等结构字段不能参数化。
- union 步骤所有 sources 字段结构必须兼容。
- 断言字段必须是 source 步骤的输出字段。
- 复杂嵌套过滤条件建议用 logic/conditions 递归表达。
- 任何字段引用不明确、参数未定义、类型不匹配都会导致校验失败或运行报错。

---

如需更多用例和特殊场景，请参考项目内各类查询用例和测试文档。 