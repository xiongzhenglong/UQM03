# UQM JSON Schema Generator

这是一个基于 OpenRouter API 的 UQM JSON Schema 生成器，能够自动读取查询用例，生成 UQM JSON 配置，并调用 UQM API 执行查询。

## 功能特性

- 🤖 **AI 驱动**: 使用 OpenRouter API (Claude-3.5-Sonnet) 智能生成 UQM JSON Schema
- 📊 **批量处理**: 自动处理 `查询用例.md` 中的所有查询案例
- 🔗 **API 集成**: 自动调用 UQM 执行 API 获取查询结果
- 💾 **结果保存**: 每个查询的问题、生成的 Schema 和执行结果保存为独立 JSON 文件
- 🛠️ **灵活配置**: 支持单个查询、范围查询和全量处理

## 目录结构

```
UQM03/
├── uqm_schema_generator.py    # 主程序
├── setup.py                   # 环境检查和设置
├── run_generator.bat          # Windows 批处理脚本
├── run_generator.ps1          # PowerShell 脚本
├── requirements.txt           # Python 依赖
├── UQM_AI_Assistant_Guide.md  # UQM 指南文档
├── 数据库表结构简化描述.md      # 数据库表结构
├── 查询用例.md                # 查询用例源文件
└── jsonResult/               # 生成结果目录
    ├── query_001_xxx.json
    ├── query_002_xxx.json
    └── ...
```

## 安装与配置

### 1. 环境要求

- Python 3.8+
- 网络连接 (访问 OpenRouter API)
- 运行中的 UQM 服务器 (默认 localhost:8000)

### 2. 安装依赖

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 API Key

获取 OpenRouter API Key: https://openrouter.ai/

```powershell
# PowerShell
$env:OPENROUTER_API_KEY = "your_api_key_here"

# CMD
set OPENROUTER_API_KEY=your_api_key_here

# 永久设置 (系统环境变量)
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "your_api_key_here", "User")
```

### 4. 验证安装

```powershell
python setup.py
```

## 使用方法

### 快速开始

```powershell
# 使用 PowerShell 脚本 (推荐)
.\run_generator.ps1

# 或使用批处理脚本
.\run_generator.bat

# 或直接运行 Python
python uqm_schema_generator.py
```

### 详细命令

#### 1. 处理单个查询

```powershell
# 处理查询 ID 为 5 的单个查询
python uqm_schema_generator.py single 5

# 使用脚本
.\run_generator.ps1 single 5
```

#### 2. 处理查询范围

```powershell
# 从查询 ID 10 开始，处理 5 个查询
python uqm_schema_generator.py range 10 5

# 使用脚本
.\run_generator.ps1 range 10 5
```

#### 3. 处理所有查询

```powershell
# 处理所有查询
python uqm_schema_generator.py range 1 100

# 使用脚本
.\run_generator.ps1 all
```

#### 4. 环境检查

```powershell
# 检查环境配置
python setup.py

# 测试 API 连接
python setup.py test

# 预览查询列表
python setup.py preview
```

## 输出文件格式

生成的 JSON 文件包含以下结构:

```json
{
  "query": {
    "id": 1,
    "title": "查询所有在职员工的基本信息",
    "description": "查询所有在职员工的基本信息。"
  },
  "generated_schema": {
    "uqm": {
      "metadata": {
        "name": "查询在职员工",
        "description": "查询所有在职员工的基本信息"
      },
      "steps": [
        {
          "name": "active_employees",
          "type": "query",
          "config": {
            "data_source": "employees",
            "dimensions": ["employee_id", "first_name", "last_name", "email", "job_title"],
            "filter": {
              "field": "is_active",
              "operator": "=",
              "value": true
            }
          }
        }
      ]
    },
    "parameters": {},
    "options": {
      "query_timeout": 30000
    }
  },
  "execution_result": {
    "success": true,
    "data": [...],
    "execution_time": "1.23s"
  },
  "metadata": {
    "generated_at": "2025-07-02T10:30:00",
    "generator_version": "1.0"
  }
}
```

## 配置选项

### 环境变量

- `OPENROUTER_API_KEY`: OpenRouter API 密钥 (必需)
- `UQM_API_BASE`: UQM API 基础 URL (默认: http://localhost:8000)

### 代码配置

在 `uqm_schema_generator.py` 中可以修改:

- OpenRouter 模型选择 (默认: anthropic/claude-3.5-sonnet)
- 请求超时设置
- 批量处理间隔时间
- 输出目录路径

## 故障排除

### 常见问题

1. **API Key 错误**
   ```
   Error: OPENROUTER_API_KEY environment variable not set
   ```
   解决: 设置正确的环境变量

2. **UQM API 连接失败**
   ```
   UQM API (localhost:8000) is not accessible
   ```
   解决: 确保 UQM 服务器正在运行

3. **JSON 解析错误**
   ```
   Failed to parse JSON for query X
   ```
   解决: 检查生成的内容，可能需要调整 prompt

4. **网络连接问题**
   ```
   OpenRouter API connection failed
   ```
   解决: 检查网络连接和防火墙设置

### 调试模式

启用详细日志:

```python
# 在 uqm_schema_generator.py 中修改
logging.basicConfig(level=logging.DEBUG)
```

### 查看生成的 Schema

所有中间结果都保存在 jsonResult 目录中，可以单独查看生成的 UQM Schema。

## 扩展功能

### 自定义 Prompt

修改 `generate_uqm_schema` 方法中的 prompt 模板来优化生成效果。

### 添加新的查询处理

在 `extract_queries_from_file` 方法中添加对不同格式查询文件的支持。

### 批量验证

添加对生成的 Schema 的语法验证功能。

## 技术架构

```
查询用例.md → 提取查询 → OpenRouter API → UQM Schema → UQM API → 结果保存
    ↓              ↓              ↓              ↓           ↓          ↓
数据库结构 ←→ AI Assistant Guide ←→ JSON Schema ←→ 执行引擎 ←→ jsonResult/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0 (2025-07-02)
- 初始版本发布
- 支持基本的查询处理和 Schema 生成
- 集成 OpenRouter API 和 UQM API
- 批量处理功能
