import React, { useEffect, useMemo } from 'react';
import { Card, Tabs, Spin, Alert, Empty } from 'antd';
import { AreaChartOutlined, CodeOutlined } from '@ant-design/icons';
import { useAppStore } from '../../store/appStore';
import { SandboxService } from '../../services/sandbox';
import ReactECharts from 'echarts-for-react';
import { CodeEditor } from '../CodeEditor/CodeEditor';
import { Table } from 'antd';

const sandboxService = new SandboxService();

export const ResultsPanel: React.FC = () => {
  const {
    currentData,
    currentRendererCode,
    currentVisualization,
    isExecutingRenderer,
    rendererError,
    activeTab,
    setActiveTab,
    executeRenderer,
  } = useAppStore();

  useEffect(() => {
    // 当渲染函数代码变化时，自动在沙箱中执行
    if (currentRendererCode && currentData) {
      executeRenderer();
    }
  }, [currentRendererCode, currentData]);

  const renderContent = () => {
    if (isExecutingRenderer) {
      return (
        <div className="flex items-center justify-center h-full">
          <Spin size="large" tip="正在安全沙箱中渲染..." />
        </div>
      );
    }

    if (rendererError) {
      return <Alert message="渲染失败" description={rendererError} type="error" showIcon />;
    }

    if (!currentVisualization) {
      return <Empty description="暂无可视化结果。请先获取数据并让 AI 生成渲染函数。" />;
    }

    if (currentVisualization.type === 'table') {
      const tableConfig = currentVisualization.config as any;
      return <Table {...tableConfig} dataSource={currentData} rowKey={(record, index) => index?.toString() ?? ''} />;
    }

    if (currentVisualization.type === 'chart') {
      return <ReactECharts option={currentVisualization.config} style={{ height: '100%', width: '100%' }} />;
    }

    return <Empty description="无法识别的可视化类型。" />;
  };
  
  const items = [
    {
      key: 'visualization',
      label: (
        <span>
          <AreaChartOutlined />
          可视化预览
        </span>
      ),
      children: <div className="p-4 h-full">{renderContent()}</div>,
    },
    {
      key: 'code',
      label: (
        <span>
          <CodeOutlined />
          渲染器代码
        </span>
      ),
      children: <CodeEditor />,
    },
  ];

  return (
    <Card
      className="h-full flex flex-col"
      bodyStyle={{ flex: 1, padding: 0, display: 'flex' }}
    >
      <Tabs
        activeKey={activeTab}
        onChange={(key) => setActiveTab(key as 'visualization' | 'code')}
        items={items}
        className="flex-1 flex flex-col"
        tabBarStyle={{ paddingLeft: 16, marginBottom: 0 }}
      />
    </Card>
  );
}; 