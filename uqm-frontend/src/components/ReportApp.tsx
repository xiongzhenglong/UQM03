import React, { useState } from 'react';
import ReportList from './ReportList';
import ReportDetail from './ReportDetail';
import ReportEditor from './ReportEditor';

const ReportApp: React.FC = () => {
  const [currentView, setCurrentView] = useState<'list' | 'detail' | 'editor'>('list');
  const [selectedReportId, setSelectedReportId] = useState<string>('');

  // 新建报表
  const handleNewReport = () => {
    setCurrentView('editor');
  };

  // 报表卡片点击
  const handleReportClick = (reportId: string) => {
    setSelectedReportId(reportId);
    setCurrentView('detail');
  };

  // 返回报表列表
  const handleBackToList = () => {
    setCurrentView('list');
    setSelectedReportId('');
  };

  // 保存报表（这里只是演示，实际可扩展为保存到后端或本地）
  const handleSaveReport = (blocks: any[]) => {
    // 这里可以将 blocks 保存到全局或后端
    setCurrentView('list');
  };

  return (
    <div>
      {currentView === 'list' && (
        <ReportList onReportClick={handleReportClick} onNewReport={handleNewReport} />
      )}
      {currentView === 'detail' && (
        <ReportDetail reportId={selectedReportId} onBack={handleBackToList} />
      )}
      {currentView === 'editor' && (
        <ReportEditor onSave={handleSaveReport} onCancel={handleBackToList} />
      )}
    </div>
  );
};

export default ReportApp; 