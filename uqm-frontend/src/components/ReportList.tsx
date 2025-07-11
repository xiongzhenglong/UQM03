import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Button, Empty, Spin, message, Popconfirm } from 'antd';
import { PlusOutlined, EyeOutlined, DeleteOutlined } from '@ant-design/icons';
import { getReports, deleteReport, type ReportListItem } from '../services/reportApi';



interface ReportListProps {
  onReportClick: (reportId: string) => void;
  onNewReport?: () => void;
}

const ReportList: React.FC<ReportListProps> = ({ onReportClick, onNewReport }) => {
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [loading, setLoading] = useState(true);

  // 加载报表列表
  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    setLoading(true);
    try {
      const reportsData = await getReports();
      // 按时间降序排列（最新的在前面）
      const sortedReports = reportsData.sort((a, b) => 
        new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
      );
      setReports(sortedReports);
    } catch (error) {
      console.error('加载报表列表失败:', error);
    } finally {
      setLoading(false);
    }
  };



  const handleReportClick = (reportId: string) => {
    onReportClick(reportId);
  };

  // 删除报表
  const handleDeleteReport = async (reportId: string, reportTitle: string) => {
    try {
      const result = await deleteReport(reportId);
      if (result.success) {
        message.success(`报表"${reportTitle}"已删除`);
        // 刷新列表
        loadReports();
      } else {
        message.error('删除失败');
      }
    } catch (error) {
      console.error('删除报表失败:', error);
      message.error('删除失败，请稍后重试');
    }
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* 页面标题 */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            我的报表
          </h1>
          <p className="text-gray-600">
            管理和查看所有报表
          </p>
        </div>

        {/* 操作按钮 */}
        <div className="mb-6 flex justify-end">
          <Button type="primary" icon={<PlusOutlined />} onClick={onNewReport}>
            新建报表
          </Button>
        </div>

        {/* 报表卡片列表 */}
        {loading ? (
          <Card>
            <div className="text-center py-12">
              <Spin size="large" />
              <p className="mt-4 text-gray-500">正在加载报表列表...</p>
            </div>
          </Card>
        ) : reports.length > 0 ? (
          <Row gutter={[16, 16]}>
            {reports.map(report => (
              <Col xs={24} sm={12} lg={8} xl={6} key={report.id}>
                <Card
                  hoverable
                  className="h-full cursor-pointer transition-all duration-200 hover:shadow-lg"
                  onClick={() => handleReportClick(report.id)}
                  cover={
                    <div className="h-32 bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                      <EyeOutlined className="text-white text-3xl" />
                    </div>
                  }
                  actions={[
                    <Button 
                      type="link" 
                      icon={<EyeOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReportClick(report.id);
                      }}
                    >
                      查看
                    </Button>,
                    <Popconfirm
                      title="删除报表"
                      description={`确定要删除报表"${report.title}"吗？此操作不可恢复。`}
                      onConfirm={(e) => {
                        e?.stopPropagation();
                        handleDeleteReport(report.id, report.title);
                      }}
                      onCancel={(e) => e?.stopPropagation()}
                      okText="确定删除"
                      cancelText="取消"
                      okType="danger"
                    >
                      <Button 
                        type="link" 
                        danger
                        icon={<DeleteOutlined />}
                        onClick={(e) => e.stopPropagation()}
                      >
                        删除
                      </Button>
                    </Popconfirm>
                  ]}
                >
                  <Card.Meta
                    title={
                      <div className="flex items-start justify-between">
                        <span className="text-lg font-semibold text-gray-900 truncate">
                          {report.title}
                        </span>
                      </div>
                    }
                    description={
                      <div className="space-y-2">
                        <p className="text-gray-600 text-sm line-clamp-3">
                          {report.description}
                        </p>
                        <div className="text-xs text-gray-400">
                          更新于 {new Date(report.updatedAt).toLocaleDateString('zh-CN')}
                        </div>
                      </div>
                    }
                  />
                </Card>
              </Col>
            ))}
          </Row>
        ) : (
          <Card>
            <Empty
              description={
                <div>
                  <p className="text-gray-500">暂无报表</p>
                  <p className="text-sm text-gray-400">点击"新建报表"创建第一个报表</p>
                </div>
              }
            />
          </Card>
        )}
      </div>
    </div>
  );
};

export default ReportList; 