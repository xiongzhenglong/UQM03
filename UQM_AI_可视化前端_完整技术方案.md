# UQM AI 可视化前端 - 完整技术方案文档

## 📋 项目概述

### 核心目标
构建一个 **AI 驱动的可视化工作台 MVP**，实现从 UQM 查询结果到动态、可编辑、可保存的图表/表格的完整生成流程。

### 核心功能流程
1. **UQM 查询执行** → 用户输入 UQM JSON，获取原始数据
2. **AI 对话生成** → 用户描述需求，AI 生成渲染函数代码
3. **代码可视化** → 渲染函数在沙箱中执行，生成图表/表格
4. **编辑与保存** → 用户可编辑代码，保存完整方案供复用

### 核心价值
- **智能生成**：AI 理解用户意图，自动生成可视化代码
- **安全执行**：Web Worker 沙箱确保代码安全执行
- **完全可控**：生成的代码完全可见可编辑
- **持久化复用**：保存查询+渲染方案，支持一键重现

## 🔧 技术栈

### 核心框架
- **React 18.2+** + **TypeScript** - 主框架
- **Vite 5.0+** - 构建工具，支持 Web Worker
- **Ant Design 5.12+** - UI 组件库

### 专用库
- **Monaco Editor** - 代码编辑器（UQM JSON + 渲染函数）
- **ECharts + echarts-for-react** - 图表渲染
- **Zustand** - 轻量状态管理
- **Axios** - HTTP 请求库

### 样式与工具
- **Tailwind CSS** - 原子化 CSS 框架
- **PostCSS + Autoprefixer** - CSS 后处理

## 📁 完整项目结构

```
uqm-frontend/
├── public/
│   └── vite.svg
├── src/
│   ├── api/
│   │   ├── uqmApi.ts              # UQM 后端 API 调用
│   │   └── aiApi.ts               # AI 服务 API 调用
│   ├── components/
│   │   ├── AIAssistant/
│   │   │   ├── AIAssistant.tsx    # AI 助手聊天界面
│   │   │   └── index.ts
│   │   ├── QueryEditor/
│   │   │   ├── QueryEditor.tsx    # UQM JSON 编辑器
│   │   │   └── index.ts
│   │   ├── ResultsPanel/
│   │   │   ├── ResultsPanel.tsx   # 可视化结果展示面板
│   │   │   └── index.ts
│   │   ├── CodeEditor/
│   │   │   ├── CodeEditor.tsx     # 渲染函数代码编辑器
│   │   │   └── index.ts
│   │   ├── SavedList/
│   │   │   ├── SavedList.tsx      # 保存的方案列表
│   │   │   └── index.ts
│   │   └── ErrorBoundary/
│   │       ├── ErrorBoundary.tsx  # 错误边界组件
│   │       └── index.ts
│   ├── services/
│   │   ├── sandbox.ts             # Web Worker 沙箱服务
│   │   └── storage.ts             # localStorage 封装服务
│   ├── store/
│   │   └── appStore.ts            # Zustand 状态管理
│   ├── types/
│   │   ├── uqm.ts                 # UQM 相关类型定义
│   │   ├── visualization.ts       # 可视化相关类型定义
│   │   └── renderer.ts            # 渲染函数类型定义
│   ├── utils/
│   │   ├── codeValidator.ts       # 代码安全检查工具
│   │   ├── constants.ts           # 常量定义
│   │   └── templates.ts           # AI 生成模板
│   ├── workers/
│   │   └── renderer.worker.ts     # Web Worker 脚本
│   ├── styles/
│   │   └── global.css             # 全局样式
│   ├── App.tsx                    # 主应用组件
│   ├── main.tsx                   # React 应用入口
│   └── vite-env.d.ts             # Vite 类型声明
├── .gitignore
├── .eslintrc.cjs
├── index.html
├── package.json
├── postcss.config.js
├── README.md
├── tailwind.config.js
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

## 📦 依赖配置

### package.json
```json
{
  "name": "uqm-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "antd": "^5.12.0",
    "@monaco-editor/react": "^4.6.0",
    "echarts": "^5.4.3",
    "echarts-for-react": "^3.0.2",
    "zustand": "^4.4.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.45.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.0",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.0.2",
    "vite": "^5.0.0"
  }
}
```

### vite.config.ts
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  worker: {
    format: 'es'
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['antd'],
          editor: ['@monaco-editor/react'],
          charts: ['echarts', 'echarts-for-react']
        }
      }
    }
  }
})
```

### tailwind.config.js
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1890ff',
        success: '#52c41a',
        warning: '#faad14',
        error: '#f5222d',
      },
    },
  },
  plugins: [],
  corePlugins: {
    preflight: false, // 禁用 Tailwind 的 reset，避免与 Ant Design 冲突
  }
}
```

### tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### index.html
```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>UQM AI 可视化工作台</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

## 🎯 核心类型定义

### src/types/visualization.ts
```typescript
// 保存的可视化方案
export interface SavedVisualization {
  id: string;
  name: string;
  description?: string;
  uqmQuery: object;              // UQM 查询 JSON
  rendererFunction: string;      // 渲染函数代码字符串
  createdAt: string;
  updatedAt: string;
}

// 可视化配置
export interface VisualizationConfig {
  type: 'table' | 'chart';
  config: TableConfig | ChartConfig;
}

// 表格配置
export interface TableConfig {
  columns: Array<{
    title: string;
    dataIndex: string;
    key: string;
    width?: number;
    sorter?: (a: any, b: any) => number;
    render?: string; // 渲染函数字符串
    filters?: Array<{ text: string; value: any }>;
  }>;
  pagination?: boolean | {
    pageSize: number;
    showSizeChanger: boolean;
    showQuickJumper: boolean;
  };
  size?: 'small' | 'middle' | 'large';
  bordered?: boolean;
  showHeader?: boolean;
}

// 图表配置 (ECharts)
export interface ChartConfig {
  title?: {
    text: string;
    subtext?: string;
  };
  tooltip?: object;
  legend?: object;
  xAxis?: object;
  yAxis?: object;
  series: any[];
  grid?: object;
  color?: string[];
  backgroundColor?: string;
}
```

### src/types/renderer.ts
```typescript
// 渲染函数类型
export type RendererFunction = (data: any[]) => VisualizationConfig;

// 沙箱执行结果
export interface SandboxResult {
  success: boolean;
  config?: VisualizationConfig;
  error?: string;
  executionTime?: number;
}

// AI 生成请求
export interface AIGenerateRequest {
  data: any[];              // 数据样本
  userPrompt: string;       // 用户描述
  context?: string;         // 上下文信息
}

// AI 生成响应
export interface AIGenerateResponse {
  success: boolean;
  rendererCode?: string;    // 生成的渲染函数代码
  explanation?: string;     // 代码说明
  error?: string;
}
```

### src/types/uqm.ts
```typescript
// UQM 查询类型
export interface UQMQuery {
  steps: UQMStep[];
  [key: string]: any;
}

export interface UQMStep {
  type: string;
  [key: string]: any;
}

// UQM 执行结果
export interface UQMExecuteResponse {
  success: boolean;
  data?: any[];
  error?: string;
  execution_time?: number;
  total_records?: number;
}
```

## 🗃️ 状态管理设计

### src/store/appStore.ts
```typescript
import { create } from 'zustand';
import { SavedVisualization, VisualizationConfig } from '../types/visualization';

interface AppState {
  // === 核心数据状态 ===
  currentUqmQuery: object | null;          // 当前 UQM 查询
  currentData: any[] | null;               // 当前查询结果数据
  currentRendererCode: string | null;      // 当前渲染函数代码
  currentVisualization: VisualizationConfig | null; // 当前可视化配置
  
  // === UI 状态 ===
  isExecutingQuery: boolean;               // 正在执行查询
  isGeneratingRenderer: boolean;           // 正在生成渲染函数
  isExecutingRenderer: boolean;            // 正在执行渲染函数
  activeTab: 'visualization' | 'code';     // 当前激活的标签页
  
  // === 保存的方案 ===
  savedVisualizations: SavedVisualization[];
  currentSavedId: string | null;           // 当前加载的保存方案 ID
  
  // === 错误状态 ===
  queryError: string | null;
  rendererError: string | null;
  aiError: string | null;
  
  // === 操作方法 ===
  // 查询相关
  setUqmQuery: (query: object) => void;
  executeQuery: () => Promise<void>;
  clearQueryError: () => void;
  
  // AI 生成相关
  generateRenderer: (prompt: string) => Promise<void>;
  clearAiError: () => void;
  
  // 渲染函数相关
  updateRendererCode: (code: string) => void;
  executeRenderer: () => Promise<void>;
  clearRendererError: () => void;
  
  // UI 控制
  setActiveTab: (tab: 'visualization' | 'code') => void;
  
  // 保存与加载
  saveVisualization: (name: string, description?: string) => Promise<void>;
  loadVisualization: (id: string) => Promise<void>;
  deleteVisualization: (id: string) => void;
  loadSavedVisualizations: () => void;
  
  // 重置状态
  resetAll: () => void;
}
```

## 🔌 API 接口设计

### src/api/uqmApi.ts
```typescript
import axios from 'axios';

const uqmClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
});

export interface UQMExecuteRequest {
  steps: any[];
  [key: string]: any;
}

export const uqmApi = {
  // 执行 UQM 查询
  async executeQuery(uqmJson: UQMExecuteRequest): Promise<UQMExecuteResponse> {
    const response = await uqmClient.post('/execute', uqmJson);
    return response.data;
  },
  
  // 验证 UQM 语法
  async validateQuery(uqmJson: object): Promise<{ valid: boolean; error?: string }> {
    try {
      const response = await uqmClient.post('/validate', uqmJson);
      return response.data;
    } catch (error) {
      return { valid: false, error: '验证请求失败' };
    }
  }
};
```

### src/api/aiApi.ts
```typescript
// AI 服务 API (MVP 阶段使用模板匹配)
export const aiApi = {
  async generateRenderer(request: AIGenerateRequest): Promise<AIGenerateResponse> {
    // MVP 阶段：使用预设模板和简单规则匹配
    // 生产环境：调用真实 AI 服务
    
    const { data, userPrompt } = request;
    
    try {
      // 分析用户意图
      const intent = analyzeUserIntent(userPrompt);
      
      // 分析数据结构
      const dataStructure = analyzeDataStructure(data);
      
      // 生成对应的渲染函数代码
      const rendererCode = generateRendererTemplate(intent, dataStructure);
      
      return {
        success: true,
        rendererCode,
        explanation: `根据您的需求"${userPrompt}"，我生成了相应的${intent.visualizationType}渲染代码。`
      };
    } catch (error) {
      return {
        success: false,
        error: `AI 生成失败: ${error.message}`
      };
    }
  }
};

// 意图分析函数
function analyzeUserIntent(prompt: string): {
  visualizationType: 'table' | 'chart';
  chartType?: 'bar' | 'line' | 'pie' | 'scatter';
  fields?: string[];
} {
  const lowerPrompt = prompt.toLowerCase();
  
  // 图表关键词检测
  const chartKeywords = {
    bar: ['柱状图', '条形图', 'bar', 'column'],
    line: ['折线图', '线图', 'line', 'trend'],
    pie: ['饼图', '圆饼图', 'pie'],
    scatter: ['散点图', 'scatter']
  };
  
  // 表格关键词
  const tableKeywords = ['表格', 'table', '列表', 'list'];
  
  // ... 具体实现逻辑
}
```

## 🛡️ 沙箱安全设计

### src/workers/renderer.worker.ts
```typescript
// Web Worker 渲染器
self.onmessage = function(e) {
  const { code, data, timeout = 5000 } = e.data;
  
  try {
    // 设置执行超时
    const timeoutId = setTimeout(() => {
      throw new Error('代码执行超时');
    }, timeout);
    
    // 创建安全的执行环境
    const safeGlobals = {
      Math,
      Date,
      JSON,
      console: {
        log: (...args: any[]) => console.log('[Renderer]', ...args),
        error: (...args: any[]) => console.error('[Renderer]', ...args),
      }
    };
    
    // 创建渲染函数
    const rendererFunction = new Function(
      'data',
      'globals', 
      `
        const { Math, Date, JSON, console } = globals;
        return (${code})(data);
      `
    );
    
    // 执行渲染函数
    const startTime = performance.now();
    const result = rendererFunction(data, safeGlobals);
    const executionTime = performance.now() - startTime;
    
    clearTimeout(timeoutId);
    
    // 验证返回结果格式
    if (!result || typeof result !== 'object') {
      throw new Error('渲染函数必须返回一个配置对象');
    }
    
    if (!['table', 'chart'].includes(result.type)) {
      throw new Error('配置对象的 type 字段必须是 "table" 或 "chart"');
    }
    
    // 返回成功结果
    self.postMessage({
      success: true,
      config: result,
      executionTime
    });
    
  } catch (error) {
    // 返回错误信息
    self.postMessage({
      success: false,
      error: error.message
    });
  }
};
```

### src/services/sandbox.ts
```typescript
import { SandboxResult, VisualizationConfig } from '../types/renderer';

export class SandboxService {
  private worker: Worker | null = null;
  
  constructor() {
    this.initWorker();
  }
  
  private initWorker() {
    try {
      this.worker = new Worker(
        new URL('../workers/renderer.worker.ts', import.meta.url),
        { type: 'module' }
      );
    } catch (error) {
      console.error('Failed to initialize worker:', error);
    }
  }
  
  async executeRenderer(
    code: string, 
    data: any[], 
    timeout = 5000
  ): Promise<SandboxResult> {
    return new Promise((resolve) => {
      if (!this.worker) {
        resolve({
          success: false,
          error: 'Worker 未初始化'
        });
        return;
      }
      
      // 设置消息监听
      const onMessage = (e: MessageEvent) => {
        this.worker!.removeEventListener('message', onMessage);
        resolve(e.data as SandboxResult);
      };
      
      this.worker.addEventListener('message', onMessage);
      
      // 发送执行请求
      this.worker.postMessage({
        code,
        data,
        timeout
      });
      
      // 设置外层超时保护
      setTimeout(() => {
        this.worker!.removeEventListener('message', onMessage);
        resolve({
          success: false,
          error: '执行超时'
        });
      }, timeout + 1000);
    });
  }
  
  destroy() {
    if (this.worker) {
      this.worker.terminate();
      this.worker = null;
    }
  }
}
```

## 🎨 核心组件设计

### 主应用布局 (App.tsx)
```typescript
import React from 'react';
import { Layout, Splitter } from 'antd';
import { QueryEditor } from './components/QueryEditor';
import { ResultsPanel } from './components/ResultsPanel';
import { AIAssistant } from './components/AIAssistant';
import { SavedList } from './components/SavedList';
import { ErrorBoundary } from './components/ErrorBoundary';

const { Header, Content } = Layout;

function App() {
  return (
    <ErrorBoundary>
      <Layout className="h-screen">
        {/* 顶部导航 */}
        <Header className="bg-white border-b px-6 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-800">
            UQM AI 可视化工作台
          </h1>
          <SavedList />
        </Header>
        
        {/* 主要内容区域 */}
        <Content className="flex-1 overflow-hidden">
          <Splitter className="h-full">
            {/* 左侧：查询编辑器 */}
            <Splitter.Panel defaultSize="40%" min="30%" max="60%">
              <QueryEditor />
            </Splitter.Panel>
            
            {/* 右侧：结果面板 */}
            <Splitter.Panel>
              <Splitter direction="vertical">
                {/* 上部：可视化结果 */}
                <Splitter.Panel defaultSize="70%" min="50%">
                  <ResultsPanel />
                </Splitter.Panel>
                
                {/* 下部：AI 助手 */}
                <Splitter.Panel>
                  <AIAssistant />
                </Splitter.Panel>
              </Splitter>
            </Splitter.Panel>
          </Splitter>
        </Content>
      </Layout>
    </ErrorBoundary>
  );
}

export default App;
```

### UQM 查询编辑器 (QueryEditor.tsx)
```typescript
import React from 'react';
import { Card, Button, Space, Alert, Spin } from 'antd';
import { PlayCircleOutlined, FileTextOutlined } from '@ant-design/icons';
import Editor from '@monaco-editor/react';
import { useAppStore } from '../store/appStore';

export const QueryEditor: React.FC = () => {
  const {
    currentUqmQuery,
    isExecutingQuery,
    queryError,
    setUqmQuery,
    executeQuery,
    clearQueryError
  } = useAppStore();
  
  const [editorValue, setEditorValue] = React.useState(
    JSON.stringify(currentUqmQuery || {
      "steps": [
        {
          "type": "query",
          "datasource": "mysql://localhost:3306/test",
          "sql": "SELECT * FROM employees LIMIT 100"
        }
      ]
    }, null, 2)
  );
  
  const handleRunQuery = async () => {
    try {
      const queryJson = JSON.parse(editorValue);
      setUqmQuery(queryJson);
      await executeQuery();
    } catch (error) {
      // JSON 解析错误处理
    }
  };
  
  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setEditorValue(value);
      if (queryError) {
        clearQueryError();
      }
    }
  };
  
  return (
    <Card 
      title={
        <Space>
          <FileTextOutlined />
          UQM 查询编辑器
        </Space>
      }
      extra={
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          loading={isExecutingQuery}
          onClick={handleRunQuery}
          disabled={!editorValue.trim()}
        >
          执行查询
        </Button>
      }
      className="h-full flex flex-col"
      bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column' }}
    >
      {queryError && (
        <Alert
          message="查询执行失败"
          description={queryError}
          type="error"
          closable
          onClose={clearQueryError}
          className="mb-4"
        />
      )}
      
      <div className="flex-1 relative">
        {isExecutingQuery && (
          <div className="absolute inset-0 bg-white bg-opacity-80 flex items-center justify-center z-10">
            <Spin size="large" tip="正在执行查询..." />
          </div>
        )}
        
        <Editor
          height="100%"
          defaultLanguage="json"
          value={editorValue}
          onChange={handleEditorChange}
          options={{
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            fontSize: 14,
            formatOnPaste: true,
            formatOnType: true,
          }}
          theme="vs-light"
        />
      </div>
    </Card>
  );
};
```

### AI 助手 (AIAssistant.tsx)
```typescript
import React from 'react';
import { Card, Input, Button, List, Avatar, Space, Alert, Spin } from 'antd';
import { RobotOutlined, SendOutlined, UserOutlined } from '@ant-design/icons';
import { useAppStore } from '../store/appStore';

interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

export const AIAssistant: React.FC = () => {
  const {
    currentData,
    isGeneratingRenderer,
    aiError,
    generateRenderer,
    clearAiError
  } = useAppStore();
  
  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = React.useState('');
  
  const handleSend = async () => {
    if (!inputValue.trim() || !currentData) return;
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    
    try {
      await generateRenderer(userMessage.content);
      
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: '已为您生成渲染函数，请查看右侧的代码编辑器。',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `抱歉，生成失败：${error.message}`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  };
  
  return (
    <Card
      title={
        <Space>
          <RobotOutlined />
          AI 助手
        </Space>
      }
      className="h-full flex flex-col"
      bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column' }}
    >
      {aiError && (
        <Alert
          message="AI 生成失败"
          description={aiError}
          type="error"
          closable
          onClose={clearAiError}
          className="mb-4"
        />
      )}
      
      {!currentData && (
        <Alert
          message="请先执行 UQM 查询获取数据"
          type="info"
          className="mb-4"
        />
      )}
      
      {/* 聊天消息列表 */}
      <div className="flex-1 overflow-auto mb-4">
        <List
          dataSource={messages}
          renderItem={(message) => (
            <List.Item className="border-none py-2">
              <List.Item.Meta
                avatar={
                  <Avatar
                    icon={message.type === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{
                      backgroundColor: message.type === 'user' ? '#1890ff' : '#52c41a'
                    }}
                  />
                }
                title={
                  <span className="text-sm text-gray-500">
                    {message.type === 'user' ? '您' : 'AI 助手'} · {message.timestamp.toLocaleTimeString()}
                  </span>
                }
                description={
                  <div className="text-gray-800 whitespace-pre-wrap">
                    {message.content}
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </div>
      
      {/* 输入区域 */}
      <Space.Compact className="w-full">
        <Input
          placeholder="描述您想要的可视化效果，例如：用表格显示姓名和薪资"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onPressEnter={handleSend}
          disabled={!currentData || isGeneratingRenderer}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={isGeneratingRenderer}
          disabled={!currentData || !inputValue.trim()}
        >
          发送
        </Button>
      </Space.Compact>
    </Card>
  );
};
```

## 🔄 实施步骤

### 第一阶段：基础框架 (1-2天)
1. **项目初始化**
   - 使用 Vite 创建 React + TypeScript 项目
   - 安装并配置所有依赖
   - 配置 Tailwind CSS + Ant Design
   - 配置 Monaco Editor

2. **基础布局实现**
   - 实现 App.tsx 主布局
   - 创建基础的空组件
   - 配置路由和状态管理
   - 实现错误边界

### 第二阶段：查询功能 (2-3天)
1. **UQM 查询编辑器**
   - Monaco Editor 集成 JSON 编辑
   - JSON 语法验证和格式化
   - 执行按钮和状态管理

2. **UQM API 集成**
   - 实现 uqmApi.ts
   - 处理请求/响应和错误
   - 数据状态管理

### 第三阶段：AI 生成功能 (3-4天)
1. **AI 助手界面**
   - 聊天界面实现
   - 消息列表和输入框
   - 用户交互流程

2. **AI 生成逻辑**
   - 实现模板匹配算法
   - 数据结构分析
   - 渲染函数代码生成

### 第四阶段：可视化渲染 (2-3天)
1. **Web Worker 沙箱**
   - 实现安全的代码执行环境
   - 错误处理和超时控制
   - 结果验证

2. **可视化组件**
   - Table 组件集成
   - ECharts 图表集成
   - 动态渲染逻辑

### 第五阶段：编辑和保存 (2天)
1. **代码编辑器**
   - 渲染函数代码编辑
   - 实时预览功能
   - 语法检查

2. **持久化功能**
   - localStorage 存储
   - 保存/加载方案
   - 方案管理界面

### 第六阶段：测试和优化 (1-2天)
1. **功能测试**
   - 端到端流程测试
   - 错误场景测试
   - 性能测试

2. **用户体验优化**
   - 加载状态优化
   - 错误提示优化
   - 界面响应式适配

## 🚀 启动命令

```bash
# 创建项目
npm create vite@latest uqm-frontend -- --template react-ts

# 安装依赖
cd uqm-frontend
npm install

# 安装额外依赖
npm install antd @monaco-editor/react echarts echarts-for-react zustand axios
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 启动开发服务器
npm run dev

# 项目将在 http://localhost:3000 启动
```

## 📝 开发注意事项

### 安全考虑
- Web Worker 隔离用户代码执行
- 严格的代码验证和超时控制
- 禁用危险的全局对象和函数

### 性能优化
- 代码分割和懒加载
- 数据虚拟化（大数据集）
- 组件 memo 和 useMemo 优化

### 用户体验
- 完善的加载状态指示
- 友好的错误提示和恢复
- 响应式设计适配移动端

### 测试策略
- 组件单元测试
- API 集成测试
- 端到端流程测试
- 沙箱安全测试

这个技术方案涵盖了所有实现细节，可以直接按照这个文档进行开发实施。 