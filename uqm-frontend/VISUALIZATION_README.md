# AI可视化生成功能说明

## 功能概述

AI可视化生成功能允许用户根据查询结果和自然语言描述，自动生成表格或图表代码，并在页面中直接渲染。

## 功能特性

### 1. 智能可视化选择
- **自动选择**: AI根据数据特点和用户需求自动选择合适的可视化方式
- **手动指定**: 用户可以指定生成表格或图表
- **智能判断**: 基于数据行数、字段类型等自动判断最佳可视化方式

### 2. 支持的可视化类型

#### 表格 (Table)
- 基于Ant Design Table组件
- 支持排序、筛选、分页
- 自动生成列配置
- 响应式设计

#### 图表 (Chart)
- 基于ECharts图表库
- 支持多种图表类型：柱状图、折线图、饼图等
- 自动选择合适的图表类型
- 交互式图表

### 3. 使用流程

1. **执行查询**: 在AI查询页面执行数据查询
2. **切换到可视化**: 点击"AI可视化"标签页
3. **描述需求**: 输入可视化需求描述
4. **生成代码**: 点击"生成可视化代码"
5. **查看结果**: 自动渲染生成的可视化

## API接口

### 生成可视化代码

**接口**: `POST /api/v1/generate-visualization`

**请求参数**:
```json
{
  "data": [
    {"name": "张三", "age": 25, "salary": 8000, "department": "技术部"},
    {"name": "李四", "age": 30, "salary": 12000, "department": "销售部"}
  ],
  "query": "生成一个按部门统计平均薪资的柱状图",
  "visualization_type": "auto",
  "options": {}
}
```

**响应结果**:
```json
{
  "success": true,
  "visualization_type": "chart",
  "config": {
    "title": {"text": "按部门统计平均薪资"},
    "tooltip": {},
    "xAxis": {"type": "category", "data": ["技术部", "销售部"]},
    "yAxis": {"type": "value"},
    "series": [{
      "name": "平均薪资",
      "type": "bar",
      "data": [9000, 12000]
    }]
  }
}
```

## 前端组件

### VisualizationGenerator

主要的可视化生成组件，提供以下功能：

- 数据信息展示
- 可视化类型选择
- 需求描述输入
- 生成按钮
- 结果渲染

### 使用示例

```tsx
import VisualizationGenerator from './VisualizationGenerator';

const MyComponent = () => {
  const data = [
    {"name": "张三", "salary": 8000, "department": "技术部"},
    {"name": "李四", "salary": 12000, "department": "销售部"}
  ];

  const handleVisualizationGenerated = (config, type) => {
    console.log('生成的可视化配置:', config);
    console.log('可视化类型:', type);
  };

  return (
    <VisualizationGenerator 
      data={data}
      onVisualizationGenerated={handleVisualizationGenerated}
    />
  );
};
```

## 使用提示

### 1. 表格可视化
适合以下场景：
- 数据行数较少（< 20行）
- 需要查看详细数据
- 需要排序和筛选功能

**示例描述**:
- "创建一个包含所有用户信息的表格"
- "生成一个产品列表，包含价格和库存信息"
- "显示订单详情，支持按状态筛选"

### 2. 图表可视化
适合以下场景：
- 需要数据趋势分析
- 需要对比不同维度的数据
- 数据量较大时

**示例描述**:
- "生成一个按部门统计平均薪资的柱状图"
- "创建一个显示月度销售额趋势的折线图"
- "制作一个产品类别占比的饼图"

### 3. 自动选择
当选择"自动选择"时，AI会根据以下因素判断：
- 数据行数：少数据倾向于表格，多数据倾向于图表
- 字段类型：数值字段多倾向于图表
- 用户描述：包含"图表"、"柱状图"等关键词时选择图表

## 配置选项

### 表格配置
```json
{
  "type": "table",
  "config": {
    "dataSource": [...],
    "columns": [
      {
        "title": "列标题",
        "dataIndex": "字段名",
        "key": "字段名",
        "sorter": true,
        "filters": [...]
      }
    ],
    "pagination": {"pageSize": 10},
    "scroll": {"x": true}
  }
}
```

### 图表配置
```json
{
  "type": "chart",
  "config": {
    "title": {"text": "图表标题"},
    "tooltip": {},
    "xAxis": {"type": "category", "data": [...]},
    "yAxis": {"type": "value"},
    "series": [
      {
        "name": "系列名",
        "type": "bar",
        "data": [...]
      }
    ]
  }
}
```

## 测试

### 后端测试
```bash
cd uqm-backend
python test_visualization_api.py
```

### 前端测试
1. 启动前端开发服务器
2. 访问 `http://localhost:5173/test-visualization.html`
3. 输入测试数据和需求描述
4. 点击生成按钮查看结果

## 环境变量配置

确保以下环境变量已正确配置：

```bash
# AI服务配置
AI_API_BASE=https://openrouter.ai/api/v1
AI_API_KEY=your_api_key_here
AI_MODEL=anthropic/claude-3.5-sonnet
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.1

# 模拟模式（用于测试）
AI_MOCK_MODE=false
```

## 故障排除

### 常见问题

1. **生成失败**
   - 检查AI API配置是否正确
   - 确认数据格式是否有效
   - 查看后端日志获取详细错误信息

2. **可视化不显示**
   - 检查生成的配置格式是否正确
   - 确认前端组件是否正确导入
   - 验证数据是否为空

3. **性能问题**
   - 大数据量时建议使用图表而非表格
   - 可以限制数据行数以提高生成速度
   - 考虑启用缓存功能

### 调试模式

设置环境变量启用调试模式：
```bash
AI_MOCK_MODE=true
```

这将使用模拟数据生成可视化配置，便于测试和开发。

## 扩展功能

### 自定义渲染器
可以扩展支持更多可视化类型：

1. 创建新的渲染器组件
2. 在VisualizationGenerator中添加对应的渲染逻辑
3. 更新AI提示词以支持新的可视化类型

### 配置保存
可以添加功能保存生成的可视化配置：

1. 保存到本地存储
2. 支持配置的导入导出
3. 提供配置模板库

### 实时更新
可以添加功能支持数据的实时更新：

1. 监听数据变化
2. 自动重新生成可视化
3. 支持动态数据源 