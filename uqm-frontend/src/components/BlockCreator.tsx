import React, { useState } from 'react';
import { Card, Tabs, message, Steps, Button, Result } from 'antd';
import { AIQueryEditor } from './AIQueryEditor';
import VisualizationGenerator from './VisualizationGenerator';
import { FileSearchOutlined, BarChartOutlined, SaveOutlined } from '@ant-design/icons';
import type { ReportBlock } from '../services/reportApi';

const { TabPane } = Tabs;
const { Step } = Steps;

interface BlockCreatorProps {
    onBlockCreated: (block: Omit<ReportBlock, 'id' | 'order'>) => void;
    onCancel: () => void;
}

const BlockCreator: React.FC<BlockCreatorProps> = ({ onBlockCreated, onCancel }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [queryResults, setQueryResults] = useState<any[]>([]);
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [currentUqmConfig, setCurrentUqmConfig] = useState<any>(null);

  const [generatedVisConfig, setGeneratedVisConfig] = useState<any>(null);
  const [generatedVisType, setGeneratedVisType] = useState<string>('');


  const handleQueryExecuted = (results: any[], query: string, uqmConfig: any) => {
    setQueryResults(results);
    setCurrentQuery(query);
    setCurrentUqmConfig(uqmConfig);
    message.success('查询执行成功，请进入下一步进行可视化');
    setCurrentStep(1); // 自动进入下一步
  };

  const handleVisualizationGenerated = (config: any, type: string) => {
    setGeneratedVisConfig(config);
    setGeneratedVisType(type);
    message.success(`成功生成可视化配置`);
    // 不自动进入下一步，让用户点击按钮确认
  };
  
  const handleFinish = () => {
    if (!generatedVisConfig || !currentUqmConfig) {
        message.error("无法创建区块，缺少UQM配置或可视化配置。");
        return;
    }

    const newBlockData = {
        type: generatedVisType as ('table' | 'chart'),
        title: generatedVisConfig.title?.text || currentQuery || "未命名区块",
        description: `基于查询: "${currentQuery}"`,
        uqmConfig: currentUqmConfig,
        config: generatedVisConfig
    };

    // 在这里打印即将创建的区块数据
    console.log('即将创建的区块数据 (BlockCreator.tsx):', {
      uqmConfig: JSON.stringify(newBlockData.uqmConfig, null, 2),
      config: JSON.stringify(newBlockData.config, null, 2),
    });

    onBlockCreated(newBlockData);
    message.success("区块已成功添加到报表！");
  };

  return (
    <div className="p-4 bg-gray-50">
      <Steps current={currentStep} className="mb-6">
        <Step title="AI查询" description="使用自然语言执行查询" icon={<FileSearchOutlined />} />
        <Step title="AI可视化" description="根据结果生成图表" icon={<BarChartOutlined />} />
        <Step title="完成" description="保存区块到报表" icon={<SaveOutlined />} />
      </Steps>

      <div style={{ display: currentStep === 0 ? 'block' : 'none' }}>
        <Card title="第一步：执行AI查询" bordered={false}>
          <AIQueryEditor onQueryExecuted={handleQueryExecuted} />
        </Card>
      </div>

      <div style={{ display: currentStep === 1 ? 'block' : 'none' }}>
        <Card title="第二步：生成可视化" bordered={false}>
          {queryResults.length > 0 ? (
            <VisualizationGenerator
              data={queryResults}
              uqmConfig={currentUqmConfig}
              onVisualizationGenerated={handleVisualizationGenerated}
            />
          ) : (
            <Result
                status="warning"
                title="请先返回上一步执行查询"
                extra={
                <Button type="primary" onClick={() => setCurrentStep(0)}>
                    返回第一步
                </Button>
                }
            />
          )}
        </Card>
      </div>

      <div style={{ display: currentStep === 2 ? 'block' : 'none' }}>
        <Result
            status="success"
            title="区块已准备就绪！"
            subTitle="点击下方按钮，将这个配置好的区块添加到您的报表中。"
            extra={[
                <Button type="primary" key="finish" onClick={handleFinish}>
                    添加到报表
                </Button>,
                <Button key="cancel" onClick={onCancel}>
                    关闭
                </Button>,
            ]}
        />
      </div>

      <div className="mt-6 flex justify-end space-x-2">
        {currentStep > 0 && (
          <Button onClick={() => setCurrentStep(currentStep - 1)}>
            上一步
          </Button>
        )}
        {currentStep < 2 && (
          <Button 
            type="primary" 
            onClick={() => setCurrentStep(currentStep + 1)}
            disabled={(currentStep === 0 && queryResults.length === 0) || (currentStep === 1 && !generatedVisConfig) }
          >
            下一步
          </Button>
        )}
      </div>

    </div>
  );
};

export default BlockCreator; 