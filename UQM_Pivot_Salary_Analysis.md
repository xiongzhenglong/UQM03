# UQM Pivot 用例 - 人力资源薪资分析

## 场景描述
人力资源部门需要分析不同部门和职位员工的平均薪资水平，以进行薪酬结构优化和市场比较。最终表格的行是部门名称，列是职位，单元格是对应的平均薪资。

## 数据透视需求
- **行（index）**: 部门名称 (departments.name)
- **列（columns）**: 职位 (employees.job_title)  
- **值（values）**: 平均薪资 (AVG(employees.salary))
- **聚合函数**: mean (平均值)

## UQM 查询配置

### 基础版本 - 简单薪资透视分析

```json
{
  "uqm": {
    "metadata": {
      "name": "DepartmentJobTitleSalaryPivotAnalysis",
      "description": "人力资源部门薪资分析：按部门和职位透视员工平均薪资，用于薪酬结构优化和市场比较。行为部门名称，列为职位，值为平均薪资。",
      "version": "1.0",
      "author": "HR Analytics Team",
      "tags": ["hr_analysis", "salary_analysis", "pivot_table", "compensation"]
    },
    "steps": [
      {
        "name": "get_employee_department_salary_data",
        "type": "query",
        "config": {
          "data_source": "employees",
          "joins": [
            {
              "type": "INNER",
              "table": "departments",
              "on": "employees.department_id = departments.department_id"
            }
          ],
          "dimensions": [
            {"expression": "departments.name", "alias": "department_name"},
            {"expression": "employees.job_title", "alias": "job_title"},
            {"expression": "employees.salary", "alias": "salary"}
          ],
          "filters": [
            {
              "field": "employees.is_active",
              "operator": "=",
              "value": true
            }
          ],
          "order_by": [
            {"field": "departments.name", "direction": "ASC"},
            {"field": "employees.job_title", "direction": "ASC"}
          ]
        }
      },
      {
        "name": "pivot_salary_by_department_and_job",
        "type": "pivot",
        "config": {
          "source": "get_employee_department_salary_data",
          "index": "department_name",
          "columns": "job_title", 
          "values": "salary",
          "agg_func": "mean",
          "fill_value": 0,
          "missing_strategy": "drop"
        }
      }
    ],
    "output": "pivot_salary_by_department_and_job"
  },
  "parameters": {},
  "options": {
    "cache_enabled": true,
    "timeout": 300
  }
}
```

### 高级版本 - 带统计信息的薪资透视分析

```json
{
  "uqm": {
    "metadata": {
      "name": "ComprehensiveSalaryPivotAnalysis",
      "description": "全面的人力资源薪资分析：包含平均薪资、最高薪资、最低薪资和员工数量的多维度透视分析。",
      "version": "2.0", 
      "author": "HR Analytics Team",
      "tags": ["hr_analysis", "salary_analysis", "pivot_table", "comprehensive_stats"]
    },
    "steps": [
      {
        "name": "get_detailed_employee_salary_data",
        "type": "query",
        "config": {
          "data_source": "employees",
          "joins": [
            {
              "type": "INNER",
              "table": "departments", 
              "on": "employees.department_id = departments.department_id"
            }
          ],
          "dimensions": [
            {"expression": "departments.name", "alias": "department_name"},
            {"expression": "employees.job_title", "alias": "job_title"},
            {"expression": "employees.salary", "alias": "salary"},
            {"expression": "employees.employee_id", "alias": "employee_id"}
          ],
          "filters": [
            {
              "field": "employees.is_active",
              "operator": "=", 
              "value": true
            }
          ]
        }
      },
      {
        "name": "pivot_average_salary",
        "type": "pivot",
        "config": {
          "source": "get_detailed_employee_salary_data",
          "index": "department_name",
          "columns": "job_title",
          "values": "salary", 
          "agg_func": "mean",
          "fill_value": 0,
          "missing_strategy": "drop",
          "column_prefix": "avg_salary_"
        }
      },
      {
        "name": "pivot_max_salary",
        "type": "pivot",
        "config": {
          "source": "get_detailed_employee_salary_data",
          "index": "department_name",
          "columns": "job_title",
          "values": "salary",
          "agg_func": "max", 
          "fill_value": 0,
          "missing_strategy": "drop",
          "column_prefix": "max_salary_"
        }
      },
      {
        "name": "pivot_min_salary",
        "type": "pivot", 
        "config": {
          "source": "get_detailed_employee_salary_data",
          "index": "department_name",
          "columns": "job_title",
          "values": "salary",
          "agg_func": "min",
          "fill_value": 0,
          "missing_strategy": "drop", 
          "column_prefix": "min_salary_"
        }
      },
      {
        "name": "pivot_employee_count",
        "type": "pivot",
        "config": {
          "source": "get_detailed_employee_salary_data", 
          "index": "department_name",
          "columns": "job_title",
          "values": "employee_id",
          "agg_func": "count",
          "fill_value": 0,
          "missing_strategy": "drop",
          "column_prefix": "count_"
        }
      }
    ],
    "output": "pivot_average_salary"
  },
  "parameters": {},
  "options": {
    "cache_enabled": true,
    "timeout": 300
  }
}
```

### 参数化版本 - 可自定义部门和职位的薪资分析

```json
{
  "uqm": {
    "metadata": {
      "name": "AdvancedParameterizedSalaryPivotAnalysis",
      "description": "高级参数化薪资透视分析，支持部门和职位过滤。通过直接参数替换实现条件过滤。",
      "version": "2.0",
      "author": "HR Analytics Team",
      "tags": ["hr_analysis", "salary_analysis", "pivot_table", "parameterized", "advanced"]
    },
    "parameters": [
      {
        "name": "target_departments",
        "type": "array",
        "description": "要分析的目标部门列表",
        "required": false,
        "default": ["信息技术部", "销售部", "人力资源部"]
      },
      {
        "name": "min_salary_threshold",
        "type": "number",
        "description": "最低薪资阈值，用于过滤薪资数据",
        "required": false,
        "default": 15000
      }
    ],
    "steps": [
      {
        "name": "get_filtered_employee_salary_data",
        "type": "query",
        "config": {
          "data_source": "employees",
          "joins": [
            {
              "type": "INNER",
              "table": "departments",
              "on": "employees.department_id = departments.department_id"
            }
          ],
          "dimensions": [
            {"expression": "departments.name", "alias": "department_name"},
            {"expression": "employees.job_title", "alias": "job_title"},
            {"expression": "employees.salary", "alias": "salary"}
          ],
          "filters": [
            {
              "field": "employees.is_active",
              "operator": "=",
              "value": true
            },
            {
              "field": "employees.salary",
              "operator": ">=", 
              "value": "$min_salary_threshold"
            },
            {
              "field": "departments.name",
              "operator": "IN",
              "value": "$target_departments"
            }
          ]
        }
      },
      {
        "name": "pivot_salary_analysis",
        "type": "pivot",
        "config": {
          "source": "get_filtered_employee_salary_data",
          "index": "department_name",
          "columns": "job_title",
          "values": "salary",
          "agg_func": "mean",
          "fill_value": 0,
          "missing_strategy": "drop"
        }
      }
    ],
    "output": "pivot_salary_analysis"
  },
  "parameters": {
    "target_departments": ["信息技术部", "销售部", "人力资源部"],
    "min_salary_threshold": 15000
  },
  "options": {
    "cache_enabled": true,
    "timeout": 300
  }
}
```

## 条件过滤器版本 - 智能参数化薪资分析

### 功能特点
✨ **智能过滤器**: 参数未传入时自动忽略相关过滤器
✨ **灵活参数**: 支持部分参数传入，无需传入所有参数
✨ **多种条件**: 支持参数存在性检查、非空检查、表达式条件等
✨ **向下兼容**: 与现有UQM系统完全兼容

### 条件过滤器语法说明

#### 1. 基础条件类型

**parameter_exists**: 检查参数是否存在
```json
{
  "field": "employees.job_title",
  "operator": "=",
  "value": "$job_title",
  "conditional": {
    "type": "parameter_exists",
    "parameter": "job_title"
  }
}
```

**parameter_not_empty**: 检查参数是否非空
```json
{
  "field": "departments.name",
  "operator": "IN",
  "value": "$target_departments",
  "conditional": {
    "type": "parameter_not_empty",
    "parameter": "target_departments",
    "empty_values": [null, []]
  }
}
```

**expression**: 自定义条件表达式
```json
{
  "field": "employees.salary",
  "operator": ">=",
  "value": "$min_salary",
  "conditional": {
    "type": "expression",
    "expression": "$min_salary != null && $min_salary > 0"
  }
}
```

### 智能条件过滤器配置

```json
{
  "uqm": {
    "metadata": {
      "name": "SmartConditionalSalaryPivotAnalysis",
      "description": "智能条件过滤器薪资透视分析，未传入的参数自动忽略相关过滤器，实现真正的灵活参数化查询。",
      "version": "5.0",
      "author": "HR Analytics Team",
      "tags": ["hr_analysis", "salary_analysis", "pivot_table", "conditional_filtering", "smart_parameters"]
    },
    "parameters": [
      {
        "name": "target_departments",
        "type": "array",
        "description": "要分析的目标部门列表，未提供时分析所有部门",
        "required": false,
        "default": null
      },
      {
        "name": "target_job_titles",
        "type": "array",
        "description": "要分析的目标职位列表，未提供时分析所有职位",
        "required": false,
        "default": null
      },
      {
        "name": "min_salary",
        "type": "number",
        "description": "最低薪资阈值，未提供或为0时不限制",
        "required": false,
        "default": null
      },
      {
        "name": "max_salary",
        "type": "number",
        "description": "最高薪资阈值，未提供或为0时不限制",
        "required": false,
        "default": null
      },
      {
        "name": "hire_date_from",
        "type": "string",
        "description": "入职日期起始，格式 YYYY-MM-DD",
        "required": false,
        "default": null
      },
      {
        "name": "hire_date_to",
        "type": "string",
        "description": "入职日期结束，格式 YYYY-MM-DD",
        "required": false,
        "default": null
      }
    ],
    "steps": [
      {
        "name": "get_smart_filtered_employee_data",
        "type": "query",
        "config": {
          "data_source": "employees",
          "joins": [
            {
              "type": "INNER",
              "table": "departments",
              "on": "employees.department_id = departments.department_id"
            }
          ],
          "dimensions": [
            {"expression": "departments.name", "alias": "department_name"},
            {"expression": "employees.job_title", "alias": "job_title"},
            {"expression": "employees.salary", "alias": "salary"}
          ],
          "filters": [
            {
              "field": "employees.is_active",
              "operator": "=",
              "value": true
            },
            {
              "field": "departments.name",
              "operator": "IN",
              "value": "$target_departments",
              "conditional": {
                "type": "parameter_not_empty",
                "parameter": "target_departments",
                "empty_values": [null, []]
              }
            },
            {
              "field": "employees.job_title",
              "operator": "IN",
              "value": "$target_job_titles",
              "conditional": {
                "type": "parameter_not_empty",
                "parameter": "target_job_titles",
                "empty_values": [null, []]
              }
            },
            {
              "field": "employees.salary",
              "operator": ">=",
              "value": "$min_salary",
              "conditional": {
                "type": "parameter_not_empty",
                "parameter": "min_salary",
                "empty_values": [null, 0]
              }
            },
            {
              "field": "employees.salary",
              "operator": "<=",
              "value": "$max_salary",
              "conditional": {
                "type": "parameter_not_empty",
                "parameter": "max_salary",
                "empty_values": [null, 0]
              }
            },
            {
              "field": "employees.hire_date",
              "operator": ">=",
              "value": "$hire_date_from",
              "conditional": {
                "type": "parameter_not_empty",
                "parameter": "hire_date_from",
                "empty_values": [null, ""]
              }
            },
            {
              "field": "employees.hire_date",
              "operator": "<=",
              "value": "$hire_date_to",
              "conditional": {
                "type": "parameter_not_empty",
                "parameter": "hire_date_to",
                "empty_values": [null, ""]
              }
            }
          ]
        }
      },
      {
        "name": "pivot_smart_salary_analysis",
        "type": "pivot",
        "config": {
          "source": "get_smart_filtered_employee_data",
          "index": "department_name",
          "columns": "job_title",
          "values": "salary",
          "agg_func": "mean",
          "fill_value": 0,
          "missing_strategy": "drop"
        }
      }
    ],
    "output": "pivot_smart_salary_analysis"
  },
  "parameters": {},
  "options": {
    "cache_enabled": true,
    "timeout": 300
  }
}
```

### 使用示例

#### 场景1：只传入部门参数
```json
{
  "parameters": {
    "target_departments": ["信息技术部", "销售部"]
  }
}
```
**效果**: 只应用部门过滤器，其他条件自动忽略

#### 场景2：传入部门和薪资范围
```json
{
  "parameters": {
    "target_departments": ["信息技术部"],
    "min_salary": 15000,
    "max_salary": 50000
  }
}
```
**效果**: 应用部门和薪资范围过滤器

#### 场景3：只传入时间范围
```json
{
  "parameters": {
    "hire_date_from": "2022-01-01",
    "hire_date_to": "2024-12-31"
  }
}
```
**效果**: 只应用时间范围过滤器

#### 场景4：不传入任何参数
```json
{
  "parameters": {}
}
```
**效果**: 只保留基础的 is_active=true 过滤器，分析所有活跃员工

### 技术优势

#### 1. 智能过滤
- **自动跳过**: 未提供的参数对应的过滤器自动跳过
- **条件检查**: 支持多种条件检查类型
- **表达式支持**: 支持复杂的条件表达式

#### 2. 用户友好
- **部分参数**: 用户只需提供关心的参数
- **向下兼容**: 与现有系统完全兼容
- **错误容忍**: 参数错误不会导致整个查询失败

#### 3. 性能优化
- **减少过滤**: 跳过不需要的过滤器，提高查询性能
- **缓存友好**: 不同参数组合可以有效利用缓存
- **资源节约**: 减少不必要的数据处理

### 实现细节

条件过滤器在参数替换阶段处理：

1. **条件评估**: 检查每个过滤器的条件是否满足
2. **过滤器移除**: 不满足条件的过滤器从配置中移除
3. **参数替换**: 对保留的过滤器进行正常的参数替换
4. **查询执行**: 使用处理后的过滤器执行查询

这种设计保证了：
- ✅ 高性能：不执行不必要的过滤条件
- ✅ 高灵活性：支持任意参数组合
- ✅ 高可靠性：参数错误不影响查询
- ✅ 高可维护性：逻辑清晰，易于扩展

## 预期输出示例

### 基础版本输出示例
```json
{
  "success": true,
  "data": [
    {
      "department_name": "人力资源部",
      "HR经理": 25000.00,
      "人事专员": 12000.00,
      "销售代表": 0,
      "软件工程师": 0,
      "IT总监": 0
    },
    {
      "department_name": "信息技术部", 
      "HR经理": 0,
      "人事专员": 0,
      "销售代表": 0,
      "软件工程师": 20000.00,
      "IT总监": 35000.00,
      "高级软件工程师": 22000.00
    },
    {
      "department_name": "销售部",
      "HR经理": 0,
      "人事专员": 0,
      "销售代表": 15000.00,
      "软件工程师": 0, 
      "IT总监": 0,
      "销售总监": 38000.00
    },
    {
      "department_name": "财务部",
      "高级财务分析师": 28000.00
    },
    {
      "department_name": "市场营销部",
      "市场专员": 14000.00
    },
    {
      "department_name": "欧洲销售部",
      "欧洲区销售经理": 42000.00,
      "销售助理": 16000.00
    },
    {
      "department_name": "研发中心",
      "运营经理": 31000.00
    }
  ],
  "metadata": {
    "name": "DepartmentJobTitleSalaryPivotAnalysis",
    "description": "人力资源部门薪资分析：按部门和职位透视员工平均薪资，用于薪酬结构优化和市场比较。",
    "version": "1.0",
    "author": "HR Analytics Team",
    "tags": ["hr_analysis", "salary_analysis", "pivot_table", "compensation"]
  },
  "execution_info": {
    "total_time": 0.0856,
    "row_count": 7,
    "cache_hit": false,
    "steps_executed": 2
  },
  "step_results": [
    {
      "step_name": "get_employee_department_salary_data",
      "step_type": "query",
      "status": "completed",
      "row_count": 12,
      "execution_time": 0.0453
    },
    {
      "step_name": "pivot_salary_by_department_and_job", 
      "step_type": "pivot",
      "status": "completed",
      "row_count": 7,
      "execution_time": 0.0403
    }
  ]
}
```

## 业务价值与应用场景

### 1. 薪酬结构分析
- **横向比较**：同一职位在不同部门的薪资差异
- **纵向比较**：同一部门内不同职位的薪资层次
- **薪酬带宽**：识别薪资范围和分布情况

### 2. 市场竞争力评估
- **基准比较**：与行业薪酬标准对比
- **人才保留**：识别薪酬偏低的关键岗位
- **招聘定价**：为新岗位制定合理薪酬标准

### 3. 组织效率优化
- **成本控制**：分析人工成本分布
- **资源配置**：优化不同部门的薪酬投入
- **绩效关联**：结合绩效数据分析薪酬合理性

### 4. 决策支持
- **预算规划**：年度薪酬预算制定
- **晋升调薪**：职业发展路径薪酬规划
- **组织调整**：部门重组时的薪酬影响评估

## 技术特点

### Pivot 步骤核心配置说明
- **source**: 数据源，来自前一步骤的查询结果
- **index**: 透视表的行索引，这里是部门名称
- **columns**: 透视表的列，这里是职位
- **values**: 要聚合的值，这里是薪资
- **agg_func**: 聚合函数，支持 mean、sum、count、min、max 等
- **fill_value**: 空值填充策略，0 表示没有该职位的部门显示为 0
- **missing_strategy**: 缺失值处理策略，drop/fill/keep

### 扩展功能
- **多值透视**: 可以同时透视多个指标（平均薪资、最高薪资、员工数量等）
- **参数化查询**: 支持动态过滤条件，提高查询灵活性
- **结果格式化**: 支持列名前缀/后缀、排序等输出定制

这个用例展示了 UQM 系统 pivot 步骤在人力资源分析中的实际应用，为 HR 部门提供了直观、灵活的薪酬数据透视分析能力。
