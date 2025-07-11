# AI可视化功能快速开始指南

## 🚀 快速开始

### 1. 环境准备

确保已安装并配置好UQM项目的基础环境：

```bash
# 克隆项目（如果还没有）
git clone <your-repo-url>
cd UQM03

# 安装后端依赖
cd uqm-backend
pip install -r requirements.txt

# 安装前端依赖
cd ../uqm-frontend
npm install
```

### 2. 配置环境变量

在 `uqm-backend` 目录下创建 `.env` 文件：

```bash
# AI服务配置
AI_API_BASE=https://openrouter.ai/api/v1
AI_API_KEY=your_openrouter_api_key_here
AI_MODEL=anthropic/claude-3.5-sonnet
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.1

# 数据库配置
DATABASE_URL=sqlite:///uqm.db

# 可选：启用模拟模式进行测试
AI_MOCK_MODE=false
```

### 3. 启动服务

#### 后端服务
```bash
cd uqm-backend
python start_with_visualization.py
```

或者手动启动：
```bash
cd uqm-backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 前端服务
```bash
cd uqm-frontend
npm run dev
```

### 4. 访问应用

- 前端应用: http://localhost:5173
- 后端API文档: http://localhost:8000/docs
- 可视化测试页面: http://localhost:5173/test-visualization.html

## 📖 使用教程

### 步骤1: 执行AI查询

1. 打开前端应用
2. 点击"AI查询"标签页
3. 输入自然语言查询，例如：
   - "查询所有用户的订单总金额，按用户分组"
   - "统计每个部门的员工数量和平均薪资"
4. 点击"生成并执行"按钮
5. 等待查询结果

### 步骤2: 生成可视化

1. 点击"AI可视化"标签页
2. 查看查询结果信息
3. 选择可视化类型（自动选择/表格/图表）
4. 输入可视化需求描述，例如：
   - "生成一个按部门统计平均薪资的柱状图"
   - "创建一个包含所有用户信息的表格"
5. 点击"生成可视化代码"按钮
6. 查看生成的可视化结果

## 🧪 测试功能

### 后端API测试

```bash
cd uqm-backend
python test_visualization_api.py
```

### 前端功能测试

1. 访问测试页面：http://localhost:5173/test-visualization.html
2. 输入测试数据
3. 描述可视化需求
4. 点击生成按钮查看结果

## 📋 功能特性

### ✅ 已实现功能

- [x] AI自然语言查询生成
- [x] 查询结果可视化生成
- [x] 表格和图表支持
- [x] 智能可视化类型选择
- [x] 实时渲染预览
- [x] 模拟模式支持
- [x] 完整的错误处理
- [x] 响应式设计

### 🎯 支持的可视化类型

#### 表格 (Table)
- Ant Design Table组件
- 自动列配置
- 排序和筛选
- 分页支持

#### 图表 (Chart)
- ECharts图表库
- 柱状图、折线图、饼图等
- 交互式图表
- 自动数据适配

## 🔧 配置选项

### AI模型配置

可以在环境变量中调整AI模型参数：

```bash
# 使用不同的AI模型
AI_MODEL=anthropic/claude-3.5-sonnet
AI_MODEL=openai/gpt-4
AI_MODEL=meta-llama/llama-3.1-8b-instruct

# 调整生成参数
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.1
```

### 模拟模式

用于开发和测试，不调用真实AI API：

```bash
AI_MOCK_MODE=true
```

## 🐛 故障排除

### 常见问题

1. **AI API调用失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 查看后端日志获取详细错误

2. **可视化不显示**
   - 确认数据格式正确
   - 检查生成的配置是否有效
   - 查看浏览器控制台错误

3. **前端无法连接后端**
   - 确认后端服务已启动
   - 检查端口配置
   - 验证代理设置

### 调试技巧

1. **启用详细日志**
   ```bash
   export LOG_LEVEL=DEBUG
   ```

2. **使用模拟模式测试**
   ```bash
   export AI_MOCK_MODE=true
   ```

3. **检查API响应**
   - 访问 http://localhost:8000/docs
   - 使用Swagger UI测试API

## 📚 更多资源

- [完整功能文档](uqm-frontend/VISUALIZATION_README.md)
- [API接口文档](http://localhost:8000/docs)
- [前端组件文档](uqm-frontend/src/components/)
- [后端服务文档](uqm-backend/src/services/)

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证。 