import React, { useState, useEffect } from 'react';
import { Button, Modal, Input, List, App, Empty, Popconfirm, Tooltip } from 'antd';
import { SaveOutlined, AppstoreAddOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import { useAppStore } from '../../store/appStore';
import type { SavedVisualization } from '../../types/visualization';

export const SavedList: React.FC = () => {
  const { message } = App.useApp();
  const { 
    savedVisualizations, 
    loadSavedVisualizations,
    saveVisualization,
    loadVisualization,
    deleteVisualization,
    currentUqmQuery,
    currentRendererCode
  } = useAppStore();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newItemName, setNewItemName] = useState('');

  useEffect(() => {
    loadSavedVisualizations();
  }, []);

  const handleSave = () => {
    if (!newItemName.trim()) {
      message.error('请输入一个名称！');
      return;
    }
    saveVisualization(newItemName.trim());
    message.success(`可视化方案 "${newItemName.trim()}" 已保存！`);
    setIsModalOpen(false);
    setNewItemName('');
  };

  const canSave = currentUqmQuery && currentRendererCode;

  return (
    <>
      <Tooltip title={!canSave ? "需要有查询和渲染代码才能保存" : "保存或加载可视化方案"}>
        <Button 
          icon={<AppstoreAddOutlined />}
          onClick={() => setIsModalOpen(true)}
        >
          我的可视化
        </Button>
      </Tooltip>

      <Modal
        title="保存与加载可视化方案"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        width={600}
      >
        <div className="mb-4">
          <Input.Group compact>
            <Input
              style={{ width: 'calc(100% - 100px)' }}
              placeholder="输入新方案的名称"
              value={newItemName}
              onChange={(e) => setNewItemName(e.target.value)}
              disabled={!canSave}
            />
            <Button type="primary" icon={<SaveOutlined />} onClick={handleSave} disabled={!canSave}>
              保存当前
            </Button>
          </Input.Group>
        </div>
        
        <List
          header={<div className="font-semibold">已保存的方案</div>}
          bordered
          dataSource={savedVisualizations}
          locale={{ emptyText: <Empty description="暂无已保存的方案" /> }}
          renderItem={(item: SavedVisualization) => (
            <List.Item
              actions={[
                <Tooltip title="加载">
                  <Button type="text" icon={<EyeOutlined />} onClick={() => {
                    loadVisualization(item.id);
                    setIsModalOpen(false);
                    message.success(`已加载方案: ${item.name}`);
                  }}/>
                </Tooltip>,
                <Popconfirm
                  title={`确定要删除 "${item.name}" 吗？`}
                  onConfirm={() => {
                    deleteVisualization(item.id)
                    message.warning(`已删除方案: ${item.name}`);
                  }}
                  okText="确定"
                  cancelText="取消"
                >
                  <Tooltip title="删除">
                    <Button type="text" danger icon={<DeleteOutlined />} />
                  </Tooltip>
                </Popconfirm>
              ]}
            >
              <List.Item.Meta
                title={item.name}
                description={`创建于: ${new Date(item.createdAt).toLocaleString()}`}
              />
            </List.Item>
          )}
        />
      </Modal>
    </>
  );
}; 