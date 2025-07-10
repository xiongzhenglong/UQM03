import type { VisualizationConfig } from './visualization';

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