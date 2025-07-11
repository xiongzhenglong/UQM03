// 演示用的 UQM 查询
export const demoUqmQuery = {
  "uqm": {
    "metadata": {
      "name": "get_it_department_active_employees",
      "description": "查询并返回信息技术部所有在职状态员工的详细信息。"
    },
    "steps": [
      {
        "name": "filter_it_department_employees",
        "type": "query",
        "config": {
          "data_source": "employees e",
          "dimensions": [
            {
              "expression": "e.employee_id",
              "alias": "employee_id"
            },
            {
              "expression": "e.first_name",
              "alias": "first_name"
            },
            {
              "expression": "e.last_name",
              "alias": "last_name"
            },
            {
              "expression": "e.email",
              "alias": "email"
            },
            {
              "expression": "e.phone_number",
              "alias": "phone_number"
            },
            {
              "expression": "e.hire_date",
              "alias": "hire_date"
            },
            {
              "expression": "e.job_title",
              "alias": "job_title"
            },
            {
              "expression": "e.salary",
              "alias": "salary"
            },
            {
              "expression": "d.name",
              "alias": "department_name"
            }
          ],
          "joins": [
            {
              "type": "inner",
              "target": "departments d",
              "on": {
                "left": "e.department_id",
                "right": "d.department_id"
              }
            }
          ],
          "filters": [
            {
              "logic": "AND",
              "conditions": [
                {
                  "field": "d.name",
                  "operator": "=",
                  "value": "信息技术部"
                },
                {
                  "field": "e.is_active",
                  "operator": "=",
                  "value": true
                }
              ]
            }
          ]
        }
      }
    ],
    "output": "filter_it_department_employees"
  },
  "parameters": {},
  "options": {
    "dialect": "mysql",
    "page": 1,
    "page_size": 3,
    "pagination_target_step": "filter_it_department_employees"
  }
};

// 模拟的查询返回数据
export const demoQueryResult = [
  {
    "employee_id": 1,
    "first_name": "张",
    "last_name": "伟",
    "email": "zhang.wei@example.com",
    "phone_number": "13800138001",
    "hire_date": "2022-01-10",
    "job_title": "IT总监",
    "salary": "35000.00",
    "department_name": "信息技术部"
  },
  {
    "employee_id": 3,
    "first_name": "李",
    "last_name": "强",
    "email": "li.qiang@example.com",
    "phone_number": "13800138003",
    "hire_date": "2022-02-20",
    "job_title": "软件工程师",
    "salary": "18000.00",
    "department_name": "信息技术部"
  },
  {
    "employee_id": 10,
    "first_name": "Emily",
    "last_name": "Jones",
    "email": "emily.jones@example.com",
    "phone_number": "13700137009",
    "hire_date": "2024-04-08",
    "job_title": "高级软件工程师",
    "salary": "22000.00",
    "department_name": "信息技术部"
  }
];

// 预设的表格渲染函数代码
export const demoTableCode = `(data) => {
  // AI-generated function to create a table configuration
  return {
    type: 'table',
    config: {
      columns: [
        {
          title: '员工ID',
          dataIndex: 'employee_id',
          key: 'employee_id',
          sorter: (a, b) => a.employee_id - b.employee_id,
        },
        {
          title: '姓名',
          dataIndex: 'first_name',
          key: 'first_name',
          render: (text, record) => \`\${record.first_name} \${record.last_name}\`,
        },
        {
          title: '邮箱',
          dataIndex: 'email',
          key: 'email',
        },
        {
          title: '职位',
          dataIndex: 'job_title',
          key: 'job_title',
        },
        {
          title: '薪资',
          dataIndex: 'salary',
          key: 'salary',
          sorter: (a, b) => parseFloat(a.salary) - parseFloat(b.salary),
          render: (text) => \`¥\${parseFloat(text).toLocaleString()}\`,
        },
        {
          title: '入职日期',
          dataIndex: 'hire_date',
          key: 'hire_date',
          sorter: (a, b) => new Date(a.hire_date) - new Date(b.hire_date),
          render: (text) => new Date(text).toLocaleDateString('zh-CN'),
        },
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

// 预设的图表渲染函数代码
export const demoChartCode = `(data) => {
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