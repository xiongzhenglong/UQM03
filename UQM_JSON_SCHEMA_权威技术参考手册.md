# UQM JSON Schema 权威技术参考手册

**版本: 2.0**
**最后更新: 2024-08-16**

---

## 1. 引言

本文档是 UQM (Unified Query Model) JSON 结构和语法的官方权威技术参考。它旨在为 AI 大语言模型 (LLM) 和高级开发人员提供一个极度精确、结构化、无歧义的指南，以确保生成和校验的 UQM JSON 的正确性和一致性。

本文档是生成和校验 UQM JSON 的**唯一事实来源 (Single Source of Truth)**。

### 1.1 核心原则

*   **绝对精确**: 所有字段、参数、类型和有效值都基于 UQM 源代码进行定义和枚举。
*   **AI 友好**: 文档采用高度结构化的 Markdown 格式，大量使用表格，便于机器解析。
*   **用例驱动**: 关键概念和常见陷阱均提供正反用例对比，以消除歧义。
*   **消除歧义**: 为所有规则建立唯一标准，明确定义边界条件。

### 1.2 目标读者

*   需要生成或解析 UQM JSON 的 AI 大语言模型。
*   使用 UQM 查询引擎的高级开发人员、数据分析师和架构师。

---

## 2. 全局请求结构

一个完整的 UQM API 请求由一个 JSON 对象表示，该对象包含 `uqm` 和 `parameters` 两个可选的顶级字段。服务器的执行端点需要的是 `uqm` 字段内的完整查询定义。

```json
{
  "uqm": {
    "metadata": { ... },
    "steps": [ ... ],
    "output": "step_name"
  },
  "parameters": {
    "param_name": "param_value"
  }
}
```

| 字段名       | 类型   | 是否必需 | 描述                                                                                                                             |
| :----------- | :----- | :------- | :------------------------------------------------------------------------------------------------------------------------------- |
| `uqm`        | Object | 是       | 包含 UQM 查询定义的完整对象。                                                                                                    |
| `parameters` | Object | 否       | **运行时参数**：一个键值对对象，用于在查询执行时动态传入变量。这些参数可以在 `steps` 的 `config` 中通过 `$param` 语法引用。 |

### 2.1 UQM 内部结构

`uqm` 对象包含 `metadata`、`steps` 和 `output` 三个核心字段。

| 字段名     | 类型          | 是否必需 | 描述                                                         |
| :--------- | :------------ | :------- | :----------------------------------------------------------- |
| `metadata` | Object        | 是       | 描述查询的元数据，如名称、描述等。                           |
| `steps`    | Array<Object> | 是       | 定义查询工作流的核心，包含一个或多个步骤（Step）对象的数组。 |
| `output`   | String        | 是       | 指定最终要输出结果的步骤的 `name`。                          |

---

## 3. 步骤 (Step) 通用结构

`steps` 数组中的每个对象都遵循统一的结构。

```json
{
  "name": "unique_step_name",
  "type": "query",
  "source": "previous_step_name",
  "config": { ... },
  "params": { ... }
}
```

| 字段名     | 类型          | 是否必需                               | 描述                                                                                                                                              |
| :--------- | :------------ | :------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`     | String        | 是                                     | 步骤的唯一标识符。在整个 `steps` 数组中必须是唯一的。                                                                                             |
| `type`     | String        | 是                                     | 步骤的类型。决定了 `config` 对象的结构和行为。                                                                                                    |
| `source`   | String/Array  | 否 (除 `Enrich`, `Pivot` 等步骤外)     | 指定该步骤的数据来源。通常是上一个步骤的 `name`。某些步骤（如 `Union`）可以接受字符串数组作为来源。                                                  |
| `config`   | Object        | 是                                     | 步骤的核心配置，其结构由 `type` 字段决定。                                                                                                        |
| `params`   | Object        | 否                                     | 定义此步骤作用域内的参数。                                                                                                                        |
| `enabled`  | Boolean       | 否                                     | 如果设置为 `false`，此步骤将被跳过。默认为 `true`。                                                                                               |
| `cache`    | Object        | 否                                     | 控制此步骤的缓存行为，如 `{"enabled": true, "ttl": 3600}`。                                                                                        |

### 3.1 步骤类型 (type)

`type` 字段决定了步骤的功能。以下是所有有效的步骤类型：

| `type`   | 功能简介                                             |
| :------- | :----------------------------------------------------- |
| `query`  | 从数据源查询、筛选、聚合和转换数据。功能最强大的核心步骤。 |
| `enrich` | 将一个数据源（主表）与另一个数据源（查找表）进行连接 (Join)。 |
| `pivot`  | 将长格式数据转换为宽格式数据（数据透视）。           |
| `unpivot`| 将宽格式数据转换为长格式数据（逆透视）。             |
| `union`  | 将两个或多个数据源的行合并在一起。                     |
| `assert` | 对数据进行质量检查和断言，不满足条件则报错。         |

---

## 4. 参数与数据引用

在 UQM 中，有两种主要的数据传递和引用方式：**外部参数注入**和**内部步骤引用**。清晰地理解这两者的区别至关重要。

### 4.1 外部参数 (`$param`)

对于需要在运行时动态改变的值（如用户输入的日期、ID 等），应使用外部参数。

1.  在顶层 `parameters` 对象中定义参数及其值。
2.  在 `steps` 的 `config` 内部，使用 `"$param.your_param_name"` 语法来引用该参数的值。

?> **正确**: 使用 `$param` 引用外部参数
```json
// 完整的 API 请求体
{
  "uqm": {
    "metadata": { "name": "查询特定用户" },
    "steps": [
      {
        "name": "get_user",
        "type": "query",
        "config": {
          "data_source": "users",
          "filters": [
            { "field": "user_id", "operator": "=", "value": "$param.target_user_id" }
          ]
        }
      }
    ],
    "output": "get_user"
  },
  "parameters": {
    "target_user_id": 12345
  }
}
```

### 4.2 内部数据引用 (步骤间数据流)

一个步骤的计算结果（数据行）可以通过 `source` 字段被后续步骤引用。关键在于，后续步骤引用的是上一步的**完整结果集**，而不是结果集中的某个特定值。

?> **错误**: 试图直接引用上一步结果中的值
> 下例中的 `value: "${dept_id}"` 是 **无效语法**。一个步骤的 `config` 无法直接解析和获取另一个步骤输出的行级数据。
```json
// ... (前一个步骤 filter_it_department 输出包含 dept_id 的行)
{
  "name": "get_employees_in_it",
  "type": "query",
  "source": "filter_it_department", // 这只是指定了数据来源，但并未加载数据
  "config": {
    "data_source": "employees",
    "filters": [
      // 错误！无法这样引用 filter_it_department 输出的 dept_id
      { "field": "e.department_id", "operator": "=", "value": "${dept_id}" }
    ]
  }
}
```

?> **正确**: 使用 `enrich` 或 `join` 关联数据
> 要实现上述目标，正确的方式是使用 `enrich` 步骤 (或 `query` 步骤中的 `joins`) 来连接两个数据集。

---

## 5. 最佳实践范例：关联查询

**目标**：查询并返回信息技术部所有在职员工的详细信息。

这是一个典型的关联查询场景。最高效、最规范的做法是使用单个 `query` 步骤，通过 `joins` 直接连接 `employees` 和 `departments` 表，然后进行筛选。

?> **推荐**: 使用单 `query` + `join` 的方式
```json
{
  "uqm": {
    "metadata": {
      "name": "get_it_department_employees",
      "description": "查询并返回信息技术部所有在职员工的详细信息。"
    },
    "steps": [
      {
        "name": "get_it_employees",
        "type": "query",
        "config": {
          "data_source": "employees e",
          "dimensions": [
            { "expression": "e.employee_id" },
            { "expression": "e.first_name" },
            { "expression": "e.last_name" },
            { "expression": "d.name", "alias": "department_name" }
          ],
          "joins": [
            {
              "type": "inner",
              "target": "departments d",
              "on": {
                "left": "e.department_id",
                "right": "d.department_id"
              }
            }
          ],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "field": "d.name",
                  "operator": "=",
                  "value": "信息技术部"
                },
                {
                  "field": "e.is_active",
                  "operator": "=",
                  "value": true
                }
              ]
            }
          ]
        }
      }
    ],
    "output": "get_it_employees"
  }
}
```
> **说明**: 这种方式将整个计算任务下推到数据库层面执行，避免了在应用内存中进行多步数据拉取和连接，性能最优，逻辑也最清晰。


---

## 6. 步骤详解

### 6.1 Query Step (`type: "query"`)

`query` 步骤是 UQM 的核心，负责数据的查询、计算和转换。它可以从数据库表或另一个步骤的结果中获取数据，并对其进行类似 SQL 的操作。

#### 6.1.1 `config` 字段

| 字段名                | 类型                 | 是否必需 | 描述                                                                                   |
| :-------------------- | :------------------- | :------- | :------------------------------------------------------------------------------------- |
| `data_source`         | String               | 是       | 数据来源。可以是数据库中的表名，也可以是另一个步骤的 `name`。                            |
| `dimensions`          | Array<Object/String> | 否       | **维度**：需要选择的列。作为分组和描述性属性。                                         |
| `metrics`             | Array<Object>        | 否       | **指标**：需要进行聚合计算的列。                                                       |
| `calculated_fields`   | Array<Object>        | 否       | **计算字段**：基于表达式动态创建的新字段，支持窗口函数。                               |
| `filters`             | Array<Object>        | 否       | **过滤器**：定义数据筛选条件，相当于 SQL 的 `WHERE` 子句。支持 `AND`/`OR` 嵌套。       |
| `joins`               | Array<Object>        | 否       | 定义与其它表或步骤的连接操作。                                                         |
| `group_by`            | Array<String>        | 否       | 定义分组依据的字段，相当于 SQL 的 `GROUP BY`。                                         |
| `having`              | Array<Object>        | 否       | 对分组后的结果进行筛选，相当于 SQL 的 `HAVING`。结构与 `filters` 相同。                |
| `order_by`            | Array<Object/String> | 否       | 定义结果的排序方式。                                                                   |
| `limit`               | Integer              | 否       | 限制返回的最大行数。                                                                   |
| `offset`              | Integer              | 否       | 跳过指定的行数，用于分页。                                                             |

**核心规则**: `config` 中必须至少包含 `dimensions`, `metrics`, `calculated_fields` 之一。

#### 6.1.2 字段对象结构

**Dimension 对象**

为了明确性和可扩展性，**强烈推荐**使用对象格式。

| 字段名       | 类型   | 是否必需 | 描述                                     |
| :----------- | :----- | :------- | :--------------------------------------- |
| `expression` | String | 是       | 字段表达式，可以是简单的列名或复杂的计算。 |
| `alias`      | String | 否       | 字段的别名。如果未提供，则使用 `expression`。 |

?> **正确 (推荐)**: 使用对象格式
```json
"dimensions": [
  { "expression": "p.product_name", "alias": "productName" },
  { "expression": "order_date" }
]
```

?> **正确 (快捷方式)**: 字符串格式仅适用于简单列名
```json
"dimensions": [
  "product_name",
  "order_date"
]
```
> **说明**: ` "product_name" ` 是 ` { "expression": "product_name", "alias": "product_name" } ` 的简写形式。

**Metric 对象**

| 字段名        | 类型   | 是否必需 | 描述                                                                 |
| :------------ | :----- | :------- | :------------------------------------------------------------------- |
| `expression`  | String | 否       | 自定义聚合表达式，如 `SUM(price * quantity)`。如果提供了此字段，将忽略 `name` 和 `aggregation`。 |
| `name`        | String | 否       | 要聚合的字段名。当未使用 `expression` 时必需。                         |
| `aggregation` | String | 否       | 聚合函数。默认为 `"SUM"`。详见下表。                                   |
| `alias`       | String | 是       | 聚合结果的别名。                                                     |

**`aggregation` 有效值**:

| 值      | 别名    | 描述       |
| :------ | :------ | :--------- |
| `SUM`   |         | 合计       |
| `COUNT` |         | 计数       |
| `AVG`   | `MEAN`  | 平均值     |
| `MAX`   |         | 最大值     |
| `MIN`   |         | 最小值     |

**Calculated Field 对象**

| 字段名       | 类型   | 是否必需 | 描述                               |
| :----------- | :----- | :------- | :--------------------------------- |
| `expression` | String | 是       | 计算字段的 SQL 表达式。            |
| `alias`      | String | 是       | 计算结果的别名。                   |

#### 6.1.3 `filters` 结构

**简单条件**:
`{ "field": "column_name", "operator": "operator_value", "value": "some_value" }`

**逻辑组合**:
`{ "logic": "AND", "conditions": [ ... ] }` 或 `{ "logic": "OR", "conditions": [ ... ] }`

**`operator` 有效值**:

| 操作符          | 描述                     | `value` 类型      |
| :-------------- | :----------------------- | :---------------- |
| `=`             | 等于                     | String, Number    |
| `!=`            | 不等于                   | String, Number    |
| `>`             | 大于                     | String, Number    |
| `>=`            | 大于等于                 | String, Number    |
| `<`             | 小于                     | String, Number    |
| `<=`            | 小于等于                 | String, Number    |
| `IN`            | 包含在列表中             | Array             |
| `NOT IN`        | 不包含在列表中           | Array             |
| `LIKE`          | 模糊匹配 (使用 `%` 通配符) | String            |
| `IS NULL`       | 值为 NULL                | (无 `value` 字段) |
| `IS NOT NULL`   | 值不为 NULL              | (无 `value` 字段) |


### 6.2 Enrich Step (`type: "enrich"`)

通过连接（Join）操作，使用一个数据集（`lookup`）的信息来丰富另一个数据集（`source`）。

#### 6.2.1 `config` 字段

| 字段名       | 类型                 | 是否必需 | 描述                                                                                              |
| :----------- | :------------------- | :------- | :------------------------------------------------------------------------------------------------ |
| `source`     | String               | 是       | **主表**: 需要被丰富数据的步骤 `name`。                                                           |
| `lookup`     | String / Object      | 是       | **查找表**: 提供信息的数据源。可以是另一个步骤的 `name`，或是一个从数据库查询的表对象。         |
| `on`         | String / Array / Object | 是       | **连接键**: 定义连接条件。                                                                        |
| `join_type`  | String               | 否       | 连接类型。默认为 `"left"`。                                                                       |

#### 6.2.2 字段详解

**`lookup` 对象**:
当从数据库直接查找时，使用对象格式：
`{ "table": "db_table_name", "columns": ["col1", "col2"], "where": [ ... ] }`

**`on` 格式**:
*   **字符串**: ` "user_id" ` (左右两表使用同名的键)
*   **数组**: ` ["company_id", "date"] ` (多键连接)
*   **对象**: ` { "left": "uid", "right": "user_id" } ` (左右两表使用不同名的键)

**`join_type` 有效值**:
基于 `pandas.merge` 实现。

| 值      | 描述                                     |
| :------ | :--------------------------------------- |
| `left`  | **左连接 (默认)**: 保留所有 `source` 的行。  |
| `right` | **右连接**: 保留所有 `lookup` 的行。         |
| `outer` | **全连接**: 保留所有 `source` 和 `lookup` 的行。 |
| `inner` | **内连接**: 只保留 `source` 和 `lookup` 中能匹配上的行。 |
| `full`  | `outer` 的别名。                         |

?> **常见陷阱: 列名冲突**
> 如果 `source` 和 `lookup` 数据源中存在同名字段（连接键除外），`enrich` 后的结果中，来自 `lookup` 数据源的同名字段会自动添加 `_y` 后缀以区分。

### 6.3 Pivot Step (`type: "pivot"`)

数据透视，将长格式数据转换为宽格式。

#### 6.3.1 `config` 字段

| 字段名           | 类型                 | 是否必需 | 描述                                                         |
| :--------------- | :------------------- | :------- | :----------------------------------------------------------- |
| `source`         | String               | 是       | 提供长格式数据的步骤 `name`。                                |
| `index`          | String / Array<String> | 是       | 作为新表**行**的字段。                                       |
| `columns`        | String / Array<String> | 是       | 其**值**将成为新表**列名**的字段。                           |
| `values`         | String / Array<String> | 是       | 需要被聚合以填充新表单元格的字段。                           |
| `agg_func`       | String / Object      | 否       | 聚合函数。默认为 `"sum"`。                                   |
| `fill_value`     | Any                  | 否       | 用于填充缺失值 (NaN)。默认为 `0`。                           |
| `column_prefix`  | String               | 否       | 为生成的新列名添加统一前缀。                                 |
| `column_suffix`  | String               | 否       | 为生成的新列名添加统一后缀。                                 |

?> **常见陷阱: 字段引用**
> `index`, `columns`, `values` 引用的字段名**必须**是上一步 `source` 输出结果中的字段名（或别名），而不是原始的 `table.column` 表达式。

#### 6.3.2 `agg_func` 详解

**`agg_func` 有效值**:

| 值      | 别名    | 描述             |
| :------ | :------ | :--------------- |
| `sum`   |         | 合计             |
| `mean`  | `avg`   | 平均值           |
| `count` |         | 计数             |
| `min`   |         | 最小值           |
| `max`   |         | 最大值           |
| `std`   |         | 标准差           |
| `var`   |         | 方差             |
| `first` |         | 第一个值         |
| `last`  |         | 最后一个值       |

?> **正确**: 使用单一聚合函数
```json
"agg_func": "mean"
```

?> **正确**: 对同一 `values` 字段应用多种聚合
```json
"values": "sales",
"agg_func": {
  "total_sales": "sum",
  "order_count": "count"
}
```
> **说明**: 当使用对象格式时，`key` (`total_sales`) 成为新列名的一部分，`value` (`sum`) 是要应用的聚合函数。


### 6.4 Unpivot Step (`type: "unpivot"`)

逆透视，将宽格式数据转换为长格式。在 pandas 中称为 `melt`。

#### 6.4.1 `config` 字段

| 字段名       | 类型                 | 是否必需 | 描述                                               |
| :----------- | :------------------- | :------- | :------------------------------------------------- |
| `source`     | String               | 是       | 提供宽格式数据的步骤 `name`。                      |
| `id_vars`    | String / Array<String> | 是       | **标识列**: 在转换中保持不变的列。                 |
| `value_vars` | Array<String>        | 是       | **转换列**: 需要被逆透视的列。                     |
| `var_name`   | String               | 否       | 存储原列名的新列的名称。默认为 `"variable"`。    |
| `value_name` | String               | 否       | 存储原单元格值的新列的名称。默认为 `"value"`。     |

?> **正确**:
```json
"id_vars": ["country", "product"],
"value_vars": ["sales_2022", "sales_2023"],
"var_name": "year",
"value_name": "sales"
```
> **说明**: `sales_2022` 和 `sales_2023` 这两列会被转换为两行，并生成一个新的 `year` 列 (值为 `sales_2022`, `sales_2023`) 和一个 `sales` 列。

### 6.5 Union Step (`type: "union"`)

将来自多个来源的数据行合并为一个数据集。

#### 6.5.1 `config` 字段

| 字段名              | 类型          | 是否必需 | 描述                                                                       |
| :------------------ | :------------ | :------- | :------------------------------------------------------------------------- |
| `sources`           | Array<String> | 是       | 需要合并的步骤 `name` 列表。**必须包含至少2个步骤**。                        |
| `add_source_column` | Boolean       | 否       | 如果为 `true`，添加一列以标识每行数据的来源步骤。默认为 `false`。           |
| `source_column`     | String        | 否       | 当 `add_source_column` 为 `true` 时，指定来源列的名称。默认为 `"source"`。    |
| `remove_duplicates` | Boolean       | 否       | 如果为 `true`，在合并后移除完全重复的行。默认为 `false`。                    |

?> **核心规则: Schema 一致性**
> 为了保证合并的正确性，所有 `sources` 中的步骤结果**应具有完全相同的列名和数据类型**。`union` 步骤本身不执行 schema 对齐。

### 6.6 Assert Step (`type: "assert"`)

对数据进行断言。如果任何断言失败，整个查询将失败。如果成功，则原样返回 `source` 的数据。

#### 6.6.1 `config` 字段

| 字段名       | 类型          | 是否必需 | 描述                             |
| :----------- | :------------ | :------- | :------------------------------- |
| `source`     | String        | 是       | 需要进行断言的步骤 `name`。      |
| `assertions` | Array<Object> | 是       | 一个或多个断言规则对象的列表。   |

#### 6.6.2 断言对象结构

每个断言对象必须包含一个 `type` 字段。

**行数断言 (`row_count`)**
检查数据集的总行数。

| 字段名      | 类型    | 描述               |
| :---------- | :------ | :----------------- |
| `type`      | String  | `"row_count"`      |
| `expected`  | Integer | 期望的确切行数。   |
| `min`       | Integer | 期望的最小行数。   |
| `max`       | Integer | 期望的最大行数。   |

**非空断言 (`not_null`)**
检查指定列不包含 `null` 或空字符串。

| 字段名   | 类型          | 描述                     |
| :------- | :------------ | :----------------------- |
| `type`   | String        | `"not_null"`             |
| `columns`| Array<String> | 需要检查非空的列名列表。 |

**唯一性断言 (`unique`)**
检查指定列（或列组合）的值是唯一的。

| 字段名   | 类型          | 描述                       |
| :------- | :------------ | :------------------------- |
| `type`   | String        | `"unique"`                 |
| `columns`| Array<String> | 需要检查唯一性的列名列表。 |

**范围断言 (`range`)**
检查数值列的值是否在指定范围内（包含边界）。

| 字段名   | 类型   | 描述                       |
| :------- | :----- | :------------------------- |
| `type`   | String | `"range"`                  |
| `column` | String | 需要检查的单个列名。       |
| `min`    | Number | 允许的最小值。             |
| `max`    | Number | 允许的最大值。             |


---
## 7. 全局配置字段速查表

下表按字母顺序列出了所有 `config` 中可能用到的字段，并注明其所属的步骤类型。

| 字段名                | 所属步骤                                  |
| :-------------------- | :---------------------------------------- |
| `add_source_column`   | `union`                                   |
| `agg_func`            | `pivot`                                   |
| `assertions`          | `assert`                                  |
| `calculated_fields`   | `query`                                   |
| `column_prefix`       | `pivot`                                   |
| `column_suffix`       | `pivot`                                   |
| `columns`             | `pivot`, `enrich` (in lookup), `assert`   |
| `data_source`         | `query`                                   |
| `dimensions`          | `query`                                   |
| `fill_value`          | `pivot`                                   |
| `filters`             | `query`                                   |
| `group_by`            | `query`                                   |
| `having`              | `query`                                   |
| `id_vars`             | `unpivot`                                 |
| `index`               | `pivot`                                   |
| `join_type`           | `enrich`, `query` (in `joins`)            |
| `joins`               | `query`                                   |
| `limit`               | `query`                                   |
| `lookup`              | `enrich`                                  |
| `metrics`             | `query`                                   |
| `offset`              | `query`                                   |
| `on`                  | `enrich`, `query` (in `joins`)            |
| `order_by`            | `query`                                   |
| `remove_duplicates`   | `union`                                   |
| `source`              | `enrich`, `pivot`, `unpivot`, `union`, `assert` |
| `source_column`       | `union`                                   |
| `sources`             | `union`                                   |
| `table`               | `enrich` (in lookup)                      |
| `target`              | `query` (in `joins`)                      |
| `value_name`          | `unpivot`                                 |
| `value_vars`          | `unpivot`                                 |
| `values`              | `pivot`                                   |
| `var_name`            | `unpivot`                                 |
| `where`               | `enrich` (in lookup)                      | 