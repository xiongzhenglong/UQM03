# UQM Backend - 统一查询模型后端执行引擎

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)](coverage.html)

UQM Backend 是一个高性能、可扩展的统一查询模型后端执行引擎，旨在提供灵活的数据处理和查询能力。

## ✨ 特性

- **🚀 高性能**: 基于 FastAPI 和异步编程，支持高并发请求
- **🔌 多数据源**: 支持 PostgreSQL、MySQL、SQLite、Redis 等多种数据源
- **⚡ 并行执行**: 支持步骤并行执行，提升处理效率
- **💾 智能缓存**: 内置多级缓存策略，优化查询性能
- **🔒 安全可靠**: 完善的验证机制，防止 SQL 注入和数据泄露
- **📊 实时监控**: 集成 Prometheus 监控和健康检查
- **🐳 容器化**: 完整的 Docker 支持，便于部署
- **📝 完整文档**: 自动生成的 API 文档和详细使用说明

## 🏗️ 架构概览

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API 层        │    │   核心引擎      │    │   连接器层      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • REST API      │    │ • UQM 解析器    │    │ • PostgreSQL    │
│ • 身份验证      │    │ • 执行引擎      │    │ • MySQL         │
│ • 请求验证      │    │ • 步骤调度器    │    │ • SQLite        │
│ • 异常处理      │    │ • 缓存管理      │    │ • Redis         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
           │                       │                       │
           └───────────────────────┼───────────────────────┘
                                   │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   步骤实现      │    │   工具层        │    │   配置层        │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • 查询步骤      │    │ • 表达式解析    │    │ • 环境配置      │
│ • 数据丰富      │    │ • 数据验证      │    │ • 日志配置      │
│ • 数据透视      │    │ • SQL 构建      │    │ • 安全配置      │
│ • 数据合并      │    │ • 异常处理      │    │ • 监控配置      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.9+
- PostgreSQL 12+ (可选)
- Redis 6+ (可选)
- Docker & Docker Compose (可选)

### 安装方式

#### 方式一：Docker 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/uqm/uqm-backend.git
cd uqm-backend

# 使用 Docker Compose 启动
docker-compose up -d

# 检查服务状态
docker-compose ps
```

#### 方式二：本地开发

```bash
# 克隆项目
git clone https://github.com/uqm/uqm-backend.git
cd uqm-backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等

# 启动服务
python -m uvicorn src.main:app --reload
```

#### 方式三：pip 安装

```bash
pip install uqm-backend

# 启动服务
uqm-server
```

### 验证安装

访问 http://localhost:8000 查看服务状态，或访问 http://localhost:8000/docs 查看 API 文档。

## 📖 使用指南

### UQM 配置示例

```json
{
  "name": "user_analysis",
  "version": "1.0.0",
  "description": "用户数据分析示例",
  "datasources": {
    "main_db": {
      "type": "postgresql",
      "connection": {
        "host": "localhost",
        "port": 5432,
        "database": "analytics",
        "username": "user",
        "password": "password"
      }
    }
  },
  "steps": [
    {
      "name": "extract_users",
      "type": "query",
      "datasource": "main_db",
      "config": {
        "sql": "SELECT id, name, email, age, department FROM users WHERE active = true"
      }
    },
    {
      "name": "enrich_users",
      "type": "enrich",
      "depends_on": ["extract_users"],
      "config": {
        "enrichments": [
          {
            "column": "age_group",
            "expression": "'Young' if age < 30 else 'Senior'"
          },
          {
            "column": "email_domain",
            "expression": "email.split('@')[1]"
          }
        ]
      }
    },
    {
      "name": "pivot_by_department",
      "type": "pivot",
      "depends_on": ["enrich_users"],
      "config": {
        "index_columns": ["department"],
        "pivot_column": "age_group",
        "value_columns": ["id"],
        "aggregation": "count"
      }
    }
  ],
  "output": {
    "format": "json",
    "file_path": "user_analysis_result.json"
  }
}
```

### API 使用示例

```python
import requests

# 提交 UQM 任务
response = requests.post(
    "http://localhost:8000/api/v1/execute",
    json=uqm_config
)

execution_id = response.json()["execution_id"]

# 查询执行状态
status_response = requests.get(
    f"http://localhost:8000/api/v1/executions/{execution_id}/status"
)

print(status_response.json())
```

### 支持的步骤类型

| 步骤类型 | 说明 | 配置示例 |
|---------|------|----------|
| `query` | SQL 查询 | `{"sql": "SELECT * FROM table"}` |
| `enrich` | 数据丰富化 | `{"enrichments": [{"column": "new_col", "expression": "old_col * 2"}]}` |
| `pivot` | 数据透视 | `{"index_columns": ["col1"], "pivot_column": "col2", "value_columns": ["col3"]}` |
| `unpivot` | 逆透视 | `{"id_columns": ["id"], "value_columns": ["val1", "val2"]}` |
| `union` | 数据合并 | `{"datasets": ["step1", "step2"], "type": "union"}` |
| `filter` | 数据筛选 | `{"condition": "age > 25"}` |
| `assert` | 数据断言 | `{"assertions": [{"name": "test", "condition": "len(df) > 0"}]}` |

## 🔧 配置说明

### 环境变量

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 应用配置
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
WORKERS=4

# 安全配置
SECRET_KEY=your-secret-key
CORS_ORIGINS=["http://localhost:3000"]

# 缓存配置
CACHE_BACKEND=redis
CACHE_TTL=3600

# 监控配置
ENABLE_METRICS=true
METRICS_PORT=9090
```

### 高级配置

查看 [配置文档](docs/configuration.md) 了解更多配置选项。

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 📊 监控

UQM Backend 内置了完整的监控系统：

- **健康检查**: `/health` 端点
- **指标监控**: Prometheus 格式的指标
- **性能分析**: 执行时间和资源使用统计
- **错误追踪**: 详细的错误日志和堆栈跟踪

### Grafana 仪表板

使用 Docker Compose 部署时，Grafana 将自动配置监控仪表板：

```bash
# 启动监控服务
docker-compose --profile monitoring up -d

# 访问 Grafana
# URL: http://localhost:3000
# 用户名: admin
# 密码: admin
```

## 🛡️ 安全特性

- **SQL 注入防护**: 自动检测和阻止潜在的 SQL 注入攻击
- **表达式安全**: 安全的表达式执行环境，防止代码注入
- **身份验证**: 支持多种身份验证机制
- **数据脱敏**: 敏感数据自动脱敏处理
- **审计日志**: 完整的操作审计追踪

## 🚀 性能优化

- **连接池**: 数据库连接池管理
- **查询缓存**: 多级缓存策略
- **并行执行**: 步骤级并行处理
- **内存优化**: 大数据集流式处理
- **查询优化**: 自动 SQL 查询优化

## 📚 文档

- [API 文档](http://localhost:8000/docs) - 交互式 API 文档
- [用户指南](docs/user-guide.md) - 详细使用说明
- [开发指南](docs/development.md) - 开发和贡献指南
- [部署指南](docs/deployment.md) - 生产环境部署
- [故障排除](docs/troubleshooting.md) - 常见问题解决

## 🤝 贡献

欢迎贡献代码！请查看 [贡献指南](CONTRIBUTING.md) 了解详细信息。

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/uqm/uqm-backend.git
cd uqm-backend

# 安装开发依赖
pip install -e ".[dev]"

# 安装 pre-commit 钩子
pre-commit install

# 运行代码质量检查
make lint

# 运行测试
make test
```

## 📄 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

## 📞 支持

- **文档**: [https://uqm-backend.readthedocs.io/](https://uqm-backend.readthedocs.io/)
- **问题报告**: [GitHub Issues](https://github.com/uqm/uqm-backend/issues)
- **讨论**: [GitHub Discussions](https://github.com/uqm/uqm-backend/discussions)
- **邮件**: team@uqm.com

## 🎯 路线图

### v1.1.0 (计划中)
- [ ] 支持更多数据源 (MongoDB, Elasticsearch)
- [ ] 图形化配置界面
- [ ] 数据血缘追踪
- [ ] 高级调度功能

### v1.2.0 (规划中)
- [ ] 机器学习步骤支持
- [ ] 流式数据处理
- [ ] 分布式执行
- [ ] 数据质量监控

## ⭐ Star 历史

[![Stargazers over time](https://starchart.cc/uqm/uqm-backend.svg)](https://starchart.cc/uqm/uqm-backend)

---

<div align="center">
  Made with ❤️ by the UQM Team
</div>
