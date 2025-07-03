# UQM Assert 断言语法修复报告

## 问题分析

通过对比 `UQM_ASSERT_查询用例.md` 和 `UQM_Complete_JSON_Schema_Reference.md` 文档，发现 assert 步骤的语法描述存在不一致，导致 AI 生成的查询使用了错误的断言语法。

### 发现的问题

1. **断言类型名称不一致**：
   - 错误使用：`column_values`
   - 正确使用：`range`

2. **断言字段名称不一致**：
   - 错误使用：`column` 字段
   - 正确使用：`field` 字段

3. **断言条件语法不一致**：
   - 错误使用：`condition` 和 `value` 字段组合
   - 正确使用：直接使用 `min`、`max`、`expected` 字段

4. **行数断言语法不一致**：
   - 错误使用：`"type": "row_count", "condition": ">", "value": 0`
   - 正确使用：`"type": "row_count", "min": 1` 或 `"expected": 100`

## 修复内容

### 1. 更新断言类型列表

**修复前：**
```json
"type": "column_values"    // ❌ 不存在的类型
"type": "unique_values"    // ❌ 错误的名称
```

**修复后：**
```json
"type": "range"           // ✅ 正确的数值范围断言
"type": "unique"          // ✅ 正确的唯一性断言
```

### 2. 更新断言字段结构

**修复前：**
```json
{
  "type": "column_values",
  "column": "salary",
  "condition": ">",
  "value": 0,
  "message": "薪资必须大于0"
}
```

**修复后：**
```json
{
  "type": "range",
  "field": "salary",
  "min": 0,
  "message": "薪资必须大于0"
}
```

### 3. 更新行数断言语法

**修复前：**
```json
{
  "type": "row_count",
  "condition": ">",
  "value": 0,
  "message": "数据不能为空"
}
```

**修复后：**
```json
{
  "type": "row_count",
  "min": 1,
  "message": "数据不能为空"
}
```

## 完整的断言类型规范

### 支持的断言类型

1. **`row_count`** - 行数断言
   ```json
   {
     "type": "row_count",
     "expected": 100,        // 期望的精确行数（可选）
     "min": 1,              // 最小行数（可选）
     "max": 1000,           // 最大行数（可选）
     "message": "行数不符合预期"
   }
   ```

2. **`range`** - 数值范围断言
   ```json
   {
     "type": "range",
     "field": "salary",
     "min": 3000,           // 最小值（可选）
     "max": 50000,          // 最大值（可选）
     "message": "薪资超出范围"
   }
   ```

3. **`unique`** - 唯一性断言
   ```json
   {
     "type": "unique",
     "field": "employee_id",
     "message": "员工ID必须唯一"
   }
   ```

4. **`not_null`** - 非空断言
   ```json
   {
     "type": "not_null",
     "field": "email",
     "message": "邮箱不能为空"
   }
   ```

5. **`value_in`** - 值在集合中断言
   ```json
   {
     "type": "value_in",
     "field": "status",
     "values": ["active", "inactive", "pending"],
     "message": "状态值无效"
   }
   ```

6. **`custom`** - 自定义表达式断言
   ```json
   {
     "type": "custom",
     "expression": "revenue > 1000 AND profit_margin > 0.1",
     "message": "收入和利润率不符合要求"
   }
   ```

## 修复示例

### 原始错误查询
```json
{
  "type": "assert",
  "config": {
    "source": "get_sales_by_product_category",
    "assertions": [
      {
        "type": "column_values",          // ❌ 错误的类型
        "column": "total_sales_amount",   // ❌ 错误的字段名
        "condition": ">=",                // ❌ 不支持的语法
        "value": 0,                       // ❌ 不支持的语法
        "message": "总销售额不能为负数。"
      }
    ]
  }
}
```

### 修复后的查询
```json
{
  "type": "assert",
  "config": {
    "source": "get_sales_by_product_category",
    "assertions": [
      {
        "type": "range",                  // ✅ 正确的类型
        "field": "total_sales_amount",    // ✅ 正确的字段名
        "min": 0,                         // ✅ 正确的语法
        "message": "总销售额不能为负数。"
      }
    ]
  }
}
```

## 验证

修复后的语法与 `UQM_ASSERT_查询用例.md` 中的实际用例完全一致，应该能够正常执行而不会出现"不支持的断言类型"错误。

## 建议

1. **文档统一性**：确保所有文档中的语法示例保持一致
2. **类型检查**：在 UQM 引擎中添加更详细的错误提示，指出正确的断言类型
3. **向前兼容**：考虑在引擎中添加对旧语法的兼容处理，提供迁移提示

---

**修复状态：** ✅ 已完成  
**验证文件：** `corrected_sales_by_category_query.json`  
**更新文档：** `UQM_Complete_JSON_Schema_Reference.md`
