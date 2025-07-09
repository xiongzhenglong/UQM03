"""
UQM执行引擎主类
负责协调整个查询执行流程
"""

import time
import hashlib
from typing import Any, Dict, List, Optional
from functools import lru_cache

from src.api.models import UQMResponse, StepResult, Metadata, StepType
from src.core.parser import UQMParser
from src.core.executor import Executor
from src.core.cache import get_cache_manager
from src.connectors.base import get_connector_manager
from src.utils.logging import LoggerMixin
from src.utils.exceptions import ValidationError, ExecutionError
from src.config.settings import get_settings


class UQMEngine(LoggerMixin):
    """UQM执行引擎主类"""
    
    def __init__(self):
        """初始化UQM执行引擎"""
        self.parser = UQMParser()
        self.cache_manager = get_cache_manager()
        self.connector_manager = get_connector_manager()
        self.settings = get_settings()
    
    async def process(self, uqm_data: Dict[str, Any], 
                     parameters: Optional[Dict[str, Any]] = None,
                     options: Optional[Dict[str, Any]] = None) -> UQMResponse:
        """
        处理UQM查询的主入口方法
        
        Args:
            uqm_data: UQM JSON数据
            parameters: 查询参数
            options: 执行选项
            
        Returns:
            查询执行结果
            
        Raises:
            ValidationError: 验证失败
            ExecutionError: 执行失败
        """
        start_time = time.time()
        
        try:
            self.log_info(
                "开始处理UQM查询",
                uqm_name=uqm_data.get("metadata", {}).get("name", "未命名")
            )
            
            # 参数预处理
            parameters = parameters or {}
            options = options or {}
            
            # 解析UQM数据
            parsed_data = self.parser.parse(uqm_data)
            
            # 参数替换
            processed_data = self._substitute_parameters(parsed_data, parameters)
            
            # 生成缓存键
            cache_key = self._generate_cache_key(processed_data, parameters)
            
            # 检查缓存
            cached_result = None
            if options.get("cache_enabled", False):
                cached_result = await self.cache_manager.get(cache_key)
                if cached_result:
                    self.log_info("命中缓存", cache_key=cache_key)
                    return cached_result
            
            # 创建执行器并执行
            executor = Executor(
                steps=processed_data["steps"],
                connector_manager=self.connector_manager,
                cache_manager=self.cache_manager,
                options=options
            )
            
            execution_result = await executor.execute()
            
            # 获取输出步骤的结果
            output_step = processed_data["output"]
            output_data = execution_result.get_step_data(output_step)
            
            # 构建响应
            execution_time = time.time() - start_time
            response = UQMResponse(
                success=True,
                data=output_data,
                metadata=Metadata(**processed_data["metadata"]),
                execution_info={
                    "total_time": execution_time,
                    "row_count": len(output_data) if output_data else 0,
                    "cache_hit": False,
                    "steps_executed": len(processed_data["steps"])
                },
                step_results=self._build_step_results(execution_result.step_results)
            )
            
            # 缓存结果
            if options.get("cache_enabled", False):
                cache_ttl = options.get("cache_ttl", self.settings.CACHE_DEFAULT_TIMEOUT)
                await self.cache_manager.set(cache_key, response, cache_ttl)
            
            self.log_info(
                "UQM查询处理完成",
                execution_time=execution_time,
                row_count=len(output_data) if output_data else 0
            )
            
            return response
            
        except ValidationError as e:
            self.log_error("UQM查询验证失败", error=str(e))
            raise
            
        except ExecutionError as e:
            self.log_error("UQM查询执行失败", error=str(e))
            raise
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_error(
                "UQM查询处理出现未知错误",
                error=str(e),
                execution_time=execution_time,
                exc_info=True
            )
            raise ExecutionError(f"查询处理失败: {e}")
    
    async def validate_query(self, uqm_data: Dict[str, Any]) -> Any:
        """
        验证UQM查询有效性
        
        Args:
            uqm_data: UQM JSON数据
            
        Returns:
            验证结果
        """
        try:
            self.log_info("开始验证UQM查询")
            
            # 使用解析器进行验证
            validation_result = self.parser.validate_schema(uqm_data)
            
            self.log_info(
                "UQM查询验证完成",
                valid=validation_result.valid,
                error_count=len(validation_result.errors) if validation_result.errors else 0
            )
            
            return validation_result
            
        except Exception as e:
            self.log_error("UQM查询验证出现错误", error=str(e))
            raise ValidationError(f"查询验证失败: {e}")
    
    def _substitute_parameters(self, uqm_data: Dict[str, Any], 
                             parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        参数替换处理，支持条件过滤器
        
        Args:
            uqm_data: 解析后的UQM数据
            parameters: 参数值字典
            
        Returns:
            参数替换后的UQM数据
        """
        try:
            self.log_info("开始参数替换", parameter_count=len(parameters))
            
            # 深拷贝数据以避免修改原始数据
            import copy
            processed_data = copy.deepcopy(uqm_data)
            
            # 先处理条件过滤器
            processed_data = self._process_conditional_filters(processed_data, parameters)
            
            # 将数据转换为JSON字符串进行参数替换
            import json
            data_str = json.dumps(processed_data, ensure_ascii=False)
            
            # 替换参数
            for param_name, param_value in parameters.items():
                # 支持两种格式：${param_name} 和 $param_name
                placeholder_with_braces = f"${{{param_name}}}"
                placeholder_without_braces = f"${param_name}"
                
                # 根据参数值类型进行替换
                if isinstance(param_value, str):
                    replacement = json.dumps(param_value, ensure_ascii=False)
                elif isinstance(param_value, (list, dict)):
                    replacement = json.dumps(param_value, ensure_ascii=False)
                else:
                    replacement = json.dumps(param_value, ensure_ascii=False)
                
                # 先处理带大括号的格式 ${param_name}
                # 先处理带引号的占位符（用于字符串值）
                data_str = data_str.replace(f'"{placeholder_with_braces}"', replacement)
                # 再处理不带引号的占位符（用于非字符串值）
                data_str = data_str.replace(placeholder_with_braces, replacement)
                
                # 再处理不带大括号的格式 $param_name
                # 先处理带引号的占位符（用于字符串值）
                data_str = data_str.replace(f'"{placeholder_without_braces}"', replacement)
                # 再处理不带引号的占位符（用于非字符串值）
                data_str = data_str.replace(placeholder_without_braces, replacement)
            
            # 转换回字典
            processed_data = json.loads(data_str)
            
            self.log_info("参数替换完成")
            return processed_data
            
        except Exception as e:
            self.log_error("参数替换失败", error=str(e))
            raise ValidationError(f"参数替换失败: {e}")
    
    def _process_conditional_filters(self, uqm_data: Dict[str, Any], 
                                   parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理条件过滤器，移除不满足条件的过滤器
        
        Args:
            uqm_data: UQM数据
            parameters: 参数值字典
            
        Returns:
            处理后的UQM数据
        """
        try:
            steps = uqm_data.get("steps", [])
            
            for step in steps:
                if step.get("type") == "query":
                    config = step.get("config", {})
                    filters = config.get("filters", [])
                    
                    # 过滤掉不满足条件的过滤器
                    valid_filters = []
                    for filter_config in filters:
                        if self._should_include_filter(filter_config, parameters):
                            valid_filters.append(filter_config)
                        else:
                            self.log_info(
                                "条件过滤器跳过",
                                filter_field=filter_config.get("field"),
                                condition=filter_config.get("conditional")
                            )
                    
                    config["filters"] = valid_filters
            
            return uqm_data
            
        except Exception as e:
            self.log_error("条件过滤器处理失败", error=str(e))
            raise ValidationError(f"条件过滤器处理失败: {e}")
    
    def _should_include_filter(self, filter_config: Dict[str, Any], 
                              parameters: Dict[str, Any]) -> bool:
        """
        判断是否应该包含该过滤器
        
        Args:
            filter_config: 过滤器配置
            parameters: 参数值字典
            
        Returns:
            是否包含该过滤器
        """
        conditional = filter_config.get("conditional")
        if not conditional:
            # 没有条件配置，直接包含
            return True
        
        condition_type = conditional.get("type")
        
        if condition_type == "parameter_exists":
            param_name = conditional.get("parameter")
            return param_name in parameters
        
        elif condition_type == "parameter_not_empty":
            param_name = conditional.get("parameter")
            empty_values = conditional.get("empty_values", [None])
            
            if param_name not in parameters:
                return False
            
            param_value = parameters[param_name]
            return param_value not in empty_values
        
        elif condition_type == "all_parameters_exist":
            param_names = conditional.get("parameters", [])
            return all(param in parameters for param in param_names)
        
        elif condition_type == "expression":
            expression = conditional.get("expression", "")
            try:
                # 简单的表达式评估（可以扩展为更复杂的表达式解析器）
                return self._evaluate_conditional_expression(expression, parameters)
            except Exception as e:
                self.log_warning(f"条件表达式评估失败: {e}")
                return False
        
        else:
            self.log_warning(f"不支持的条件类型: {condition_type}")
            return True
    
    def _evaluate_conditional_expression(self, expression: str, 
                                       parameters: Dict[str, Any]) -> bool:
        """
        评估条件表达式
        
        Args:
            expression: 条件表达式
            parameters: 参数值字典
            
        Returns:
            表达式结果
        """
        # 替换参数占位符
        eval_expression = expression
        
        # 检查表达式中是否有未提供的参数
        import re
        param_pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*)'
        required_params = re.findall(param_pattern, expression)
        
        for param_name in required_params:
            placeholder = f"${param_name}"
            
            if param_name not in parameters:
                # 参数不存在，用null替换
                replacement = "None"
            else:
                param_value = parameters[param_name]
                # 根据参数值类型进行替换
                if param_value is None:
                    replacement = "None"
                elif isinstance(param_value, str):
                    replacement = f'"{param_value}"'
                elif isinstance(param_value, bool):
                    replacement = "True" if param_value else "False"
                elif isinstance(param_value, list):
                    replacement = str(param_value)
                else:
                    replacement = str(param_value)
            
            eval_expression = eval_expression.replace(placeholder, replacement)
        
        # 简单的表达式评估（这里可以使用更安全的表达式解析器）
        try:
            # 将JavaScript式的null转换为Python的None
            eval_expression = eval_expression.replace("null", "None")
            eval_expression = eval_expression.replace("&&", " and ")
            eval_expression = eval_expression.replace("||", " or ")
            eval_expression = eval_expression.replace("!=", " != ")
            eval_expression = eval_expression.replace("==", " == ")
            
            # 安全评估表达式
            result = bool(eval(eval_expression))
            self.log_info(f"表达式评估成功: {expression} -> {eval_expression} = {result}")
            return result
        except Exception as e:
            self.log_warning(f"表达式评估失败: {expression} -> {eval_expression}, 错误: {e}")
            return False
    
    def _generate_cache_key(self, uqm_data: Dict[str, Any], 
                           parameters: Dict[str, Any]) -> str:
        """
        生成缓存键
        
        Args:
            uqm_data: UQM数据
            parameters: 参数
            
        Returns:
            缓存键
        """
        try:
            # 创建包含UQM数据和参数的字典
            cache_data = {
                "uqm": uqm_data,
                "parameters": parameters
            }
            
            # 序列化并生成hash
            import json
            data_str = json.dumps(cache_data, sort_keys=True)
            cache_key = hashlib.md5(data_str.encode('utf-8')).hexdigest()
            
            return f"uqm_cache:{cache_key}"
            
        except Exception as e:
            self.log_error("生成缓存键失败", error=str(e))
            # 如果生成缓存键失败，返回一个基于时间的键（不会命中缓存）
            return f"uqm_cache:no_cache_{int(time.time())}"
    
    def _build_step_results(self, step_results: Dict[str, Any]) -> List[StepResult]:
        """
        构建步骤结果列表
        
        Args:
            step_results: 执行器返回的步骤结果
            
        Returns:
            步骤结果列表
        """
        results = []
        
        for step_name, step_data in step_results.items():
            result = StepResult(
                step_name=step_name,
                step_type=StepType(step_data.get("type", "query")),
                status=step_data.get("status", "completed"),
                data=step_data.get("data"),
                row_count=step_data.get("row_count", 0),
                execution_time=step_data.get("execution_time", 0.0),
                cache_hit=step_data.get("cache_hit", False),
                error=step_data.get("error")
            )
            results.append(result)
        
        return results


# 全局引擎实例
_uqm_engine: Optional[UQMEngine] = None


@lru_cache()
def get_uqm_engine() -> UQMEngine:
    """获取UQM引擎实例(单例模式)"""
    global _uqm_engine
    
    if _uqm_engine is None:
        _uqm_engine = UQMEngine()
    
    return _uqm_engine
