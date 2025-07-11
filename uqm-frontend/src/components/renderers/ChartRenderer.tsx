import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface ChartRendererProps {
  config: any;
}

const ChartRenderer: React.FC<ChartRendererProps> = ({ config }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (chartRef.current && config) {
      // 销毁之前的图表实例
      if (chartInstance.current) {
        chartInstance.current.dispose();
      }

      // 创建新的图表实例
      chartInstance.current = echarts.init(chartRef.current);
      chartInstance.current.setOption(config);
    }

    // 清理函数
    return () => {
      if (chartInstance.current) {
        chartInstance.current.dispose();
      }
    };
  }, [config]);

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

  return (
    <div 
      ref={chartRef} 
      style={{ width: '100%', height: '400px' }}
      className="border border-gray-200 rounded-lg"
    />
  );
};

export default ChartRenderer; 