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