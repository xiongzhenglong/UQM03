import React, { useState, useEffect } from 'react';
import { Card, Table, Spin, Alert, Button, message, Tag } from 'antd';
import { ReloadOutlined, SettingOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { uqmApi } from '../../api/uqmApi';
import type { UQMExecuteResponse } from '../../types/uqm';

// 定义数据项接口
interface DataItem {
  [key: string]: any;
}

// 定义组件 Props 接口
interface TableBlockProps {
  blockId?: string;
  title?: string;
  description?: string;
  uqmConfig?: object; // UQM 查询配置
  onEdit?: () => void; // 编辑按钮点击事件
  config?: any; // AI 返回的完整配置
  data?: any[]; // AI 返回的数据
}

const TableBlock: React.FC<TableBlockProps> = ({
  blockId,
  title: initialTitle,
  description,
  uqmConfig,
  onEdit,
  config,
  data
}) => {
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState<DataItem[]>([]);
  const [columns, setColumns] = useState<ColumnsType<DataItem>>([]);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [tableTitle, setTableTitle] = useState(initialTitle);
  const [tableDescription, setTableDescription] = useState(description);

  // 从 config 生成表格配置
  const processConfig = (cfg: any, dataSource?: DataItem[]) => {
    // 如果 config 直接包含列配置（AI 生成的表格配置）
    if (cfg && cfg.columns && Array.isArray(cfg.columns)) {
      console.log('使用保存的列配置:', cfg.columns);
      setColumns(cfg.columns as ColumnsType<DataItem>);
      if (dataSource) {
        setDataSource(dataSource);
      }
      if (cfg.title && cfg.title.text) {
        setTableTitle(cfg.title.text);
      }
      return;
    }
    
    // 如果是图表 config（包含 series、xAxis 等）
    if (cfg && cfg.series && cfg.xAxis && cfg.xAxis.data) {
      const newColumns = [
        {
          title: cfg.xAxis.name || 'Category',
          dataIndex: 'category',
          key: 'category',
        },
        {
          title: cfg.yAxis.name || 'Value',
          dataIndex: 'value',
          key: 'value',
        },
      ];
      const newDataSource = cfg.xAxis.data.map((item: any, index: number) => ({
        key: index,
        category: item,
        value: cfg.series[0].data[index],
      }));
      setColumns(newColumns as ColumnsType<DataItem>);
      setDataSource(newDataSource);
      if (cfg.title && cfg.title.text) {
        setTableTitle(cfg.title.text);
      }
    } else if (data) {
        const newColumns = generateColumns(data);
        setColumns(newColumns);
        setDataSource(data);
    }
  };


  // 生成表格列配置
  const generateColumns = (data: DataItem[]): ColumnsType<DataItem> => {
    if (!data || data.length === 0) return [];

    const firstRow = data[0];
    return Object.keys(firstRow).map(key => ({
      title: key,
      dataIndex: key,
      key: key,
      sorter: (a, b) => {
        if (typeof a[key] === 'number' && typeof b[key] === 'number') {
          return a[key] - b[key];
        }
        if (typeof a[key] === 'string' && typeof b[key] === 'string') {
          return a[key].localeCompare(b[key]);
        }
        return 0;
      },
    }));
  };

  // 请求数据
  const fetchData = async () => {
    if (!uqmConfig || Object.keys(uqmConfig).length === 0) {
        console.log('fetchData: uqmConfig 为空，跳过请求');
        return;
    }

    setLoading(true);
    setError(null);
    
    try {
      // 在这里打印即将发送的配置
      console.log('即将发送到 /execute 的 uqmConfig:', uqmConfig);
      console.log('即将发送到 /execute 的 uqmConfig (JSON):', JSON.stringify(uqmConfig, null, 2));

      const response: UQMExecuteResponse = await uqmApi.executeQuery(uqmConfig as any);
      
      if (response.success) {
        const responseData = response.data || [];
        setDataSource(responseData);
        
        // 如果有保存的列配置，优先使用保存的配置
        if (config && config.columns && Array.isArray(config.columns)) {
          console.log('数据请求成功，使用保存的列配置:', config.columns);
          setColumns(config.columns as ColumnsType<DataItem>);
        } else {
          // 否则自动生成列配置
          console.log('数据请求成功，自动生成列配置');
          setColumns(generateColumns(responseData));
        }
        
        setLastUpdate(new Date());

        if (response.config && response.config.title && response.config.title.text) {
          setTableTitle(response.config.title.text);
        } else {
          setTableTitle(initialTitle);
        }
        if (responseData.length > 0) {
            message.success('数据刷新成功');
        }
      } else {
        throw new Error(response.error || '查询失败');
      }
    } catch (error) {
      console.error('请求数据失败:', error);
      setError((error as Error).message);
      message.error('请求数据失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // 效果钩子
  useEffect(() => {
    console.log('TableBlock useEffect 触发:', { 
      hasUqmConfig: !!uqmConfig && Object.keys(uqmConfig).length > 0, 
      hasConfig: !!config, 
      hasData: !!data 
    });
    
    // 优先使用 uqmConfig 发送请求获取实时数据
    if (uqmConfig && Object.keys(uqmConfig).length > 0) {
      console.log('使用 uqmConfig 发送请求');
      fetchData();
    } else if (config) {
      console.log('使用 config 处理静态配置');
      processConfig(config);
    } else if (data) {
      console.log('使用 data 处理静态数据');
      const newColumns = generateColumns(data);
      setColumns(newColumns);
      setDataSource(data);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(uqmConfig), JSON.stringify(config), data]);


  const handleRefresh = () => {
    if (uqmConfig) {
        fetchData();
    }
  };

  const finalTitle = tableTitle || '数据表格';
  const antdTableTitle = finalTitle ? () => <h4 style={{ margin: 0 }}>{finalTitle}</h4> : undefined;

  if (!loading && dataSource.length === 0 && !error) {
    if (config || data) {
    } else if (!uqmConfig || Object.keys(uqmConfig).length === 0) {
        return (
            <Card title="表格" className="h-full shadow-sm">
                <div className="p-4 text-center text-gray-500">
                    <p>请先提供有效的查询配置</p>
                    {onEdit && <Button onClick={onEdit} className="mt-2">编辑配置</Button>}
                </div>
            </Card>
        );
    }
  }


  return (
    <Card
      className="h-full shadow-sm"
      title={
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-lg">📊</span>
            <span className="font-medium">{finalTitle}</span>
            <Tag color="blue">表格</Tag>
          </div>
          <div className="flex items-center space-x-2">
            {uqmConfig && (
                <Button
                size="small"
                icon={<ReloadOutlined />}
                onClick={handleRefresh}
                loading={loading}
                title="刷新数据"
                />
            )}
            {onEdit && (
              <Button
                size="small"
                icon={<SettingOutlined />}
                onClick={onEdit}
                title="编辑配置"
              />
            )}
          </div>
        </div>
      }
      bodyStyle={{ padding: 0 }}
    >
      <div className="p-4">
        <div className="mb-2">
          {tableDescription && <p className="text-gray-600 text-sm mb-2">{tableDescription}</p>}
          {lastUpdate && uqmConfig && (
            <p className="text-xs text-gray-400">
              最后更新: {lastUpdate.toLocaleString()}
            </p>
          )}
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-48">
            <Spin />
          </div>
        ) : error ? (
          <Alert message={`加载失败: ${error}`} type="error" showIcon />
        ) : (
          <Table
            title={antdTableTitle}
            dataSource={dataSource}
            columns={columns}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              size: 'small',
            }}
            size="small"
            scroll={{ x: 'max-content' }}
            rowKey={(record, index) => {
              const possibleKeys = ['id', 'employee_id', 'user_id', 'record_id'];
              for (const key of possibleKeys) {
                if (record[key] !== undefined) {
                  return record[key];
                }
              }
              return index || 0;
            }}
          />
        )}
      </div>
    </Card>
  );
};

export default TableBlock; 