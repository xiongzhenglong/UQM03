import React, { useState, useEffect } from 'react';
import { Layout, Menu, Button, Space, message } from 'antd';
import { 
  HomeOutlined, 
  BarChartOutlined, 
  PlusOutlined,
  EditOutlined,
  EyeOutlined
} from '@ant-design/icons';
import ReportList from './components/ReportList';
import ReportDetail from './components/ReportDetail';
import ReportEditor from './components/ReportEditor';
import { getReports, getReport } from './services/reportApi';
import type { Report, ReportListItem } from './services/reportApi';

const { Header, Content, Sider } = Layout;

type ViewMode = 'list' | 'detail' | 'editor' | 'new';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewMode>('list');
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [currentReport, setCurrentReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);

  // 加载报表列表
  const loadReports = async () => {
    setLoading(true);
    try {
      const reportsData = await getReports();
      setReports(reportsData);
    } catch (error) {
      console.error('加载报表列表失败:', error);
      message.error('加载报表列表失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // 加载单个报表详情
  const loadReportDetail = async (reportId: string) => {
    setLoading(true);
    try {
      const reportData = await getReport(reportId);
      if (reportData) {
        setCurrentReport(reportData);
        setCurrentView('detail');
      } else {
        message.error('加载报表详情失败');
      }
    } catch (error) {
      console.error('加载报表详情失败:', error);
      message.error('加载报表详情失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // 编辑报表
  const handleEditReport = async (reportId: string) => {
    setLoading(true);
    try {
      const reportData = await getReport(reportId);
      if (reportData) {
        setCurrentReport(reportData);
        setCurrentView('editor');
      } else {
        message.error('加载报表失败');
      }
    } catch (error) {
      console.error('加载报表失败:', error);
      message.error('加载报表失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // 新建报表
  const handleNewReport = () => {
    setCurrentReport(null);
    setCurrentView('editor');
  };

  // 保存报表后的回调
  const handleReportSaved = () => {
    message.success('报表保存成功！');
    loadReports(); // 重新加载报表列表
    setCurrentView('list');
  };

  // 取消编辑
  const handleCancelEdit = () => {
    setCurrentView('list');
    setCurrentReport(null);
  };

  // 查看报表详情
  const handleViewReport = (reportId: string) => {
    loadReportDetail(reportId);
  };

  // 组件挂载时加载报表列表
  useEffect(() => {
    loadReports();
  }, []);

  // 渲染当前视图
  const renderCurrentView = () => {
    switch (currentView) {
      case 'list':
        return (
          <ReportList
            onReportClick={handleViewReport}
            onNewReport={handleNewReport}
          />
        );
      case 'detail':
        return currentReport ? (
          <ReportDetail
            reportId={currentReport.id}
            onBack={() => setCurrentView('list')}
            onEdit={() => setCurrentView('editor')}
          />
        ) : null;
      case 'editor':
        return (
          <ReportEditor
            reportId={currentReport?.id}
            initialTitle={currentReport?.title || ''}
            initialDescription={currentReport?.description || ''}
            onSave={handleReportSaved}
            onCancel={handleCancelEdit}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        display: 'flex', 
        alignItems: 'center', 
        background: '#fff',
        borderBottom: '1px solid #f0f0f0',
        padding: '0 24px'
      }}>
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold text-gray-800 m-0">
              UQM 报表系统
            </h1>
            <div className="text-sm text-gray-500">
              {currentView === 'list' && '我的报表'}
              {currentView === 'detail' && currentReport?.title}
              {currentView === 'editor' && (currentReport ? '编辑报表' : '新建报表')}
            </div>
          </div>
          
          {currentView === 'list' && (
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={handleNewReport}
            >
              新建报表
            </Button>
          )}
          
          {currentView === 'detail' && currentReport && (
            <Space>
              <Button 
                icon={<EditOutlined />}
                onClick={() => setCurrentView('editor')}
              >
                编辑报表
              </Button>
              <Button 
                icon={<EyeOutlined />}
                onClick={() => setCurrentView('list')}
              >
                返回列表
              </Button>
            </Space>
          )}
        </div>
      </Header>
      
      <Content style={{ padding: '24px', background: '#f5f5f5' }}>
        {renderCurrentView()}
      </Content>
    </Layout>
  );
};

export default App;
