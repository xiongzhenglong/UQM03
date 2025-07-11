// UQM API 服务
export interface UqmQuery {
  uqm: {
    metadata: {
      name: string;
      description: string;
    };
    steps: any[];
    output: string;
  };
  parameters: Record<string, any>;
  options: {
    dialect: string;
    page?: number;
    page_size?: number;
    pagination_target_step?: string;
  };
}

export interface UqmResponse {
  success: boolean;
  data: any[];
  total?: number;
  page?: number;
  page_size?: number;
  error?: string;
}

// 执行 UQM 查询
export const executeUqmQuery = async (query: UqmQuery): Promise<UqmResponse> => {
  try {
    // 这里应该调用实际的 UQM 后端 API
    // 目前返回模拟数据
    const response = await fetch('/api/uqm/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(query),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('UQM 查询执行失败:', error);
    throw error;
  }
};

// 获取查询历史
export const getQueryHistory = async (): Promise<UqmQuery[]> => {
  try {
    const response = await fetch('/api/uqm/history');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('获取查询历史失败:', error);
    return [];
  }
}; 