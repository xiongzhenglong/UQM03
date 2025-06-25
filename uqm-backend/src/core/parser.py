"""
UQM JSON解析器模块
负责解析和验证UQM JSON定义
"""

import json
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path

import jsonschema
from jsonschema import validate, ValidationError as JsonSchemaValidationError

from src.api.models import ValidationError as UQMValidationError, ValidationResponse
from src.utils.logging import LoggerMixin
from src.utils.exceptions import ParseError, ValidationError


class UQMParser(LoggerMixin):
    """UQM数据解析器"""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        初始化UQM解析器
        
        Args:
            schema_path: UQM Schema文件路径
        """
        self.schema_path = schema_path
        self.schema = None
        
        if schema_path:
            self.schema = self._load_schema(schema_path)
        else:
            # 使用内置的基础Schema
            self.schema = self._get_default_schema()
    
    def parse(self, uqm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析UQM数据
        
        Args:
            uqm_data: UQM JSON数据
            
        Returns:
            解析后的UQM数据
            
        Raises:
            ParseError: 解析失败
        """
        try:
            self.log_info("开始解析UQM数据")
            
            # 验证基本结构
            self._validate_basic_structure(uqm_data)
            
            # 提取各个组件
            metadata = self.extract_metadata(uqm_data)
            steps = self.extract_steps(uqm_data)
            parameters = self.extract_parameters(uqm_data)
            output_step = self.get_output_step(uqm_data)
            
            # 验证步骤依赖关系
            self._validate_step_dependencies(steps)
            
            # 解析步骤执行顺序
            execution_order = self._resolve_step_order(steps)
            
            parsed_data = {
                "metadata": metadata,
                "steps": steps,
                "parameters": parameters,
                "output": output_step,
                "execution_order": execution_order
            }
            
            self.log_info(
                "UQM数据解析完成",
                step_count=len(steps),
                output_step=output_step
            )
            
            return parsed_data
            
        except Exception as e:
            self.log_error("UQM数据解析失败", error=str(e))
            raise ParseError(f"UQM数据解析失败: {e}")
    
    def extract_steps(self, uqm_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        提取步骤列表
        
        Args:
            uqm_data: UQM数据
            
        Returns:
            步骤列表
        """
        steps = uqm_data.get("steps", [])
        
        if not isinstance(steps, list):
            raise ParseError("steps必须是一个数组")
        
        if not steps:
            raise ParseError("至少需要定义一个步骤")
        
        # 验证每个步骤的基本结构
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ParseError(f"步骤 {i} 必须是一个对象")
            
            if "name" not in step:
                raise ParseError(f"步骤 {i} 缺少name字段")
            
            if "type" not in step:
                raise ParseError(f"步骤 {step['name']} 缺少type字段")
            
            if "config" not in step:
                raise ParseError(f"步骤 {step['name']} 缺少config字段")
        
        return steps
    
    def get_output_step(self, uqm_data: Dict[str, Any]) -> str:
        """
        获取输出步骤名称
        
        Args:
            uqm_data: UQM数据
            
        Returns:
            输出步骤名称
        """
        output_step = uqm_data.get("output")
        
        if not output_step:
            # 如果没有指定输出步骤，使用最后一个步骤
            steps = uqm_data.get("steps", [])
            if steps:
                output_step = steps[-1]["name"]
            else:
                raise ParseError("无法确定输出步骤")
        
        # 验证输出步骤是否存在
        step_names = {step["name"] for step in uqm_data.get("steps", [])}
        if output_step not in step_names:
            raise ParseError(f"输出步骤 '{output_step}' 不存在")
        
        return output_step
    
    def extract_metadata(self, uqm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取元数据
        
        Args:
            uqm_data: UQM数据
            
        Returns:
            元数据字典
        """
        metadata = uqm_data.get("metadata", {})
        
        if not isinstance(metadata, dict):
            raise ParseError("metadata必须是一个对象")
        
        # 设置默认值
        default_metadata = {
            "name": "未命名查询",
            "description": "",
            "version": "1.0",
            "author": "",
            "tags": []
        }
        
        # 合并默认值和用户提供的元数据
        result = {**default_metadata, **metadata}
        
        return result
    
    def extract_parameters(self, uqm_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        提取参数定义
        
        Args:
            uqm_data: UQM数据
            
        Returns:
            参数定义列表
        """
        parameters = uqm_data.get("parameters", [])
        
        if not isinstance(parameters, list):
            raise ParseError("parameters必须是一个数组")
        
        # 验证每个参数定义
        for i, param in enumerate(parameters):
            if not isinstance(param, dict):
                raise ParseError(f"参数 {i} 必须是一个对象")
            
            if "name" not in param:
                raise ParseError(f"参数 {i} 缺少name字段")
            
            if "type" not in param:
                raise ParseError(f"参数 {param['name']} 缺少type字段")
        
        return parameters
    
    def validate_schema(self, uqm_data: Dict[str, Any]) -> ValidationResponse:
        """
        验证UQM数据是否符合Schema
        
        Args:
            uqm_data: UQM数据
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        try:
            # 如果有Schema，进行Schema验证
            if self.schema:
                try:
                    validate(instance=uqm_data, schema=self.schema)
                except JsonSchemaValidationError as e:
                    errors.append(UQMValidationError(
                        field=".".join(str(x) for x in e.path),
                        message=e.message,
                        value=e.instance
                    ))
            
            # 进行业务逻辑验证
            try:
                self.parse(uqm_data)
            except ParseError as e:
                errors.append(UQMValidationError(
                    field="general",
                    message=str(e),
                    value=None
                ))
            
            # 检查潜在的警告
            warnings.extend(self._check_warnings(uqm_data))
            
            return ValidationResponse(
                valid=len(errors) == 0,
                errors=errors if errors else None,
                warnings=warnings if warnings else None
            )
            
        except Exception as e:
            self.log_error("UQM验证过程出现错误", error=str(e))
            return ValidationResponse(
                valid=False,
                errors=[UQMValidationError(
                    field="validation",
                    message=f"验证过程出现错误: {e}",
                    value=None
                )]
            )
    
    def _validate_basic_structure(self, uqm_data: Dict[str, Any]) -> None:
        """验证UQM基本结构"""
        if not isinstance(uqm_data, dict):
            raise ParseError("UQM数据必须是一个JSON对象")
        
        required_fields = ["steps"]
        for field in required_fields:
            if field not in uqm_data:
                raise ParseError(f"缺少必需字段: {field}")
    
    def _validate_step_dependencies(self, steps: List[Dict[str, Any]]) -> None:
        """
        验证步骤依赖关系
        
        Args:
            steps: 步骤列表
        """
        step_names = {step["name"] for step in steps}
        
        for step in steps:
            step_name = step["name"]
            step_config = step.get("config", {})
            
            # 检查source引用
            if "source" in step_config:
                source = step_config["source"]
                if isinstance(source, str) and source not in step_names:
                    raise ParseError(f"步骤 '{step_name}' 引用了不存在的源步骤: '{source}'")
                elif isinstance(source, list):
                    for src in source:
                        if src not in step_names:
                            raise ParseError(f"步骤 '{step_name}' 引用了不存在的源步骤: '{src}'")
            
            # 检查sources引用（用于union步骤）
            if "sources" in step_config:
                sources = step_config["sources"]
                if isinstance(sources, list):
                    for src in sources:
                        if src not in step_names:
                            raise ParseError(f"步骤 '{step_name}' 引用了不存在的源步骤: '{src}'")
    
    def _resolve_step_order(self, steps: List[Dict[str, Any]]) -> List[str]:
        """
        解析步骤执行顺序（拓扑排序）
        
        Args:
            steps: 步骤列表
            
        Returns:
            按执行顺序排列的步骤名称列表
        """
        # 构建依赖图
        dependencies = {}
        step_names = set()
        
        for step in steps:
            step_name = step["name"]
            step_names.add(step_name)
            dependencies[step_name] = set()
            
            step_config = step.get("config", {})
            
            # 添加source依赖
            if "source" in step_config:
                source = step_config["source"]
                if isinstance(source, str):
                    dependencies[step_name].add(source)
                elif isinstance(source, list):
                    dependencies[step_name].update(source)
            
            # 添加sources依赖
            if "sources" in step_config:
                sources = step_config["sources"]
                if isinstance(sources, list):
                    dependencies[step_name].update(sources)
        
        # 拓扑排序
        result = []
        visited = set()
        temp_visited = set()
        
        def visit(node: str):
            if node in temp_visited:
                raise ParseError(f"检测到循环依赖，涉及步骤: {node}")
            
            if node not in visited:
                temp_visited.add(node)
                
                for dep in dependencies.get(node, set()):
                    visit(dep)
                
                temp_visited.remove(node)
                visited.add(node)
                result.append(node)
        
        for step_name in step_names:
            if step_name not in visited:
                visit(step_name)
        
        return result
    
    def _check_warnings(self, uqm_data: Dict[str, Any]) -> List[str]:
        """检查潜在的警告问题"""
        warnings = []
        
        # 检查元数据完整性
        metadata = uqm_data.get("metadata", {})
        if not metadata.get("description"):
            warnings.append("建议添加查询描述")
        
        if not metadata.get("author"):
            warnings.append("建议添加作者信息")
        
        # 检查步骤数量
        steps = uqm_data.get("steps", [])
        if len(steps) > 10:
            warnings.append("步骤数量较多，可能影响性能")
        
        # 检查参数使用
        parameters = uqm_data.get("parameters", [])
        if parameters:
            param_names = {param["name"] for param in parameters}
            uqm_str = json.dumps(uqm_data)
            
            for param_name in param_names:
                if f"${param_name}" not in uqm_str:
                    warnings.append(f"参数 '{param_name}' 定义了但未使用")
        
        return warnings
    
    def _load_schema(self, schema_path: str) -> Dict[str, Any]:
        """
        加载UQM Schema文件
        
        Args:
            schema_path: Schema文件路径
            
        Returns:
            Schema字典
        """
        try:
            schema_file = Path(schema_path)
            if not schema_file.exists():
                raise FileNotFoundError(f"Schema文件不存在: {schema_path}")
            
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            self.log_info("UQM Schema加载成功", schema_path=schema_path)
            return schema
            
        except Exception as e:
            self.log_error("加载UQM Schema失败", error=str(e))
            raise ParseError(f"加载UQM Schema失败: {e}")
    
    def _get_default_schema(self) -> Dict[str, Any]:
        """获取默认的UQM Schema"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["steps"],
            "properties": {
                "metadata": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "version": {"type": "string"},
                        "author": {"type": "string"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "parameters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "type"],
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "default": {},
                            "required": {"type": "boolean"},
                            "description": {"type": "string"}
                        }
                    }
                },
                "steps": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "type", "config"],
                        "properties": {
                            "name": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": ["query", "enrich", "pivot", "unpivot", "union", "assert"]
                            },
                            "config": {"type": "object"}
                        }
                    }
                },
                "output": {"type": "string"}
            }
        }
