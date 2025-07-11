import React from 'react';
import { Table } from 'antd';
import type { TableProps } from 'antd';
import type { ColumnsType } from 'antd/es/table';

interface TableRendererProps {
  config: any;
  dataSource: any[];
}

const TableRenderer: React.FC<TableRendererProps> = ({ config, dataSource }) => {
  const { title, ...restConfig } = config || {};

  let finalDataSource = dataSource;
  let finalColumns: ColumnsType<any> | undefined = restConfig.columns;

  // 如果 config 是图表类型，则从中转换数据
  if (config && config.series && config.xAxis && config.xAxis.data) {
    finalColumns = [
      {
        title: config.xAxis.name || 'Category',
        dataIndex: 'category',
        key: 'category',
      },
      {
        title: config.yAxis.name || 'Value',
        dataIndex: 'value',
        key: 'value',
      },
    ];
    finalDataSource = config.xAxis.data.map((item: any, index: number) => ({
      key: `${item}-${index}`, // 确保 key 的唯一性
      category: item,
      value: config.series[0].data[index],
    }));
  }

  let titleNode: React.ReactNode = null;
  if (title) {
    if (typeof title === 'string') {
      titleNode = <h4 style={{ margin: 0 }}>{title}</h4>;
    } else if (typeof title === 'object' && title.text) {
      titleNode = <h4 style={{ margin: 0 }}>{title.text}</h4>;
    }
  }

  const tableProps: TableProps<any> = {
    ...restConfig,
    columns: finalColumns,
    title: titleNode ? () => titleNode : undefined,
    dataSource: finalDataSource,
    rowKey: (record: any) => {
      const possibleKeys = ['id', 'key', 'employee_id', 'user_id'];
      for (const key of possibleKeys) {
        if (record[key] !== undefined && record[key] !== null) {
          return record[key];
        }
      }
      return JSON.stringify(record); 
    },
    scroll: { x: 'max-content' },
    pagination: config.pagination !== false ? {
        pageSize: 10, 
        showSizeChanger: true, 
        ...config.pagination
    } : false,
  };

  return (
    <div className="w-full overflow-x-auto p-4 bg-white rounded-lg shadow">
      <Table {...tableProps} />
    </div>
  );
};

export default TableRenderer; 