# UQM引擎日期函数处理Bug修复报告

## 问题概述

UQM引擎在处理MySQL日期函数时存在严重bug，导致包含日期函数的查询无法正常执行。

## Bug详情

### 1. 日期函数解析失败

**错误信息**: 
```
(1525, "Incorrect DATETIME value: 'DATE_SUB(CURDATE(), INTERVAL 6 MONTH)'")
```

**问题描述**: 
- UQM引擎将MySQL日期函数当作字符串字面值处理
- 没有正确解析和执行日期函数表达式
- 导致SQL查询语法错误

**影响范围**:
- 所有使用日期函数的查询
- `DATE_SUB()`, `DATE_ADD()`, `CURDATE()`, `NOW()` 等函数
- `INTERVAL` 表达式

### 2. 步骤间数据过滤Bug

**问题描述**:
- 在多步骤查询中，对前一步骤结果进行过滤时返回空结果
- 即使使用硬编码日期值，过滤步骤仍然无法正常工作
- 步骤间字段引用和数据传递存在问题

**测试案例**:
```json
{
  "steps": [
    {
      "name": "step1",
      "type": "query", 
      "config": {
        "data_source": "orders o",
        "dimensions": ["o.customer_id"],
        "metrics": [{"name": "o.order_date", "aggregation": "MAX", "alias": "last_order_date"}],
        "group_by": ["o.customer_id"]
      }
    },
    {
      "name": "step2",
      "type": "query",
      "config": {
        "data_source": "step1",
        "dimensions": ["customer_id", "last_order_date"],
        "filters": [{"field": "last_order_date", "operator": "<", "value": "2025-01-03"}]
      }
    }
  ]
}
```

**结果**: step1返回9行数据，step2返回0行数据

## 根本原因分析

### 1. 值处理机制缺陷
- UQM引擎没有区分字面值和SQL函数表达式
- 缺少对MySQL函数的预处理和解析机制
- 直接将函数字符串传递给数据库，导致类型错误

### 2. 步骤数据传递机制问题
- 步骤间字段名映射不正确
- 数据类型在传递过程中可能丢失或转换错误
- 过滤条件在步骤数据上执行失败

## 修复建议

### 1. 日期函数处理修复

在`src/steps/query_step.py`中添加日期函数解析器：

```python
def _process_date_functions(self, value: str) -> str:
    """
    处理日期函数表达式
    """
    if isinstance(value, str):
        # 检测并处理MySQL日期函数
        date_functions = [
            'CURDATE()', 'NOW()', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP'
        ]
        
        # 处理DATE_SUB, DATE_ADD等函数
        if any(func in value.upper() for func in ['DATE_SUB', 'DATE_ADD', 'INTERVAL']):
            # 不要用引号包围，直接作为SQL表达式处理
            return value
            
        # 处理其他日期函数
        for func in date_functions:
            if func in value.upper():
                return value
    
    # 普通字符串值用引号包围
    return f"'{value}'"
```

### 2. 步骤数据过滤修复

在`src/steps/query_step.py`中修复字段引用：

```python
def _build_step_data_query(self, source_data: List[Dict], config: Dict) -> str:
    """
    构建基于步骤数据的查询
    """
    # 确保字段名正确映射
    dimensions = config.get('dimensions', [])
    filters = config.get('filters', [])
    
    # 修复字段引用问题
    for filter_condition in filters:
        field_name = filter_condition['field']
        # 确保字段名在源数据中存在
        if field_name not in source_data[0].keys():
            # 尝试查找别名映射
            field_name = self._resolve_field_alias(field_name, source_data)
            filter_condition['field'] = field_name
    
    # 构建WHERE条件
    where_clause = self._build_where_clause(filters)
    
    return f"SELECT {','.join(dimensions)} FROM step_data WHERE {where_clause}"
```

### 3. 临时解决方案

在修复引擎之前，可以使用以下workaround：

1. **使用硬编码日期值**:
```json
{
  "field": "last_order_date",
  "operator": "<", 
  "value": "2025-01-03"
}
```

2. **合并为单步查询**:
```json
{
  "name": "lapsed_customers_direct",
  "type": "query",
  "config": {
    "data_source": "orders o",
    "dimensions": ["o.customer_id"],
    "metrics": [{"name": "o.order_date", "aggregation": "MAX", "alias": "last_order_date"}],
    "joins": [{"type": "INNER", "table": "customers c", "on": "o.customer_id = c.customer_id"}],
    "group_by": ["o.customer_id"],
    "having": [{"field": "last_order_date", "operator": "<", "value": "2025-01-03"}]
  }
}
```

## 优先级和影响

- **优先级**: 高（影响所有日期相关查询）
- **影响范围**: 核心查询功能
- **修复复杂度**: 中等
- **向后兼容性**: 需要保证

## 测试用例

### 测试用例1: 日期函数支持
```json
{
  "filters": [
    {"field": "created_date", "operator": ">", "value": "DATE_SUB(NOW(), INTERVAL 30 DAY)"},
    {"field": "updated_date", "operator": "<=", "value": "CURDATE()"}
  ]
}
```

### 测试用例2: 步骤间过滤
```json
{
  "steps": [
    {"name": "base_data", "type": "query", "config": {...}},
    {"name": "filtered_data", "type": "query", "config": {"data_source": "base_data", "filters": [...]}}
  ]
}
```

## 建议修复时间线

1. **短期(1-2周)**: 实现日期函数解析修复
2. **中期(2-4周)**: 修复步骤间数据传递机制
3. **长期(1个月)**: 完善测试覆盖率和文档

---

**Bug状态**: 🔴 未修复  
**报告日期**: 2025-07-03  
**影响版本**: 当前所有版本  
**报告人**: GitHub Copilot AI Assistant
