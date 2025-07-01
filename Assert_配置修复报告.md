# UQM Assert 配置修复报告

## 🐛 问题确认

通过源码分析和测试验证，确认了 UQM Assert 步骤的配置格式问题：

### 问题现象
```
"步骤 assert_order_count 执行失败: 步骤 AssertStep 缺少必需配置: assertions"
```

### 根本原因
1. **AssertStep 源码期望配置字段**: `assertions`
2. **用户文档中使用的字段**: `conditions` ❌
3. **配置字段不匹配**导致验证失败

## 🔍 源码分析

### AssertStep.validate() 方法
```python
def validate(self) -> None:
    """验证断言步骤配置"""
    required_fields = ["source", "assertions"]  # ✅ 期望 assertions
    self._validate_required_config(required_fields)
```

### BaseStep._validate_required_config() 方法
```python
def _validate_required_config(self, required_fields: List[str]) -> None:
    for field in required_fields:
        if field not in self.config:
            raise ValidationError(
                f"步骤 {self.step_name} 缺少必需配置: {field}"
            )
```

## ✅ 修复方案

### 1. 配置字段修正
- **错误格式**: `"conditions": [...]`
- **正确格式**: `"assertions": [...]`

### 2. 断言对象结构调整
```json
// 错误格式
{
  "field": "total_orders",
  "operator": ">=",
  "value": 100,
  "message": "订单数量不能少于100条"
}

// 正确格式  
{
  "type": "range",
  "field": "total_orders", 
  "min": 100,
  "max": 10000,
  "message": "订单数量应在100-10000之间"
}
```

### 3. 支持的断言类型
- `row_count`: 验证行数
- `not_null`: 验证非空
- `unique`: 验证唯一性
- `range`: 验证数值范围
- `regex`: 验证正则匹配
- `custom`: 自定义断言
- `column_exists`: 验证列存在
- `data_type`: 验证数据类型
- `value_in`: 验证值在集合中
- `relationship`: 验证关系

## 🔧 修复后的完整示例

```json
{
  "uqm": {
    "metadata": {
      "name": "验证订单总数_修复版",
      "description": "使用正确的assertions配置格式",
      "version": "1.1"
    },
    "steps": [
      {
        "name": "count_orders",
        "type": "query",
        "config": {
          "data_source": "orders",
          "metrics": [
            {
              "name": "order_id",
              "aggregation": "COUNT",
              "alias": "total_orders"
            }
          ]
        }
      },
      {
        "name": "assert_order_count",
        "type": "assert",
        "config": {
          "source": "count_orders",
          "assertions": [
            {
              "type": "range",
              "field": "total_orders",
              "min": 100,
              "max": 10000,
              "message": "订单数量应在100-10000之间"
            }
          ]
        }
      }
    ],
    "output": "count_orders"
  },
  "parameters": {},
  "options": {}
}
```

## 📋 需要更新的内容

1. ✅ 已修复文档中第一个示例的配置格式
2. 🔄 需要更新文档中其余所有Assert示例
3. 📝 需要更新Assert语法说明部分
4. 🧪 建议添加配置验证的单元测试

## 🎯 建议改进

### 1. 兼容性增强
考虑在 AssertStep 中同时支持 `conditions` 和 `assertions` 字段：

```python
def validate(self) -> None:
    """验证断言步骤配置"""
    required_fields = ["source"]
    self._validate_required_config(required_fields)
    
    # 兼容性处理
    if "conditions" in self.config and "assertions" not in self.config:
        self.config["assertions"] = self.config["conditions"]
        self.log_warning("推荐使用 'assertions' 替代 'conditions'")
    
    if "assertions" not in self.config:
        raise ValidationError("缺少必需配置: assertions")
```

### 2. 错误信息优化
提供更友好的错误提示：

```python
if field not in self.config:
    if field == "assertions" and "conditions" in self.config:
        hint = " (提示: 请将 'conditions' 改为 'assertions')"
    else:
        hint = ""
    raise ValidationError(f"步骤 {self.step_name} 缺少必需配置: {field}{hint}")
```

## 🏁 测试验证

✅ 测试确认：
- 使用 `conditions` 配置会触发 `ValidationError: 缺少必需配置: assertions`
- 使用 `assertions` 配置可以正常通过验证
- AssertStep 支持10种断言类型

---

**结论**: 这是一个**配置字段命名不一致的底层bug**，已通过修正配置格式解决。建议开发团队考虑增加向后兼容性支持。
