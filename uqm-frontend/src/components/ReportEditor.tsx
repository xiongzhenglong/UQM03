import React, { useState, useEffect } from 'react';
import { Card, Button, Space, Modal, message, Popconfirm, Input } from 'antd';
import { PlusOutlined, DeleteOutlined, DragOutlined, EditOutlined, SaveOutlined } from '@ant-design/icons';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { v4 as uuidv4 } from 'uuid';

import { saveReport, getReport } from '../services/reportApi';
import type { Report, ReportBlock } from '../services/reportApi';
import TableBlock from './blocks/TableBlock';
import ChartBlock from './blocks/ChartBlock';
import BlockCreator from './BlockCreator';

interface SortableBlockProps {
  block: ReportBlock;
  onDelete: (id: string) => void;
  onEdit: (block: ReportBlock) => void;
}

const SortableBlock: React.FC<SortableBlockProps> = ({ block, onDelete, onEdit }) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: block.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const renderBlockContent = () => {
    const commonProps = {
      blockId: block.id,
      title: block.title,
      description: block.description,
      uqmConfig: block.uqmConfig,
      config: block.config,
      onEdit: () => onEdit(block),
    };

    switch (block.type) {
      case 'table':
        return <TableBlock {...commonProps} />;
      case 'chart':
        // ChartBlock 可能有额外的属性，例如 chartType
        return <ChartBlock {...commonProps} chartType={block.config?.type || 'bar'} />;
      default:
        return <div className="text-red-500">未知区块类型: {block.type}</div>;
    }
  };

  return (
    <div ref={setNodeRef} style={style} className="mb-4 relative">
      <div className="absolute top-2 right-2 z-10 opacity-0 hover:opacity-100 transition-opacity">
        <Space>
          <Button type="primary" size="small" icon={<EditOutlined />} onClick={() => onEdit(block)} />
          <Popconfirm
            title="确定要删除这个区块吗？"
            onConfirm={() => onDelete(block.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="primary" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
          <div {...attributes} {...listeners} className="cursor-move p-1 bg-gray-200 rounded">
            <DragOutlined className="text-gray-500" />
          </div>
        </Space>
      </div>
      {renderBlockContent()}
    </div>
  );
};

interface ReportEditorProps {
  reportId?: string;
  onSave: (reportId: string) => void;
  onCancel: () => void;
}

const ReportEditor: React.FC<ReportEditorProps> = ({ reportId, onSave, onCancel }) => {
  const [blocks, setBlocks] = useState<ReportBlock[]>([]);
  const [title, setTitle] = useState('新报表');
  const [description, setDescription] = useState('这是一个新报表的描述');
  const [isLoading, setIsLoading] = useState(false);
  const [isCreatorVisible, setIsCreatorVisible] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  useEffect(() => {
    if (reportId) {
      loadExistingReport();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reportId]);

  const loadExistingReport = async () => {
    if (!reportId) return;
    setIsLoading(true);
    try {
      const report = await getReport(reportId);
      if (report) {
        setTitle(report.title);
        setDescription(report.description);
        setBlocks(report.blocks.sort((a, b) => a.order - b.order));
      }
    } catch (error) {
      message.error("加载报表失败");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDragEnd = (event: any) => {
    const { active, over } = event;
    if (active.id !== over.id) {
      setBlocks((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);
        const newItems = arrayMove(items, oldIndex, newIndex);
        return newItems.map((item, index) => ({ ...item, order: index }));
      });
    }
  };

  const handleAddBlock = (blockData: Omit<ReportBlock, 'id' | 'order'>) => {
    const newBlock: ReportBlock = {
      ...blockData,
      id: uuidv4(),
      order: blocks.length,
    };
    
    // 在这里打印即将添加的区块数据
    console.log('即将添加的区块数据 (ReportEditor.tsx):', {
      uqmConfig: JSON.stringify(newBlock.uqmConfig, null, 2),
      config: JSON.stringify(newBlock.config, null, 2),
    });

    setBlocks((prevBlocks) => [...prevBlocks, newBlock]);
    setIsCreatorVisible(false);
  };

  const handleDeleteBlock = (blockId: string) => {
    setBlocks((prev) => prev.filter((b) => b.id !== blockId));
  };

  const handleEditBlock = (block: ReportBlock) => {
    message.info(`编辑区块的功能待实现 (ID: ${block.id})`);
  };

  const handleSaveReport = async () => {
    setIsLoading(true);
    const reportToSave: Report = {
      id: reportId || uuidv4(),
      title,
      description,
      blocks,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    try {
      await saveReport(reportToSave);
      message.success('报表已成功保存！');
      onSave(reportToSave.id);
    } catch (error) {
      message.error('报表保存失败');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 bg-gray-100">
      <Card>
        <div className="flex justify-between items-center mb-4">
          <div>
            <Input
              value={title}
              onChange={e => setTitle(e.target.value)}
              className="text-2xl font-bold"
              placeholder="报表标题"
            />
            <Input.TextArea
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="报表描述"
              autoSize={{ minRows: 1, maxRows: 3 }}
              className="mt-2"
            />
          </div>
          <Space>
            <Button onClick={onCancel}>取消</Button>
            <Button type="primary" icon={<SaveOutlined />} onClick={handleSaveReport} loading={isLoading}>
              保存报表
            </Button>
          </Space>
        </div>

        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <SortableContext items={blocks.map(b => b.id)} strategy={verticalListSortingStrategy}>
            {blocks.map((block) => (
              <SortableBlock
                key={block.id}
                block={block}
                onDelete={handleDeleteBlock}
                onEdit={handleEditBlock}
              />
            ))}
          </SortableContext>
        </DndContext>

        <Button
          type="dashed"
          onClick={() => setIsCreatorVisible(true)}
          block
          icon={<PlusOutlined />}
          className="mt-4"
        >
          添加新区块
        </Button>
      </Card>

      <Modal
        title="创建新区块"
        open={isCreatorVisible}
        onCancel={() => setIsCreatorVisible(false)}
        footer={null}
        width="90vw"
        style={{ top: 20 }}
        destroyOnClose
      >
        <BlockCreator
          onBlockCreated={handleAddBlock}
          onCancel={() => setIsCreatorVisible(false)}
        />
      </Modal>
    </div>
  );
};

export default ReportEditor; 