# UQM 断言消息显示修复报告

## 问题描述

用户在使用UQM系统的断言功能时发现，当断言失败时，系统显示的是通用错误消息，而不是用户在配置中自定义的 `message` 字段内容。

### 原始问题
用户配置：
```json
{
    "type": "custom",
    "expression": "invalid_email_count > 0",
    "message": "发现无效的邮箱格式"
}
```

期望错误消息：`发现无效的邮箱格式`

实际错误消息：`自定义断言失败，1 行不满足条件`

## 根本原因分析

在 `src/steps/assert_step.py` 文件中，各种断言方法在返回失败结果时，使用的是硬编码的错误消息，而没有使用用户配置中的 `message` 字段。

### 问题代码示例

**自定义断言问题**：
```python
def _assert_custom(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
    # ...断言逻辑...
    if failed_rows:
        return {
            "passed": False,
            "message": f"自定义断言失败，{len(failed_rows)} 行不满足条件",  # 硬编码消息
            "details": {"failed_rows": failed_rows[:10]}
        }
```

**范围断言问题**：
```python
def _assert_range(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
    # ...断言逻辑...
    if out_of_range_records:
        return {
            "passed": False,
            "message": f"发现 {len(out_of_range_records)} 个超出范围的值: {assertion.get('message', '')}",  # 格式不当
            "details": {"out_of_range_records": out_of_range_records[:10]}
        }
```

## 解决方案

### 修改内容

1. **修复自定义断言消息处理**
2. **修复范围断言消息处理**
3. **修复行数断言消息处理**

### 具体修改

#### 1. 自定义断言 (_assert_custom)

**修改前**：
```python
def _assert_custom(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
    """自定义断言"""
    expression = assertion.get("expression")
    
    if not expression:
        return {"passed": False, "message": "缺少expression参数"}
    
    # ...断言逻辑...
    if failed_rows:
        return {
            "passed": False,
            "message": f"自定义断言失败，{len(failed_rows)} 行不满足条件",
            "details": {"failed_rows": failed_rows[:10]}
        }
```

**修改后**：
```python
def _assert_custom(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
    """自定义断言"""
    expression = assertion.get("expression")
    custom_message = assertion.get("message", "自定义断言失败")
    
    if not expression:
        return {"passed": False, "message": "缺少expression参数"}
    
    # ...断言逻辑...
    if failed_rows:
        return {
            "passed": False,
            "message": custom_message,  # 使用用户自定义消息
            "details": {"failed_rows": failed_rows[:10], "expression": expression}
        }
```

#### 2. 范围断言 (_assert_range)

**修改前**：
```python
if out_of_range_records:
    return {
        "passed": False,
        "message": f"发现 {len(out_of_range_records)} 个超出范围的值: {assertion.get('message', '')}",
        "details": {"out_of_range_records": out_of_range_records[:10]}
    }
```

**修改后**：
```python
if out_of_range_records:
    return {
        "passed": False,
        "message": custom_message,  # 直接使用用户自定义消息
        "details": {"out_of_range_records": out_of_range_records[:10]}
    }
```

#### 3. 行数断言 (_assert_row_count)

**修改前**：
```python
if expected_count is not None and actual_count != expected_count:
    return {
        "passed": False,
        "message": f"期望行数 {expected_count}，实际行数 {actual_count}",
        "details": {"expected": expected_count, "actual": actual_count}
    }
```

**修改后**：
```python
if expected_count is not None and actual_count != expected_count:
    message = custom_message or f"期望行数 {expected_count}，实际行数 {actual_count}"
    return {
        "passed": False,
        "message": message,  # 优先使用用户自定义消息
        "details": {"expected": expected_count, "actual": actual_count}
    }
```

## 测试验证

### 测试用例1：自定义断言消息
**配置**:
```json
{
    "type": "custom",
    "expression": "invalid_email_count == 0",
    "message": "发现无效的邮箱格式"
}
```
**结果**: ✅ 显示用户自定义消息 "发现无效的邮箱格式"

### 测试用例2：范围断言消息
**配置**:
```json
{
    "type": "range",
    "field": "product_price",
    "max": 100000,
    "message": "产品价格超过限制"
}
```
**结果**: ✅ 显示用户自定义消息 "产品价格超过限制"

### 测试用例3：行数断言消息
**配置**:
```json
{
    "type": "row_count",
    "expected": 0,
    "message": "发现重复的客户邮箱地址"
}
```
**结果**: ✅ 显示用户自定义消息 "发现重复的客户邮箱地址"

## 修复前后对比

### 修复前
```
断言检查报告:
总计: 3, 通过: 2, 失败: 1
✓ custom: 自定义断言通过
✓ custom: 自定义断言通过
✗ custom: 自定义断言失败，1 行不满足条件
```

### 修复后
```
断言检查报告:
总计: 3, 通过: 2, 失败: 1
✓ custom: 自定义断言通过
✓ custom: 自定义断言通过
✗ custom: 发现无效的邮箱格式
```

## 用户配置示例

现在用户的断言配置可以正确显示自定义消息：

```json
{
    "name": "assert_data_quality",
    "type": "assert",
    "config": {
        "source": "data_quality_check",
        "assertions": [
            {
                "type": "custom",
                "expression": "null_email_count == 0",
                "message": "发现客户邮箱字段为空"
            },
            {
                "type": "custom",
                "expression": "invalid_email_count == 0",
                "message": "发现无效的邮箱格式"
            },
            {
                "type": "range",
                "field": "product_price",
                "max": 100000,
                "message": "产品价格超过限制"
            },
            {
                "type": "row_count",
                "expected": 0,
                "message": "发现重复的客户邮箱地址"
            }
        ]
    }
}
```

当断言失败时，将显示用户定义的有意义的错误消息，而不是通用的技术性消息。

## 影响范围

### 正面影响
1. **用户体验提升**: 错误消息更加清晰和有意义
2. **业务语义**: 错误消息符合业务上下文
3. **可读性**: 非技术用户也能理解错误含义
4. **调试效率**: 更容易定位和解决数据质量问题

### 风险评估
1. **低风险**: 只是改变了错误消息的显示，不影响断言逻辑
2. **向后兼容**: 如果没有提供自定义消息，会使用默认消息
3. **测试覆盖**: 所有主要断言类型都经过测试验证

## 建议

1. **文档更新**: 在用户手册中强调 `message` 字段的重要性
2. **最佳实践**: 建议为所有断言都提供有意义的自定义消息
3. **国际化**: 考虑支持多语言错误消息
4. **监控**: 收集用户反馈，持续优化错误消息的有用性

## 总结

此次修复成功解决了断言消息显示的问题。现在用户配置的 `message` 字段会正确显示在断言失败报告中，大大提升了用户体验和系统的可用性。

**修复状态**: ✅ 完成并验证通过  
**测试覆盖**: ✅ 自定义、范围、行数断言全部测试通过  
**用户体验**: ✅ 显著提升错误消息的可读性  
**业务价值**: ✅ 错误消息更符合业务语义
