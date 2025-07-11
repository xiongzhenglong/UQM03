/**
 * 简单的数据服务 - 为AI生成的组件提供数据获取接口
 */

// 全局存储当前查询结果
let currentQueryResult: any[] = [];
let currentQueryInfo: string = '';

/**
 * 设置当前查询结果（AI查询执行后调用）
 */
export const setCurrentQueryResult = (data: any[], queryInfo?: string): void => {
  currentQueryResult = data || [];
  currentQueryInfo = queryInfo || '';
  
  // 同时保存到localStorage作为备份
  try {
    localStorage.setItem('current_query_result', JSON.stringify(data));
    if (queryInfo) {
      localStorage.setItem('current_query_info', queryInfo);
    }
  } catch (error) {
    console.error('保存查询结果失败:', error);
  }
};

/**
 * 获取当前查询结果 - AI生成的组件调用这个函数
 */
export const getCurrentQueryResult = (): any[] => {
  // 优先从内存获取
  if (currentQueryResult.length > 0) {
    return currentQueryResult;
  }
  
  // 从localStorage获取
  try {
    const stored = localStorage.getItem('current_query_result');
    if (stored) {
      const data = JSON.parse(stored);
      currentQueryResult = data;
      return data;
    }
  } catch (error) {
    console.error('获取查询结果失败:', error);
  }
  
  return [];
};

/**
 * 获取当前查询信息
 */
export const getCurrentQueryInfo = (): string => {
  if (currentQueryInfo) {
    return currentQueryInfo;
  }
  
  try {
    return localStorage.getItem('current_query_info') || '';
  } catch {
    return '';
  }
};

/**
 * 清空当前查询结果
 */
export const clearCurrentQueryResult = (): void => {
  currentQueryResult = [];
  currentQueryInfo = '';
  localStorage.removeItem('current_query_result');
  localStorage.removeItem('current_query_info');
};

/**
 * 数据处理工具函数
 */
export const processData = {
  // 数据格式化
  formatData: (data: any[]): any[] => {
    return data.map(item => {
      const formatted = { ...item };
      // 处理日期格式
      Object.keys(formatted).forEach(key => {
        if (formatted[key] && typeof formatted[key] === 'string') {
          // 检查是否为日期格式
          if (formatted[key].match(/^\d{4}-\d{2}-\d{2}/)) {
            formatted[key] = new Date(formatted[key]).toLocaleDateString();
          }
        }
      });
      return formatted;
    });
  },

  // 数据聚合
  aggregateData: (data: any[], groupBy: string, aggregateField: string, operation: 'sum' | 'avg' | 'count' = 'sum') => {
    const groups: Record<string, any[]> = {};
    
    data.forEach(item => {
      const key = item[groupBy] || 'unknown';
      if (!groups[key]) groups[key] = [];
      groups[key].push(item);
    });

    return Object.entries(groups).map(([key, items]) => {
      let value = 0;
      switch (operation) {
        case 'sum':
          value = items.reduce((sum, item) => sum + (Number(item[aggregateField]) || 0), 0);
          break;
        case 'avg':
          value = items.reduce((sum, item) => sum + (Number(item[aggregateField]) || 0), 0) / items.length;
          break;
        case 'count':
          value = items.length;
          break;
      }
      return { [groupBy]: key, [aggregateField]: value, count: items.length };
    });
  },

  // 数据过滤
  filterData: (data: any[], filters: Record<string, any>) => {
    return data.filter(item => {
      return Object.entries(filters).every(([key, value]) => {
        if (typeof value === 'function') {
          return value(item[key]);
        }
        return item[key] === value;
      });
    });
  },

  // 数据排序
  sortData: (data: any[], field: string, order: 'asc' | 'desc' = 'asc') => {
    return [...data].sort((a, b) => {
      const aVal = a[field];
      const bVal = b[field];
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return order === 'asc' ? aVal - bVal : bVal - aVal;
      }
      
      const aStr = String(aVal || '');
      const bStr = String(bVal || '');
      return order === 'asc' ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr);
    });
  }
};

// 默认导出
export default {
  setCurrentQueryResult,
  getCurrentQueryResult,
  getCurrentQueryInfo,
  clearCurrentQueryResult,
  processData
}; 