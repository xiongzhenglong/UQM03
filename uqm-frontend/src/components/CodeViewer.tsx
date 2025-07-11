import React, { useState } from 'react';
import { Card, Tabs, Button, message, Tooltip, Space } from 'antd';
import { CopyOutlined, DownloadOutlined, EyeOutlined, CodeOutlined } from '@ant-design/icons';

const { TabPane } = Tabs;

interface CodeViewerProps {
  data: any[];
  config: any;
  type: string;
  query: string;
}

const CodeViewer: React.FC<CodeViewerProps> = ({ data, config, type, query }) => {
  const [activeTab, setActiveTab] = useState('component');

  const copyToClipboard = (text: string, description: string) => {
    navigator.clipboard.writeText(text).then(() => {
      message.success(`${description}已复制到剪贴板`);
    }).catch(() => {
      message.error('复制失败，请手动复制');
    });
  };

  const downloadCode = (text: string, filename: string) => {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    message.success(`代码已下载为 ${filename}`);
  };

  const generateComponentCode = () => {
    const dataInfo = {
      rowCount: data.length,
      columns: data.length > 0 ? Object.keys(data[0]) : [],
      sampleData: data.slice(0, 3)
    };

    if (type === 'table') {
      return `// 基于 ${dataInfo.rowCount} 行数据生成的表格组件
// 数据字段: ${dataInfo.columns.join(', ')}
// 用户需求: ${query}
// 生成时间: ${new Date().toLocaleString()}

import React, { useState, useEffect } from 'react';
import { Table, Spin, Alert } from 'antd';
import { getCurrentQueryResult, getCurrentQueryInfo, processData } from '../services/dataService';

interface TableData {
${dataInfo.columns.map(col => `  ${col}: any;`).join('\n')}
}

const GeneratedTable: React.FC = () => {
  const [data, setData] = useState<TableData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      // 从数据服务获取当前查询结果
      const queryData = getCurrentQueryResult();
      const queryInfo = getCurrentQueryInfo();
      
      if (queryData.length === 0) {
        setError('没有可用的查询数据，请先执行AI查询');
      } else {
        // 格式化数据
        const formattedData = processData.formatData(queryData);
        setData(formattedData);
        setError(null);
      }
    } catch (err) {
      setError('获取数据失败');
    } finally {
      setLoading(false);
    }
  }, []);

  // 表格配置 - 基于数据结构动态生成
  const tableConfig = {
    columns: ${JSON.stringify(dataInfo.columns.map(col => ({
      title: col,
      dataIndex: col,
      key: col,
      sorter: true,
      ellipsis: true
    })), null, 4)},
    pagination: { pageSize: 10 },
    scroll: { x: true },
    size: 'small' as const
  };

  if (loading) {
    return <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '50px' }} />;
  }

  if (error) {
    return <Alert message="错误" description={error} type="error" showIcon />;
  }

  return (
    <div className="w-full overflow-x-auto">
      <div className="mb-4 text-sm text-gray-600">
        数据行数: {data.length} | 查询: {getCurrentQueryInfo()}
      </div>
      <Table 
        {...tableConfig}
        dataSource={data}
        rowKey={(record, index) => index?.toString() || '0'}
      />
    </div>
  );
};

export default GeneratedTable;`;
    } else if (type === 'chart') {
      return `// 基于 ${dataInfo.rowCount} 行数据生成的图表组件
// 数据字段: ${dataInfo.columns.join(', ')}
// 用户需求: ${query}
// 生成时间: ${new Date().toLocaleString()}

import React, { useState, useEffect, useRef } from 'react';
import { Spin, Alert } from 'antd';
import * as echarts from 'echarts';
import { getCurrentQueryResult, getCurrentQueryInfo, processData } from '../services/dataService';

interface ChartData {
${dataInfo.columns.map(col => `  ${col}: any;`).join('\n')}
}

interface GeneratedChartProps {
  height?: string | number;
}

const GeneratedChart: React.FC<GeneratedChartProps> = ({ 
  height = '400px' 
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  const [data, setData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      // 从数据服务获取当前查询结果
      const queryData = getCurrentQueryResult();
      const queryInfo = getCurrentQueryInfo();
      
      if (queryData.length === 0) {
        setError('没有可用的查询数据，请先执行AI查询');
      } else {
        // 格式化数据
        const formattedData = processData.formatData(queryData);
        setData(formattedData);
        setError(null);
      }
    } catch (err) {
      setError('获取数据失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (chartRef.current && data.length > 0) {
      // 销毁之前的图表实例
      if (chartInstance.current) {
        chartInstance.current.dispose();
      }

      // 根据数据动态生成图表配置
      const chartConfig = generateChartConfig(data);
      
      // 创建新的图表实例
      chartInstance.current = echarts.init(chartRef.current);
      chartInstance.current.setOption(chartConfig);
    }

    // 清理函数
    return () => {
      if (chartInstance.current) {
        chartInstance.current.dispose();
      }
    };
  }, [data]);

  // 响应式处理
  useEffect(() => {
    const handleResize = () => {
      if (chartInstance.current) {
        chartInstance.current.resize();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // 动态生成图表配置
  const generateChartConfig = (chartData: ChartData[]) => {
    const numericColumns = ${JSON.stringify(dataInfo.columns.filter(col => 
      data.some(row => typeof row[col] === 'number')
    ))};
    const stringColumns = ${JSON.stringify(dataInfo.columns.filter(col => 
      data.some(row => typeof row[col] === 'string')
    ))};

    if (numericColumns.length === 0) {
      return {
        title: { text: '暂无数值数据可显示' },
        xAxis: { type: 'category', data: [] },
        yAxis: { type: 'value' },
        series: []
      };
    }

    const xAxisData = chartData.map((item, index) => 
      stringColumns.length > 0 ? item[stringColumns[0]] : \`项目\${index + 1}\`
    );
    const seriesData = chartData.map(item => item[numericColumns[0]]);

    return {
      title: { 
        text: getCurrentQueryInfo() || '数据图表',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          const data = params[0];
          return \`\${data.name}: \${data.value}\`;
        }
      },
      xAxis: {
        type: 'category',
        data: xAxisData,
        axisLabel: { rotate: 45 }
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        name: numericColumns[0],
        type: 'bar',
        data: seriesData,
        itemStyle: {
          color: '#1890ff'
        }
      }]
    };
  };

  if (loading) {
    return <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '50px' }} />;
  }

  if (error) {
    return <Alert message="错误" description={error} type="error" showIcon />;
  }

  return (
    <div>
      <div className="mb-4 text-sm text-gray-600">
        数据行数: {data.length} | 查询: {getCurrentQueryInfo()}
      </div>
      <div 
        ref={chartRef} 
        style={{ width: '100%', height }}
        className="border border-gray-200 rounded-lg"
      />
    </div>
  );
};

export default GeneratedChart;`;
    }

    return '';
  };

  const generateDataProcessingCode = () => {
    if (!data || data.length === 0) return '';

    const columns = Object.keys(data[0] || {});
    const numericColumns = columns.filter(col => 
      data.some(row => typeof row[col] === 'number')
    );
    const stringColumns = columns.filter(col => 
      data.some(row => typeof row[col] === 'string')
    );
    const dateColumns = columns.filter(col => 
      data.some(row => row[col] && (row[col] instanceof Date || typeof row[col] === 'string' && row[col].match(/^\d{4}-\d{2}-\d{2}/)))
    );

    return `// 数据处理工具函数
// 基于原始响应数据 ${data.length} 行，${columns.length} 个字段
// 用户需求: ${query}
// 生成时间: ${new Date().toLocaleString()}

// 数据类型定义
interface RawData {
${columns.map(col => `  ${col}: any;`).join('\n')}
}

interface ProcessedData extends RawData {
  // 处理后的数据可能包含额外的计算字段
}

// 1. 数据预处理和清理
export const processRawData = (rawData: RawData[]): ProcessedData[] => {
  // 清理空值和无效数据
  const cleanedData = rawData.filter(row => 
    row !== null && row !== undefined && Object.keys(row).length > 0
  );
  
  // 数据类型转换和标准化
  const processedData = cleanedData.map(row => ({
    ...row,
    // 数值字段转换
${numericColumns.map(col => `    ${col}: Number(row.${col}) || 0,`).join('\n')}
    // 字符串字段清理
${stringColumns.map(col => `    ${col}: String(row.${col} || '').trim(),`).join('\n')}
    // 日期字段转换
${dateColumns.map(col => `    ${col}: row.${col} ? new Date(row.${col}) : null,`).join('\n')}
  }));
  
  return processedData;
};

// 2. 数据聚合函数
export const aggregateData = <T extends keyof RawData>(
  data: ProcessedData[], 
  groupBy: T, 
  aggregateField: keyof RawData,
  operation: 'sum' | 'avg' | 'count' | 'max' | 'min' = 'avg'
): Array<{ [K in T]: any } & { value: number }> => {
  const groups: Record<string, number[]> = {};
  
  data.forEach(row => {
    const key = String(row[groupBy]);
    if (!groups[key]) {
      groups[key] = [];
    }
    const value = Number(row[aggregateField]);
    if (!isNaN(value)) {
      groups[key].push(value);
    }
  });
  
  return Object.entries(groups).map(([key, values]) => {
    let result: number;
    switch (operation) {
      case 'sum':
        result = values.reduce((sum, val) => sum + val, 0);
        break;
      case 'avg':
        result = values.reduce((sum, val) => sum + val, 0) / values.length;
        break;
      case 'count':
        result = values.length;
        break;
      case 'max':
        result = Math.max(...values);
        break;
      case 'min':
        result = Math.min(...values);
        break;
      default:
        result = values.reduce((sum, val) => sum + val, 0) / values.length;
    }
    
    return {
      [groupBy]: key,
      value: result
    } as any;
  });
};

// 3. 数据过滤函数
export const filterData = (
  data: ProcessedData[], 
  conditions: Partial<Record<keyof RawData, any | ((value: any) => boolean)>>
): ProcessedData[] => {
  return data.filter(row => {
    return Object.entries(conditions).every(([field, condition]) => {
      const value = row[field as keyof RawData];
      
      if (typeof condition === 'function') {
        return condition(value);
      }
      
      return value === condition;
    });
  });
};

// 4. 数据排序函数
export const sortData = <T extends keyof RawData>(
  data: ProcessedData[], 
  sortField: T, 
  order: 'asc' | 'desc' = 'asc'
): ProcessedData[] => {
  return [...data].sort((a, b) => {
    const aVal = a[sortField];
    const bVal = b[sortField];
    
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return order === 'asc' ? aVal - bVal : bVal - aVal;
    }
    
    const aStr = String(aVal || '');
    const bStr = String(bVal || '');
    
    if (order === 'asc') {
      return aStr.localeCompare(bStr);
    } else {
      return bStr.localeCompare(aStr);
    }
  });
};

// 5. 数据统计函数
export const getDataStats = (data: ProcessedData[]): Record<string, any> => {
  if (data.length === 0) return {};
  
  const stats: Record<string, any> = {
    totalRows: data.length,
    columns: Object.keys(data[0]),
    numericColumns: ${numericColumns.map(col => `"${col}"`).join(', ')},
    stringColumns: ${stringColumns.map(col => `"${col}"`).join(', ')},
  };
  
  // 为数值字段计算统计信息
  numericColumns.forEach(col => {
    const values = data.map(row => Number(row[col])).filter(v => !isNaN(v));
    if (values.length > 0) {
      stats[col] = {
        min: Math.min(...values),
        max: Math.max(...values),
        avg: values.reduce((sum, val) => sum + val, 0) / values.length,
        sum: values.reduce((sum, val) => sum + val, 0),
        count: values.length
      };
    }
  });
  
  return stats;
};

// 使用示例:
// const processedData = processRawData(rawData);
// const stats = getDataStats(processedData);
// const aggregatedData = aggregateData(processedData, 'department', 'salary', 'avg');
// const filteredData = filterData(processedData, { status: 'active' });
// const sortedData = sortData(processedData, 'salary', 'desc');`;
  };

  const generateUsageExample = () => {
    const componentName = type === 'table' ? 'GeneratedTable' : 'GeneratedChart';
    const fileName = type === 'table' ? 'GeneratedTable.tsx' : 'GeneratedChart.tsx';
    const dataFileName = 'dataProcessor.ts';

    return `// 使用示例 - 如何集成生成的组件
// 生成时间: ${new Date().toLocaleString()}

import React from 'react';
import { Card, Button, message } from 'antd';
import ${componentName} from './${fileName}';
import { getCurrentQueryResult, getCurrentQueryInfo, processData } from '../services/dataService';

const DataVisualizationPage: React.FC = () => {

  // 检查数据是否可用
  const checkDataAvailability = () => {
    const data = getCurrentQueryResult();
    const queryInfo = getCurrentQueryInfo();
    
    if (data.length === 0) {
      message.warning('没有可用的查询数据，请先执行AI查询');
      return false;
    }
    
    message.success(\`当前有 \${data.length} 行数据可用，查询: \${queryInfo}\`);
    return true;
  };

  // 数据处理示例
  const handleDataProcessing = () => {
    const data = getCurrentQueryResult();
    if (data.length === 0) {
      message.error('没有数据可处理');
      return;
    }

    try {
      // 示例1: 数据格式化
      const formattedData = processData.formatData(data);
      console.log('格式化数据:', formattedData.slice(0, 3));

      // 示例2: 数据聚合（假设有数值字段）
      const numericFields = Object.keys(data[0]).filter(key => 
        typeof data[0][key] === 'number'
      );
      const stringFields = Object.keys(data[0]).filter(key => 
        typeof data[0][key] === 'string'
      );

      if (numericFields.length > 0 && stringFields.length > 0) {
        const aggregatedData = processData.aggregateData(
          data, 
          stringFields[0], 
          numericFields[0], 
          'avg'
        );
        console.log('聚合数据:', aggregatedData);
      }

      // 示例3: 数据过滤和排序
      if (numericFields.length > 0) {
        const sortedData = processData.sortData(data, numericFields[0], 'desc');
        console.log('排序数据前5项:', sortedData.slice(0, 5));
      }

      message.success('数据处理完成，请查看控制台输出');
    } catch (error) {
      message.error('数据处理失败');
      console.error('处理错误:', error);
    }
  };

  return (
    <div className="p-6">
      <Card title="数据可视化页面" className="mb-4">
        <div className="mb-4 space-x-2">
          <Button onClick={checkDataAvailability}>
            检查数据可用性
          </Button>
          <Button onClick={handleDataProcessing} type="primary">
            数据处理示例
          </Button>
        </div>
        
        <div className="text-sm text-gray-600 mb-4">
          <p>• 此组件会自动从数据服务获取当前查询结果</p>
          <p>• 确保在使用前已执行过AI查询</p>
          <p>• 数据会自动格式化和处理</p>
        </div>
      </Card>

      {/* 渲染生成的组件 */}
      <Card title="可视化结果">
        <${componentName} ${type === 'chart' ? 'height="500px"' : ''} />
      </Card>
    </div>
  );
};

export default DataVisualizationPage;`;
  };

  const renderCodeTab = (title: string, code: string, language: string, filename: string) => (
    <div className="relative">
      <div className="absolute top-2 right-2 z-10">
        <Space>
          <Tooltip title="复制代码">
            <Button
              size="small"
              icon={<CopyOutlined />}
              onClick={() => copyToClipboard(code, title)}
            />
          </Tooltip>
          <Tooltip title="下载文件">
            <Button
              size="small"
              icon={<DownloadOutlined />}
              onClick={() => downloadCode(code, filename)}
            />
          </Tooltip>
        </Space>
      </div>
      <div className="bg-gray-900 text-green-400 p-4 rounded overflow-x-auto">
        <pre className="text-sm">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );

  return (
    <Card title="生成的代码" className="mt-4">
      <Tabs activeKey={activeTab} onChange={setActiveTab} size="small">
        <TabPane tab="组件代码" key="component">
          {renderCodeTab(
            '组件代码',
            generateComponentCode(),
            'typescript',
            type === 'table' ? 'GeneratedTable.tsx' : 'GeneratedChart.tsx'
          )}
        </TabPane>
        <TabPane tab="数据处理" key="processing">
          {renderCodeTab(
            '数据处理代码',
            generateDataProcessingCode(),
            'typescript',
            'dataProcessor.ts'
          )}
        </TabPane>
        <TabPane tab="使用示例" key="usage">
          {renderCodeTab(
            '使用示例',
            generateUsageExample(),
            'typescript',
            'DataVisualizationPage.tsx'
          )}
        </TabPane>
        <TabPane tab="配置JSON" key="config">
          {renderCodeTab(
            '配置JSON',
            JSON.stringify(config, null, 2),
            'json',
            'config.json'
          )}
        </TabPane>
      </Tabs>
    </Card>
  );
};

export default CodeViewer; 