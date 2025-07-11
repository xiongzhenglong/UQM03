import React, { useState } from 'react';
import { Card, Tabs, message } from 'antd';
import { AIQueryEditor } from './AIQueryEditor';
import VisualizationGenerator from './VisualizationGenerator';

const { TabPane } = Tabs;

const AIQueryPage: React.FC = () => {
  const [queryResults, setQueryResults] = useState<any[]>([]);
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [currentUqmConfig, setCurrentUqmConfig] = useState<any>(null);

  const handleQueryExecuted = (results: any[], query: string, uqmConfig: any) => {
    setQueryResults(results);
    setCurrentQuery(query);
    setCurrentUqmConfig(uqmConfig);
    message.success('查询执行成功，可以进行可视化生成');
  };

  const handleVisualizationGenerated = (config: any, type: string) => {
    message.success(`成功生成${type === 'table' ? '表格' : '图表'}可视化`);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI智能查询与可视化
          </h1>
          <p className="text-gray-600">
            使用自然语言进行数据查询，并自动生成可视化图表
          </p>
        </div>

        <Tabs defaultActiveKey="query" size="large">
          <TabPane tab="AI查询" key="query">
            <Card className="shadow-sm">
              <AIQueryEditor onQueryExecuted={handleQueryExecuted} />
            </Card>
          </TabPane>
          
          <TabPane tab="AI可视化" key="visualization">
            <Card className="shadow-sm">
              {queryResults.length > 0 ? (
                <div>
                  <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded">
                    <div className="text-sm text-green-700">
                      <strong>查询结果:</strong> {queryResults.length} 行数据
                    </div>
                    <div className="text-xs text-green-600 mt-1">
                      查询: {currentQuery}
                    </div>
                  </div>
                  <VisualizationGenerator 
                    data={queryResults}
                    uqmConfig={currentUqmConfig}
                    onVisualizationGenerated={handleVisualizationGenerated}
                  />
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-gray-500 mb-4">
                    <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    暂无查询结果
                  </h3>
                  <p className="text-gray-500">
                    请先在"AI查询"标签页中执行查询，然后返回此页面进行可视化生成
                  </p>
                </div>
              )}
            </Card>
          </TabPane>
        </Tabs>

        {/* 功能说明 */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="AI查询功能" className="shadow-sm">
            <ul className="list-disc list-inside space-y-2 text-gray-600">
              <li>使用自然语言描述查询需求</li>
              <li>AI自动生成UQM JSON Schema</li>
              <li>支持复杂的数据查询和聚合</li>
              <li>实时执行并返回结果</li>
              <li>支持保存和重用查询</li>
            </ul>
          </Card>
          
          <Card title="AI可视化功能" className="shadow-sm">
            <ul className="list-disc list-inside space-y-2 text-gray-600">
              <li>基于查询结果自动生成可视化</li>
              <li>支持表格和多种图表类型</li>
              <li>智能选择合适的可视化方式</li>
              <li>可自定义可视化需求描述</li>
              <li>生成的代码可直接渲染</li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AIQueryPage; 