# UQM AI 自然语言查询功能

## 功能概述

UQM前端新增了基于AI的自然语言查询功能，用户可以通过自然语言描述查询需求，系统会自动生成并执行相应的UQM查询。

## 主要功能

### 1. 自然语言输入
- 支持中文自然语言描述查询需求
- 提供丰富的查询示例和提示
- 实时输入验证和错误提示

### 2. AI查询生成
- 调用后端AI服务生成UQM Schema
- 显示生成的查询结构和配置
- 支持查看完整的Schema详情

### 3. 查询执行
- 执行生成的UQM查询
- 显示查询结果和统计信息
- 支持数据表格展示

### 4. Schema管理
- 保存生成的Schema到本地存储
- 查看和管理已保存的查询
- 支持加载和删除保存的查询

## 使用方法

### 1. 启动应用
```bash
# 确保后端服务正在运行
cd uqm-backend
python start_with_ai.py

# 启动前端服务
cd uqm-frontend
npm run dev
```

### 2. 使用AI查询
1. 打开应用，默认进入AI查询页面
2. 在文本框中输入自然语言查询，例如：
   - "查询所有用户的订单总金额"
   - "统计每个产品类别的平均价格"
   - "查询最近7天的订单数量"
3. 点击"生成查询"按钮生成Schema
4. 点击"执行查询"按钮获取结果
5. 或直接点击"生成并执行"按钮

### 3. 保存和加载查询
1. 生成Schema后，点击"保存Schema"按钮
2. 在右侧面板查看已保存的查询
3. 点击"加载"按钮可以重新使用保存的查询

## 查询示例

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

## 技术架构

### 前端组件
- `AIQueryPage.tsx` - AI查询主页面
- `AIQueryEditor.tsx` - AI查询编辑器组件
- `AppWithAI.tsx` - 集成AI功能的主应用

### API接口
- `uqmApi.ts` - UQM API客户端
- 支持AI生成和执行接口

### 数据存储
- 使用localStorage保存Schema
- 支持查询历史管理

## 配置要求

### 后端配置
确保后端已正确配置AI相关环境变量：
```bash
AI_API_KEY=your_openrouter_api_key
AI_MODEL=anthropic/claude-3.5-sonnet
AI_API_BASE=https://openrouter.ai/api/v1
```

### 前端配置
确保前端能正确访问后端API：
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

## 故障排除

### 常见问题

1. **AI生成失败**
   - 检查后端AI配置是否正确
   - 确认网络连接正常
   - 查看浏览器控制台错误信息

2. **查询执行失败**
   - 检查数据库连接
   - 确认Schema格式正确
   - 查看后端日志

3. **页面加载失败**
   - 确认前端服务正常运行
   - 检查API代理配置
   - 查看浏览器网络请求

### 调试技巧

1. 打开浏览器开发者工具
2. 查看Network标签页的API请求
3. 查看Console标签页的错误信息
4. 检查localStorage中的保存数据

## 扩展功能

### 计划中的功能
- [ ] 查询模板管理
- [ ] 查询结果导出
- [ ] 查询历史记录
- [ ] 批量查询执行
- [ ] 查询性能优化

### 自定义开发
如需添加新功能，可以参考现有组件结构：
1. 在`components`目录下创建新组件
2. 在`api`目录下添加新的API接口
3. 在`types`目录下定义相关类型
4. 在主应用中集成新功能 