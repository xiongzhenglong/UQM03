# UQM 自定义断言字段修复报告

## 问题描述

用户在使用UQM系统的自定义断言功能时遇到以下错误：
```
{
    "error": {
        "code": "HTTP_500",
        "message": {
            "code": "EXECUTION_ERROR",
            "message": "步骤 assert_data_quality 执行失败: 断言执行失败: 断言检查失败:\n断言检查报告:\n总计: 3, 通过: 0, 失败: 3\n\n✗ custom: 缺少expression参数\n✗ custom: 缺少expression参数\n✗ custom: 缺少expression参数",
            "details": {}
        },
        "details": {}
    }
}
```

## 根本原因分析

问题出现在用户配置与系统实现的字段名称不匹配：

1. **用户配置使用的字段**: `condition`
2. **系统实现期望的字段**: `expression`

在 `src/steps/assert_step.py` 文件的 `_assert_custom()` 方法中：
```python
def _assert_custom(self, data: List[Dict[str, Any]], assertion: Dict[str, Any]) -> Dict[str, Any]:
    """自定义断言"""
    expression = assertion.get("expression")  # 期望 expression 字段
    
    if not expression:
        return {"passed": False, "message": "缺少expression参数"}
```

但用户配置使用的是：
```json
{
    "type": "custom",
    "condition": "null_email_count == 0",  // 使用了 condition 字段
    "message": "发现客户邮箱字段为空"
}
```

## 解决方案

### 修改内容

更新了 `UQM_ASSERT_查询用例.md` 文档中所有自定义断言的配置，将 `condition` 字段改为 `expression` 字段。

### 具体修改

1. **数据完整性验证配置**：
```json
// 修改前
{
    "type": "custom",
    "condition": "null_email_count == 0",
    "message": "发现客户邮箱字段为空"
}

// 修改后  
{
    "type": "custom",
    "expression": "null_email_count == 0",
    "message": "发现客户邮箱字段为空"
}
```

2. **日期逻辑验证配置**：
```json
// 修改前
{
    "type": "custom",
    "condition": "future_orders_count == 0",
    "message": "发现订单日期为未来时间的异常数据"
}

// 修改后
{
    "type": "custom",
    "expression": "future_orders_count == 0", 
    "message": "发现订单日期为未来时间的异常数据"
}
```

3. **性能验证配置**：
```json
// 修改前
{
    "type": "custom",
    "condition": "execution_time <= 5000",
    "message": "查询执行时间超过5秒，需要优化"
}

// 修改后
{
    "type": "custom",
    "expression": "execution_time <= 5000",
    "message": "查询执行时间超过5秒，需要优化"
}
```

4. **文档示例更新**：
```json
// 修改前
{
    "type": "custom",
    "condition": "revenue > 1000 AND profit_margin > 0.1",
    "message": "收入应大于1000且利润率大于10%"
}

// 修改后
{
    "type": "custom",
    "expression": "revenue > 1000 AND profit_margin > 0.1",
    "message": "收入应大于1000且利润率大于10%"
}
```

## 测试验证

### 测试用例1：正确的expression字段
**配置**:
```json
{
    "type": "custom",
    "expression": "null_email_count == 0",
    "message": "发现客户邮箱字段为空"
}
```
**结果**: ✅ 配置验证通过，断言执行成功

### 测试用例2：断言失败检测
**数据**:
```json
{
    "null_email_count": 5,
    "invalid_email_count": 2
}
```
**结果**: ✅ 正确检测到数据质量问题并报告失败

### 测试用例3：旧的condition字段
**配置**:
```json
{
    "type": "custom",
    "condition": "null_email_count == 0",
    "message": "发现客户邮箱字段为空"
}
```
**结果**: ✅ 正确检测到"缺少expression参数"错误

## 修复前后对比

### 修复前
- 用户配置使用 `condition` 字段
- 系统报错："缺少expression参数"
- 自定义断言功能无法正常工作

### 修复后
- 用户配置使用 `expression` 字段
- 系统正确执行自定义断言
- 支持复杂的条件表达式评估
- 准确报告断言结果

## 用户配置示例

现在用户可以正常使用以下配置：

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
                "expression": "null_name_count == 0", 
                "message": "发现客户姓名字段为空"
            },
            {
                "type": "custom",
                "expression": "invalid_email_count == 0",
                "message": "发现无效的邮箱格式"
            }
        ]
    }
}
```

## 影响范围

### 正面影响
1. **功能正常化**: 自定义断言功能现在可以正常工作
2. **文档一致性**: 配置示例与系统实现保持一致
3. **用户体验**: 用户不再遇到"缺少expression参数"错误

### 风险评估
1. **低风险**: 只是修改了配置字段名称，没有改变核心逻辑
2. **向前兼容**: 新的配置格式符合系统设计
3. **文档更新**: 确保所有示例都使用正确的字段名

## 建议

1. **API文档更新**: 确保所有API文档中的自定义断言示例都使用 `expression` 字段
2. **用户通知**: 通知现有用户更新他们的配置文件
3. **版本兼容**: 考虑在未来版本中同时支持 `condition` 和 `expression` 字段以保持向后兼容

## 总结

此次修复成功解决了用户自定义断言功能的配置问题。通过将用户配置中的 `condition` 字段统一改为 `expression` 字段，使配置与系统实现保持一致，确保自定义断言功能正常工作。

**修复状态**: ✅ 完成并验证通过  
**测试覆盖**: ✅ 完整测试用例  
**文档更新**: ✅ 所有相关示例已更新  
**功能验证**: ✅ 自定义断言功能正常工作
