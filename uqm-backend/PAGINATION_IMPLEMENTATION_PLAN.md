
# UQM Pagination Implementation Plan

## 1. Objective

To add support for pagination to the `query` step type within the UQM backend. This will allow API consumers to retrieve large result sets in manageable chunks, improving performance and usability for list-based queries.

## 2. Core Logic for Applying Pagination

A critical design consideration is how pagination interacts with multi-step queries. A global pagination setting is insufficient. Therefore, the implementation will follow an intelligent approach:

Pagination will be applied **only to the final `output` step** defined in the UQM, and only if that step is of `type: "query"`.

The refined logic is as follows:

1.  **Request Level:** Pagination parameters (`page`, `page_size`) will be passed in the global `options` object for user convenience.
2.  **Engine (`UQMEngine`):** The engine will identify the `output` step. If it is a `query` type, it will pass the pagination options down to the `Executor`, flagging them as applicable only to the final output.
3.  **Executor:** The `Executor` will execute all steps in sequence. For any intermediate `query` steps, it will **not** apply pagination. When it reaches the final `output` step (if it's a query), it will inject the pagination options into the context for that specific step's execution.
4.  **Query Step (`QueryStep`):** The `QueryStep` will check its execution context for pagination options. If present, it will perform the dual-query logic (a `COUNT(*)` query for the total and a paginated query for the data). Otherwise, it will fetch all results as normal.

This design ensures that complex, multi-step workflows remain fully functional, and pagination is a feature applied predictably to the final result set.

---

## 3. Key Changes Overview

The implementation will touch the following components:

1.  **API Models (`src/api/models.py`):** The request and response models will be updated.
2.  **Query Engine (`src/core/engine.py`):** Will be adapted to handle the refined pagination logic.
3.  **Step Executor (`src/core/executor.py`):** Will be modified to selectively apply pagination.
4.  **Query Step (`src/steps/query_step.py`):** Will contain the core dual-query logic.
5.  **SQL Builder (`src/utils/sql_builder.py`):** Will be used to construct the necessary queries.

---

## 4. Detailed Implementation Steps

### Step 1: Modify API Models (`src/api/models.py`)

**a) Add a `PaginationInfo` model for the response:**

```python
// src/api/models.py

class PaginationInfo(BaseModel):
    """分页信息模型"""
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_items: int = Field(..., description="总项目数")
    total_pages: int = Field(..., description="总页数")
```

**b) Update `UQMResponse` model:**

The `pagination` object will be nested inside `execution_info` for a clean response structure.

```python
// src/api/models.py

class UQMResponse(BaseModel):
    """UQM响应数据模型"""
    # ... existing fields ...
    execution_info: Dict[str, Any] = Field(default_factory=dict, description="执行信息")
    # The 'pagination' key will now be part of the execution_info dictionary
```

In the response `schema_extra`, this would look like:
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

### Step 2: Update `QueryStep` for Pagination Logic (`src/steps/query_step.py`)

The `_execute_with_database` method will be updated to handle the dual-query logic.

**a) Modify `QueryStep.execute`'s return signature:**

It will now return a dictionary containing both the data and the total count: `{"data": [...], "total_count": ...}`.

**b) Implement the dual-query logic in `_execute_with_database`:**

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
    # Use limit/offset from the step's own config as a default
    limit = self.config.get("limit")
    offset = self.config.get("offset")

    # If pagination options are passed in the context, they trigger the pagination logic
    if page and page_size:
        # 1. Build and execute the COUNT query to get the total number of items
        count_query = self.build_count_query()
        count_result = await connector.execute_query(count_query)
        total_count = count_result[0].get('total', 0) if count_result else 0

        # 2. Calculate limit and offset for the data query based on pagination params
        limit = page_size
        offset = (page - 1) * page_size
    
    # 3. Build and execute the main data query with the correct limit and offset
    self.config['limit'] = limit
    self.config['offset'] = offset
    data_query = self.build_query()
    data_result = await connector.execute_query(data_query)
    
    return {"data": data_result, "total_count": total_count}

def build_count_query(self) -> str:
    """
    构建用于获取总行数的SQL COUNT查询
    This query is similar to build_query but selects COUNT(*) and omits ORDER BY, LIMIT, OFFSET.
    """
    # Re-use parts from build_query for FROM, JOIN, WHERE, GROUP BY, HAVING
    query = self.sql_builder.build_select_query(
        select_fields=["COUNT(*) as total"],
        from_table=self.config["data_source"],
        joins=self.config.get("joins", []),
        where_conditions=self.config.get("filters", []),
        group_by=self.config.get("group_by", []),
        having=self.config.get("having", [])
    )
    # If there is a GROUP BY, we need to count the number of resulting groups
    if self.config.get("group_by"):
        return f"SELECT COUNT(*) as total FROM ({query}) as subquery"

    return query
```

### Step 3: Adapt `Executor` and `Engine` (`src/core/executor.py`, `src/core/engine.py`)

**a) In `UQMEngine.process`:**

The engine will identify the output step and pass pagination options to the executor.

```python
// src/core/engine.py in process

# ...
output_step_name = processed_data["output"]
output_step_config = next((step for step in processed_data["steps"] if step["name"] == output_step_name), None)

# Pass pagination options to executor ONLY if the output step is a query
pagination_options_for_executor = {}
if output_step_config and output_step_config['type'] == 'query':
    pagination_options_for_executor = {
        "page": options.get("page"),
        "page_size": options.get("page_size")
    }

executor = Executor(
    steps=processed_data["steps"],
    # ... other args
    options=self.options, # Pass all options
    output_step_name=output_step_name,
    pagination_options=pagination_options_for_executor
)
execution_result = await executor.execute()
# ...
# Construct final response with pagination info if applicable
# ...
```

**b) In `Executor._execute_step`:**

The executor will selectively inject pagination options into the context for the final query step.

```python
// src/core/executor.py in _execute_step

# ...
context = self._prepare_execution_context(config)

# Inject pagination options ONLY for the final output query step
if step_name == self.output_step_name and step_type == "query" and self.pagination_options:
    context["options"].update(self.pagination_options)

# Execute the step
step_execution_output = await self._execute_step_by_type(step_type, config, context)

# Handle the new return structure from QueryStep
if step_type == 'query' and isinstance(step_execution_output, dict):
    step_data = step_execution_output.get("data")
    self.step_results[step_name]["total_count"] = step_execution_output.get("total_count")
else:
    step_data = step_execution_output
# ...
```

### Step 4: Example Usage

The example request and response remain the same as in the previous version of the plan, as the user-facing API contract is unchanged. This revised internal logic simply makes it work correctly for all use cases. 