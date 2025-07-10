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