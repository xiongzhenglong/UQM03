import React, { useEffect, useState } from 'react';
import { Card, Tabs, Button, Space, message, Spin } from 'antd';
import { PlayCircleOutlined, EyeOutlined, CodeOutlined } from '@ant-design/icons';
import { demoUqmQuery, demoQueryResult, demoTableCode, demoChartCode } from '../utils/demoData';
import { useStore } from '../store/store';

import TableRenderer from './renderers/TableRenderer';
import ChartRenderer from './renderers/ChartRenderer';
import SimpleCodeEditor from './SimpleCodeEditor';

const { TabPane } = Tabs;

const DemoPage: React.FC = () => {
  const { 
    setQueryData, 
    setQueryResult, 
    setCurrentVisualization, 
    setCurrentCode,
    setLoading,
    setError 
  } = useStore();
  
  const [activeTab, setActiveTab] = useState('visualization');
  const [tableConfig, setTableConfig] = useState<any>(null);
  const [chartConfig, setChartConfig] = useState<any>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  // 自动执行演示查询
  useEffect(() => {
    executeDemoQuery();
  }, []);

  const executeDemoQuery = async () => {
    setIsExecuting(true);
    setLoading(true);
    setError(null);
    
    try {
      // 设置预设的查询数据
      setQueryData(demoUqmQuery);
      
      // 模拟查询执行（使用预设数据）
      await new Promise(resolve => setTimeout(resolve, 500)); // 模拟网络延迟
      
      // 设置查询结果
      setQueryResult(demoQueryResult);
      
      // 直接生成表格配置（不使用 Function 构造函数）
      const tableConfig = {
        columns: [
          {
            title: '员工ID',
            dataIndex: 'employee_id',
            key: 'employee_id',
            sorter: (a: any, b: any) => a.employee_id - b.employee_id,
          },
          {
            title: '姓名',
            dataIndex: 'first_name',
            key: 'first_name',
            render: (text: string, record: any) => `${record.first_name} ${record.last_name}`,
          },
          {
            title: '邮箱',
            dataIndex: 'email',
            key: 'email',
          },
          {
            title: '职位',
            dataIndex: 'job_title',
            key: 'job_title',
          },
          {
            title: '薪资',
            dataIndex: 'salary',
            key: 'salary',
            sorter: (a: any, b: any) => parseFloat(a.salary) - parseFloat(b.salary),
            render: (text: string) => `¥${parseFloat(text).toLocaleString()}`,
          },
          {
            title: '入职日期',
            dataIndex: 'hire_date',
            key: 'hire_date',
            sorter: (a: any, b: any) => new Date(a.hire_date).getTime() - new Date(b.hire_date).getTime(),
            render: (text: string) => new Date(text).toLocaleDateString('zh-CN'),
          },
        ],
        dataSource: demoQueryResult,
        pagination: { pageSize: 10, showSizeChanger: true, showQuickJumper: true },
        bordered: true,
        size: 'small' as const,
        showHeader: true,
        scroll: { x: 'max-content' }
      };
      setTableConfig(tableConfig);
      
      // 直接生成图表配置
      const salaryData = demoQueryResult.map((item: any) => ({
        name: `${item.first_name} ${item.last_name}`,
        salary: parseFloat(item.salary)
      }));
      
      // 按薪资排序
      salaryData.sort((a: any, b: any) => b.salary - a.salary);
      
      const names = salaryData.map((item: any) => item.name);
      const salaries = salaryData.map((item: any) => item.salary);

      const chartConfig = {
        title: {
          text: '员工薪资分布',
          subtext: '按薪资从高到低排序',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          formatter: function(params: any) {
            return `${params[0].name}<br/>薪资: ¥${params[0].value.toLocaleString()}`;
          }
        },
        xAxis: {
          type: 'category',
          data: names,
          axisLabel: {
            rotate: 45,
            fontSize: 10
          }
        },
        yAxis: {
          type: 'value',
          name: '薪资 (元)',
          axisLabel: {
            formatter: '¥{value}'
          }
        },
        series: [{
          name: '薪资',
          type: 'bar',
          data: salaries,
          itemStyle: {
            color: function(params: any) {
              const colors = ['#91cc75', '#fac858', '#ee6666'];
              const maxSalary = Math.max(...salaries);
              const ratio = salaries[params.dataIndex] / maxSalary;
              if (ratio > 0.8) return colors[2];
              if (ratio > 0.5) return colors[1];
              return colors[0];
            }
          },
          label: {
            show: true,
            position: 'top',
            formatter: '¥{c}'
          }
        }],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        }
      };
      setChartConfig(chartConfig);
      
      // 设置当前可视化（默认显示表格）
      setCurrentVisualization({
        id: 'demo-table',
        name: '员工信息表格',
        type: 'table',
        config: tableConfig,
        code: demoTableCode,
        createdAt: new Date().toISOString()
      });
      
      // 设置当前代码
      setCurrentCode(demoTableCode);
      
      message.success('演示查询执行成功！');
      
    } catch (error) {
      console.error('演示查询执行失败:', error);
      setError('演示查询执行失败');
      message.error('演示查询执行失败');
    } finally {
      setIsExecuting(false);
      setLoading(false);
    }
  };

  const handleTabChange = (key: string) => {
    setActiveTab(key);
    
    if (key === 'table') {
      setCurrentVisualization({
        id: 'demo-table',
        name: '员工信息表格',
        type: 'table',
        config: tableConfig,
        code: demoTableCode,
        createdAt: new Date().toISOString()
      });
      setCurrentCode(demoTableCode);
    } else if (key === 'chart') {
      setCurrentVisualization({
        id: 'demo-chart',
        name: '员工薪资分布图',
        type: 'chart',
        config: chartConfig,
        code: demoChartCode,
        createdAt: new Date().toISOString()
      });
      setCurrentCode(demoChartCode);
    }
  };

  const handleCodeChange = async (code: string) => {
    try {
      setCurrentCode(code);
      
      // 简单的代码执行（仅用于演示）
      // 在实际环境中，这里会使用更安全的沙箱执行
      console.log('代码已更新:', code);
      message.success('代码已更新！');
    } catch (error) {
      console.error('代码执行失败:', error);
      message.error('代码执行失败: ' + (error as Error).message);
    }
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* 页面标题 */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            UQM AI 可视化演示
          </h1>
          <p className="text-gray-600">
            预设查询：信息技术部员工信息查询与可视化展示
          </p>
        </div>

        {/* 查询信息卡片 */}
        <Card className="mb-6" title="查询信息">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700">查询名称</label>
              <p className="text-gray-900">{demoUqmQuery.uqm.metadata.name}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">描述</label>
              <p className="text-gray-900">{demoUqmQuery.uqm.metadata.description}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">数据条数</label>
              <p className="text-gray-900">{demoQueryResult.length} 条记录</p>
            </div>
          </div>
        </Card>

        {/* 操作按钮 */}
        <div className="mb-6">
          <Space>
            <Button 
              type="primary" 
              icon={<PlayCircleOutlined />}
              onClick={executeDemoQuery}
              loading={isExecuting}
            >
              重新执行查询
            </Button>
            <Button 
              icon={<EyeOutlined />}
              onClick={() => setActiveTab('visualization')}
            >
              查看可视化
            </Button>
            <Button 
              icon={<CodeOutlined />}
              onClick={() => setActiveTab('code')}
            >
              查看代码
            </Button>
          </Space>
        </div>

        {/* 主要内容区域 */}
        <Card>
          <Tabs activeKey={activeTab} onChange={handleTabChange}>
            <TabPane tab="可视化展示" key="visualization">
              <div className="space-y-6">
                {/* 表格展示 */}
                <div>
                  <h3 className="text-lg font-semibold mb-3">员工信息表格</h3>
                  {tableConfig ? (
                    <TableRenderer config={tableConfig} />
                  ) : (
                    <div className="text-center py-8">
                      <Spin size="large" />
                      <p className="mt-2 text-gray-500">正在生成表格...</p>
                    </div>
                  )}
                </div>

                {/* 图表展示 */}
                <div>
                  <h3 className="text-lg font-semibold mb-3">员工薪资分布图</h3>
                  {chartConfig ? (
                    <ChartRenderer config={chartConfig} />
                  ) : (
                    <div className="text-center py-8">
                      <Spin size="large" />
                      <p className="mt-2 text-gray-500">正在生成图表...</p>
                    </div>
                  )}
                </div>
              </div>
            </TabPane>

            <TabPane tab="表格代码" key="table">
              <div>
                <h3 className="text-lg font-semibold mb-3">表格渲染函数代码</h3>
                <SimpleCodeEditor
                  value={demoTableCode}
                  onChange={handleCodeChange}
                  language="javascript"
                  height="400px"
                />
              </div>
            </TabPane>

            <TabPane tab="图表代码" key="chart">
              <div>
                <h3 className="text-lg font-semibold mb-3">图表渲染函数代码</h3>
                <SimpleCodeEditor
                  value={demoChartCode}
                  onChange={handleCodeChange}
                  language="javascript"
                  height="400px"
                />
              </div>
            </TabPane>

            <TabPane tab="原始数据" key="data">
              <div>
                <h3 className="text-lg font-semibold mb-3">查询返回的原始数据</h3>
                <pre className="bg-gray-100 p-4 rounded-lg overflow-auto max-h-96 text-sm">
                  {JSON.stringify(demoQueryResult, null, 2)}
                </pre>
              </div>
            </TabPane>
          </Tabs>
        </Card>
      </div>
    </div>
  );
};

export default DemoPage; 