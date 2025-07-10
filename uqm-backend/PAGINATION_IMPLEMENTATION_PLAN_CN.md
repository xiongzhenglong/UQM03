# UQM 分页功能实现计划

## 1. 目标

为 UQM 后端的 `query` 步骤类型添加分页支持。这将允许 API 的使用者以可管理的块（chunk）来获取大的结果集，从而为列表类查询提升性能和可用性。

## 2. 应用分页的核心逻辑

一个关键的设计考量是分页功能如何与多步骤查询交互。一个全局的分页设置是不够的。因此，实现将遵循一种智能的方法：

分页将**仅应用于 UQM 中定义的最终 `output` 步骤**，并且**仅当该步骤类型为 `"query"` 时**。

优化后的逻辑如下：

1.  **请求层面:** 为了方便用户，分页参数 (`page`, `page_size`) 将在全局的 `options` 对象中传递。
2.  **引擎 (`UQMEngine`):** 引擎将识别 `output` 步骤。如果它是一个 `query` 类型，引擎会将分页选项向下传递给 `Executor`，并标记它们仅适用于最终输出。
3.  **执行器 (`Executor`):** `Executor` 将按顺序执行所有步骤。对于任何中间的 `query` 步骤，它将**不应用**分页。当它到达最终的 `output` 步骤时（如果它是一个查询），它将把分页选项注入到该特定步骤执行的上下文中。
4.  **查询步骤 (`QueryStep`):** `QueryStep` 将检查其执行上下文以获取分页选项。如果存在，它将执行双查询逻辑（一个 `COUNT(*)` 查询用于获取总数，一个分页查询用于获取数据）。否则，它将像往常一样获取所有结果。

这种设计确保了复杂的多步骤工作流保持完全的功能性，并且分页是一个可预测地应用于最终结果集的功能。

---

## 3. 主要变更概览

该实现将涉及以下组件：

1.  **API 模型 (`src/api/models.py`):** 更新请求和响应模型。
2.  **查询引擎 (`src/core/engine.py`):** 将进行适配以处理优化的分页逻辑。
3.  **步骤执行器 (`src/core/executor.py`):** 将被修改以选择性地应用分页。
4.  **查询步骤 (`src/steps/query_step.py`):** 将包含核心的双查询逻辑。
5.  **SQL 构建器 (`src/utils/sql_builder.py`):** 将用于构建必要的查询。

---

## 4. 详细实现步骤

### 步骤 1: 修改 API 模型 (`src/api/models.py`)

**a) 为响应添加一个 `PaginationInfo` 模型:**

```python
// src/api/models.py

class PaginationInfo(BaseModel):
    """分页信息模型"""
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_items: int = Field(..., description="总项目数")
    total_pages: int = Field(..., description="总页数")
```

**b) 更新 `UQMResponse` 模型:**

`pagination` 对象将嵌套在 `execution_info` 内部，以保持响应结构的清晰。

```python
// src/api/models.py

class UQMResponse(BaseModel):
    """UQM响应数据模型"""
    # ... 已有字段 ...
    execution_info: Dict[str, Any] = Field(default_factory=dict, description="执行信息")
    # 'pagination' 键现在将是 execution_info 字典的一部分
```

在响应的 `schema_extra` 中，它看起来会是这样：
```json
"execution_info": {
    "total_time": 0.08,
    "row_count": 5,
    "cache_hit": false,
    "pagination": {
        "page": 2,
        "page_size": 5,
        "total_items": 12,
        "total_pages": 3
    }
}
```

### 步骤 2: 更新 `QueryStep` 的分页逻辑 (`src/steps/query_step.py`)

`_execute_with_database` 方法将被更新以处理双查询逻辑。

**a) 修改 `QueryStep.execute` 的返回签名:**

它现在将返回一个包含数据和总数的字典：`{"data": [...], "total_count": ...}`。

**b) 在 `_execute_with_database` 中实现双查询逻辑:**

```python
// src/steps/query_step.py

async def _execute_with_database(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    使用数据库执行查询，并处理分页
    """
    connector_manager = context["connector_manager"]
    connector = await connector_manager.get_default_connector()
    options = context.get("options", {})
    page = options.get("page")
    page_size = options.get("page_size")

    total_count = None
    # 使用步骤自身配置中的 limit/offset 作为默认值
    limit = self.config.get("limit")
    offset = self.config.get("offset")

    # 如果在上下文中传递了分页选项，则触发分页逻辑
    if page and page_size:
        # 1. 构建并执行 COUNT 查询以获取项目总数
        count_query = self.build_count_query()
        count_result = await connector.execute_query(count_query)
        total_count = count_result[0].get('total', 0) if count_result else 0

        # 2. 基于分页参数计算数据查询的 limit 和 offset
        limit = page_size
        offset = (page - 1) * page_size
    
    # 3. 使用正确的 limit 和 offset 构建并执行主数据查询
    self.config['limit'] = limit
    self.config['offset'] = offset
    data_query = self.build_query()
    data_result = await connector.execute_query(data_query)
    
    return {"data": data_result, "total_count": total_count}

def build_count_query(self) -> str:
    """
    构建用于获取总行数的SQL COUNT查询。
    此查询与 build_query 类似，但选择 COUNT(*) 并省略 ORDER BY, LIMIT, OFFSET。
    """
    # 复用 build_query 的 FROM, JOIN, WHERE, GROUP BY, HAVING 部分
    query = self.sql_builder.build_select_query(
        select_fields=["COUNT(*) as total"],
        from_table=self.config["data_source"],
        joins=self.config.get("joins", []),
        where_conditions=self.config.get("filters", []),
        group_by=self.config.get("group_by", []),
        having=self.config.get("having", [])
    )
    # 如果存在 GROUP BY，我们需要计算结果组的数量
    if self.config.get("group_by"):
        return f"SELECT COUNT(*) as total FROM ({query}) as subquery"

    return query
```

### 步骤 3: 适配 `Executor` 和 `Engine` (`src/core/executor.py`, `src/core/engine.py`)

**a) 在 `UQMEngine.process` 中:**

引擎将识别输出步骤并传递分页选项给执行器。

```python
// src/core/engine.py in process

# ...
output_step_name = processed_data["output"]
output_step_config = next((step for step in processed_data["steps"] if step["name"] == output_step_name), None)

# 仅当输出步骤是 query 类型时，才将分页选项传递给执行器
pagination_options_for_executor = {}
if output_step_config and output_step_config['type'] == 'query':
    pagination_options_for_executor = {
        "page": options.get("page"),
        "page_size": options.get("page_size")
    }

executor = Executor(
    steps=processed_data["steps"],
    # ... 其他参数
    options=self.options, # 传递所有选项
    output_step_name=output_step_name,
    pagination_options=pagination_options_for_executor
)
execution_result = await executor.execute()
# ...
# 如果适用，构造带有分页信息的最终响应
# ...
```

**b) 在 `Executor._execute_step` 中:**

执行器将选择性地将分页选项注入到最终查询步骤的上下文中。

```python
// src/core/executor.py in _execute_step

# ...
context = self._prepare_execution_context(config)

# 仅为最终的输出查询步骤注入分页选项
if step_name == self.output_step_name and step_type == "query" and self.pagination_options:
    context["options"].update(self.pagination_options)

# 执行步骤
step_execution_output = await self._execute_step_by_type(step_type, config, context)

# 处理来自 QueryStep 的新返回结构
if step_type == 'query' and isinstance(step_execution_output, dict):
    step_data = step_execution_output.get("data")
    self.step_results[step_name]["total_count"] = step_execution_output.get("total_count")
else:
    step_data = step_execution_output
# ...
```

### 步骤 4: 示例用法

示例请求和响应与之前版本的计划保持一致，因为面向用户的 API 契约没有改变。这个经过修订的内部逻辑只是使其能够正确地适用于所有用例。

## 5. 实现状态

- [x] 更新 API 模型 - ✅ 已完成
- [x] 修改 UQMEngine - ✅ 已完成  
- [x] 更新 Executor - ✅ 已完成
- [x] 增强 QueryStep - ✅ 已完成
- [x] 测试验证 - ✅ 已完成

## 6. 测试结果

分页功能已成功实现并通过完整测试！

### 测试场景覆盖
1. **基本分页查询** - ✅ 通过
   - 第1页数据：5条记录 (ID: 1-5)
   - 第2页数据：5条记录 (ID: 6-10)
   - 分页元数据：总记录12条，总页数3页

2. **多步骤查询选择性分页** - ✅ 通过
   - 对第一个query步骤进行分页
   - 后续enrich步骤正常处理分页数据
   - 最终结果包含正确的部门信息

### 关键特性验证
- ✅ 精确的分页目标定位：通过 `pagination_target_step` 指定
- ✅ 双查询逻辑：COUNT查询获取总数 + LIMIT/OFFSET分页查询
- ✅ 正确的分页元数据计算：页码、页大小、总数、总页数
- ✅ 与现有功能兼容：不影响非分页查询和其他步骤类型
- ✅ 多步骤查询支持：只对指定步骤分页，不干扰其他步骤

### 实际测试数据
```
第1页 (page=1, page_size=5):
   1. ID:1 - 张伟 - IT总监
   2. ID:2 - 王芳 - HR经理  
   3. ID:3 - 李强 - 软件工程师
   4. ID:4 - 刘娜 - 人事专员
   5. ID:5 - 陈军 - 销售总监

第2页 (page=2, page_size=5):
   1. ID:6 - 杨静 - 销售代表
   2. ID:7 - Ming Li - 高级财务分析师
   3. ID:8 - Peter Schmidt - 欧洲区销售经理
   4. ID:9 - Yuki Tanaka - 市场专员
   5. ID:10 - Emily Jones - 高级软件工程师

多步骤分页 (page=1, page_size=3):
   1. ID:1 - 张伟 - 部门:信息技术部
   2. ID:2 - 王芳 - 部门:人力资源部
   3. ID:3 - 李强 - 部门:信息技术部
```

## 7. 功能总结

分页功能现已完全集成到UQM系统中，具备以下特性：

- 🎯 **精确控制**：通过 `pagination_target_step` 精确指定要分页的步骤
- 🔄 **智能降级**：如果未指定目标步骤，默认尝试对最终输出步骤分页
- 📊 **完整元数据**：提供页码、页大小、总记录数、总页数等信息
- 🧩 **无缝集成**：与现有UQM功能完全兼容，不影响其他步骤类型
- ⚡ **性能优化**：使用标准的数据库分页技术（LIMIT/OFFSET）
- 🔍 **准确计数**：通过COUNT查询提供精确的总记录数

---