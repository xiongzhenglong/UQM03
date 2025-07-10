import React, { useState } from 'react';
import { Card, Button, Space, Alert, Spin, App } from 'antd';
import { PlayCircleOutlined, FileTextOutlined, CheckCircleOutlined, SyncOutlined } from '@ant-design/icons';
import Editor from '@monaco-editor/react';
import { useAppStore } from '../../store/appStore';
import { uqmApi } from '../../api/uqmApi';

export const QueryEditor: React.FC = () => {
  const { message } = App.useApp();
  const {
    currentUqmQuery,
    isExecutingQuery,
    queryError,
    setUqmQuery,
    executeQuery,
    clearQueryError
  } = useAppStore();

  const [editorValue, setEditorValue] = useState(
    JSON.stringify(currentUqmQuery || {
      "steps": [
        {
          "type": "query",
          "datasource": "mysql://root:password@localhost:3306/test",
          "sql": "SELECT * FROM employees LIMIT 100"
        }
      ]
    }, null, 2)
  );
  const [isValidating, setIsValidating] = useState(false);

  const handleRunQuery = async () => {
    try {
      const queryJson = JSON.parse(editorValue);
      setUqmQuery(queryJson);
      await executeQuery(); // 这个 action 稍后会实现
      message.success('查询执行成功！');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'JSON 格式无效';
      message.error(`查询失败: ${errorMessage}`);
    }
  };

  const handleValidate = async () => {
    try {
      setIsValidating(true);
      const queryJson = JSON.parse(editorValue);
      const result = await uqmApi.validateQuery(queryJson);
      if (result.valid) {
        message.success('UQM 语法验证通过！');
      } else {
        message.error(`语法验证失败: ${result.error}`);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'JSON 格式无效';
      message.error(`验证失败: ${errorMessage}`);
    } finally {
      setIsValidating(false);
    }
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setEditorValue(value);
      if (queryError) {
        clearQueryError();
      }
    }
  };
  
  // 将 store 中的 query 同步到编辑器
  React.useEffect(() => {
    if (currentUqmQuery) {
      setEditorValue(JSON.stringify(currentUqmQuery, null, 2));
    }
  }, [currentUqmQuery]);

  return (
    <Card 
      title={
        <Space>
          <FileTextOutlined />
          UQM 查询编辑器
        </Space>
      }
      extra={
        <Space>
          <Button
            icon={<CheckCircleOutlined />}
            loading={isValidating}
            onClick={handleValidate}
          >
            验证语法
          </Button>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            loading={isExecutingQuery}
            onClick={handleRunQuery}
            disabled={!editorValue.trim()}
          >
            执行查询
          </Button>
        </Space>
      }
      className="h-full flex flex-col"
      bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0 }}
    >
      {queryError && (
        <Alert
          message="查询执行失败"
          description={queryError}
          type="error"
          closable
          onClose={clearQueryError}
          className="m-4"
        />
      )}
      
      <div className="flex-1 relative">
        {(isExecutingQuery || isValidating) && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10">
            <Spin size="large" tip={isExecutingQuery ? "正在执行查询..." : "正在验证..."} />
          </div>
        )}
        
        <Editor
          height="100%"
          defaultLanguage="json"
          value={editorValue}
          onChange={handleEditorChange}
          options={{
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            fontSize: 14,
            formatOnPaste: true,
            formatOnType: true,
            automaticLayout: true,
          }}
          theme="vs-light"
        />
      </div>
    </Card>
  );
}; 