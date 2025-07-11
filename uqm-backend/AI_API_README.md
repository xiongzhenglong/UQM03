# UQM AI 生成接口使用指南

## 概述

UQM后端新增了基于AI的自然语言到JSON Schema转换功能，支持通过自然语言描述生成UQM查询配置。

## 环境配置

在启动服务前，需要在环境变量中配置AI相关参数：

```bash
# AI配置
AI_API_BASE=https://openrouter.ai/api/v1
AI_API_KEY=your_openrouter_api_key_here
AI_MODEL=anthropic/claude-3.5-sonnet
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.1
```

### 支持的AI模型

- `anthropic/claude-3.5-sonnet` (推荐)
- `google/gemini-2.5-flash-lite-preview-06-17`
- `openai/gpt-4o`
- 其他OpenRouter支持的模型

## API接口

### 1. 生成UQM Schema

**端点**: `POST /api/v1/generate`

**功能**: 根据自然语言描述生成UQM JSON Schema

**请求示例**:
```json
{
  "query": "查询所有用户的订单总金额，按用户分组",
  "options": {
    "include_parameters": true,
    "include_options": true
  }
}
```

**响应示例**:
```json
{
    "uqm": {
        "metadata": {
            "name": "用户订单总金额查询",
            "description": "查询所有用户的订单总金额，按用户分组"
        },
        "steps": [
            {
                "name": "user_orders",
                "type": "query",
                "config": {
                    "data_source": "orders",
                    "dimensions": ["user_id"],
                    "calculated_fields": [
                        {
                            "name": "total_amount",
                            "expression": "SUM(amount)"
                        }
                    ],
                    "group_by": ["user_id"]
                }
            }
        ],
        "output": "user_orders"
    },
    "parameters": {},
    "options": {
        "cache_enabled": true
    }
}
```

### 2. 生成并执行UQM查询

**端点**: `POST /api/v1/generate-and-execute`

**功能**: 根据自然语言描述生成UQM Schema并立即执行

**请求示例**:
```json
{
  "query": "查询最近7天的订单数量"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-01-01",
      "order_count": 25
    },
    {
      "date": "2024-01-02", 
      "order_count": 30
    }
  ],
  "metadata": {
    "name": "最近7天订单数量查询",
    "description": "查询最近7天的订单数量"
  },
  "execution_info": {
    "total_time": 3.2,
    "row_count": 7,
    "cache_hit": false
  }
}
```

## 使用示例

### Python客户端示例

```python
import requests
import json

# 配置
API_BASE = "http://localhost:8000/api/v1"

# 生成Schema
def generate_schema(query):
    response = requests.post(
        f"{API_BASE}/generate",
        json={"query": query}
    )
    if response.status_code == 200:
        return response.json()  # 直接返回schema
    else:
        raise Exception(f"生成失败: {response.text}")

# 生成并执行
def generate_and_execute(query):
    response = requests.post(
        f"{API_BASE}/generate-and-execute",
        json={"query": query}
    )
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 生成Schema
    schema_result = generate_schema("查询所有用户的订单总金额")
    print("生成的Schema:", json.dumps(schema_result, indent=2, ensure_ascii=False))
    
    # 生成并执行
    result = generate_and_execute("查询最近7天的订单数量")
    print("执行结果:", json.dumps(result, indent=2, ensure_ascii=False))
```

### JavaScript/TypeScript客户端示例

```typescript
// 配置
const API_BASE = "http://localhost:8000/api/v1";

// 生成Schema
async function generateSchema(query: string) {
    const response = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query })
    });
    if (response.ok) {
        return response.json();  // 直接返回schema
    } else {
        throw new Error(`生成失败: ${response.statusText}`);
    }
}

// 生成并执行
async function generateAndExecute(query: string) {
    const response = await fetch(`${API_BASE}/generate-and-execute`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query })
    });
    return response.json();
}

// 使用示例
async function main() {
    // 生成Schema
    const schemaResult = await generateSchema("查询所有用户的订单总金额");
    console.log("生成的Schema:", schemaResult);
    
    // 生成并执行
    const result = await generateAndExecute("查询最近7天的订单数量");
    console.log("执行结果:", result);
}
```

## 查询示例

以下是一些自然语言查询的示例：

### 基础查询
- "查询所有用户信息"
- "获取订单表中的所有数据"
- "查询产品库存大于10的产品"

### 聚合查询
- "统计每个用户的订单总金额"
- "计算每个产品类别的平均价格"
- "查询每个月的订单数量"

### 条件查询
- "查询状态为已完成的订单"
- "获取最近30天创建的订单"
- "查询金额大于1000的订单"

### 关联查询
- "查询用户及其订单信息"
- "获取产品及其库存信息"
- "查询订单及其用户详情"

## 注意事项

1. **API密钥**: 确保正确配置OpenRouter API密钥
2. **查询描述**: 尽量详细和准确地描述查询需求
3. **数据库结构**: AI会根据配置的数据库结构生成查询
4. **错误处理**: 如果生成失败，检查查询描述或重试
5. **性能**: 生成过程可能需要几秒钟时间

## 故障排除

### 常见错误

1. **AI_API_KEY未设置**
   ```
   错误: AI_API_KEY环境变量未设置
   解决: 在环境变量中设置有效的OpenRouter API密钥
   ```

2. **AI生成失败**
   ```
   错误: AI生成失败，请检查查询描述或重试
   解决: 尝试更详细地描述查询需求
   ```

3. **Schema结构无效**
   ```
   错误: 生成的Schema结构无效
   解决: 检查数据库结构配置是否正确
   ```

### 调试建议

1. 检查日志输出，查看详细的错误信息
2. 确认数据库结构文档是否正确加载
3. 验证AI API密钥是否有效
4. 尝试使用更简单的查询描述