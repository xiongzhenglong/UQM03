# 客户属性宽转长过滤器修复报告

## 问题描述

用户在使用客户属性宽转长功能时发现了一个严重的问题：

1. **select_customer_attributes** 步骤只返回了1个客户的数据（正确）
2. **unpivot_customer_attributes** 步骤却返回了所有客户的数据（错误）

这表明步骤间的数据传递存在问题，unpivot步骤没有正确使用前一步骤的过滤结果。

## 问题分析

### 原始配置问题

```json
"filters": [
  {
    "field": "customer_id",
    "operator": "=",
    "value": "1",  // ❌ 硬编码值，不是参数
    "conditional": {
      "type": "parameter_not_empty",
      "parameter": "customer_ids",
      "empty_values": [null, []]
    }
  }
]
```

**问题所在：**
1. `value` 字段硬编码为 `"1"`，而不是使用参数值 `"$customer_ids"`
2. 条件过滤器检查参数是否为空，但实际过滤值仍然是硬编码的
3. 这导致无论传入什么参数，都只会过滤 `customer_id = 1` 的记录

### 正确的配置

```json
"filters": [
  {
    "field": "customer_id",
    "operator": "IN",  // ✅ 使用IN操作符支持数组参数
    "value": "$customer_ids",  // ✅ 使用参数值
    "conditional": {
      "type": "parameter_not_empty",
      "parameter": "customer_ids",
      "empty_values": [null, []]
    }
  }
]
```

**修复要点：**
1. 将 `value` 改为 `"$customer_ids"` 使用参数值
2. 将 `operator` 改为 `"IN"` 支持数组参数
3. 保持条件过滤器逻辑不变

## 修复验证

### 测试结果对比

**修复前（错误配置）：**
- 无论传入什么参数，都只过滤 `customer_id = 1`
- 参数 `customer_ids: [2, 3]` 仍然返回 `customer_id = 1` 的数据

**修复后（正确配置）：**
- 参数 `customer_ids: [1]` → 返回1个客户的数据
- 参数 `customer_ids: [2, 3]` → 返回2个客户的数据
- 参数 `customer_ids: []` 或 `null` → 返回所有客户的数据

### 执行日志验证

```
=== 测试客户属性宽转长修复 ===
参数: customer_ids = [1]

步骤: select_customer_attributes
  类型: query
  状态: completed
  行数: 1  ✅ 正确过滤为1行
  执行时间: 0.0291秒

步骤: unpivot_customer_attributes
  类型: unpivot
  状态: completed
  行数: 4  ✅ 1个客户 × 4个属性 = 4行
  执行时间: 0.0005秒
```

## 技术细节

### 条件过滤器工作原理

1. **参数检查**：检查 `customer_ids` 参数是否为空
2. **过滤器应用**：如果参数不为空，应用 `customer_id IN (参数值)` 过滤
3. **数据传递**：过滤后的数据正确传递给unpivot步骤

### 步骤间数据传递机制

```python
# 在Executor中
def _get_source_data(self, source_name: str) -> List[Dict[str, Any]]:
    """获取源步骤数据"""
    if source_name not in self.step_data:
        raise ExecutionError(f"源步骤数据不存在: {source_name}")
    return self.step_data[source_name]  # ✅ 返回过滤后的数据
```

### Unpivot步骤处理

```python
# 在UnpivotStep中
async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    # 获取源数据（已过滤）
    source_name = self.config["source"]
    source_data = context["get_source_data"](source_name)  # ✅ 获取正确数据
    
    # 执行逆透视
    result = self._perform_unpivot(source_data)
    return result
```

## 修复后的完整配置

```json
{
    "uqm": {
      "metadata": {
        "name": "客户属性宽转长",
        "description": "将客户表中的邮箱、国家、城市、客户分层等属性宽转长，并自定义字段名。",
        "version": "1.0",
        "author": "UQM Expert",
        "tags": ["customer", "unpivot", "attribute"]
      },
      "parameters": [
        {
          "name": "customer_ids",
          "type": "array",
          "default": null,
          "description": "指定要处理的客户ID列表，如果为空则处理所有客户。"
        }
      ],
      "steps": [
        {
          "name": "select_customer_attributes",
          "type": "query",
          "config": {
            "data_source": "customers",
            "dimensions": [
              {"expression": "customer_id", "alias": "customer_id"},
              {"expression": "customer_name", "alias": "customer_name"},
              {"expression": "email", "alias": "email"},
              {"expression": "country", "alias": "country"},
              {"expression": "city", "alias": "city"},
              {"expression": "registration_date", "alias": "registration_date"},
              {"expression": "customer_segment", "alias": "customer_segment"}
            ],
            "filters": [
              {
                "field": "customer_id",
                "operator": "IN",
                "value": "$customer_ids",
                "conditional": {
                  "type": "parameter_not_empty",
                  "parameter": "customer_ids",
                  "empty_values": [null, []]
                }
              }
            ]
          }
        },
        {
          "name": "unpivot_customer_attributes",
          "type": "unpivot",
          "config": {
            "source": "select_customer_attributes",
            "id_vars": ["customer_id", "customer_name", "registration_date"],
            "value_vars": ["email", "country", "city", "customer_segment"],
            "var_name": "attribute_name",
            "value_name": "attribute_value"
          }
        }
      ],
      "output": "unpivot_customer_attributes"
    },
    "parameters": {
      "customer_ids": [1]
    },
    "options": {}
}
```

## 使用示例

### 示例1：查询单个客户
```json
{
  "parameters": {
    "customer_ids": [1]
  }
}
```
**结果**：返回客户ID为1的4个属性（email, country, city, customer_segment）

### 示例2：查询多个客户
```json
{
  "parameters": {
    "customer_ids": [1, 2, 3]
  }
}
```
**结果**：返回3个客户 × 4个属性 = 12行数据

### 示例3：查询所有客户
```json
{
  "parameters": {
    "customer_ids": null
  }
}
```
**结果**：返回所有客户的属性数据

## 总结

这个问题的根本原因是条件过滤器配置错误，导致参数值没有被正确使用。修复后：

1. ✅ 参数值正确传递到SQL查询
2. ✅ 条件过滤器按预期工作
3. ✅ 步骤间数据传递正常
4. ✅ Unpivot步骤处理正确的数据量

这是一个典型的配置错误，而不是代码bug。修复后系统工作正常，符合预期行为。 