import React, { useState, useEffect, useRef } from 'react';
import { Button, Spin, message, Card, Space, Tag, Select, Row, Col } from 'antd';
import { ReloadOutlined, SettingOutlined } from '@ant-design/icons';
import * as echarts from 'echarts';

const { Option } = Select;

interface ChartBlockProps {
  blockId: string;
  title: string;
  description: string;
  uqmConfig: any;
  chartType?: 'bar' | 'line' | 'pie' | 'scatter';
  onEdit?: () => void;
}

interface DataItem {
  [key: string]: any;
}

const ChartBlock: React.FC<ChartBlockProps> = ({
  blockId,
  title,
  description,
  uqmConfig,
  chartType = 'bar',
  onEdit
}) => {
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState<DataItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [currentChartType, setCurrentChartType] = useState(chartType);
  
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  // 初始化图表
  useEffect(() => {
    if (chartRef.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    return () => {
      if (chartInstance.current) {
        chartInstance.current.dispose();
      }
    };
  }, []);

  // 生成图表配置
  const generateChartOption = (data: DataItem[], type: string) => {
    if (!data || data.length === 0) return {};

    const keys = Object.keys(data[0]);
    if (keys.length < 2) return {};

    // 默认使用前两个字段作为x轴和y轴
    const xField = keys[0];
    const yField = keys[1];

    const xData = data.map(item => item[xField]);
    const yData = data.map(item => item[yField]);

    const baseOption = {
      title: {
        text: title,
        left: 'center',
        textStyle: {
          fontSize: 14,
          fontWeight: 'normal'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: xData,
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value'
      },
      series: []
    };

    switch (type) {
      case 'bar':
        return {
          ...baseOption,
          series: [{
            name: yField,
            type: 'bar',
            data: yData,
            itemStyle: {
              color: '#1890ff'
            }
          }]
        };
      
      case 'line':
        return {
          ...baseOption,
          series: [{
            name: yField,
            type: 'line',
            data: yData,
            smooth: true,
            itemStyle: {
              color: '#52c41a'
            }
          }]
        };
      
      case 'pie':
        return {
          title: {
            text: title,
            left: 'center'
          },
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          series: [{
            name: yField,
            type: 'pie',
            radius: '50%',
            data: data.map(item => ({
              name: item[xField],
              value: item[yField]
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }]
        };
      
      case 'scatter':
        return {
          ...baseOption,
          series: [{
            name: yField,
            type: 'scatter',
            data: data.map(item => [item[xField], item[yField]]),
            itemStyle: {
              color: '#fa8c16'
            }
          }]
        };
      
      default:
        return baseOption;
    }
  };

  // 更新图表
  const updateChart = (data: DataItem[], type: string) => {
    if (chartInstance.current && data.length > 0) {
      const option = generateChartOption(data, type);
      chartInstance.current.setOption(option, true);
    }
  };

  // 请求数据
  const fetchData = async () => {
    if (!uqmConfig) {
      message.error('缺少查询配置');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/v1/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(uqmConfig),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setDataSource(result.data || []);
        updateChart(result.data || [], currentChartType);
        setLastUpdate(new Date());
        message.success('数据刷新成功');
      } else {
        throw new Error(result.message || '查询失败');
      }
    } catch (error) {
      console.error('请求数据失败:', error);
      setError((error as Error).message);
      message.error('请求数据失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // 切换图表类型
  const handleChartTypeChange = (type: string) => {
    setCurrentChartType(type as any);
    updateChart(dataSource, type);
  };

  // 组件挂载时自动加载数据
  useEffect(() => {
    if (uqmConfig) {
      fetchData();
    }
  }, [uqmConfig]);

  // 窗口大小变化时重绘图表
  useEffect(() => {
    const handleResize = () => {
      if (chartInstance.current) {
        chartInstance.current.resize();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <Card
      title={
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-lg">📈</span>
            <span className="font-medium">{title}</span>
            <Tag color="green">图表</Tag>
          </div>
          <Space>
            <Select
              value={currentChartType}
              onChange={handleChartTypeChange}
              size="small"
              style={{ width: 100 }}
            >
              <Option value="bar">柱状图</Option>
              <Option value="line">折线图</Option>
              <Option value="pie">饼图</Option>
              <Option value="scatter">散点图</Option>
            </Select>
            <Button
              type="text"
              size="small"
              icon={<SettingOutlined />}
              onClick={onEdit}
              title="编辑配置"
            />
            <Button
              type="text"
              size="small"
              icon={<ReloadOutlined />}
              onClick={fetchData}
              loading={loading}
              title="刷新数据"
            />
          </Space>
        </div>
      }
      className="mb-4"
    >
      <div className="mb-2">
        <p className="text-gray-600 text-sm mb-2">{description}</p>
        {lastUpdate && (
          <p className="text-xs text-gray-400">
            最后更新: {lastUpdate.toLocaleString('zh-CN')}
          </p>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
          <p className="text-red-600 text-sm">错误: {error}</p>
          <Button size="small" onClick={fetchData} className="mt-2">
            重试
          </Button>
        </div>
      )}

      <Spin spinning={loading}>
        <div 
          ref={chartRef} 
          style={{ 
            width: '100%', 
            height: '400px',
            minHeight: '400px'
          }} 
        />
        
        {!loading && !error && dataSource.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <div className="text-2xl mb-2">📈</div>
            <p>暂无数据</p>
            <Button size="small" onClick={fetchData} className="mt-2">
              刷新数据
            </Button>
          </div>
        )}
      </Spin>
    </Card>
  );
};

export default ChartBlock; 