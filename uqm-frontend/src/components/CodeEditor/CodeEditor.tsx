import React, { useState, useEffect } from 'react';
import { Card, Button, Space, App, Tooltip, Empty } from 'antd';
import { CodeOutlined, SyncOutlined } from '@ant-design/icons';
import Editor from '@monaco-editor/react';
import { useAppStore } from '../../store/appStore';

export const CodeEditor: React.FC = () => {
  const { message } = App.useApp();
  const {
    currentRendererCode,
    updateRendererCode,
    executeRenderer,
    isExecutingRenderer
  } = useAppStore();

  const [localCode, setLocalCode] = useState<string | undefined>(currentRendererCode || '');

  useEffect(() => {
    // 当 store 中的代码（例如 AI 生成的）更新时，同步到本地编辑器状态
    setLocalCode(currentRendererCode || '');
  }, [currentRendererCode]);

  const handleApplyChanges = () => {
    if (localCode) {
      updateRendererCode(localCode);
      // executeRenderer will be triggered automatically by the effect in ResultsPanel
      message.success('代码已更新并开始渲染！');
    }
  };
  
  if (currentRendererCode === null) {
    return <Empty description="暂无渲染器代码。请让 AI 为您生成一个。" className="mt-10" />;
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 relative">
        <Editor
          height="100%"
          language="javascript"
          value={localCode}
          onChange={(value) => setLocalCode(value)}
          options={{
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            fontSize: 14,
            formatOnPaste: true,
            automaticLayout: true,
          }}
          theme="vs-dark"
        />
      </div>
      <div className="p-2 border-t bg-gray-50 flex justify-end">
        <Button
          type="primary"
          icon={<SyncOutlined />}
          onClick={handleApplyChanges}
          loading={isExecutingRenderer}
          disabled={!localCode || localCode === currentRendererCode}
        >
          应用更改并渲染
        </Button>
      </div>
    </div>
  );
}; 