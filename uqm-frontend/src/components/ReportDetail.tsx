import React, { useState, useEffect } from 'react';
import { Card, Button, Space, Breadcrumb, Tag, Divider, Spin, Empty } from 'antd';
import { ArrowLeftOutlined, EditOutlined, DownloadOutlined, ShareAltOutlined } from '@ant-design/icons';

import { getReport, type Report } from '../services/reportApi';
import TableBlock from './blocks/TableBlock';
import ChartBlock from './blocks/ChartBlock';

interface ReportDetailProps {
  reportId: string;
  onBack: () => void;
  onEdit?: () => void;
}

const ReportDetail: React.FC<ReportDetailProps> = ({ reportId, onBack, onEdit }) => {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReport();
  }, [reportId]);

  const loadReport = async () => {
    setLoading(true);
    try {
      const reportData = await getReport(reportId);
      setReport(reportData);
    } catch (error) {
      console.error('加载报表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    if (onEdit) {
      onEdit();
    }
  };

  if (loading) {
    return (
      <div className="p-6 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <Spin size="large" />
            <p className="mt-4 text-gray-500">正在加载报表...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="p-6 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">报表不存在</h1>
            <p className="text-gray-600 mb-6">找不到指定的报表，请检查报表ID是否正确。</p>
            <Button type="primary" onClick={onBack}>
              返回报表列表
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* 报表头部 */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button 
                type="text" 
                icon={<ArrowLeftOutlined />} 
                onClick={onBack}
                className="text-gray-600 hover:text-gray-900"
              >
                返回
              </Button>
              <Divider type="vertical" />
              <div>
                <Breadcrumb
                  items={[
                    { title: '我的报表' },
                    { title: report.title },
                  ]}
                />
              </div>
            </div>
            <Space>
              <Button icon={<EditOutlined />} onClick={handleEdit}>
                编辑报表
              </Button>
              <Button icon={<DownloadOutlined />}>
                导出
              </Button>
              <Button icon={<ShareAltOutlined />}>
                分享
              </Button>
            </Space>
          </div>
        </div>
      </div>

      {/* 报表信息卡片 */}
      <div className="max-w-7xl mx-auto px-6 py-4">
        <Card className="mb-6">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                {report.title}
              </h1>
              <p className="text-gray-600 mb-3">
                {report.description}
              </p>
              <div className="text-sm text-gray-500">
                创建于: {new Date(report.createdAt).toLocaleDateString('zh-CN')}
              </div>
            </div>
            <div className="flex flex-col items-end gap-2">
              <div className="text-sm text-gray-500">
                最后更新: {new Date(report.updatedAt).toLocaleDateString('zh-CN')}
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* 报表内容 */}
      <div className="max-w-7xl mx-auto px-6 pb-6">
        {report.blocks && report.blocks.length > 0 ? (
          report.blocks.map(block => (
            block.type === 'table' ? (
              <TableBlock
                key={block.id}
                blockId={block.id}
                title={block.title}
                description={block.description}
                uqmConfig={block.uqmConfig}
                config={block.config}
              />
            ) : (
              <ChartBlock
                key={block.id}
                blockId={block.id}
                title={block.title}
                description={block.description}
                uqmConfig={block.uqmConfig}
                chartType={block.config?.chartType || 'bar'}
              />
            )
          ))
        ) : (
          <Card>
            <div className="text-center py-12">
              <div className="text-gray-400">
                <div className="text-4xl mb-4">📊</div>
                <div className="text-lg mb-2">暂无区块</div>
                <div className="text-sm">请在编辑模式下添加区块</div>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ReportDetail; 