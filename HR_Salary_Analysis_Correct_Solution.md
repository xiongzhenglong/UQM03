# 人力资源部门薪资分析 - 正确解决方案

## 需求分析
**目标**：按部门和职位透视员工平均薪资，用于薪酬结构优化和市场比较
- **行**：部门名称
- **列**：职位
- **值**：平均薪资

## 思考规则与设计原则

### 1. 数据流设计原则
```
原始数据 → 预处理(获取基础数据) → 透视转换 → 最终结果
```

### 2. 关键设计决策

#### 决策1：两步骤方案 vs 单步骤方案
- **选择**：两步骤方案
- **原因**：
  - 第一步：获取干净的基础数据（员工、部门、薪资）
  - 第二步：进行透视操作
  - 逻辑清晰，便于调试和维护

#### 决策2：聚合时机选择
- **选择**：在pivot步骤中进行聚合
- **原因**：
  - 第一步只获取原始数据，不进行聚合
  - 避免GROUP BY相关的SQL语法错误
  - 让pivot步骤负责按行/列分组并聚合

#### 决策3：字段处理策略
- **选择**：使用别名统一字段名
- **原因**：
  - 第一步输出的字段名要与第二步输入匹配
  - 使用清晰的别名便于理解

### 3. 错误分析

#### 原始错误方案的问题：
1. **同时使用dimensions和calculated_fields + group_by**
   - 错误：在dimensions中包含原始salary字段，同时使用AVG聚合
   - 后果：SQL GROUP BY语法错误

2. **聚合逻辑混乱**
   - dimensions中有3个字段，但group_by只有2个
   - SQL引擎无法确定如何处理salary字段

## 正确解决方案

```json
{
  "uqm": {
    "metadata": {
      "name": "hr_salary_analysis_by_department_and_job",
      "description": "人力资源部门薪资分析：按部门和职位透视员工平均薪资，用于薪酬结构优化和市场比较",
      "version": "1.0",
      "author": "HR Analytics Team",
      "tags": ["hr_analysis", "salary_analysis", "pivot_analysis"]
    },
    "steps": [
      {
        "name": "get_employee_salary_data",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": [
            {
              "expression": "departments.name",
              "alias": "department_name"
            },
            {
              "expression": "employees.job_title",
              "alias": "job_title"
            },
            {
              "expression": "employees.salary",
              "alias": "salary"
            }
          ],
          "joins": [
            {
              "type": "INNER",
              "table": "departments",
              "on": "employees.department_id = departments.department_id"
            }
          ],
          "filters": [
            {
              "field": "employees.is_active",
              "operator": "=",
              "value": true
            }
          ],
          "order_by": [
            {
              "field": "departments.name",
              "direction": "ASC"
            },
            {
              "field": "employees.job_title",
              "direction": "ASC"
            }
          ]
        }
      },
      {
        "name": "pivot_salary_by_department_and_job",
        "type": "pivot",
        "config": {
          "source": "get_employee_salary_data",
          "group_by": ["department_name"],
          "pivot_column": "job_title",
          "value_column": "salary",
          "aggregation": "avg",
          "column_prefix": "avg_salary_",
          "fill_value": 0
        }
      }
    ],
    "output": "pivot_salary_by_department_and_job"
  },
  "parameters": {},
  "options": {
    "query_timeout": 30000,
    "cache_enabled": true
  }
}
```

## 方案设计思路详解

### 步骤1：get_employee_salary_data
**目的**：获取员工薪资基础数据

**关键点**：
1. **只使用dimensions**：不进行任何聚合操作
2. **表连接**：INNER JOIN确保只获取有部门的员工
3. **字段别名**：统一字段命名，便于后续步骤引用
4. **过滤条件**：只包含在职员工
5. **排序**：按部门和职位排序，便于查看

**输出数据格式**：
```
department_name | job_title     | salary
信息技术部      | IT总监        | 35000.00
信息技术部      | 软件工程师    | 18000.00
人力资源部      | HR经理        | 25000.00
...
```

### 步骤2：pivot_salary_by_department_and_job
**目的**：将数据透视为部门×职位的薪资矩阵

**关键点**：
1. **group_by**: 指定行维度（部门名称）
2. **pivot_column**: 指定列维度（职位）
3. **value_column**: 指定值字段（薪资）
4. **aggregation**: 使用avg计算平均薪资
5. **column_prefix**: 为新列添加前缀便于识别
6. **fill_value**: 空值填充为0

**输出数据格式**：
```
department_name | avg_salary_IT总监 | avg_salary_软件工程师 | avg_salary_HR经理
信息技术部      | 35000.00         | 20000.00             | 0
人力资源部      | 0                | 0                    | 25000.00
...
```

## 核心设计原则总结

### 1. 单一职责原则
- 每个步骤只负责一个明确的功能
- 第一步：数据获取和清洗
- 第二步：数据透视和聚合

### 2. 数据流清晰性
- 步骤间的数据传递格式明确
- 字段命名一致性
- 避免复杂的嵌套逻辑

### 3. SQL兼容性
- 遵循标准SQL语法规则
- 避免GROUP BY语法陷阱
- 确保聚合操作的正确性

### 4. 可维护性
- 使用有意义的步骤名和字段别名
- 添加清晰的描述信息
- 合理的排序和过滤逻辑

## 常见错误避免指南

### ❌ 错误做法
```json
{
  "dimensions": ["dept", "job", "salary"],
  "calculated_fields": [{"name": "avg_sal", "expression": "AVG(salary)"}],
  "group_by": ["dept", "job"]
}
```
**问题**：同时使用dimensions和calculated_fields会导致SQL语法冲突

### ✅ 正确做法
```json
// 方案1：纯维度查询（推荐用于pivot前的数据准备）
{
  "dimensions": [
    {"expression": "dept", "alias": "department"},
    {"expression": "job", "alias": "job_title"},
    {"expression": "salary", "alias": "salary"}
  ]
}

// 方案2：聚合查询（用于直接聚合场景）
{
  "dimensions": ["dept", "job"],
  "calculated_fields": [{"name": "avg_salary", "expression": "AVG(salary)"}],
  "group_by": ["dept", "job"]
}
```

---

**总结**：正确的UQM设计需要清晰的数据流规划、遵循SQL语法规则、保持步骤间的逻辑一致性。透视分析场景特别适合使用两步骤方案：先获取清洁数据，再进行透视聚合。
