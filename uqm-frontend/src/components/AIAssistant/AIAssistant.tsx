import React, { useState, useRef, useEffect } from 'react';
import { Card, Input, Button, List, Avatar, Space, Alert, App, Tooltip } from 'antd';
import { RobotOutlined, SendOutlined, UserOutlined } from '@ant-design/icons';
import { useAppStore } from '../../store/appStore';

interface ChatMessage {
  id: string;
  type: 'user' | 'ai' | 'system';
  content: string;
  timestamp: Date;
}

export const AIAssistant: React.FC = () => {
  const { message } = App.useApp();
  const {
    currentData,
    isGeneratingRenderer,
    aiError,
    generateRenderer, // Action to be implemented in store
    clearAiError,
  } = useAppStore();
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const listEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    
    try {
      // This will trigger the AI generation logic in the store
      await generateRenderer(userMessage.content);
      
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: '已为您生成渲染函数，请在 “结果面板” 的 “渲染器代码” 标签页中查看和编辑。',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiResponse]);

    } catch (error: any) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `抱歉，生成失败：${error.message}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const isSendDisabled = !currentData || !inputValue.trim() || isGeneratingRenderer;

  return (
    <Card
      title={
        <Space>
          <RobotOutlined />
          AI 助手
        </Space>
      }
      className="h-full flex flex-col"
      bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '12px' }}
    >
      {!currentData && (
        <Alert
          message="请先成功执行一次查询"
          description="获取到数据后，我才能为您生成可视化方案。"
          type="info"
          showIcon
          className="m-2"
        />
      )}
      
      <div className="flex-1 overflow-auto mb-2 pr-2">
        <List
          dataSource={messages}
          renderItem={(msg) => (
            <List.Item key={msg.id} className="border-none py-2">
              <List.Item.Meta
                avatar={
                  <Avatar
                    icon={msg.type === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{
                      backgroundColor: msg.type === 'user' ? '#1890ff' : '#52c41a'
                    }}
                  />
                }
                title={
                  <span className="text-xs text-gray-500">
                    {msg.type === 'user' ? '您' : 'AI 助手'} · {msg.timestamp.toLocaleTimeString()}
                  </span>
                }
                description={
                  <div className="bg-gray-100 rounded-lg px-3 py-2 text-gray-800 whitespace-pre-wrap">
                    {msg.content}
                  </div>
                }
              />
            </List.Item>
          )}
        />
        <div ref={listEndRef} />
      </div>
      
      <Tooltip title={!currentData ? "请先执行查询获取数据" : ""}>
        <Space.Compact className="w-full">
          <Input
            placeholder="例如：用表格展示"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onPressEnter={handleSend}
            disabled={!currentData || isGeneratingRenderer}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={isGeneratingRenderer}
            disabled={isSendDisabled}
          >
            发送
          </Button>
        </Space.Compact>
      </Tooltip>
    </Card>
  );
}; 