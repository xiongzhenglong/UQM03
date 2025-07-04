# UQM 技术规范文档 - JSON Schema & 参数传递

## 📋 文档说明

本文档专门为 AI 系统和开发者提供精确的 UQM JSON Schema 定义和参数传递规范。重点关注技术实现细节，确保参数传递的准确性和查询构建的正确性。

## 🏗️ 核心 JSON Schema 结构

### 1. 顶层请求结构

```typescript
interface UQMRequest {
  uqm: {
    metadata: MetadataConfig;
    steps: StepConfig[];
    output?: string;  // 可选，默认最后一个步骤
  };
  parameters?: Record<string, any>;  // 运行时参数
  options?: ExecutionOptions;       // 执行选项
}
```

### 2. 参数传递机制

#### 2.1 参数定义格式
```typescript
interface ParameterConfig {
  [key: string]: any;  // 参数名到值的映射
}
```

#### 2.2 参数引用语法
- **格式1**: `$parameter_name`
- **格式2**: `${parameter_name}`
- **支持类型**: string, number, boolean, array, object, null

#### 2.3 参数引用示例
```json
{
  "parameters": {
    "department_id": 1,
    "salary_min": 5000,
    "status_list": ["active", "pending"],
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    }
  }
}
```

在查询中使用：
```json
{
  "filters": [
    {
      "field": "department_id",
      "operator": "=",
      "value": "$department_id"
    },
    {
      "field": "salary",
      "operator": ">=", 
      "value": "${salary_min}"
    },
    {
      "field": "status",
      "operator": "IN",
      "value": "$status_list"
    }
  ]
}
```

## 🔧 Step 类型 Schema 定义

### 1. query 步骤 Schema

```typescript
interface QueryStep {
  name: string;
  type: "query";
  config: {
    data_source: string;                    // 表名或前置步骤名
    dimensions?: (string | DimensionConfig)[];  // 维度字段
    metrics?: MetricConfig[];               // 聚合字段
    calculated_fields?: CalculatedFieldConfig[];  // 计算字段
    filters?: FilterConfig[];               // 过滤条件
    joins?: JoinConfig[];                   // 表连接
    group_by?: string[];                    // 分组字段
    having?: FilterConfig[];                // HAVING条件
    order_by?: OrderConfig[];               // 排序
    limit?: number;                         // 行数限制
    offset?: number;                        // 偏移量
  };
}

interface DimensionConfig {
  expression: string;
  alias: string;
}

interface MetricConfig {
  name?: string;           // 字段名（用于聚合函数）
  aggregation?: string;    // 聚合函数
  expression?: string;     // 自定义表达式
  alias: string;          // 别名
}

interface CalculatedFieldConfig {
  alias: string;
  expression: string;
}

interface FilterConfig {
  field: string;
  operator: string;
  value: any;
  conditional?: {
    type: "expression";
    expression: string;
  };
}

interface JoinConfig {
  type: "INNER" | "LEFT" | "RIGHT" | "FULL";
  table: string;
  on: string;
}

interface OrderConfig {
  field: string;
  direction: "ASC" | "DESC";
}
```

### 2. assert 步骤 Schema

```typescript
interface AssertStep {
  name: string;
  type: "assert";
  config: {
    source: string;                    // 源步骤名
    assertions: AssertionConfig[];     // 断言规则
  };
}

interface AssertionConfig {
  type: "row_count" | "range" | "unique" | "not_null" | "value_in" | "custom";
  field?: string;                      // 字段名（type特定）
  expected?: number;                   // 期望值（row_count）
  min?: number;                        // 最小值（row_count, range）
  max?: number;                        // 最大值（row_count, range）
  values?: any[];                      // 允许值（value_in）
  expression?: string;                 // 自定义表达式（custom）
  message: string;                     // 错误消息
}
```

### 3. pivot 步骤 Schema

```typescript
interface PivotStep {
  name: string;
  type: "pivot";
  config: {
    source: string;                    // 源步骤名
    index: string;                     // 行索引字段
    columns: string;                   // 列字段
    values: string;                    // 值字段
    agg_func?: string;                 // 聚合函数，默认"sum"
    column_prefix?: string;            // 列名前缀
    fill_value?: any;                  // 填充值，默认null
  };
}
```

### 4. union 步骤 Schema

```typescript
interface UnionStep {
  name: string;
  type: "union";
  config: {
    sources: string[];                 // 源步骤名数组
    union_type?: "all" | "distinct";   // 联合类型，默认"all"
    column_mapping?: {                 // 列映射
      [source: string]: {
        [oldColumn: string]: string;
      };
    };
  };
}
```

### 5. enrich 步骤 Schema

```typescript
interface EnrichStep {
  name: string;
  type: "enrich";
  config: {
    source: string;                    // 源步骤名
    lookup: {
      table: string;                   // 查找表名
      columns: string[];               // 要获取的列
    };
    on: {
      left: string;                    // 左侧字段
      right: string;                   // 右侧字段
      operator?: string;               // 连接操作符，默认"="
    };
    join_type?: "left" | "inner" | "right" | "full";  // 连接类型
  };
}
```

## 🎯 参数传递核心规则

### 1. 参数值类型映射

```typescript
type ParameterValue = 
  | string 
  | number 
  | boolean 
  | null 
  | Array<any> 
  | Record<string, any>;
```

### 2. 参数引用上下文

参数可以在以下位置使用：
- `filters[].value`
- `calculated_fields[].expression`
- `metrics[].expression`
- `dimensions[].expression`
- `joins[].on`
- `having[].value`
- `limit`
- `offset`

### 3. 参数替换示例

**输入参数：**
```json
{
  "parameters": {
    "dept_id": 1,
    "year": 2024,
    "status_list": ["active", "pending"]
  }
}
```

**查询配置：**
```json
{
  "filters": [
    {
      "field": "department_id",
      "operator": "=",
      "value": "$dept_id"
    },
    {
      "field": "YEAR(hire_date)",
      "operator": "=",
      "value": "${year}"
    },
    {
      "field": "status",
      "operator": "IN",
      "value": "$status_list"
    }
  ]
}
```

**实际执行时替换为：**
```json
{
  "filters": [
    {
      "field": "department_id",
      "operator": "=",
      "value": 1
    },
    {
      "field": "YEAR(hire_date)",
      "operator": "=",
      "value": 2024
    },
    {
      "field": "status",
      "operator": "IN",
      "value": ["active", "pending"]
    }
  ]
}
```

## 🔍 字段引用规则

### 1. 表别名规则

当使用表别名时：
- `data_source` 必须包含别名：`"employees e"`
- 所有字段必须使用表别名前缀：`"e.employee_id"`
- `metrics.name` 必须包含表别名：`"e.salary"`

### 2. 字段引用限制

#### 2.1 同步骤字段引用限制
```json
{
  "config": {
    "calculated_fields": [
      {
        "alias": "sales_rank",
        "expression": "ROW_NUMBER() OVER (ORDER BY total_sales DESC)"
      }
    ],
    "filters": [
      {
        "field": "sales_rank",    // ❌ 错误：不能引用同步骤的计算字段
        "operator": "<=",
        "value": 5
      }
    ]
  }
}
```

#### 2.2 正确的多步骤引用
```json
{
  "steps": [
    {
      "name": "step1",
      "type": "query",
      "config": {
        "calculated_fields": [
          {
            "alias": "sales_rank",
            "expression": "ROW_NUMBER() OVER (ORDER BY total_sales DESC)"
          }
        ]
      }
    },
    {
      "name": "step2",
      "type": "query",
      "config": {
        "data_source": "step1",
        "filters": [
          {
            "field": "sales_rank",    // ✅ 正确：可以引用前步骤字段
            "operator": "<=",
            "value": 5
          }
        ]
      }
    }
  ]
}
```

### 3. 输出步骤字段定义

最终输出步骤必须明确定义字段：
```json
{
  "name": "final_output",
  "type": "query",
  "config": {
    "data_source": "previous_step",
    "dimensions": ["category"],           // ✅ 必须定义输出字段
    "metrics": [
      {
        "name": "total_sales",
        "aggregation": "SUM",
        "alias": "total_sales"
      }
    ],
    "filters": [
      {
        "field": "category",
        "operator": "=",
        "value": "$category"
      }
    ]
  }
}
```

## 🎨 操作符规范

### 1. 比较操作符
```typescript
type ComparisonOperator = 
  | "=" | "!=" | "<" | "<=" | ">" | ">="
  | "LIKE" | "NOT LIKE"
  | "IS NULL" | "IS NOT NULL";
```

### 2. 集合操作符
```typescript
type SetOperator = "IN" | "NOT IN" | "BETWEEN" | "NOT BETWEEN";
```

### 3. 逻辑操作符
```typescript
type LogicalOperator = "AND" | "OR" | "NOT";
```

### 4. 聚合函数
```typescript
type AggregationFunction = 
  | "COUNT" | "SUM" | "AVG" | "MIN" | "MAX"
  | "COUNT_DISTINCT" | "STDDEV" | "VARIANCE";
```

## 📊 完整技术示例

### 示例1：参数化查询
```json
{
  "uqm": {
    "metadata": {
      "name": "员工薪资查询",
      "description": "根据参数查询员工薪资信息"
    },
    "steps": [
      {
        "name": "query_employees",
        "type": "query",
        "config": {
          "data_source": "employees e",
          "dimensions": [
            "e.employee_id",
            "e.first_name",
            "e.last_name",
            "d.name AS department_name"
          ],
          "metrics": [
            {
              "name": "e.salary",
              "aggregation": "AVG",
              "alias": "avg_salary"
            }
          ],
          "joins": [
            {
              "type": "INNER",
              "table": "departments d",
              "on": "e.department_id = d.department_id"
            }
          ],
          "filters": [
            {
              "field": "e.department_id",
              "operator": "=",
              "value": "$department_id"
            },
            {
              "field": "e.salary",
              "operator": ">=",
              "value": "${min_salary}"
            },
            {
              "field": "e.hire_date",
              "operator": "BETWEEN",
              "value": "$date_range"
            }
          ],
          "group_by": ["e.employee_id", "e.first_name", "e.last_name", "d.name"]
        }
      }
    ]
  },
  "parameters": {
    "department_id": 1,
    "min_salary": 5000,
    "date_range": ["2023-01-01", "2024-12-31"]
  }
}
```

### 示例2：多步骤处理
```json
{
  "uqm": {
    "metadata": {
      "name": "销售排名分析",
      "description": "计算销售排名并筛选前N名"
    },
    "steps": [
      {
        "name": "calculate_sales",
        "type": "query",
        "config": {
          "data_source": "order_items oi",
          "dimensions": ["p.category"],
          "metrics": [
            {
              "name": "oi.quantity",
              "aggregation": "SUM",
              "alias": "total_quantity"
            }
          ],
          "calculated_fields": [
            {
              "alias": "sales_amount",
              "expression": "SUM(oi.quantity * oi.unit_price)"
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
        "name": "add_rankings",
        "type": "query",
        "config": {
          "data_source": "calculate_sales",
          "dimensions": ["category"],
          "metrics": [
            {
              "name": "total_quantity",
              "aggregation": "SUM",
              "alias": "total_quantity"
            },
            {
              "name": "sales_amount",
              "aggregation": "SUM",
              "alias": "sales_amount"
            }
          ],
          "calculated_fields": [
            {
              "alias": "sales_rank",
              "expression": "ROW_NUMBER() OVER (ORDER BY sales_amount DESC)"
            }
          ]
        }
      },
      {
        "name": "filter_top_results",
        "type": "query",
        "config": {
          "data_source": "add_rankings",
          "dimensions": ["category"],
          "metrics": [
            {
              "name": "total_quantity",
              "aggregation": "SUM",
              "alias": "total_quantity"
            },
            {
              "name": "sales_amount",
              "aggregation": "SUM",
              "alias": "sales_amount"
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
              "field": "sales_rank",
              "operator": "<=",
              "value": "$top_n"
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
    "output": "filter_top_results"
  },
  "parameters": {
    "top_n": 5
  }
}
```

## 🚨 关键技术约束

### 1. 字段引用约束
- 同步骤内不能在 `filters` 中引用 `calculated_fields` 或 `metrics` 的别名
- 必须使用多步骤查询处理计算字段的过滤
- 聚合结果的过滤使用 `having` 而不是 `filters`

### 2. 表别名约束
- 使用表别名时，所有字段引用必须包含表别名前缀
- `data_source` 中的表别名定义必须与字段引用一致

### 3. 参数传递约束
- 参数值必须是有效的 JSON 数据类型
- 参数引用语法：`$param` 或 `${param}`
- 参数替换在执行时进行，不影响 Schema 结构

### 4. 输出步骤约束
- 最终输出步骤必须明确定义所有输出字段
- 不能只有 `filters` 而缺少字段定义

---

**技术说明：** 本文档专注于 JSON Schema 和参数传递的技术实现，为 AI 系统提供精确的构建指导。
