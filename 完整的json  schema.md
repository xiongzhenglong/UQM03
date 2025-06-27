# UQM 完整 JSON Schema 参考文档

## 概述

统一查询模型（UQM）是一个数据查询和处理引擎，支持多种数据操作步骤的链式执行。本文档基于源代码分析，提供完整的 JSON Schema 定义和使用说明。

## 1. 根级结构 (Root Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "UQM Configuration Schema",
  "description": "统一查询模型（UQM）配置文件的 JSON Schema 定义",
  "type": "object",
  "required": ["metadata", "steps"],
  "properties": {
    "metadata": {"$ref": "#/definitions/metadata"},
    "steps": {"$ref": "#/definitions/steps"},
    "parameters": {"$ref": "#/definitions/parameters"},
    "output": {"$ref": "#/definitions/output"},
    "options": {"$ref": "#/definitions/options"}
  }
}
```

### 说明
- **metadata**: 查询的元数据信息（必需）
- **steps**: 执行步骤列表（必需）
- **parameters**: 参数定义（可选）
- **output**: 输出配置（可选，默认最后一个步骤）
- **options**: 执行选项（可选）

## 2. 元数据定义 (Metadata)

```json
{
  "definitions": {
    "metadata": {
      "type": "object",
      "required": ["name"],
      "properties": {
        "name": {
          "type": "string",
          "description": "查询名称",
          "minLength": 1,
          "maxLength": 100
        },
        "description": {
          "type": "string",
          "description": "查询描述",
          "maxLength": 500
        },
        "version": {
          "type": "string",
          "description": "版本号",
          "pattern": "^\\d+\\.\\d+(\\.\\d+)?$",
          "default": "1.0"
        },
        "author": {
          "type": "string",
          "description": "作者",
          "maxLength": 100
        },
        "created_at": {
          "type": "string",
          "format": "date-time",
          "description": "创建时间"
        },
        "updated_at": {
          "type": "string",
          "format": "date-time",
          "description": "更新时间"
        },
        "tags": {
          "type": "array",
          "description": "标签列表",
          "items": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
          },
          "uniqueItems": true
        }
      }
    }
  }
}
```

### 示例
```json
{
  "metadata": {
    "name": "用户分析查询",
    "description": "分析用户行为数据的查询流程",
    "version": "1.0.0",
    "author": "数据团队",
    "tags": ["用户分析", "行为数据"]
  }
}
```

## 3. 步骤定义 (Steps)

### 3.1 基础步骤结构

```json
{
  "definitions": {
    "steps": {
      "type": "array",
      "description": "执行步骤列表",
      "minItems": 1,
      "items": {
        "$ref": "#/definitions/step"
      }
    },
    "step": {
      "type": "object",
      "required": ["name", "type", "config"],
      "properties": {
        "name": {
          "type": "string",
          "description": "步骤名称",
          "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$"
        },
        "type": {
          "type": "string",
          "description": "步骤类型",
          "enum": ["query", "enrich", "pivot", "unpivot", "union", "assert"]
        },
        "config": {
          "type": "object",
          "description": "步骤配置"
        },
        "description": {
          "type": "string",
          "description": "步骤描述"
        },
        "enabled": {
          "type": "boolean",
          "description": "是否启用",
          "default": true
        },
        "cache": {
          "type": "object",
          "properties": {
            "enabled": {"type": "boolean", "default": false},
            "ttl": {"type": "integer", "minimum": 0, "default": 3600}
          }
        }
      }
    }
  }
}
```

### 3.2 查询步骤 (Query Step)

```json
{
  "definitions": {
    "query_config": {
      "type": "object",
      "required": ["data_source"],
      "properties": {
        "data_source": {
          "type": "string",
          "description": "数据源名称（表名或前置步骤名）"
        },
        "dimensions": {
          "type": "array",
          "description": "维度字段列表",
          "items": {
            "oneOf": [
              {"type": "string"},
              {
                "type": "object",
                "properties": {
                  "field": {"type": "string"},
                  "alias": {"type": "string"},
                  "expression": {"type": "string"}
                }
              }
            ]
          }
        },
        "metrics": {
          "type": "array",
          "description": "指标字段列表",
          "items": {
            "type": "object",
            "properties": {
              "field": {"type": "string"},
              "aggregation": {
                "type": "string",
                "enum": ["sum", "count", "avg", "min", "max", "count_distinct"]
              },
              "alias": {"type": "string"}
            }
          }
        },
        "filters": {
          "type": "array",
          "description": "过滤条件",
          "items": {
            "type": "object",
            "properties": {
              "field": {"type": "string"},
              "operator": {
                "type": "string",
                "enum": ["=", "!=", ">", ">=", "<", "<=", "in", "not_in", "like", "not_like", "is_null", "is_not_null"]
              },
              "value": {},
              "condition": {
                "type": "string",
                "enum": ["and", "or"],
                "default": "and"
              }
            }
          }
        },
        "joins": {
          "type": "array",
          "description": "连接配置",
          "items": {
            "type": "object",
            "properties": {
              "table": {"type": "string"},
              "type": {
                "type": "string",
                "enum": ["inner", "left", "right", "full"],
                "default": "inner"
              },
              "on": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "left": {"type": "string"},
                    "right": {"type": "string"}
                  }
                }
              }
            }
          }
        },
        "order_by": {
          "type": "array",
          "description": "排序字段",
          "items": {
            "type": "object",
            "properties": {
              "field": {"type": "string"},
              "direction": {
                "type": "string",
                "enum": ["asc", "desc"],
                "default": "asc"
              }
            }
          }
        },
        "limit": {
          "type": "integer",
          "description": "限制返回行数",
          "minimum": 1
        },
        "offset": {
          "type": "integer",
          "description": "偏移量",
          "minimum": 0
        }
      }
    }
  }
}
```

### 查询步骤示例
```json
{
  "name": "user_query",
  "type": "query",
  "description": "查询活跃用户数据",
  "config": {
    "data_source": "users",
    "dimensions": [
      "user_id",
      {"field": "created_at", "alias": "注册日期"},
      {"expression": "YEAR(created_at)", "alias": "注册年份"}
    ],
    "metrics": [
      {"field": "login_count", "aggregation": "sum", "alias": "总登录次数"},
      {"field": "user_id", "aggregation": "count_distinct", "alias": "用户数"}
    ],
    "filters": [
      {"field": "status", "operator": "=", "value": "active"},
      {"field": "created_at", "operator": ">=", "value": "2023-01-01"}
    ],
    "order_by": [
      {"field": "注册日期", "direction": "desc"}
    ],
    "limit": 1000
  }
}
```

### 3.3 数据丰富化步骤 (Enrich Step)

```json
{
  "definitions": {
    "enrich_config": {
      "type": "object",
      "required": ["source", "lookup", "on"],
      "properties": {
        "source": {
          "type": "string",
          "description": "源数据步骤名称"
        },
        "lookup": {
          "oneOf": [
            {
              "type": "string",
              "description": "查找表步骤名称"
            },
            {
              "type": "object",
              "description": "查找表配置",
              "properties": {
                "table": {"type": "string"},
                "columns": {
                  "type": "array",
                  "items": {"type": "string"}
                },
                "where": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "field": {"type": "string"},
                      "operator": {"type": "string"},
                      "value": {}
                    }
                  }
                }
              }
            }
          ]
        },
        "on": {
          "oneOf": [
            {"type": "string"},
            {
              "type": "object",
              "properties": {
                "left": {"type": "string"},
                "right": {"type": "string"}
              }
            },
            {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "left": {"type": "string"},
                  "right": {"type": "string"}
                }
              }
            }
          ]
        },
        "join_type": {
          "type": "string",
          "enum": ["left", "right", "inner", "outer"],
          "default": "left"
        },
        "columns": {
          "type": "array",
          "description": "要添加的列",
          "items": {
            "oneOf": [
              {"type": "string"},
              {
                "type": "object",
                "properties": {
                  "source": {"type": "string"},
                  "alias": {"type": "string"}
                }
              }
            ]
          }
        }
      }
    }
  }
}
```

### 丰富化步骤示例
```json
{
  "name": "enrich_user_info",
  "type": "enrich",
  "description": "丰富用户信息",
  "config": {
    "source": "user_query",
    "lookup": {
      "table": "user_profiles",
      "columns": ["user_id", "department", "location", "manager_id"]
    },
    "on": {"left": "user_id", "right": "user_id"},
    "join_type": "left",
    "columns": [
      "department",
      {"source": "location", "alias": "工作地点"},
      "manager_id"
    ]
  }
}
```

### 3.4 透视表步骤 (Pivot Step)

```json
{
  "definitions": {
    "pivot_config": {
      "type": "object",
      "required": ["source", "index", "columns", "values"],
      "properties": {
        "source": {
          "type": "string",
          "description": "源数据步骤名称"
        },
        "index": {
          "type": "array",
          "description": "行索引字段",
          "items": {"type": "string"},
          "minItems": 1
        },
        "columns": {
          "type": "string",
          "description": "列字段"
        },
        "values": {
          "type": "array",
          "description": "值字段",
          "items": {"type": "string"},
          "minItems": 1
        },
        "aggfunc": {
          "type": "string",
          "description": "聚合函数",
          "enum": ["sum", "count", "avg", "min", "max", "first", "last"],
          "default": "sum"
        },
        "fill_value": {
          "description": "填充值",
          "default": null
        }
      }
    }
  }
}
```

### 透视表步骤示例
```json
{
  "name": "sales_pivot",
  "type": "pivot",
  "description": "创建销售数据透视表",
  "config": {
    "source": "sales_data",
    "index": ["product_category", "sales_rep"],
    "columns": "quarter",
    "values": ["sales_amount"],
    "aggfunc": "sum",
    "fill_value": 0
  }
}
```

### 3.5 反透视步骤 (Unpivot Step)

```json
{
  "definitions": {
    "unpivot_config": {
      "type": "object",
      "required": ["source", "id_vars", "value_vars"],
      "properties": {
        "source": {
          "type": "string",
          "description": "源数据步骤名称"
        },
        "id_vars": {
          "type": "array",
          "description": "标识字段",
          "items": {"type": "string"},
          "minItems": 1
        },
        "value_vars": {
          "type": "array",
          "description": "值字段",
          "items": {"type": "string"},
          "minItems": 1
        },
        "var_name": {
          "type": "string",
          "description": "变量名列名",
          "default": "variable"
        },
        "value_name": {
          "type": "string",
          "description": "值列名",
          "default": "value"
        }
      }
    }
  }
}
```

### 3.6 合并步骤 (Union Step)

```json
{
  "definitions": {
    "union_config": {
      "type": "object",
      "required": ["sources"],
      "properties": {
        "sources": {
          "type": "array",
          "description": "要合并的数据源列表",
          "items": {"type": "string"},
          "minItems": 2
        },
        "union_type": {
          "type": "string",
          "description": "合并类型",
          "enum": ["union", "union_all"],
          "default": "union"
        },
        "ignore_index": {
          "type": "boolean",
          "description": "是否忽略索引",
          "default": true
        },
        "sort": {
          "type": "boolean",
          "description": "是否排序结果",
          "default": false
        }
      }
    }
  }
}
```

### 3.7 断言步骤 (Assert Step)

```json
{
  "definitions": {
    "assert_config": {
      "type": "object",
      "required": ["source", "assertions"],
      "properties": {
        "source": {
          "type": "string",
          "description": "要验证的数据源"
        },
        "assertions": {
          "type": "array",
          "description": "断言列表",
          "items": {
            "type": "object",
            "required": ["name", "condition"],
            "properties": {
              "name": {
                "type": "string",
                "description": "断言名称"
              },
              "condition": {
                "type": "string",
                "description": "断言条件表达式"
              },
              "message": {
                "type": "string",
                "description": "失败消息"
              },
              "severity": {
                "type": "string",
                "enum": ["error", "warning", "info"],
                "default": "error"
              }
            }
          }
        }
      }
    }
  }
}
```

## 4. 参数定义 (Parameters)

```json
{
  "definitions": {
    "parameters": {
      "type": "array",
      "description": "参数定义列表",
      "items": {
        "type": "object",
        "required": ["name", "type"],
        "properties": {
          "name": {
            "type": "string",
            "description": "参数名称"
          },
          "type": {
            "type": "string",
            "description": "参数类型",
            "enum": ["string", "number", "integer", "boolean", "date", "datetime", "array", "object"]
          },
          "default": {
            "description": "默认值"
          },
          "required": {
            "type": "boolean",
            "description": "是否必需",
            "default": true
          },
          "description": {
            "type": "string",
            "description": "参数描述"
          },
          "validation": {
            "type": "object",
            "description": "验证规则",
            "properties": {
              "min": {"type": "number"},
              "max": {"type": "number"},
              "pattern": {"type": "string"},
              "enum": {"type": "array"},
              "format": {"type": "string"}
            }
          }
        }
      }
    }
  }
}
```

### 参数示例
```json
{
  "parameters": [
    {
      "name": "start_date",
      "type": "date",
      "required": true,
      "description": "开始日期",
      "validation": {
        "format": "YYYY-MM-DD"
      }
    },
    {
      "name": "limit",
      "type": "integer",
      "default": 100,
      "required": false,
      "description": "返回记录数限制",
      "validation": {
        "min": 1,
        "max": 10000
      }
    }
  ]
}
```

## 5. 输出配置 (Output)

```json
{
  "definitions": {
    "output": {
      "type": "string",
      "description": "输出步骤名称，默认为最后一个步骤"
    }
  }
}
```

## 6. 执行选项 (Options)

```json
{
  "definitions": {
    "options": {
      "type": "object",
      "properties": {
        "cache_enabled": {
          "type": "boolean",
          "description": "是否启用缓存",
          "default": true
        },
        "timeout": {
          "type": "integer",
          "description": "超时时间（秒）",
          "minimum": 1,
          "default": 300
        },
        "parallel": {
          "type": "boolean",
          "description": "是否并行执行",
          "default": false
        },
        "validate_data": {
          "type": "boolean",
          "description": "是否验证数据",
          "default": true
        },
        "fail_fast": {
          "type": "boolean",
          "description": "遇到错误时立即停止",
          "default": true
        }
      }
    }
  }
}
```

## 7. 完整示例

```json
{
  "metadata": {
    "name": "用户行为分析",
    "description": "分析用户登录行为和购买模式",
    "version": "1.2.0",
    "author": "数据分析团队",
    "tags": ["用户分析", "行为数据", "购买分析"]
  },
  "parameters": [
    {
      "name": "analysis_date",
      "type": "date",
      "required": true,
      "description": "分析日期"
    },
    {
      "name": "user_segment",
      "type": "string",
      "default": "all",
      "required": false,
      "description": "用户分群",
      "validation": {
        "enum": ["all", "premium", "regular", "new"]
      }
    }
  ],
  "steps": [
    {
      "name": "extract_users",
      "type": "query",
      "description": "提取用户基础数据",
      "config": {
        "data_source": "users",
        "dimensions": ["user_id", "email", "created_at", "status"],
        "filters": [
          {"field": "status", "operator": "=", "value": "active"},
          {"field": "created_at", "operator": "<=", "value": "{{analysis_date}}"}
        ]
      }
    },
    {
      "name": "extract_login_data",
      "type": "query",
      "description": "提取登录数据",
      "config": {
        "data_source": "user_logins",
        "dimensions": ["user_id", "login_date"],
        "metrics": [
          {"field": "session_id", "aggregation": "count", "alias": "login_count"}
        ],
        "filters": [
          {"field": "login_date", "operator": "=", "value": "{{analysis_date}}"}
        ]
      }
    },
    {
      "name": "enrich_user_logins",
      "type": "enrich",
      "description": "丰富用户登录数据",
      "config": {
        "source": "extract_users",
        "lookup": "extract_login_data",
        "on": {"left": "user_id", "right": "user_id"},
        "join_type": "left",
        "columns": ["login_count"]
      }
    },
    {
      "name": "extract_purchase_data",
      "type": "query",
      "description": "提取购买数据",
      "config": {
        "data_source": "orders",
        "dimensions": ["user_id"],
        "metrics": [
          {"field": "order_amount", "aggregation": "sum", "alias": "total_spent"},
          {"field": "order_id", "aggregation": "count", "alias": "order_count"}
        ],
        "filters": [
          {"field": "order_date", "operator": "=", "value": "{{analysis_date}}"},
          {"field": "status", "operator": "=", "value": "completed"}
        ]
      }
    },
    {
      "name": "final_user_analysis",
      "type": "enrich",
      "description": "合并所有用户数据",
      "config": {
        "source": "enrich_user_logins",
        "lookup": "extract_purchase_data",
        "on": {"left": "user_id", "right": "user_id"},
        "join_type": "left",
        "columns": ["total_spent", "order_count"]
      }
    },
    {
      "name": "validate_results",
      "type": "assert",
      "description": "验证结果数据质量",
      "config": {
        "source": "final_user_analysis",
        "assertions": [
          {
            "name": "check_user_count",
            "condition": "COUNT(*) > 0",
            "message": "结果集不能为空"
          },
          {
            "name": "check_data_consistency",
            "condition": "SUM(CASE WHEN login_count IS NULL THEN 1 ELSE 0 END) / COUNT(*) < 0.1",
            "message": "登录数据缺失率不应超过10%",
            "severity": "warning"
          }
        ]
      }
    }
  ],
  "output": "final_user_analysis",
  "options": {
    "cache_enabled": true,
    "timeout": 600,
    "validate_data": true,
    "fail_fast": false
  }
}
```

## 8. API 响应格式

### 8.1 成功响应
```json
{
  "success": true,
  "data": [
    {"user_id": 1, "email": "user1@example.com", "login_count": 3, "total_spent": 150.00},
    {"user_id": 2, "email": "user2@example.com", "login_count": 1, "total_spent": 75.50}
  ],
  "metadata": {
    "name": "用户行为分析",
    "description": "分析用户登录行为和购买模式"
  },
  "execution_info": {
    "total_time": 2.34,
    "row_count": 1250,
    "cache_hit": false,
    "parameters_used": {
      "analysis_date": "2023-12-01",
      "user_segment": "all"
    }
  },
  "step_results": [
    {
      "step_name": "extract_users",
      "step_type": "query",
      "status": "completed",
      "row_count": 1500,
      "execution_time": 0.45,
      "cache_hit": false
    }
  ]
}
```

### 8.2 错误响应
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "步骤配置验证失败",
    "details": {
      "step_name": "extract_users",
      "field": "data_source",
      "message": "data_source字段不能为空"
    }
  }
}
```

## 9. 最佳实践

### 9.1 步骤命名
- 使用描述性名称，如 `extract_user_data`、`calculate_metrics`
- 使用小写字母和下划线
- 保持名称简洁但能表达步骤功能

### 9.2 参数使用
- 使用双花括号包围参数名：`{{parameter_name}}`
- 为所有参数提供默认值（可选参数）
- 添加详细的参数描述和验证规则

### 9.3 性能优化
- 合理使用缓存配置
- 避免在循环中使用重量级步骤
- 考虑步骤执行顺序和依赖关系

### 9.4 错误处理
- 使用断言步骤验证关键数据质量
- 设置合理的超时时间
- 提供清晰的错误消息

这个 JSON Schema 基于实际的源代码分析，涵盖了 UQM 系统的所有核心功能，可以作为开发和使用 UQM 查询的权威参考。