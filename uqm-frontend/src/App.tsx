import React from 'react';
import { Layout, message, notification } from 'antd';
import { Resizable } from 're-resizable';
import { QueryEditor } from './components/QueryEditor';
import { ResultsPanel } from './components/ResultsPanel';
import { AIAssistant } from './components/AIAssistant';
import { SavedList } from './components/SavedList';
import { ErrorBoundary } from './components/ErrorBoundary';
import { useAppStore } from './store/appStore';

const { Header, Content } = Layout;

function App() {
  // 这两个 hooks 用于在 Ant Design 的 <App> 上下文中显示全局消息
  message.useMessage();
  notification.useNotification();

  return (
    <ErrorBoundary>
      <Layout className="h-screen bg-gray-50">
        <Header className="bg-white border-b px-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <img src="/vite.svg" alt="logo" className="h-8 w-8" />
            <h1 className="text-lg font-semibold text-gray-800 m-0">
              UQM AI 可视化工作台
            </h1>
          </div>
          <SavedList />
        </Header>
        
        <Content className="flex-1 overflow-hidden p-2">
          <div className="flex h-full gap-2">
            <Resizable
              defaultSize={{ width: '40%', height: '100%' }}
              minWidth="25%"
              maxWidth="70%"
              enable={{ right: true }}
              className="shadow-sm border rounded-lg overflow-hidden bg-white"
            >
              <QueryEditor />
            </Resizable>

            <div className="flex-1 flex flex-col gap-2">
              <Resizable
                defaultSize={{ width: '100%', height: '65%' }}
                minHeight="40%"
                maxHeight="85%"
                enable={{ bottom: true }}
                className="shadow-sm border rounded-lg overflow-hidden flex-1 bg-white"
              >
                <ResultsPanel />
              </Resizable>

              <div className="shadow-sm border rounded-lg overflow-hidden flex-1 bg-white">
                <AIAssistant />
              </div>
            </div>
          </div>
        </Content>
      </Layout>
    </ErrorBoundary>
  );
}

export default App;
