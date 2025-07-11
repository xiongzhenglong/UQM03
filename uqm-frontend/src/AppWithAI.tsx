import React, { useState } from 'react';
import AIQueryPage from './components/AIQueryPage';
import ReportList from './components/ReportList';
import ReportDetail from './components/ReportDetail';
import ReportEditor from './components/ReportEditor';

type ViewMode = 'ai-query' | 'list' | 'detail' | 'editor';

const AppWithAI: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewMode>('list');
  const [currentReport, setCurrentReport] = useState<any>(null);

  const handleViewReport = (reportId: string) => {
    // 这里可以实现加载报表详情的逻辑
    console.log('查看报表:', reportId);
    setCurrentView('detail');
  };

  const handleNewReport = () => {
    setCurrentReport(null);
    setCurrentView('editor');
  };

  const handleEditReport = (reportId: string) => {
    // 这里可以实现加载报表编辑的逻辑
    console.log('编辑报表:', reportId);
    setCurrentView('editor');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'ai-query':
        return <AIQueryPage />;
      case 'list':
        return (
          <ReportList
            onReportClick={handleViewReport}
            onNewReport={handleNewReport}
          />
        );
      case 'detail':
        return (
          <ReportDetail
            reportId={currentReport?.id || ''}
            onBack={() => setCurrentView('list')}
            onEdit={() => setCurrentView('editor')}
          />
        );
      case 'editor':
        return (
          <ReportEditor
            reportId={currentReport?.id}
            onSave={(reportId) => {
              console.log('报表保存成功, ID:', reportId);
              setCurrentReport({ id: reportId }); // 更新当前报表ID，以便返回详情页
              setCurrentView('detail');
            }}
            onCancel={() => setCurrentView(currentReport?.id ? 'detail' : 'list')}
          />
        );
      default:
        return <AIQueryPage />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 主内容区域 */}
      <main>
        {renderCurrentView()}
      </main>
    </div>
  );
};

export default AppWithAI; 