"""
AI服务模块
提供自然语言到UQM JSON Schema的转换功能
"""

import os
import json
import re
from functools import lru_cache
from typing import Dict, Any, Optional, List
import httpx  # 使用httpx进行异步HTTP请求
import logging

from src.config.settings import get_settings  # 恢复这个重要的导入

# from .data_analyzer import get_data_analyzer # 移除复杂的data_analyzer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AIService:
    """AI服务类，用于生成UQM JSON Schema"""
    
    def __init__(self):
        """初始化AI服务，加载配置"""
        settings = get_settings()
        self.api_base = settings.AI_API_BASE
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # 从配置中获取文件名
        self.guide_file = settings.UQM_GUIDE_FILE
        self.schema_file = settings.DB_SCHEMA_FILE

    @lru_cache()
    def _load_guide_content(self) -> str:
        """加载UQM指南内容"""
        try:
            # 尝试从项目根目录的不同层级加载
            guide_paths = [
                self.guide_file,
                f"../{self.guide_file}",
                f"../../{self.guide_file}"
            ]
            
            for path in guide_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        logger.info(f"成功加载UQM指南: {path}")
                        return content
            
            logger.warning(f"未找到UQM指南文件 '{self.guide_file}'，使用默认内容")
            return self._get_default_guide_content()
            
        except Exception as e:
            logger.error(f"加载UQM指南失败: {e}")
            return self._get_default_guide_content()
    
    @lru_cache()
    def _load_schema_content(self) -> str:
        """加载数据库结构内容"""
        try:
            # 尝试从项目根目录的不同层级加载
            schema_paths = [
                self.schema_file,
                f"../{self.schema_file}",
                f"../../{self.schema_file}"
            ]
            
            for path in schema_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        logger.info(f"成功加载数据库结构: {path}")
                        return content
            
            logger.warning(f"未找到数据库结构文件 '{self.schema_file}'，使用默认内容")
            return self._get_default_schema_content()
            
        except Exception as e:
            logger.error(f"加载数据库结构失败: {e}")
            return self._get_default_schema_content()
    
    def _get_default_guide_content(self) -> str:
        """获取默认的UQM指南内容"""
        return """
# UQM JSON Schema 指南

## 基本结构
UQM查询由以下部分组成：
- metadata: 查询元数据
- steps: 查询步骤
- output: 输出配置

## 步骤类型
- query: 基础查询
- enrich: 数据丰富
- pivot: 数据透视
- unpivot: 数据逆透视
- union: 数据合并
- assert: 数据断言

## 字段引用格式
- 表名.字段名
- 参数化使用${参数名}格式

## 聚合计算
- 使用calculated_fields进行聚合计算
- 聚合查询需要配合group_by使用
"""
    
    def _get_default_schema_content(self) -> str:
        """获取默认的数据库结构内容"""
        return """
# 数据库表结构

## 用户表 (users)
- id: 用户ID (主键)
- name: 用户姓名
- email: 邮箱
- created_at: 创建时间
- status: 状态

## 订单表 (orders)
- id: 订单ID (主键)
- user_id: 用户ID (外键)
- amount: 订单金额
- status: 订单状态
- created_at: 创建时间

## 产品表 (products)
- id: 产品ID (主键)
- name: 产品名称
- price: 价格
- category: 分类
- stock: 库存
"""
    
    async def generate_uqm_schema(self, natural_language_query: str) -> Optional[Dict[str, Any]]:
        """
        根据自然语言查询生成UQM JSON Schema
        
        Args:
            natural_language_query: 自然语言查询描述
            
        Returns:
            生成的UQM JSON Schema或None
        """
        try:
            # 检查是否为模拟模式
            if os.getenv("AI_MOCK_MODE", "false").lower() == "true":
                logger.info("使用模拟模式生成Schema")
                return self._generate_mock_schema(natural_language_query)
            
            prompt = self._build_prompt(natural_language_query)
            
            response = await self._call_ai_api(prompt)
            if not response:
                return None
            
            # 提取JSON
            schema = self._extract_json_from_response(response)
            if not schema:
                return None
            
            # 验证Schema结构
            if self._validate_schema_structure(schema):
                logger.info("成功生成UQM Schema")
                return schema
            else:
                logger.error("生成的Schema结构无效")
                return None
                
        except Exception as e:
            logger.error(f"生成UQM Schema失败: {e}")
            return None

    async def generate_visualization_code(self, data: List[Dict[str, Any]], query: str, visualization_type: str = "auto") -> Optional[Dict[str, Any]]:
        """
        根据数据和查询生成可视化代码
        
        Args:
            data: 要可视化的数据
            query: 用户查询描述
            visualization_type: 可视化类型 ("table", "chart", "auto")
            
        Returns:
            生成的可视化配置或None
        """
        try:
            # 检查是否为模拟模式
            if os.getenv("AI_MOCK_MODE", "false").lower() == "true":
                logger.info("使用模拟模式生成可视化代码")
                return self._generate_mock_visualization(data, query, visualization_type)
            
            prompt = self._build_visualization_prompt(data, query, visualization_type)
            
            response = await self._call_ai_api(prompt)
            if not response:
                return None
            
            config = self._extract_json_from_response(response)
            if not config:
                return None
            
            # 强制设置 visualization_type
            if visualization_type != "auto":
                config['visualization_type'] = visualization_type
            elif 'visualization_type' not in config:
                config['visualization_type'] = 'table'  # 默认为表格

            if self._validate_visualization_config(config):
                logger.info("成功生成可视化配置")
                return config
            else:
                logger.error("生成的可视化配置无效")
                # 即使无效，也尝试返回，让前端处理
                return config
                
        except Exception as e:
            logger.error(f"生成可视化代码失败: {e}")
            return {"error": str(e), "visualization_type": "table"}

    def _generate_mock_schema(self, query: str) -> Dict[str, Any]:
        """生成模拟Schema用于测试"""
        return {
            "uqm": {
                "metadata": {
                    "name": f"模拟查询_{query[:10]}",
                    "description": query
                },
                "steps": [
                    {
                        "name": "mock_step",
                        "type": "query",
                        "config": {
                            "data_source": "users",
                            "dimensions": ["id", "name"],
                            "calculated_fields": [],
                            "filters": []
                        }
                    }
                ],
                "output": "mock_step"
            },
            "parameters": {},
            "options": {
                "cache_enabled": True
            }
        }

    def _generate_mock_visualization(self, data: List[Dict[str, Any]], query: str, visualization_type: str) -> Dict[str, Any]:
        """生成模拟可视化配置用于测试"""
        logger.info(f"生成模拟可视化: query='{query}', type='{visualization_type}'")
        
        # 决定最终的可视化类型
        final_vis_type = visualization_type
        if final_vis_type == 'auto':
            if "图" in query or "chart" in query.lower() or "bar" in query.lower() or "pie" in query.lower():
                final_vis_type = "chart"
            else:
                final_vis_type = "table"

        if final_vis_type == "chart" and data:
            # 生成图表配置
            first_row = data[0]
            keys = list(first_row.keys())
            
            category_col = keys[0]
            value_col = keys[1] if len(keys) > 1 else keys[0]

            return {
                "visualization_type": "chart",
                "config": {
                    "title": {"text": f"模拟图表: {query}"},
                    "xAxis": {
                        "type": "category",
                        "data": [row.get(category_col) for row in data],
                        "name": category_col
                    },
                    "yAxis": {"type": "value", "name": value_col},
                    "series": [{"name": value_col, "type": "bar", "data": [row.get(value_col) for row in data]}]
                }
            }
        else:
            # 生成表格配置
            return {
                "visualization_type": "table",
                "config": {
                    "title": {"text": f"模拟表格: {query}"},
                    "columns": [{"title": key, "dataIndex": key, "key": key} for key in data[0].keys()] if data else []
                }
            }

    def _build_prompt(self, query: str) -> str:
        """构建AI提示词（用于生成UQM Schema）"""
        guide_content = self._load_guide_content()
        schema_content = self._load_schema_content()
        
        return f"""
作为UQM专家，请根据以下信息生成标准的UQM JSON配置：

数据库表结构：
{schema_content}

UQM指南：
{guide_content}

查询需求：
{query}

请严格按照UQM JSON格式要求生成完整的API调用结构，包含：
1. uqm字段（包含metadata、steps、output）
2. parameters字段（动态参数）
3. options字段（执行选项）

注意：
- 必须使用calculated_fields进行聚合计算
- 聚合查询需要配合group_by使用
- 字段引用格式：表名.字段名
- 参数化使用${{参数名}}格式
- 返回纯JSON格式，不要包含任何解释文字
- metadata.name应该简洁描述查询目的
- 确保所有必需字段都存在

请返回有效的JSON格式：
"""
    
    async def _call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API（使用httpx异步调用）"""
        try:
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                logger.info("AI API调用成功")
                return content
            else:
                logger.error(f"AI API调用失败: {response.status_code} - {response.text}")
                return None

        except httpx.RequestError as e:
            logger.error(f"AI API请求异常: {e}")
            return None
        except Exception as e:
            logger.error(f"AI API调用时发生未知异常: {e}")
            return None
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """从AI响应中提取JSON"""
        try:
            # 优先从markdown代码块中提取
            json_match = re.search(r'```(json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(2)
                return json.loads(json_str)

            # 如果没有找到markdown块，尝试直接解析整个响应
            # 有时AI会返回一个不被包裹的纯JSON字符串
            json_match_direct = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match_direct:
                json_str = json_match_direct.group()
                return json.loads(json_str)

            logger.error("在AI响应中未找到有效的JSON内容")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}. 响应内容: {response[:500]}")
            return None
    
    def _validate_schema_structure(self, schema: Dict[str, Any]) -> bool:
        """验证Schema结构"""
        try:
            # 检查必需字段
            if 'uqm' not in schema:
                logger.error("Schema缺少uqm字段")
                return False
            
            uqm = schema['uqm']
            required_fields = ['metadata', 'steps']
            for field in required_fields:
                if field not in uqm:
                    logger.error(f"UQM缺少必需字段: {field}")
                    return False
            
            # 检查metadata
            metadata = uqm['metadata']
            if 'name' not in metadata:
                logger.error("metadata缺少name字段")
                return False
            
            # 检查steps
            steps = uqm['steps']
            if not isinstance(steps, list) or len(steps) == 0:
                logger.error("steps必须是非空数组")
                return False
            
            # 检查每个step
            for i, step in enumerate(steps):
                if not isinstance(step, dict):
                    logger.error(f"step {i}必须是对象")
                    return False
                
                if 'name' not in step or 'type' not in step:
                    logger.error(f"step {i}缺少name或type字段")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Schema结构验证失败: {e}")
            return False

    def _build_visualization_prompt(self, data: List[Dict[str, Any]], query: str, visualization_type: str) -> str:
        """构建可视化生成的提示词（只加载必要信息）"""
        # 数据样本
        sample_data = data[:5] if data else []
        try:
            data_preview = json.dumps(sample_data, ensure_ascii=False, indent=2, default=str)
        except TypeError:
            data_preview = "[]"
        
        # 数据库结构
        schema_content = self._load_schema_content()

        prompt = f"""
你是一个专业的数据可视化专家。请根据用户的查询需求和提供的数据结构信息，生成合适的可视化JSON配置。

## 用户查询
{query}

## 数据库表结构 (可参考的上下文)
{schema_content}

## 数据样本 (前5行)
```json
{data_preview}
```

## 可视化类型偏好
{visualization_type} (如果设为'auto'，请根据用户查询和数据结构智能选择'table'或'chart')

## 要求
1.  **严格只返回JSON格式的配置**，不要包含任何其他说明文字或markdown标记。
2.  你的返回结果必须是一个能被 `json.loads()` 直接解析的字符串。
3.  根据用户查询和数据结构，智能选择最合适的可视化方式（`table`或`chart`）。
4.  如果是表格(`table`)，生成Ant Design Table的`columns`配置。**绝对不要在配置中包含`dataSource`字段**。
5.  如果是图表(`chart`)，生成ECharts的`option`配置，包含标题、图例和从数据中提取或计算得出的series。

## 返回的JSON格式示例
```json
{{
  "visualization_type": "table",
  "config": {{
    "columns": [
      {{"title": "列标题", "dataIndex": "字段名", "key": "字段名", "sorter": true}}
    ]
  }}
}}
```

请严格按照以上要求，为用户查询生成最合适的可视化JSON配置：
"""
        return prompt

    def _validate_visualization_config(self, config: Dict[str, Any]) -> bool:
        """验证可视化配置的有效性"""
        try:
            if not isinstance(config, dict):
                return False
            
            if "visualization_type" not in config or "config" not in config:
                return False
            
            viz_type = config["visualization_type"]  # 修复这里的拼写错误
            if viz_type not in ["table", "chart"]:
                return False
            
            if not isinstance(config["config"], dict):
                return False
            
            # 基本验证通过
            return True
            
        except Exception as e:
            logger.error(f"验证可视化配置失败: {e}")
            return False


# 全局AI服务实例
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """获取AI服务实例（单例模式）"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service 