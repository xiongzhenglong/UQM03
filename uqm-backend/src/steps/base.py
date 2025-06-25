"""
步骤基类定义
定义所有步骤的抽象基类和通用功能
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.utils.logging import LoggerMixin
from src.utils.exceptions import ExecutionError, ValidationError


class BaseStep(ABC, LoggerMixin):
    """所有步骤的抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化步骤
        
        Args:
            config: 步骤配置
        """
        self.config = config
        self.step_name = config.get("name", self.__class__.__name__)
        
        # 验证配置
        self.validate()
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        执行步骤（抽象方法）
        
        Args:
            context: 执行上下文
            
        Returns:
            步骤执行结果
        """
        pass
    
    @abstractmethod
    def validate(self) -> None:
        """验证步骤配置（抽象方法）"""
        pass
    
    def _prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备执行上下文
        
        Args:
            context: 原始上下文
            
        Returns:
            准备好的上下文
        """
        # 添加步骤特定的上下文信息
        prepared_context = context.copy()
        prepared_context["step_config"] = self.config
        prepared_context["step_name"] = self.step_name
        
        return prepared_context
    
    def _log_execution(self, start_time: float, end_time: float, 
                      result_count: int = 0) -> None:
        """
        记录执行日志
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            result_count: 结果数量
        """
        execution_time = end_time - start_time
        
        self.log_info(
            f"步骤 {self.step_name} 执行完成",
            execution_time=execution_time,
            result_count=result_count
        )
    
    def _handle_error(self, error: Exception) -> None:
        """
        处理执行错误
        
        Args:
            error: 错误信息
        """
        self.log_error(
            f"步骤 {self.step_name} 执行失败",
            error=str(error),
            exc_info=True
        )
        
        # 根据错误类型抛出相应的异常
        if isinstance(error, (ValidationError, ExecutionError)):
            raise error
        else:
            raise ExecutionError(f"步骤 {self.step_name} 执行失败: {error}")
    
    def _validate_required_config(self, required_fields: List[str]) -> None:
        """
        验证必需的配置字段
        
        Args:
            required_fields: 必需字段列表
        """
        for field in required_fields:
            if field not in self.config:
                raise ValidationError(
                    f"步骤 {self.step_name} 缺少必需配置: {field}"
                )
    
    def _get_config_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    async def _execute_with_timing(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        带计时的执行方法
        
        Args:
            context: 执行上下文
            
        Returns:
            执行结果
        """
        start_time = time.time()
        
        try:
            self.log_info(f"开始执行步骤: {self.step_name}")
            
            # 准备上下文
            prepared_context = self._prepare_context(context)
            
            # 执行步骤
            result = await self.execute(prepared_context)
            
            end_time = time.time()
            
            # 记录执行日志
            self._log_execution(
                start_time=start_time,
                end_time=end_time,
                result_count=len(result) if result else 0
            )
            
            return result
            
        except Exception as e:
            end_time = time.time()
            self._handle_error(e)
    
    def get_step_type(self) -> str:
        """
        获取步骤类型
        
        Returns:
            步骤类型
        """
        # 从类名推断步骤类型
        class_name = self.__class__.__name__
        if class_name.endswith("Step"):
            step_type = class_name[:-4].lower()
        else:
            step_type = class_name.lower()
        
        return step_type
    
    def get_dependencies(self) -> List[str]:
        """
        获取步骤依赖
        
        Returns:
            依赖步骤列表
        """
        dependencies = []
        
        # 检查source配置
        source = self.config.get("source")
        if source:
            if isinstance(source, str):
                dependencies.append(source)
            elif isinstance(source, list):
                dependencies.extend(source)
        
        # 检查sources配置
        sources = self.config.get("sources")
        if sources and isinstance(sources, list):
            dependencies.extend(sources)
        
        return dependencies
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.__class__.__name__}(name={self.step_name})"
    
    def __repr__(self) -> str:
        """对象表示"""
        return f"{self.__class__.__name__}(name={self.step_name}, config={self.config})"
