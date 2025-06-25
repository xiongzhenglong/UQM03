根据您提供的代码来源，该文件实际上是**统一查询模型 (UQM) 后端执行引擎**的代码库合并表示。因此，我将根据这些代码为您生成 UQM 配置的详细 JSON Schema，并提供相应的解释。这个 Schema 将描述如何构建有效的 UQM 请求，以便与后端引擎交互。

---

### UQM 配置的详尽 JSON Schema

以下是基于您提供的 UQM 后端代码生成的 JSON Schema，它详细定义了 UQM 配置的结构、字段类型和约束。

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "UQM Query Definition Schema",
  "description": "统一查询模型 (UQM) 的 JSON 定义规范，用于后端执行引擎。",
  "type": "object",
  "required": ["steps"],
  "properties": {
    "metadata": {
      "type": "object",
      "description": "关于UQM查询的元数据信息。",
      "properties": {
        "name": {
          "type": "string",
          "description": "查询的名称。",
          "default": "未命名查询"
        },
        "description": {
          "type": "string",
          "description": "查询的详细描述。"
        },
        "version": {
          "type": "string",
          "description": "查询的版本号。",
          "default": "1.0"
        },
        "author": {
          "type": "string",
          "description": "查询的作者。"
        },
        "created_at": {
          "type": "string",
          "format": "date-time",
          "description": "查询的创建时间（ISO 8601格式）。"
        },
        "updated_at": {
          "type": "string",
          "format": "date-time",
          "description": "查询的最后更新时间（ISO 8601格式）。"
        },
        "tags": {
          "type": "array",
          "items": { "type": "string" },
          "description": "与查询相关的标签列表。"
        }
      },
      "examples": [
        {
          "name": "示例查询",
          "description": "这是一个示例UQM查询"
        }
      ]
    },
    "parameters": {
      "type": "array",
      "description": "定义UQM查询中可用的参数列表。",
      "items": {
        "type": "object",
        "required": ["name", "type"],
        "properties": {
          "name": {
            "type": "string",
            "description": "参数名称。"
          },
          "type": {
            "type": "string",
            "description": "参数的数据类型（例如：string, integer, float, boolean）。"
          },
          "default": {
            "description": "参数的默认值，如果未提供则使用此值。"
          },
          "required": {
            "type": "boolean",
            "description": "参数是否必需。",
            "default": true
          },
          "description": {
            "type": "string",
            "description": "参数的描述。"
          }
        }
      }
    },
    "steps": {
      "type": "array",
      "description": "UQM查询的执行步骤列表，按顺序定义。",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["name", "type", "config"],
        "properties": {
          "name": {
            "type": "string",
            "description": "步骤的唯一名称，用于引用和输出。"
          },
          "type": {
            "type": "string",
            "description": "步骤的类型。",
            "enum": ["query", "enrich", "pivot", "unpivot", "union", "assert"]
          },
          "config": {
            "type": "object",
            "description": "当前步骤的详细配置。"
          }
        },
        "discriminator": {
          "propertyName": "type",
          "mapping": {
            "query": "#/$defs/QueryStepConfig",
            "enrich": "#/$defs/EnrichStepConfig",
            "pivot": "#/$defs/PivotStepConfig",
            "unpivot": "#/$defs/UnpivotStepConfig",
            "union": "#/$defs/UnionStepConfig",
            "assert": "#/$defs/AssertStepConfig"
          }
        }
      },
      "examples": [
        [
          {
            "name": "step1",
            "type": "query",
            "config": {
              "data_source": "users",
              "dimensions": ["id", "name"],
              "metrics": [],
              "filters": []
            }
          }
        ]
      ]
    },
    "output": {
      "type": "string",
      "description": "指定作为UQM查询最终结果的步骤名称。",
      "examples": ["step1"]
    },
    "options": {
      "type": "object",
      "description": "UQM执行时的可选配置，例如缓存设置。",
      "properties": {
        "cache_enabled": {
          "type": "boolean",
          "description": "是否启用查询结果缓存，默认为true。"
        },
        "cache_ttl": {
          "type": "integer",
          "description": "缓存的生存时间（秒），默认为配置文件中的CACHE_DEFAULT_TIMEOUT。"
        },
        "timeout": {
          "type": "integer",
          "description": "查询执行的超时时间（秒）。"
        },
        "continue_on_error": {
          "type": "boolean",
          "description": "如果某个步骤执行失败，是否继续执行后续步骤，默认为false。"
        }
      },
      "examples": [
        {
          "cache_enabled": true,
          "timeout": 300
        }
      ]
    },
    "parameters_values": {
      "type": "object",
      "description": "运行时提供的参数值，用于替换UQM定义中的占位符。这些参数会由Pydantic的UQMRequest模型进行验证。"
    }
  },
  "$defs": {
    "QueryStepConfig": {
      "type": "object",
      "description": "查询步骤的配置，用于从数据源提取数据。",
      "required": ["data_source"],
      "properties": {
        "data_source": {
          "type": "string",
          "description": "要查询的数据源名称（例如表名或视图名）。"
        },
        "dimensions": {
          "type": "array",
          "description": "要选择的维度（列）。",
          "items": {
            "oneOf": [
              { "type": "string" },
              {
                "type": "object",
                "properties": {
                  "name": { "type": "string", "description": "字段名称。" },
                  "alias": { "type": "string", "description": "字段别名。" },
                  "expression": { "type": "string", "description": "自定义SQL表达式。" }
                },
                "anyOf": [{ "required": ["name"] }, { "required": ["expression"] }]
              }
            ]
          },
          "minItems": 0
        },
        "metrics": {
          "type": "array",
          "description": "要计算的指标（聚合列）。",
          "items": {
            "oneOf": [
              { "type": "string" },
              {
                "type": "object",
                "properties": {
                  "name": { "type": "string", "description": "指标字段名称。" },
                  "alias": { "type": "string", "description": "指标别名。" },
                  "aggregation": { "type": "string", "description": "聚合函数（例如：SUM, COUNT, AVG, MAX, MIN）。", "default": "SUM" },
                  "expression": { "type": "string", "description": "自定义SQL表达式。" }
                },
                "anyOf": [{ "required": ["name"] }, { "required": ["expression"] }]
              }
            ]
          },
          "minItems": 0
        },
        "calculated_fields": {
          "type": "array",
          "description": "自定义计算字段。",
          "items": {
            "type": "object",
            "required": ["alias", "expression"],
            "properties": {
              "alias": { "type": "string", "description": "计算字段的别名。" },
              "expression": { "type": "string", "description": "计算字段的SQL表达式。" }
            }
          }
        },
        "filters": {
          "type": "array",
          "description": "WHERE子句的过滤条件列表。",
          "items": { "$ref": "#/$defs/SQLCondition" }
        },
        "joins": {
          "type": "array",
          "description": "JOIN操作的配置列表。",
          "items": {
            "type": "object",
            "required": ["table", "on"],
            "properties": {
              "type": {
                "type": "string",
                "description": "JOIN类型（例如：INNER, LEFT, RIGHT, FULL）。",
                "default": "INNER"
              },
              "table": {
                "type": "string",
                "description": "要连接的表名。"
              },
              "on": {
                "oneOf": [
                  { "type": "string", "description": "JOIN条件字符串（例如：'t1.id = t2.ref_id'）。" },
                  { "$ref": "#/$defs/SQLCondition" }
                ],
                "description": "JOIN条件。"
              }
            }
          }
        },
        "group_by": {
          "type": "array",
          "description": "GROUP BY子句的字段列表。",
          "items": { "type": "string" }
        },
        "having": {
          "type": "array",
          "description": "HAVING子句的过滤条件列表。",
          "items": { "$ref": "#/$defs/SQLCondition" }
        },
        "order_by": {
          "type": "array",
          "description": "ORDER BY子句的排序字段列表。",
          "items": {
            "oneOf": [
              { "type": "string" },
              {
                "type": "object",
                "required": ["field"],
                "properties": {
                  "field": { "type": "string", "description": "排序字段。" },
                  "direction": { "type": "string", "enum": ["ASC", "DESC"], "default": "ASC", "description": "排序方向。" }
                }
              }
            ]
          }
        },
        "limit": {
          "type": "integer",
          "description": "限制返回的行数。"
        },
        "offset": {
          "type": "integer",
          "description": "跳过的行数。"
        }
      }
    },
    "EnrichStepConfig": {
      "type": "object",
      "description": "丰富化步骤的配置，通过连接查找表来丰富源数据。",
      "required": ["source", "lookup", "on"],
      "properties": {
        "source": {
          "type": "string",
          "description": "要丰富化的源数据的步骤名称。"
        },
        "lookup": {
          "oneOf": [
            {
              "type": "string",
              "description": "查找表数据的来源步骤名称。"
            },
            {
              "type": "object",
              "required": ["table"],
              "properties": {
                "table": {
                  "type": "string",
                  "description": "从数据库中查找表的名称。"
                },
                "columns": {
                  "type": "array",
                  "items": { "type": "string" },
                  "description": "从查找表中选择的列，默认为所有列（'*'）。"
                },
                "where": {
                  "type": "array",
                  "description": "查找表的过滤条件。",
                  "items": { "$ref": "#/$defs/SQLCondition" }
                }
              }
            }
          ],
          "description": "定义查找表的来源：可以是另一个步骤的输出，也可以是数据库表。"
        },
        "on": {
          "oneOf": [
            {
              "type": "string",
              "description": "用于连接源数据和查找表的单列名称（两表中的列名相同）。"
            },
            {
              "type": "array",
              "items": { "type": "string" },
              "description": "用于连接源数据和查找表的多列名称列表（两表中的列名相同）。"
            },
            {
              "type": "object",
              "required": ["left", "right"],
              "properties": {
                "left": { "type": "string", "description": "源数据中的连接列。" },
                "right": { "type": "string", "description": "查找表中的连接列。" },
                "condition": { "type": "string", "description": "更复杂的连接条件，例如 'source.id = lookup.ref_id AND source.status = 'active''" }
              }
            }
          ],
          "description": "定义连接源数据和查找表的条件。"
        },
        "join_type": {
          "type": "string",
          "description": "连接类型。",
          "enum": ["left", "right", "inner", "outer"],
          "default": "left"
        },
        "missing_strategy": {
          "type": "string",
          "description": "处理连接后缺失值（即查找表中无匹配项）的策略。",
          "enum": ["keep", "drop", "fill"],
          "default": "keep"
        },
        "fill_value": {
          "description": "当missing_strategy为'fill'时，用于填充缺失值的值。"
        }
      }
    },
    "PivotStepConfig": {
      "type": "object",
      "description": "透视步骤的配置，将数据从长格式转换为宽格式。",
      "required": ["source", "index", "columns", "values"],
      "properties": {
        "source": {
          "type": "string",
          "description": "要透视的源数据的步骤名称。"
        },
        "index": {
          "oneOf": [
            { "type": "string" },
            { "type": "array", "items": { "type": "string" } }
          ],
          "description": "用作新DataFrame索引的列或列列表。"
        },
        "columns": {
          "oneOf": [
            { "type": "string" },
            { "type": "array", "items": { "type": "string" } }
          ],
          "description": "用作新DataFrame列的列或列列表，其唯一值将成为新列名。"
        },
        "values": {
          "oneOf": [
            { "type": "string" },
            { "type": "array", "items": { "type": "string" } }
          ],
          "description": "用于填充新DataFrame值区域的列或列列表。"
        },
        "agg_func": {
          "oneOf": [
            {
              "type": "string",
              "description": "应用于values的单一聚合函数名称。",
              "enum": ["sum", "mean", "avg", "count", "min", "max", "std", "var", "first", "last"]
            },
            {
              "type": "object",
              "description": "映射values列到聚合函数的对象，支持为每个值列指定不同的聚合函数。",
              "patternProperties": {
                "^[a-zA-Z0-9_]+$": {
                  "type": "string",
                  "enum": ["sum", "mean", "avg", "count", "min", "max", "std", "var", "first", "last"]
                }
              },
              "additionalProperties": false
            }
          ],
          "default": "sum",
          "description": "聚合函数或聚合函数映射。"
        },
        "fill_value": {
          "type": ["number", "string", "boolean", "null"],
          "description": "用于填充透视表中NaN/缺失值的值。",
          "default": 0
        },
        "missing_strategy": {
          "type": "string",
          "description": "处理透视操作前源数据中缺失值的策略。",
          "enum": ["drop", "fill"],
          "default": "drop"
        },
        "missing_fill_value": {
          "description": "当missing_strategy为'fill'时，用于填充缺失值的值。",
          "default": 0
        },
        "null_strategy": {
          "type": "string",
          "description": "处理透视操作后结果中空值的策略。",
          "enum": ["keep", "drop", "fill", "zero"],
          "default": "keep"
        },
        "null_fill_value": {
          "description": "当null_strategy为'fill'时，用于填充空值的值。",
          "default": 0
        },
        "column_prefix": {
          "type": "string",
          "description": "为新生成的列名添加前缀。"
        },
        "column_suffix": {
          "type": "string",
          "description": "为新生成的列名添加后缀。"
        },
        "sort_by": {
          "oneOf": [
            { "type": "string" },
            { "type": "array", "items": { "type": "string" } }
          ],
          "description": "结果DataFrame的排序字段或字段列表。"
        },
        "sort_ascending": {
          "type": "boolean",
          "description": "排序方向，true为升序，false为降序。",
          "default": true
        }
      }
    },
    "UnpivotStepConfig": {
      "type": "object",
      "description": "逆透视步骤的配置，将数据从宽格式转换为长格式。",
      "required": ["source", "id_vars", "value_vars"],
      "properties": {
        "source": {
          "type": "string",
          "description": "要逆透视的源数据的步骤名称。"
        },
        "id_vars": {
          "oneOf": [
            { "type": "string" },
            { "type": "array", "items": { "type": "string" } }
          ],
          "description": "作为标识符变量的列或列列表，即不逆透视的列。"
        },
        "value_vars": {
          "oneOf": [
            { "type": "string" },
            { "type": "array", "items": { "type": "string" } }
          ],
          "description": "要逆透视的列或列列表。"
        },
        "var_name": {
          "type": "string",
          "description": "新变量列的名称，该列将包含来自value_vars的原始列名。",
          "default": "variable"
        },
        "value_name": {
          "type": "string",
          "description": "新值列的名称，该列将包含来自value_vars的原始值。",
          "default": "value"
        }
      }
    },
    "UnionStepConfig": {
      "type": "object",
      "description": "合并步骤的配置，用于合并多个数据集。",
      "required": ["sources"],
      "properties": {
        "sources": {
          "type": "array",
          "description": "要合并的源数据集的步骤名称列表。",
          "minItems": 2,
          "items": { "type": "string" }
        },
        "mode": {
          "type": "string",
          "description": "合并模式。",
          "enum": ["union", "union_all", "intersect", "except"],
          "default": "union"
        },
        "add_source_column": {
          "type": "boolean",
          "description": "是否在结果中添加一列指示每条记录的来源步骤名称。",
          "default": false
        },
        "source_column": {
          "type": "string",
          "description": "如果add_source_column为true，此列的名称。",
          "default": "_source"
        },
        "strict_schema": {
          "type": "boolean",
          "description": "在合并时是否严格检查源数据集的列结构一致性。如果为true，不一致会抛出错误。",
          "default": false
        }
      }
    },
    "AssertStepConfig": {
      "type": "object",
      "description": "断言步骤的配置，用于验证数据质量和业务规则。",
      "required": ["source", "assertions"],
      "properties": {
        "source": {
          "type": "string",
          "description": "要进行断言检查的源数据的步骤名称。"
        },
        "assertions": {
          "type": "array",
          "description": "要执行的断言规则列表。",
          "items": { "$ref": "#/$defs/AssertionRule" },
          "minItems": 1
        },
        "on_failure": {
          "type": "string",
          "description": "当断言失败时如何处理。",
          "enum": ["error", "warning", "ignore"],
          "default": "error"
        }
      }
    },
    "AssertionRule": {
      "type": "object",
      "required": ["type"],
      "properties": {
        "type": {
          "type": "string",
          "description": "断言的类型。",
          "enum": [
            "row_count", "not_null", "unique", "range", "regex", "custom",
            "column_exists", "data_type", "value_in", "relationship"
          ]
        }
      },
      "oneOf": [
        {
          "properties": {
            "type": { "const": "row_count" },
            "expected": { "type": "integer", "description": "期望的精确行数。" },
            "min": { "type": "integer", "description": "最小行数。" },
            "max": { "type": "integer", "description": "最大行数。" }
          },
          "minProperties": 2, "description": "行数断言。"
        },
        {
          "properties": {
            "type": { "const": "not_null" },
            "columns": {
              "oneOf": [
                { "type": "string" },
                { "type": "array", "items": { "type": "string" } }
              ],
              "description": "要检查非空值的列或列列表。"
            }
          },
          "required": ["columns"], "description": "非空断言。"
        },
        {
          "properties": {
            "type": { "const": "unique" },
            "columns": {
              "oneOf": [
                { "type": "string" },
                { "type": "array", "items": { "type": "string" } }
              ],
              "description": "要检查唯一性的列或列列表。"
            }
          },
          "required": ["columns"], "description": "唯一性断言。"
        },
        {
          "properties": {
            "type": { "const": "range" },
            "column": { "type": "string", "description": "要检查值范围的列。" },
            "min": { "type": "number", "description": "允许的最小值。" },
            "max": { "type": "number", "description": "允许的最大值。" }
          },
          "required": ["column"], "minProperties": 3, "description": "值范围断言。"
        },
        {
          "properties": {
            "type": { "const": "regex" },
            "column": { "type": "string", "description": "要检查正则表达式匹配的列。" },
            "pattern": { "type": "string", "description": "正则表达式模式。" }
          },
          "required": ["column", "pattern"], "description": "正则表达式断言。"
        },
        {
          "properties": {
            "type": { "const": "custom" },
            "expression": { "type": "string", "description": "用于自定义断言的Python表达式。" }
          },
          "required": ["expression"], "description": "自定义断言。"
        },
        {
          "properties": {
            "type": { "const": "column_exists" },
            "columns": {
              "oneOf": [
                { "type": "string" },
                { "type": "array", "items": { "type": "string" } }
              ],
              "description": "要检查是否存在的列或列列表。"
            }
          },
          "required": ["columns"], "description": "列存在断言。"
        },
        {
          "properties": {
            "type": { "const": "data_type" },
            "column": { "type": "string", "description": "要检查数据类型的列。" },
            "expected_type": { "type": "string", "enum": ["int", "float", "str", "bool", "number"], "description": "期望的数据类型。" }
          },
          "required": ["column", "expected_type"], "description": "数据类型断言。"
        },
        {
          "properties": {
            "type": { "const": "value_in" },
            "column": { "type": "string", "description": "要检查值是否在允许集合中的列。" },
            "allowed_values": {
              "type": "array",
              "description": "允许的值列表。",
              "items": { }
            }
          },
          "required": ["column", "allowed_values"], "description": "值域断言。"
        },
        {
          "properties": {
            "type": { "const": "relationship" },
            "expression": { "type": "string", "description": "用于定义列之间关系的表达式。目前此断言类型功能尚未完全实现。" }
          },
          "required": ["expression"], "description": "字段关系断言。"
        }
      ]
    },
    "SQLCondition": {
      "type": "object",
      "description": "单个SQL条件表达式。",
      "properties": {
        "field": {
          "type": "string",
          "description": "条件操作的字段名称。"
        },
        "operator": {
          "type": "string",
          "description": "操作符（例如：=, >, <, >=, <=, !=, LIKE, IN, BETWEEN, IS NULL, IS NOT NULL）。",
          "default": "="
        },
        "value": {
          "description": "与字段比较的值。对于IN和BETWEEN操作符，可以是数组。",
          "oneOf": [
            { "type": ["string", "number", "boolean", "null"] },
            { "type": "array", "items": { "type": ["string", "number", "boolean", "null"] } }
          ]
        }
      },
      "required": ["field", "operator"],
      "oneOf": [
        { "properties": { "operator": { "not": { "enum": ["IS NULL", "IS NOT NULL"] } } }, "required": ["value"] },
        { "properties": { "operator": { "enum": ["IS NULL", "IS NOT NULL"] } } }
      ]
    }
  }
}
```

---

### JSON Schema 解释说明

这个 JSON Schema 定义了 UQM (统一查询模型) 后端引擎所能处理的查询结构的蓝图。它旨在提供一个清晰、结构化的方式来描述复杂的数据操作流程，包括数据提取、转换、合并和验证。

#### 1. 顶层结构 (Root)

*   `$schema`: 指示此JSON Schema遵循的草案版本，便于工具理解 [非来源信息]。
*   `title`: Schema 的标题，描述其用途 [非来源信息]。
*   `description`: 对整个 UQM 定义的简要说明 [非来源信息]。
*   `type`: 根元素的类型，必须是 `object`。
*   `required`: 必需的顶层字段，`steps` 是 UQM 定义中不可或缺的部分，因为它定义了所有操作序列。
*   **`properties`**:
    *   **`metadata`**:
        *   类型为 `object`，用于存储 UQM 查询的元数据，如名称、描述、版本、作者等。这些信息有助于更好地管理和理解查询的目的和来源。
        *   `name`: 查询的名称，默认为"未命名查询"。
        *   `description`: 查询的描述。
        *   `version`: 查询的版本号，默认为"1.0"。
        *   `author`: 查询的作者。
        *   `created_at`, `updated_at`: 查询的创建和更新时间。
        *   `tags`: 一组用于分类和搜索的标签。
    *   **`parameters`**:
        *   类型为 `array`，包含 UQM 查询中可定义的参数列表。每个参数都是一个对象，包含 `name` (参数名)、`type` (数据类型)、`default` (默认值)、`required` (是否必需) 和 `description` (描述)。这些参数可以在查询步骤中作为占位符被替换。
    *   **`steps`**:
        *   类型为 `array`，是 UQM 定义的核心，包含一系列按顺序执行的步骤。
        *   `minItems: 1`：至少需要定义一个步骤。
        *   每个 `step` 对象必须包含 `name` (步骤的唯一名称)、`type` (步骤类型) 和 `config` (步骤配置)。
        *   `discriminator` 和 `mapping`：这部分利用 JSON Schema 的多态性，根据 `type` 字段的值，`config` 字段将引用 `$defs` 中定义的具体步骤配置Schema，例如 `query` 类型对应 `QueryStepConfig` [非来源信息]。
    *   **`output`**:
        *   类型为 `string`，指定哪个步骤的输出数据将作为整个 UQM 查询的最终结果。如果未指定，默认使用最后一个步骤的名称。
    *   **`options`**:
        *   类型为 `object`，提供运行时执行 UQM 的可选配置，如 `cache_enabled` (是否启用缓存) 和 `cache_ttl` (缓存有效期)。还支持 `timeout` 和 `continue_on_error` (是否在步骤失败时继续执行) 等选项。
    *   **`parameters_values`**:
        *   类型为 `object`，这是一个运行时才会提供的字段，用于传递实际的参数值给 UQM 请求。它与 `parameters` 定义的元数据信息不同。

#### 2. 步骤配置定义 (`$defs` 部分)

`$defs` 部分包含了各种特定步骤类型的详细配置 Schema。

*   **`QueryStepConfig` (查询步骤配置)**:
    *   **`data_source`**: 必需，指定要查询的表名或数据源名称。
    *   **`dimensions`**: 要选择的维度列，可以是字符串数组，也可以是包含 `name`、`alias` 和 `expression` 的对象。
    *   **`metrics`**: 要计算的聚合指标，可以是字符串数组或包含 `name`、`alias`、`aggregation` (聚合函数如 SUM, AVG) 和 `expression` 的对象。
    *   **`calculated_fields`**: 定义在查询中动态计算的新列，每个字段需要 `alias` (别名) 和 `expression` (SQL表达式)。
    *   **`filters`**: 对应 SQL 的 `WHERE` 子句，包含一系列条件对象。
    *   **`joins`**: 定义 SQL 的 `JOIN` 操作，包括 `type` (连接类型如 INNER, LEFT)、`table` (连接的表) 和 `on` (连接条件)。
    *   **`group_by`**: 对应 SQL 的 `GROUP BY` 子句。
    *   **`having`**: 对应 SQL 的 `HAVING` 子句，用于对分组后的结果进行过滤。
    *   **`order_by`**: 对应 SQL 的 `ORDER BY` 子句，可指定排序字段和方向 (ASC/DESC)。
    *   **`limit`**, **`offset`**: 对应 SQL 的 `LIMIT` 和 `OFFSET` 子句，用于分页和限制结果集大小。

*   **`EnrichStepConfig` (丰富化步骤配置)**:
    *   **`source`**: 必需，要丰富化的源数据来自哪个步骤的输出。
    *   **`lookup`**: 必需，定义查找表的来源。可以是另一个步骤的名称，也可以是包含 `table` (表名)、`columns` (选择列) 和 `where` (过滤条件) 的数据库查询配置。
    *   **`on`**: 必需，定义源数据与查找表之间的连接条件，可以是单列名、多列名数组或自定义的 `left` / `right` 列映射加 `condition`。
    *   **`join_type`**: 连接类型，默认为 "left"。
    *   **`missing_strategy`**: 处理缺失值的策略，如 `keep` (保留)、`drop` (删除) 或 `fill` (填充)，默认为 "keep"。
    *   **`fill_value`**: 当 `missing_strategy` 为 "fill" 时，用于填充的值。

*   **`PivotStepConfig` (透视步骤配置)**:
    *   **`source`**: 必需，要透视的源数据来自哪个步骤的输出。
    *   **`index`**: 必需，用作新数据表索引的列或列列表。
    *   **`columns`**: 必需，其唯一值将成为新数据表中列名的列或列列表。
    *   **`values`**: 必需，用于填充新数据表值区域的列或列列表。
    *   **`agg_func`**: 聚合函数，可以是单个函数名字符串 (如 "sum", "mean")，也可以是映射 `values` 列到不同聚合函数的对象。
    *   **`fill_value`**: 用于填充透视表中缺失值的值，默认为 0。
    *   **`missing_strategy`**, **`missing_fill_value`**: 处理透视前源数据中缺失值的策略。
    *   **`null_strategy`**, **`null_fill_value`**: 处理透视后结果中空值的策略。
    *   **`column_prefix`**, **`column_suffix`**: 用于为新生成的列名添加前缀和后缀。
    *   **`sort_by`**, **`sort_ascending`**: 对透视结果进行排序的配置。

*   **`UnpivotStepConfig` (逆透视步骤配置)**:
    *   **`source`**: 必需，要逆透视的源数据来自哪个步骤的输出。
    *   **`id_vars`**: 必需，作为标识符变量的列或列列表，即不进行逆透视的列。
    *   **`value_vars`**: 必需，要进行逆透视的列或列列表。
    *   **`var_name`**: 新变量列的名称，默认为 "variable"。
    *   **`value_name`**: 新值列的名称，默认为 "value"。

*   **`UnionStepConfig` (合并步骤配置)**:
    *   **`sources`**: 必需，包含至少 2 个元素，列出要合并的源数据集的步骤名称。
    *   **`mode`**: 合并模式，包括 `union` (去重合并)、`union_all` (保留重复合并)、`intersect` (交集) 和 `except` (差集)，默认为 "union"。
    *   **`add_source_column`**: 是否在结果中添加一列来标识每条记录来自哪个源，默认为 `false`。
    *   **`source_column`**: 如果 `add_source_column` 为 `true`，此列的名称，默认为 "_source"。
    *   **`strict_schema`**: 是否严格检查源数据集的列结构兼容性，默认为 `false`。

*   **`AssertStepConfig` (断言步骤配置)**:
    *   **`source`**: 必需，要进行断言检查的源数据来自哪个步骤的输出。
    *   **`assertions`**: 必需，包含一系列断言规则。每个规则都是一个 `AssertionRule` 对象。
    *   **`on_failure`**: 当断言失败时如何处理，包括 `error` (抛出错误)、`warning` (记录警告) 和 `ignore` (忽略失败)，默认为 "error"。

*   **`AssertionRule` (断言规则)**:
    *   **`type`**: 必需，定义了具体要执行的断言类型。支持多种类型，例如：
        *   `row_count`: 检查行数是否符合 `expected`、`min` 或 `max` 值。
        *   `not_null`: 检查指定 `columns` 是否存在空值。
        *   `unique`: 检查指定 `columns` 的值是否唯一。
        *   `range`: 检查指定 `column` 的值是否在 `min` 和 `max` 范围内。
        *   `regex`: 检查指定 `column` 的值是否匹配给定的 `pattern` (正则表达式)。
        *   `custom`: 执行一个自定义的 Python `expression` 来验证数据。
        *   `column_exists`: 检查指定 `columns` 是否存在。
        *   `data_type`: 检查指定 `column` 的数据类型是否符合 `expected_type` (int, float, str, bool, number)。
        *   `value_in`: 检查指定 `column` 的值是否在 `allowed_values` 列表中。
        *   `relationship`: 用于检查字段间的复杂关系，例如日期字段的顺序等，目前代码中实现有限。

*   **`SQLCondition` (SQL条件)**:
    *   定义了 SQL 中 `WHERE` 或 `HAVING` 子句中的单个条件。
    *   **`field`**: 条件的字段名。
    *   **`operator`**: 比较操作符，如 `=`、`>`、`<`、`LIKE`、`IN`、`BETWEEN`、`IS NULL`、`IS NOT NULL` 等。
    *   **`value`**: 比较的值，对于 `IN` 或 `BETWEEN` 操作符，可以是数组。

这个 JSON Schema 详细地揭示了 UQM 后端引擎所期望的输入格式，以及它如何通过组合不同的步骤来执行复杂的数据查询和转换任务。通过遵循这个 Schema，用户可以构建出结构良好、可被 UQM 引擎正确解析和执行的查询定义。