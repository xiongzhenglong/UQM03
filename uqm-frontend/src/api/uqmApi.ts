import axios from 'axios';
import type { UQMExecuteResponse } from '../types/uqm';

export type { UQMExecuteResponse };

const uqmClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
});

export interface UQMExecuteRequest {
  uqm: {
    metadata: {
      name: string;
      description: string;
    };
    steps: any[];
    output: string;
  };
  parameters?: Record<string, any>;
  options?: Record<string, any>;
}

export interface AIGenerateRequest {
  query: string;
  options?: Record<string, any>;
}

export interface AIGenerateResponse {
  uqm: {
    metadata: {
      name: string;
      description: string;
    };
    steps: any[];
    output: string;
  };
  parameters: Record<string, any>;
  options: Record<string, any>;
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
      if (axios.isAxiosError(error)) {
        return { valid: false, error: error.response?.data?.error || '验证请求失败' };
      }
      return { valid: false, error: '一个未知错误发生' };
    }
  },

  // AI生成UQM Schema
  async generateSchema(request: AIGenerateRequest): Promise<AIGenerateResponse> {
    const response = await uqmClient.post('/generate', request);
    return response.data;
  },

  // AI生成并执行查询
  async generateAndExecute(request: AIGenerateRequest): Promise<UQMExecuteResponse> {
    const response = await uqmClient.post('/generate-and-execute', request);
    return response.data;
  }
};

// AI生成可视化代码
export const generateVisualization = async (
  data: any[],
  query: string,
  visualizationType: string = 'auto',
  options?: any
): Promise<{
  success: boolean;
  visualization_type: string;
  config: any;
  error?: string;
}> => {
  try {
    const response = await fetch('/api/v1/generate-visualization', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        data,
        query,
        visualization_type: visualizationType,
        options
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || '生成可视化代码失败');
    }

    return await response.json();
  } catch (error) {
    console.error('生成可视化代码失败:', error);
    throw error;
  }
}; 