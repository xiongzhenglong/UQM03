# UQM 开发者指南与API参考

## 📖 文档简介

本指南面向需要集成UQM（统一查询模型）的后端和前端开发者，详细介绍如何调用UQM API以及构建有效的UQM JSON查询载荷来获取应用程序所需的数据。

UQM是一个高性能、可扩展的统一查询模型执行引擎，支持多步骤数据处理管道，包括查询、数据丰富、透视、合并、断言等操作。

> 💡 **相关文档**: 如需了解UQM的设计理念和架构概览，请参考《UQM架构蓝图》文档。

## 🚀 API端点规范

### 主要端点

UQM后端提供以下主要API端点：

#### 1. 执行UQM查询
```http
POST /api/v1/execute
Content-Type: application/json
```

**请求体结构：**
```json
{
  "uqm": {
    // UQM配置JSON对象
  },
  "parameters": {
    // 动态参数键值对
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "user_id": 12345
  },
  "options": {
    "timeout": 30,        // 超时时间（秒）
    "cache_enabled": true, // 是否启用缓存
    "parallel": false     // 是否并行执行
  }
}
```

**成功响应（200）：**
```json
{
  "success": true,
  "data": [
    {
      "column1": "value1",
      "column2": 100,
      "column3": "2024-01-01"
    }
  ],
  "metadata": {
    "execution_time": 1.23,
    "row_count": 1000,
    "columns": ["column1", "column2", "column3"],
    "cache_hit": false,
    "query_id": "uuid-123-456"
  },
  "pagination": {
    "total": 1000,
    "page": 1,
    "page_size": 100,
    "has_next": true
  }
}
```

#### 2. 验证UQM配置
```http
POST /api/v1/validate
Content-Type: application/json
```

#### 3. 异步执行查询
```http
POST /api/v1/execute/async
Content-Type: application/json
```

#### 4. 查询任务状态
```http
GET /api/v1/jobs/{job_id}
```

### 常见错误响应

| 状态码 | 描述 | 示例响应 |
|--------|------|----------|
| 400 | 请求参数错误 | `{"success": false, "error": "Invalid UQM configuration", "details": "Missing required field: metadata.name"}` |
| 404 | 资源未找到 | `{"success": false, "error": "Data source not found", "details": "Table 'users' does not exist"}` |
| 422 | 数据验证错误 | `{"success": false, "error": "Validation error", "details": "Parameter 'start_date' must be in YYYY-MM-DD format"}` |
| 500 | 服务器内部错误 | `{"success": false, "error": "Execution failed", "details": "Database connection timeout"}` |
| 504 | 执行超时 | `{"success": false, "error": "Query timeout", "details": "Execution exceeded 30 seconds limit"}` |

## 🔧 UQM Schema深度解析：查询规则详解

### 顶层结构

每个UQM配置包含以下核心部分：

```json
{
  "metadata": {
    // 查询元数据信息
  },
  "parameters": [
    // 参数定义数组
  ],
  "steps": [
    // 执行步骤管道
  ],
  "output": {
    // 输出配置（可选）
  }
}
```

#### metadata - 元数据
```json
{
  "metadata": {
    "name": "用户行为分析",           // 必需：查询名称
    "description": "分析用户购买行为", // 可选：描述
    "version": "1.0.0",            // 可选：版本号
    "author": "数据团队",           // 可选：作者
    "tags": ["用户分析", "电商"]    // 可选：标签数组
  }
}
```

#### parameters - 参数定义
```json
{
  "parameters": [
    {
      "name": "start_date",
      "type": "date",
      "default": "2024-01-01",
      "required": true,
      "description": "开始日期"
    },
    {
      "name": "category_id",
      "type": "integer",
      "required": false,
      "description": "商品分类ID"
    }
  ]
}
```

### steps管道：多步骤处理

UQM的核心是steps管道，支持链式数据处理。每个步骤的基础结构：

```json
{
  "name": "step_name",        // 步骤标识符
  "type": "query|enrich|pivot|unpivot|union|assert",
  "config": {
    // 步骤特定配置
  },
  "description": "步骤描述",   // 可选
  "enabled": true,           // 可选：是否启用
  "cache": {                 // 可选：缓存配置
    "enabled": true,
    "ttl": 3600
  }
}
```

#### 1. query步骤 - 数据查询

用于从数据源查询数据，支持复杂的SQL操作。

```json
{
  "name": "base_query",
  "type": "query",
  "config": {
    "data_source": "orders",     // 数据源：表名或前置步骤名
    "dimensions": [              // 维度字段
      "user_id",
      "category_name",
      {
        "field": "order_date",
        "alias": "date",
        "expression": "DATE(order_date)"
      }
    ],
    "metrics": [                 // 指标字段
      {
        "field": "amount",
        "aggregation": "sum",
        "alias": "total_amount"
      },
      {
        "field": "order_id",
        "aggregation": "count",
        "alias": "order_count"
      }
    ],
    "joins": [                   // 连接配置
      {
        "type": "left",
        "table": "users",
        "on": {
          "and": [               // 多条件连接
            {"left": "user_id", "right": "id"},
            {"left": "status", "right": "active"}
          ]
        }
      }
    ],
    "filter": {                  // 过滤条件（聚合前）
      "and": [
        {
          "field": "order_date",
          "operator": ">=",
          "value": "${start_date}"
        },
        {
          "or": [
            {"field": "status", "operator": "=", "value": "completed"},
            {"field": "status", "operator": "=", "value": "shipped"}
          ]
        }
      ]
    },
    "having": {                  // Having条件（聚合后）
      "field": "total_amount",
      "operator": ">",
      "value": 1000
    },
    "window_functions": [        // 窗口函数
      {
        "function": "ROW_NUMBER",
        "alias": "rank",
        "partition_by": ["category_name"],
        "order_by": [
          {"field": "total_amount", "direction": "desc"}
        ],
        "frame": {
          "type": "rows",
          "start": "unbounded_preceding",
          "end": "current_row"
        }
      }
    ],
    "order_by": [
      {"field": "total_amount", "direction": "desc"}
    ],
    "limit": 100
  }
}
```

#### 2. enrich步骤 - 数据丰富

用于为现有数据添加额外信息。

```json
{
  "name": "enrich_user_info",
  "type": "enrich",
  "config": {
    "source": "base_query",      // 源数据步骤
    "enrich_source": "user_profiles",
    "join_keys": {
      "left": "user_id",
      "right": "user_id"
    },
    "fields": [                  // 要添加的字段
      "user_name",
      "user_segment",
      "registration_date"
    ]
  }
}
```

#### 3. pivot步骤 - 数据透视

将行数据转换为列数据。

```json
{
  "name": "sales_pivot",
  "type": "pivot",
  "config": {
    "source": "base_query",
    "group_by": ["user_id", "user_name"],
    "pivot_column": "category_name",
    "value_column": "total_amount",
    "aggregation": "sum",
    "column_prefix": "category_"  // 新列前缀
  }
}
```

#### 4. unpivot步骤 - 反透视

将列数据转换为行数据。

```json
{
  "name": "unpivot_categories",
  "type": "unpivot",
  "config": {
    "source": "sales_pivot",
    "id_columns": ["user_id", "user_name"],
    "value_columns": ["category_electronics", "category_clothing"],
    "variable_name": "category",
    "value_name": "amount"
  }
}
```

#### 5. union步骤 - 数据合并

合并多个数据集。

```json
{
  "name": "union_all_sales",
  "type": "union",
  "config": {
    "sources": ["q1_sales", "q2_sales", "q3_sales", "q4_sales"],
    "union_type": "all"          // all | distinct
  }
}
```

#### 6. assert步骤 - 数据断言

验证数据质量和业务规则。

```json
{
  "name": "data_quality_check",
  "type": "assert",
  "config": {
    "source": "final_result",
    "assertions": [
      {
        "name": "min_records",
        "expression": "row_count >= 100",
        "message": "结果集记录数不足100条"
      },
      {
        "name": "amount_positive",
        "expression": "min(total_amount) > 0",
        "message": "存在负数金额"
      }
    ]
  }
}
```

### 高级特性

#### 1. 复杂过滤条件

支持嵌套的AND/OR逻辑：

```json
{
  "filter": {
    "and": [
      {
        "field": "order_date",
        "operator": "between",
        "value": ["2024-01-01", "2024-12-31"]
      },
      {
        "or": [
          {
            "and": [
              {"field": "category", "operator": "=", "value": "electronics"},
              {"field": "amount", "operator": ">", "value": 500}
            ]
          },
          {
            "field": "vip_level", "operator": "in", "value": ["gold", "platinum"]
          }
        ]
      }
    ]
  }
}
```

#### 2. 多条件连接

支持复杂的表连接条件：

```json
{
  "joins": [
    {
      "type": "inner",
      "table": "order_details",
      "on": {
        "and": [
          {"left": "order_id", "right": "order_id"},
          {"left": "tenant_id", "right": "tenant_id"},
          {
            "expression": "orders.order_date = order_details.created_date::date"
          }
        ]
      }
    }
  ]
}
```

#### 3. 窗口函数详解

```json
{
  "window_functions": [
    {
      "function": "RANK",           // 窗口函数名
      "alias": "sales_rank",        // 结果列别名
      "partition_by": ["region", "category"],  // 分区字段
      "order_by": [                 // 排序字段
        {"field": "total_sales", "direction": "desc"},
        {"field": "order_count", "direction": "asc"}
      ],
      "frame": {                    // 窗口框架（可选）
        "type": "rows",             // rows | range
        "start": "2_preceding",     // 开始位置
        "end": "1_following"        // 结束位置
      }
    }
  ]
}
```

## 📚 实用查询模式：常见场景示例

### 示例1：动态过滤的销售数据聚合

这是一个典型的BI图表查询，支持动态日期范围过滤。

```json
{
  "metadata": {
    "name": "销售趋势分析",
    "description": "按日期聚合销售数据，支持动态日期范围"
  },
  "parameters": [
    {
      "name": "start_date",
      "type": "date",
      "required": true,
      "description": "开始日期"
    },
    {
      "name": "end_date", 
      "type": "date",
      "required": true,
      "description": "结束日期"
    },
    {
      "name": "category_filter",
      "type": "string",
      "required": false,
      "description": "商品分类过滤"
    }
  ],
  "steps": [
    {
      "name": "daily_sales",
      "type": "query",
      "config": {
        "data_source": "orders",
        "dimensions": [
          {
            "field": "order_date",
            "alias": "date",
            "expression": "DATE(order_date)"
          },
          "category_name"
        ],
        "metrics": [
          {
            "field": "amount",
            "aggregation": "sum",
            "alias": "total_sales"
          },
          {
            "field": "order_id",
            "aggregation": "count",
            "alias": "order_count"
          },
          {
            "field": "amount",
            "aggregation": "avg",
            "alias": "avg_order_value"
          }
        ],
        "filter": {
          "and": [
            {
              "field": "order_date",
              "operator": ">=",
              "value": "${start_date}"
            },
            {
              "field": "order_date",
              "operator": "<=",
              "value": "${end_date}"
            },
            {
              "field": "status",
              "operator": "=",
              "value": "completed"
            }
          ]
        },
        "order_by": [
          {"field": "date", "direction": "asc"}
        ]
      }
    }
  ]
}
```

### 示例2：多步骤数据丰富分析

先聚合事实表数据，然后通过enrich步骤添加维度属性。

```json
{
  "metadata": {
    "name": "用户购买行为分析",
    "description": "分析用户购买行为并丰富用户画像信息"
  },
  "parameters": [
    {
      "name": "analysis_period",
      "type": "integer",
      "default": 30,
      "description": "分析周期（天）"
    }
  ],
  "steps": [
    {
      "name": "user_purchase_summary",
      "type": "query",
      "config": {
        "data_source": "orders",
        "dimensions": ["user_id"],
        "metrics": [
          {
            "field": "amount",
            "aggregation": "sum",
            "alias": "total_spent"
          },
          {
            "field": "order_id",
            "aggregation": "count",
            "alias": "order_frequency"
          },
          {
            "field": "amount",
            "aggregation": "avg",
            "alias": "avg_order_value"
          },
          {
            "field": "order_date",
            "aggregation": "max",
            "alias": "last_order_date"
          }
        ],
        "filter": {
          "and": [
            {
              "field": "order_date",
              "operator": ">=",
              "value": "CURRENT_DATE - INTERVAL '${analysis_period}' DAY"
            },
            {
              "field": "status",
              "operator": "in",
              "value": ["completed", "shipped"]
            }
          ]
        },
        "having": {
          "field": "total_spent",
          "operator": ">",
          "value": 0
        }
      }
    },
    {
      "name": "enrich_user_profile",
      "type": "enrich",
      "config": {
        "source": "user_purchase_summary",
        "enrich_source": "user_profiles",
        "join_keys": {
          "left": "user_id",
          "right": "user_id"
        },
        "fields": [
          "user_name",
          "email",
          "registration_date",
          "user_segment",
          "city",
          "age_group"
        ]
      }
    },
    {
      "name": "calculate_metrics",
      "type": "query",
      "config": {
        "data_source": "enrich_user_profile",
        "dimensions": [
          "user_id",
          "user_name", 
          "user_segment",
          "city",
          "age_group"
        ],
        "metrics": [
          {
            "field": "total_spent",
            "aggregation": "sum",
            "alias": "total_spent"
          },
          {
            "field": "order_frequency", 
            "aggregation": "sum",
            "alias": "order_frequency"
          }
        ],
        "calculated_fields": [
          {
            "name": "customer_value_score",
            "expression": "total_spent * 0.6 + order_frequency * 0.4",
            "alias": "clv_score"
          },
          {
            "name": "days_since_last_order",
            "expression": "CURRENT_DATE - last_order_date",
            "alias": "recency"
          }
        ],
        "order_by": [
          {"field": "clv_score", "direction": "desc"}
        ]
      }
    }
  ]
}
```

### 示例3：窗口函数排名分析

使用窗口函数找出每个分类的前3名商品。

```json
{
  "metadata": {
    "name": "分类TOP商品排名",
    "description": "使用窗口函数计算每个分类的销量排名"
  },
  "parameters": [
    {
      "name": "top_n",
      "type": "integer", 
      "default": 3,
      "description": "每个分类显示的TOP商品数量"
    }
  ],
  "steps": [
    {
      "name": "product_sales_ranking",
      "type": "query",
      "config": {
        "data_source": "order_items",
        "joins": [
          {
            "type": "inner",
            "table": "products",
            "on": {"left": "product_id", "right": "id"}
          },
          {
            "type": "inner", 
            "table": "categories",
            "on": {"left": "products.category_id", "right": "categories.id"}
          }
        ],
        "dimensions": [
          "categories.name as category_name",
          "products.name as product_name",
          "products.id as product_id"
        ],
        "metrics": [
          {
            "field": "quantity",
            "aggregation": "sum",
            "alias": "total_quantity"
          },
          {
            "field": "price * quantity",
            "aggregation": "sum", 
            "alias": "total_revenue"
          }
        ],
        "window_functions": [
          {
            "function": "ROW_NUMBER",
            "alias": "sales_rank",
            "partition_by": ["category_name"],
            "order_by": [
              {"field": "total_quantity", "direction": "desc"},
              {"field": "total_revenue", "direction": "desc"}
            ]
          },
          {
            "function": "PERCENTILE_CONT",
            "arguments": [0.5],
            "alias": "median_quantity",
            "partition_by": ["category_name"],
            "order_by": [{"field": "total_quantity", "direction": "asc"}]
          }
        ],
        "filter": {
          "field": "order_date",
          "operator": ">=",
          "value": "CURRENT_DATE - INTERVAL '90' DAY"
        }
      }
    },
    {
      "name": "filter_top_products",
      "type": "query",
      "config": {
        "data_source": "product_sales_ranking",
        "dimensions": [
          "category_name",
          "product_name", 
          "sales_rank",
          "total_quantity",
          "total_revenue",
          "median_quantity"
        ],
        "filter": {
          "field": "sales_rank",
          "operator": "<=",
          "value": "${top_n}"
        },
        "order_by": [
          {"field": "category_name", "direction": "asc"},
          {"field": "sales_rank", "direction": "asc"}
        ]
      }
    }
  ]
}
```

### 示例4：数据透视分析

将用户-分类的销售数据进行透视，便于横向对比。

```json
{
  "metadata": {
    "name": "用户分类销售透视分析",
    "description": "将用户在各分类的消费数据进行透视展示"
  },
  "steps": [
    {
      "name": "user_category_sales",
      "type": "query", 
      "config": {
        "data_source": "orders",
        "joins": [
          {
            "type": "inner",
            "table": "order_items", 
            "on": {"left": "id", "right": "order_id"}
          },
          {
            "type": "inner",
            "table": "products",
            "on": {"left": "order_items.product_id", "right": "products.id"}
          }
        ],
        "dimensions": [
          "user_id",
          "products.category_name"
        ],
        "metrics": [
          {
            "field": "order_items.price * order_items.quantity",
            "aggregation": "sum",
            "alias": "category_spending"
          }
        ],
        "filter": {
          "field": "order_date",
          "operator": ">=", 
          "value": "2024-01-01"
        }
      }
    },
    {
      "name": "pivot_user_spending",
      "type": "pivot",
      "config": {
        "source": "user_category_sales",
        "group_by": ["user_id"],
        "pivot_column": "category_name",
        "value_column": "category_spending", 
        "aggregation": "sum",
        "column_prefix": "spending_",
        "fill_value": 0
      }
    },
    {
      "name": "enrich_user_totals",
      "type": "query",
      "config": {
        "data_source": "pivot_user_spending",
        "dimensions": ["user_id"],
        "calculated_fields": [
          {
            "name": "total_spending",
            "expression": "COALESCE(spending_electronics, 0) + COALESCE(spending_clothing, 0) + COALESCE(spending_books, 0)",
            "alias": "total_spending"
          },
          {
            "name": "primary_category", 
            "expression": "CASE WHEN spending_electronics >= spending_clothing AND spending_electronics >= spending_books THEN 'electronics' WHEN spending_clothing >= spending_books THEN 'clothing' ELSE 'books' END",
            "alias": "primary_category"
          }
        ],
        "filter": {
          "field": "total_spending",
          "operator": ">",
          "value": 100
        },
        "order_by": [
          {"field": "total_spending", "direction": "desc"}
        ]
      }
    }
  ]
}
```

## 🛠️ 最佳实践与错误处理

### 开发最佳实践

#### 1. 参数化查询
**✅ 推荐做法：**
```json
{
  "filter": {
    "field": "order_date",
    "operator": ">=", 
    "value": "${start_date}"
  }
}
```

**❌ 避免做法：**
```json
{
  "filter": {
    "field": "order_date",
    "operator": ">=",
    "value": "2024-01-01"  // 硬编码日期
  }
}
```

#### 2. 模块化步骤设计
将复杂逻辑拆分为多个简单步骤，便于调试和维护：
```json
{
  "steps": [
    {"name": "base_data", "type": "query", ...},
    {"name": "enriched_data", "type": "enrich", ...},
    {"name": "calculated_metrics", "type": "query", ...},
    {"name": "final_ranking", "type": "query", ...}
  ]
}
```

#### 3. 缓存策略
为耗时步骤启用缓存：
```json
{
  "name": "expensive_aggregation",
  "type": "query",
  "cache": {
    "enabled": true,
    "ttl": 3600  // 1小时
  },
  "config": {...}
}
```

#### 4. 数据质量检查
使用assert步骤验证关键业务规则：
```json
{
  "name": "quality_check",
  "type": "assert", 
  "config": {
    "assertions": [
      {
        "name": "data_freshness",
        "expression": "max(order_date) >= CURRENT_DATE - INTERVAL '1' DAY",
        "message": "数据更新不及时，最新数据已超过1天"
      }
    ]
  }
}
```

#### 5. 性能优化建议

- **合理使用索引**：确保过滤字段和连接字段有适当索引
- **限制结果集大小**：使用`limit`和分页避免大结果集
- **并行执行**：独立步骤可设置`"parallel": true`
- **选择性投影**：只查询需要的字段，避免`SELECT *`
- **适当使用窗口函数**：比子查询更高效

### 错误处理与调试

#### API错误响应格式
```json
{
  "success": false,
  "error": "错误类型",
  "details": "详细错误信息",
  "error_code": "UQM_001",
  "request_id": "req_123456",
  "timestamp": "2024-07-01T10:30:00Z",
  "context": {
    "step_name": "base_query",
    "line": 15,
    "field": "data_source"
  }
}
```

#### 常见错误类型

| 错误码 | 错误类型 | 描述 | 解决方案 |
|--------|----------|------|----------|
| UQM_001 | 配置验证错误 | JSON Schema验证失败 | 检查配置格式是否符合Schema |
| UQM_002 | 参数缺失 | 必需参数未提供 | 补充missing的参数 |
| UQM_003 | 数据源不存在 | 表或步骤引用错误 | 检查data_source名称 |
| UQM_004 | SQL执行错误 | 数据库查询失败 | 检查SQL语法和权限 |
| UQM_005 | 连接超时 | 数据库连接超时 | 检查网络和数据库状态 |
| UQM_006 | 内存不足 | 结果集过大导致OOM | 增加limit或优化查询 |
| UQM_007 | 断言失败 | 数据质量检查未通过 | 检查数据质量或调整断言条件 |

#### 调试技巧

1. **启用调试模式**：
```json
{
  "options": {
    "debug": true,
    "explain_plan": true
  }
}
```

2. **分步执行**：
```json
{
  "output": {
    "step": "intermediate_step"  // 输出中间步骤结果
  }
}
```

3. **查看执行计划**：
```json
{
  "options": {
    "dry_run": true  // 只生成SQL不执行
  }
}
```

### 监控与性能分析

#### 关键指标监控
- 查询执行时间
- 内存使用量
- 缓存命中率
- 并发连接数
- 错误率统计

#### 性能分析工具
```http
GET /api/v1/metrics
```

返回详细的性能指标，包括：
```json
{
  "performance": {
    "avg_response_time": 1.23,
    "p95_response_time": 3.45,
    "queries_per_second": 125.6,
    "cache_hit_rate": 0.78
  },
  "resources": {
    "memory_usage": "512MB",
    "cpu_usage": "25%",
    "active_connections": 15
  }
}
```

## 🎯 总结

UQM提供了强大而灵活的数据查询和处理能力，通过合理使用其多步骤管道架构，可以构建复杂的数据分析流程。记住以下关键点：

1. **善用参数化**：提高查询的复用性和安全性
2. **模块化设计**：将复杂逻辑拆分为简单步骤
3. **性能优化**：合理使用缓存、索引和限制
4. **质量保证**：使用断言步骤验证数据质量
5. **错误处理**：充分利用调试信息快速定位问题

通过遵循这些最佳实践，您可以高效地利用UQM构建可靠的数据应用程序。

---

📞 **技术支持**：如有疑问，请联系开发团队或查阅详细的API文档。
