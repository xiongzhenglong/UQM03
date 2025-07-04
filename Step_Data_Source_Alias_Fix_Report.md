# 步骤数据源别名支持修复报告

## 问题描述

在处理多步骤查询时，系统无法正确识别带别名的步骤引用，导致查询执行失败。

### 具体错误
- **错误信息**: `Table 'uqm_db.latest_order_date' doesn't exist`
- **问题场景**: 当第二个步骤的`data_source`使用`"latest_order_date lod"`格式时，系统无法识别`latest_order_date`是前面步骤的输出结果

### 问题分析

1. **第一步骤**: `latest_order_date` 执行成功，产生数据存储在`step_data`中
2. **第二步骤**: `data_source: "latest_order_date lod"` 试图引用第一步的结果并使用别名`lod`
3. **系统错误**: `_is_step_data_source`方法只检查完整字符串匹配，无法识别带别名的步骤引用

## 根本原因

在`src/steps/query_step.py`中的`_is_step_data_source`方法存在问题：

```python
def _is_step_data_source(self, data_source: str, context: Dict[str, Any]) -> bool:
    step_data = context.get("step_data", {})
    return data_source in step_data  # 无法处理 "step_name alias" 格式
```

## 解决方案

### 1. 修复步骤数据源识别逻辑

修改`_is_step_data_source`方法，支持解析带别名的步骤引用：

```python
def _is_step_data_source(self, data_source: str, context: Dict[str, Any]) -> bool:
    """
    检查数据源是否是步骤数据
    
    Args:
        data_source: 数据源名称（可能包含别名，如 "step_name alias"）
        context: 执行上下文
        
    Returns:
        是否是步骤数据源
    """
    step_data = context.get("step_data", {})
    
    # 处理带别名的步骤引用，如 "latest_order_date lod"
    # 提取步骤名称（第一个单词）
    step_name = data_source.split()[0]
    
    return step_name in step_data
```

### 2. 修复步骤数据获取逻辑

修改`_execute_with_step_data`方法，正确提取步骤名称：

```python
async def _execute_with_step_data(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    使用步骤数据执行查询
    
    Args:
        context: 执行上下文
        
    Returns:
        查询结果
    """
    data_source = self.config["data_source"]
    get_source_data = context["get_source_data"]
    
    # 处理带别名的步骤引用，如 "latest_order_date lod"
    # 提取步骤名称（第一个单词）
    step_name = data_source.split()[0]
    
    # 获取源数据
    source_data = get_source_data(step_name)
    
    # 对源数据进行处理
    result = self._process_step_data(source_data)
    
    return result
```

## 修复效果

### 修复前
- 系统将`"latest_order_date lod"`当作数据库表名处理
- 导致SQL查询失败：`Table 'uqm_db.latest_order_date' doesn't exist`

### 修复后
- 系统正确识别`latest_order_date`为步骤名称
- 成功从`step_data`中获取前一步骤的结果
- 支持在后续处理中使用别名`lod`

## 支持的语法格式

修复后系统支持以下数据源引用格式：

1. **简单步骤引用**: `"step_name"`
2. **带别名的步骤引用**: `"step_name alias"`
3. **数据库表引用**: `"table_name"`
4. **带别名的数据库表引用**: `"table_name alias"`

## 测试用例

以下是修复后支持的典型用例：

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
        "data_source": "step1 s1",  // 使用步骤引用+别名
        "dimensions": ["s1.customer_id", "s1.last_order_date"],
        "joins": [{"type": "INNER", "table": "customers c", "on": "s1.customer_id = c.customer_id"}]
      }
    }
  ]
}
```

## 向后兼容性

此修复完全向后兼容，不会影响现有查询的正常运行：

- 原有的简单步骤引用（如`"step_name"`）继续正常工作
- 数据库表引用保持不变
- 只是新增了对带别名步骤引用的支持

## 结论

通过修复`_is_step_data_source`和`_execute_with_step_data`方法，系统现在能够正确处理带别名的步骤引用，解决了多步骤查询中的数据源识别问题。这个修复使得UQM系统的多步骤查询功能更加完善和实用。

**修复状态**: ✅ 已完成
**影响范围**: 多步骤查询功能
**风险等级**: 低（向后兼容）
