import axios from 'axios';
import type { UQMExecuteResponse } from '../types/uqm';

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
      if (axios.isAxiosError(error)) {
        return { valid: false, error: error.response?.data?.error || '验证请求失败' };
      }
      return { valid: false, error: '一个未知错误发生' };
    }
  }
}; 