import React, { useState } from 'react';
import { Button, Input, Select, Card, Spin, message, Tabs, Modal, Form } from 'antd';
import type { Report, ReportBlock } from '../services/reportApi';
import { saveReport } from '../services/reportApi';
import { generateVisualization } from '../api/uqmApi';
import TableRenderer from './renderers/TableRenderer';
import ChartRenderer from './renderers/ChartRenderer';
import CodeViewer from './CodeViewer';
import { SaveOutlined } from '@ant-design/icons';
import { v4 as uuidv4 } from 'uuid';

const { TextArea } = Input;
const { Option } = Select;
const { TabPane } = Tabs;

interface VisualizationGeneratorProps {
  data: any[];
  uqmConfig?: any; // UQM查询配置
  onVisualizationGenerated?: (config: any, type: string) => void;
}

const VisualizationGenerator: React.FC<VisualizationGeneratorProps> = ({
  data,
  uqmConfig,
  onVisualizationGenerated
}) => {
  const [query, setQuery] = useState('');
  const [visualizationType, setVisualizationType] = useState('auto');
  const [loading, setLoading] = useState(false);
  const [generatedConfig, setGeneratedConfig] = useState<any>(null);
  const [generatedType, setGeneratedType] = useState<string>('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();


  const handleGenerateVisualization = async () => {
    if (!query.trim()) {
      message.error('请输入可视化需求描述');
      return;
    }

    if (!data || data.length === 0) {
      message.error('没有数据可以可视化');
      return;
    }

    setLoading(true);
    setGeneratedConfig(null); // 重置之前的生成结果
    setGeneratedType('');   // 重置之前的生成结果
    try {
      const result = await generateVisualization(
        data,
        query,
        visualizationType
      );

      if (result.success) {
        setGeneratedConfig(result.config);
        setGeneratedType(result.visualization_type);
        message.success(`成功生成 ${result.visualization_type === 'chart' ? '图表' : '表格'}`);
        
        // 回调通知父组件
        if (onVisualizationGenerated) {
          onVisualizationGenerated(result.config, result.visualization_type);
        }
      } else {
        message.error(result.error || '生成失败');
      }
    } catch (error) {
      console.error('生成可视化失败:', error);
      message.error('生成可视化代码失败');
    } finally {
      setLoading(false);
    }
  };

  const showSaveModal = () => {
    if (!generatedConfig || !uqmConfig) {
      message.warning('请先生成查询和可视化结果后再保存。');
      return;
    }
    form.setFieldsValue({
      title: generatedConfig.title?.text || query || '新的报表区块',
      description: '',
    });
    setIsModalVisible(true);
  };

  const handleSaveOk = async () => {
    try {
      const values = await form.validateFields();
      
      const newBlock: ReportBlock = {
        id: uuidv4(),
        type: generatedType as ('table' | 'chart'),
        title: values.title,
        description: values.description,
        uqmConfig: uqmConfig,
        config: generatedConfig,
        order: 0,
      };

      const newReport: Report = {
        id: uuidv4(),
        title: values.title,
        description: `围绕 "${values.title}" 的专项报表`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        blocks: [newBlock],
      };

      await saveReport(newReport);
      
      message.success('报表区块已成功保存为一个新的报表！');
      setIsModalVisible(false);
      form.resetFields();

    } catch (error) {
      console.error('保存失败:', error);
      message.error('保存报表区块失败，请查看控制台');
    }
  };

  const handleSaveCancel = () => {
    setIsModalVisible(false);
  };


  return (
    <div className="space-y-4">
      <Card title="AI可视化生成器" className="w-full">
        <div className="space-y-4">
          {/* 数据信息 */}
          <div className="bg-gray-50 p-3 rounded">
            <div className="text-sm text-gray-600">
              数据信息: {data?.length || 0} 行数据
              {data?.[0] && `, ${Object.keys(data[0]).length} 个字段`}
            </div>
            {data?.[0] && (
              <div className="text-xs text-gray-500 mt-1">
                字段: {Object.keys(data[0]).join(', ')}
              </div>
            )}
            {/* 数据类型分析 */}
            {data?.[0] && (
              <div className="text-xs text-gray-500 mt-1">
                数据类型: {
                  Object.entries(data[0]).map(([key, value]) => 
                    `${key}: ${typeof value}`
                  ).join(', ')
                }
              </div>
            )}
          </div>

          {/* 可视化类型选择 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              可视化类型
            </label>
            <Select
              value={visualizationType}
              onChange={setVisualizationType}
              className="w-full"
            >
              <Option value="auto">自动选择</Option>
              <Option value="table">表格</Option>
              <Option value="chart">图表</Option>
            </Select>
          </div>

          {/* 需求描述 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              可视化需求描述
            </label>
            <TextArea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="请描述您希望如何可视化这些数据，例如：'生成一个按部门统计平均薪资的柱状图' 或 '创建一个包含所有用户信息的表格'"
              rows={4}
              className="w-full"
            />
          </div>

          {/* 生成按钮 */}
          <div>
            <Button
              type="primary"
              onClick={handleGenerateVisualization}
              loading={loading}
              disabled={!query.trim() || !data?.length}
              className="w-full"
            >
              {loading ? '生成中...' : '生成可视化代码'}
            </Button>
          </div>

          {/* 使用提示 */}
          <div className="bg-blue-50 p-3 rounded text-sm text-blue-700">
            <div className="font-medium mb-1">使用提示：</div>
            <ul className="list-disc list-inside space-y-1">
              <li>描述您想要的可视化效果，AI会自动选择合适的图表类型</li>
              <li>可以指定具体的图表类型（柱状图、折线图、饼图等）</li>
              <li>可以要求特定的排序、筛选或聚合方式</li>
              <li>生成的代码可以直接在页面中渲染</li>
              <li>查看"生成的代码"标签页获取完整的组件代码</li>
            </ul>
          </div>
        </div>
      </Card>

      {loading && (
        <div className="text-center p-8">
            <Spin size="large" tip="正在为您生成可视化..."/>
        </div>
      )}

      {generatedConfig && !loading && (
        <Tabs 
          defaultActiveKey="1" 
          type="card" 
          className="mt-4"
          tabBarExtraContent={
            <Button 
              icon={<SaveOutlined />} 
              onClick={showSaveModal}
              disabled={!generatedConfig || !uqmConfig}
            >
              保存为报表区块
            </Button>
          }
        >
          <TabPane tab="可视化结果" key="1">
            {generatedType === 'table' && (
              <Card title="生成的表格">
                <TableRenderer config={generatedConfig} dataSource={data} />
              </Card>
            )}
            {generatedType === 'chart' && (
              <Card title="生成的图表">
                <ChartRenderer config={generatedConfig} />
              </Card>
            )}
          </TabPane>
          <TabPane tab="生成的代码" key="2">
             <CodeViewer
                data={data}
                config={generatedConfig}
                type={generatedType}
                query={query}
              />
          </TabPane>
        </Tabs>
      )}

      <Modal
        title="保存报表区块"
        visible={isModalVisible}
        onOk={handleSaveOk}
        onCancel={handleSaveCancel}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical" name="form_in_modal">
          <Form.Item
            name="title"
            label="区块标题"
            rules={[{ required: true, message: '请输入区块标题!' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="description" label="区块描述">
            <TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

    </div>
  );
};

export default VisualizationGenerator; 