// 报表API服务
export interface ReportBlock {
  id: string;
  type: 'table' | 'chart';
  title: string;
  description: string;
  uqmConfig: any; // UQM查询配置
  config: any; // 可视化配置
  order: number;
}

export interface Report {
  id: string;
  title: string;
  description: string;
  createdAt: string;
  updatedAt: string;
  blocks: ReportBlock[];
}

export interface ReportListItem {
  id: string;
  title: string;
  description: string;
  createdAt: string;
  updatedAt: string;
  filename: string;
}

// 获取报表列表
export const getReports = async (): Promise<ReportListItem[]> => {
  try {
    const response = await fetch('/api/v1/reports');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('获取报表列表失败:', error);
    return [];
  }
};

// 获取单个报表详情
export const getReport = async (reportId: string): Promise<Report | null> => {
  try {
    const response = await fetch(`/api/v1/reports/${reportId}`);
    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('获取报表详情失败:', error);
    return null;
  }
};

// 创建/保存报表
export const saveReport = async (report: Report): Promise<{ success: boolean; id: string }> => {
  try {
    const response = await fetch('/api/v1/reports', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(report),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('保存报表失败:', error);
    throw error;
  }
};

// 删除报表
export const deleteReport = async (reportId: string): Promise<{ success: boolean }> => {
  try {
    const response = await fetch(`/api/v1/reports/${reportId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('删除报表失败:', error);
    throw error;
  }
}; 