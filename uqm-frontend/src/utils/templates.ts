/**
 * 生成 Ant Design 表格配置的渲染函数模板
 * @param allFields 所有可用字段
 * @param selectedFields 用户意图选择的字段（可选）
 * @returns {string} 渲染函数代码字符串
 */
export const tableTemplate = (allFields: string[], selectedFields?: string[]): string => {
  const fieldsToUse = selectedFields && selectedFields.length > 0 ? selectedFields : allFields;
  
  // 字段显示名称映射
  const fieldDisplayNames: { [key: string]: string } = {
    'employee_id': '员工ID',
    'first_name': '姓名',
    'last_name': '姓',
    'email': '邮箱',
    'phone_number': '电话',
    'hire_date': '入职日期',
    'job_title': '职位',
    'salary': '薪资',
    'department_name': '部门',
    'is_active': '在职状态'
  };

  // 智能生成列配置
  const columns = fieldsToUse.map(field => {
    const displayName = fieldDisplayNames[field] || field;
    let columnConfig = `{
      title: '${displayName}',
      dataIndex: '${field}',
      key: '${field}'`;

    // 为数字字段添加排序
    if (field.includes('salary') || field.includes('id')) {
      columnConfig += `,
      sorter: (a, b) => ${field.includes('salary') ? 'parseFloat(a.salary) - parseFloat(b.salary)' : 'a.employee_id - b.employee_id'}`;
    }

    // 为日期字段添加排序
    if (field.includes('date')) {
      columnConfig += `,
      sorter: (a, b) => new Date(a.hire_date) - new Date(b.hire_date)`;
    }

    // 特殊渲染逻辑
    if (field === 'first_name') {
      columnConfig += `,
      render: (text, record) => \`\${record.first_name} \${record.last_name}\``;
    } else if (field === 'salary') {
      columnConfig += `,
      render: (text) => \`¥\${parseFloat(text).toLocaleString()}\``;
    } else if (field === 'hire_date') {
      columnConfig += `,
      render: (text) => new Date(text).toLocaleDateString('zh-CN')`;
    }

    columnConfig += `
    }`;
    return columnConfig;
  }).join(',\n    ');

  return `(data) => {
  // AI-generated function to create a table configuration
  return {
    type: 'table',
    config: {
      columns: [
        ${columns}
      ],
      dataSource: data,
      pagination: { pageSize: 10, showSizeChanger: true, showQuickJumper: true },
      bordered: true,
      size: 'small',
      showHeader: true,
      scroll: { x: 'max-content' }
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
  // 检测是否有薪资字段
  const hasSalary = allFields.includes('salary');
  const hasName = allFields.includes('first_name') && allFields.includes('last_name');
  
  if (hasSalary && hasName) {
    // 薪资分布柱状图
    return `(data) => {
  // AI-generated function to create a bar chart configuration
  const salaryData = data.map(item => ({
    name: \`\${item.first_name} \${item.last_name}\`,
    salary: parseFloat(item.salary)
  }));
  
  // 按薪资排序
  salaryData.sort((a, b) => b.salary - a.salary);
  
  const names = salaryData.map(item => item.name);
  const salaries = salaryData.map(item => item.salary);

  return {
    type: 'chart',
    config: {
      title: {
        text: '员工薪资分布',
        subtext: '按薪资从高到低排序',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        formatter: function(params) {
          return \`\${params[0].name}<br/>薪资: ¥\${params[0].value.toLocaleString()}\`;
        }
      },
      xAxis: {
        type: 'category',
        data: names,
        axisLabel: {
          rotate: 45,
          fontSize: 10
        }
      },
      yAxis: {
        type: 'value',
        name: '薪资 (元)',
        axisLabel: {
          formatter: '¥{value}'
        }
      },
      series: [{
        name: '薪资',
        type: 'bar',
        data: salaries,
        itemStyle: {
          color: function(params) {
            const colors = ['#91cc75', '#fac858', '#ee6666'];
            const maxSalary = Math.max(...salaries);
            const ratio = salaries[params.dataIndex] / maxSalary;
            if (ratio > 0.8) return colors[2];
            if (ratio > 0.5) return colors[1];
            return colors[0];
          }
        },
        label: {
          show: true,
          position: 'top',
          formatter: '¥{c}'
        }
      }],
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      }
    }
  };
}`;
  } else {
    // 通用柱状图模板
    const xAxisField = allFields.find(f => typeof (allFields[0] as any)[f] === 'string') || allFields[0];
    const yAxisField = allFields.find(f => typeof (allFields[0] as any)[f] === 'number') || allFields[1];

    return `(data) => {
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
  }
};

/**
 * 生成饼图配置的渲染函数模板
 */
export const pieChartTemplate = (allFields: string[], selectedFields?: string[]): string => {
  const categoryField = allFields.find(f => f.includes('department') || f.includes('title')) || allFields[0];
  
  return `(data) => {
  // AI-generated function to create a pie chart configuration
  const categoryCount = {};
  data.forEach(item => {
    const category = item['${categoryField}'];
    categoryCount[category] = (categoryCount[category] || 0) + 1;
  });
  
  const pieData = Object.entries(categoryCount).map(([name, value]) => ({
    name,
    value
  }));

  return {
    type: 'chart',
    config: {
      title: {
        text: '${categoryField} 分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [{
        name: '${categoryField}',
        type: 'pie',
        radius: '50%',
        data: pieData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    }
  };
}`;
};

/**
 * 生成折线图配置的渲染函数模板
 */
export const lineChartTemplate = (allFields: string[], selectedFields?: string[]): string => {
  const hasDate = allFields.includes('hire_date');
  const hasSalary = allFields.includes('salary');
  
  if (hasDate && hasSalary) {
    return `(data) => {
  // AI-generated function to create a line chart configuration
  const sortedData = data.sort((a, b) => new Date(a.hire_date) - new Date(b.hire_date));
  
  const dates = sortedData.map(item => new Date(item.hire_date).toLocaleDateString('zh-CN'));
  const salaries = sortedData.map(item => parseFloat(item.salary));

  return {
    type: 'chart',
    config: {
      title: {
        text: '薪资趋势',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: dates
      },
      yAxis: {
        type: 'value',
        name: '薪资 (元)'
      },
      series: [{
        name: '薪资',
        type: 'line',
        data: salaries,
        smooth: true,
        markPoint: {
          data: [
            { type: 'max', name: '最高薪资' },
            { type: 'min', name: '最低薪资' }
          ]
        }
      }],
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      }
    }
  };
}`;
  } else {
    return `(data) => {
  // Generic line chart
  const xData = data.map((item, index) => index + 1);
  const yData = data.map(item => Object.values(item)[0]);

  return {
    type: 'chart',
    config: {
      xAxis: {
        type: 'category',
        data: xData
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        data: yData,
        type: 'line'
      }],
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      }
    }
  };
}`;
  }
}; 