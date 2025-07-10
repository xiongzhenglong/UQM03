/**
 * 生成 Ant Design 表格配置的渲染函数模板
 * @param allFields 所有可用字段
 * @param selectedFields 用户意图选择的字段（可选）
 * @returns {string} 渲染函数代码字符串
 */
export const tableTemplate = (allFields: string[], selectedFields?: string[]): string => {
  const fieldsToUse = selectedFields && selectedFields.length > 0 ? selectedFields : allFields;
  
  const columns = fieldsToUse.map(field => `{
      title: '${field}',
      dataIndex: '${field}',
      key: '${field}',
      sorter: (a, b) => typeof a['${field}'] === 'number' && typeof b['${field}'] === 'number' ? a['${field}'] - b['${field}'] : String(a['${field}']).localeCompare(String(b['${field}'])),
    }`).join(',\n    ');

  return `(data) => {
  // AI-generated function to create a table configuration
  return {
    type: 'table',
    config: {
      columns: [
        ${columns}
      ],
      dataSource: data,
      pagination: { pageSize: 10 },
      bordered: true,
      size: 'small',
    }
  };
}`;
};

/**
 * 生成 ECharts 柱状图配置的渲染函数模板
 * @param allFields 所有可用字段
 * @param selectedFields 用户意图选择的字段（可选）
 * @returns {string} 渲染函数代码字符串
 */
export const barChartTemplate = (allFields: string[], selectedFields?: string[]): string => {
  // 简单地选择第一个字符串类型的字段作为 x 轴，第一个数字类型的字段作为 y 轴
  const xAxisField = allFields.find(f => typeof (allFields[0] as any)[f] === 'string') || allFields[0];
  const yAxisField = allFields.find(f => typeof (allFields[0] as any)[f] === 'number') || allFields[1];

  return `(data: Array<{[key: string]: any}>) => {
  // AI-generated function to create a bar chart configuration
  const labels = [...new Set(data.map(item => item['${xAxisField}']))];
  const values = labels.map(label => {
    const filteredData = data.filter(item => item['${xAxisField}'] === label);
    return filteredData.reduce((sum, item) => sum + (Number(item['${yAxisField}']) || 0), 0);
  });

  return {
    type: 'chart',
    config: {
      tooltip: {},
      xAxis: {
        type: 'category',
        data: labels,
      },
      yAxis: {
        type: 'value',
      },
      series: [{
        data: values,
        type: 'bar',
        label: {
          show: true,
          position: 'top'
        }
      }],
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
    }
  };
}`;
}; 