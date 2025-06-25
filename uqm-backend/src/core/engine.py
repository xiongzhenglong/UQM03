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
            if options.get("cache_enabled", True):
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
            if options.get("cache_enabled", True):
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
        参数替换处理
        
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
            
            # 将数据转换为JSON字符串进行参数替换
            import json
            data_str = json.dumps(processed_data)
            
            # 替换参数
            for param_name, param_value in parameters.items():
                placeholder = f"${param_name}"
                # 如果参数值是字符串，需要添加引号
                if isinstance(param_value, str):
                    replacement = json.dumps(param_value)
                else:
                    replacement = json.dumps(param_value)
                
                data_str = data_str.replace(f'"{placeholder}"', replacement)
                data_str = data_str.replace(placeholder, replacement)
            
            # 转换回字典
            processed_data = json.loads(data_str)
            
            self.log_info("参数替换完成")
            return processed_data
            
        except Exception as e:
            self.log_error("参数替换失败", error=str(e))
            raise ValidationError(f"参数替换失败: {e}")
    
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
