# UQM AI 功能快速开始指南

## 🚀 快速开始

### 1. 环境准备

确保您已安装Python 3.8+和必要的依赖：

```bash
# 安装依赖
pip install -r requirements.txt
```

### 2. 配置AI环境

#### 方法一：使用启动脚本（推荐）

```bash
python start_with_ai.py
```

脚本会引导您完成所有配置步骤。

#### 方法二：手动配置

创建 `.env` 文件并添加以下配置：

```bash
# AI配置
AI_API_BASE=https://openrouter.ai/api/v1
AI_API_KEY=your_openrouter_api_key_here
AI_MODEL=anthropic/claude-3.5-sonnet
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.1
```

### 3. 启动服务

```bash
# 使用启动脚本
python start_with_ai.py

# 或手动启动
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 测试AI功能

```bash
# 运行测试脚本
python test_ai_api.py
```

## 📖 API使用

### 生成UQM Schema

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "查询所有用户的订单总金额"
  }'
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

### 生成并执行查询

```bash
curl -X POST "http://localhost:8000/api/v1/generate-and-execute" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "查询最近7天的订单数量"
  }'
```

## 🔧 配置说明

### AI模型选择

| 模型 | 特点 | 推荐场景 |
|------|------|----------|
| `anthropic/claude-3.5-sonnet` | 高质量，稳定 | 生产环境 |
| `google/gemini-2.5-flash-lite-preview-06-17` | 快速，经济 | 开发测试 |
| `openai/gpt-4o` | 最新，功能强 | 复杂查询 |

### 参数调优

- `AI_TEMPERATURE`: 0.1-0.3 适合结构化查询
- `AI_MAX_TOKENS`: 4000-8000 根据查询复杂度调整

## 🎯 查询示例

### 基础查询
```json
{
  "query": "查询所有用户信息"
}
```

### 聚合查询
```json
{
  "query": "统计每个用户的订单总金额"
}
```

### 条件查询
```json
{
  "query": "查询状态为已完成的订单"
}
```

### 时间查询
```json
{
  "query": "查询最近30天的订单数量"
}
```

## 🐛 故障排除

### 常见问题

1. **API密钥错误**
   ```
   错误: AI_API_KEY环境变量未设置
   解决: 检查.env文件中的AI_API_KEY配置
   ```

2. **连接超时**
   ```
   错误: AI API调用超时
   解决: 检查网络连接，或增加超时时间
   ```

3. **生成失败**
   ```
   错误: AI生成失败
   解决: 尝试更详细的查询描述
   ```

### 调试技巧

1. 查看日志输出
2. 使用测试脚本验证
3. 检查环境变量配置
4. 确认指南文件存在

## 📚 更多信息

- [完整API文档](AI_API_README.md)
- [UQM技术手册](../UQM_JSON_SCHEMA_权威技术参考手册.md)
- [数据库结构](../数据库表结构简化描述.md)

## 🤝 支持

如遇问题，请：

1. 查看日志文件
2. 运行测试脚本
3. 检查配置文档
4. 提交Issue反馈 