"""
步骤执行器模块
负责按顺序执行UQM定义的各个步骤
"""

import time
import hashlib
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from src.steps.query_step import QueryStep
from src.steps.enrich_step import EnrichStep
from src.steps.pivot_step import PivotStep
from src.steps.unpivot_step import UnpivotStep
from src.steps.union_step import UnionStep
from src.steps.assert_step import AssertStep
from src.core.cache import BaseCacheManager
from src.connectors.base import BaseConnectorManager
from src.utils.logging import LoggerMixin
from src.utils.exceptions import ExecutionError


@dataclass
class ExecutionResult:
    """执行结果数据类"""
    step_results: Dict[str, Any]
    step_data: Dict[str, List[Dict[str, Any]]]
    
    def get_step_data(self, step_name: str) -> Optional[List[Dict[str, Any]]]:
        """获取指定步骤的数据"""
        return self.step_data.get(step_name)


class Executor(LoggerMixin):
    """步骤执行管理器"""
    
    def __init__(self, steps: List[Dict[str, Any]], 
                 connector_manager: BaseConnectorManager,
                 cache_manager: BaseCacheManager,
                 options: Optional[Dict[str, Any]] = None):
        """
        初始化执行器
        
        Args:
            steps: 步骤列表
            connector_manager: 连接器管理器
            cache_manager: 缓存管理器
            options: 执行选项
        """
        self.steps = steps
        self.connector_manager = connector_manager
        self.cache_manager = cache_manager
        self.options = options or {}
        
        # 步骤执行结果存储
        self.step_results: Dict[str, Any] = {}
        self.step_data: Dict[str, List[Dict[str, Any]]] = {}
        
        # 步骤类型映射
        self.step_classes = {
            "query": QueryStep,
            "enrich": EnrichStep,
            "pivot": PivotStep,
            "unpivot": UnpivotStep,
            "union": UnionStep,
            "assert": AssertStep
        }
    
    async def execute(self) -> ExecutionResult:
        """
        执行所有步骤
        
        Returns:
            执行结果
            
        Raises:
            ExecutionError: 执行失败
        """
        try:
            self.log_info("开始执行步骤", step_count=len(self.steps))
            
            for step_config in self.steps:
                step_name = step_config["name"]
                
                try:
                    # 执行单个步骤
                    await self._execute_step(step_config)
                    
                    self.log_info(f"步骤 {step_name} 执行完成")
                    
                except Exception as e:
                    self.log_error(f"步骤 {step_name} 执行失败", error=str(e))
                    
                    # 记录步骤执行失败
                    self.step_results[step_name] = {
                        "type": step_config["type"],
                        "status": "failed",
                        "error": str(e),
                        "execution_time": 0.0,
                        "row_count": 0,
                        "cache_hit": False
                    }
                    
                    # 根据选项决定是否继续执行
                    if not self.options.get("continue_on_error", False):
                        raise ExecutionError(f"步骤 {step_name} 执行失败: {e}")
            
            self.log_info("所有步骤执行完成")
            
            return ExecutionResult(
                step_results=self.step_results,
                step_data=self.step_data
            )
            
        except ExecutionError:
            raise
        except Exception as e:
            self.log_error("步骤执行过程出现未知错误", error=str(e), exc_info=True)
            raise ExecutionError(f"步骤执行失败: {e}")
    
    async def _execute_step(self, step_config: Dict[str, Any]) -> None:
        """
        执行单个步骤
        
        Args:
            step_config: 步骤配置
        """
        step_name = step_config["name"]
        step_type = step_config["type"]
        config = step_config["config"]
        
        start_time = time.time()
        
        try:
            self.log_info(f"开始执行步骤: {step_name} (类型: {step_type})")
            
            # 检查缓存
            cache_key = self._generate_cache_key(step_config)
            cached_data = None
            cache_hit = False
            
            if self.options.get("cache_enabled", False):
                cached_data = await self.cache_manager.get(cache_key)
                if cached_data is not None:
                    cache_hit = True
                    self.log_info(f"步骤 {step_name} 命中缓存")
            
            if cache_hit:
                # 使用缓存数据
                step_data = cached_data
            else:
                # 执行步骤
                step_data = await self._execute_step_by_type(step_type, config)
                
                # 缓存结果
                if self.options.get("cache_enabled", False) and step_data:
                    cache_ttl = self._parse_ttl(config.get("cache_ttl", "1h"))
                    await self.cache_manager.set(cache_key, step_data, cache_ttl)
            
            execution_time = time.time() - start_time
            
            # 记录步骤执行结果
            self.step_results[step_name] = {
                "type": step_type,
                "status": "completed",
                "execution_time": execution_time,
                "row_count": len(step_data) if step_data else 0,
                "cache_hit": cache_hit
            }
            
            # 存储步骤数据
            self.step_data[step_name] = step_data or []
            
            self.log_info(
                f"步骤 {step_name} 执行完成",
                execution_time=execution_time,
                row_count=len(step_data) if step_data else 0,
                cache_hit=cache_hit
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_error(
                f"步骤 {step_name} 执行失败",
                error=str(e),
                execution_time=execution_time
            )
            raise ExecutionError(f"步骤 {step_name} 执行失败: {e}")
    
    async def _execute_step_by_type(self, step_type: str, 
                                   config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据步骤类型执行步骤
        
        Args:
            step_type: 步骤类型
            config: 步骤配置
            
        Returns:
            步骤执行结果数据
        """
        if step_type not in self.step_classes:
            raise ExecutionError(f"不支持的步骤类型: {step_type}")
        
        # 获取步骤类
        step_class = self.step_classes[step_type]
        
        # 创建步骤实例
        step_instance = step_class(config)
        
        # 准备执行上下文
        context = self._prepare_execution_context(config)
        
        # 执行步骤
        result = await step_instance.execute(context)
        
        return result
    
    def _prepare_execution_context(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备步骤执行上下文
        
        Args:
            config: 步骤配置
            
        Returns:
            执行上下文
        """
        context = {
            "connector_manager": self.connector_manager,
            "cache_manager": self.cache_manager,
            "options": self.options,
            "step_data": self.step_data,
            "get_source_data": self._get_source_data
        }
        
        return context
    
    def _get_source_data(self, source_name: Union[str, List[str]]) -> Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
        """
        获取源步骤数据
        
        Args:
            source_name: 源步骤名称或名称列表
            
        Returns:
            源步骤数据
        """
        if isinstance(source_name, str):
            if source_name not in self.step_data:
                raise ExecutionError(f"源步骤数据不存在: {source_name}")
            return self.step_data[source_name]
        
        elif isinstance(source_name, list):
            result = {}
            for name in source_name:
                if name not in self.step_data:
                    raise ExecutionError(f"源步骤数据不存在: {name}")
                result[name] = self.step_data[name]
            return result
        
        else:
            raise ExecutionError(f"无效的源步骤名称类型: {type(source_name)}")
    
    def _generate_cache_key(self, step_config: Dict[str, Any]) -> str:
        """
        生成步骤缓存键
        
        Args:
            step_config: 步骤配置
            
        Returns:
            缓存键
        """
        try:
            # 创建包含步骤配置和依赖数据的字典
            cache_data = {
                "step_config": step_config,
                "dependency_data": {}
            }
            
            # 添加依赖步骤的数据hash
            config = step_config.get("config", {})
            if "source" in config:
                source = config["source"]
                if isinstance(source, str):
                    cache_data["dependency_data"][source] = self._get_data_hash(source)
                elif isinstance(source, list):
                    for src in source:
                        cache_data["dependency_data"][src] = self._get_data_hash(src)
            
            if "sources" in config:
                sources = config["sources"]
                if isinstance(sources, list):
                    for src in sources:
                        cache_data["dependency_data"][src] = self._get_data_hash(src)
            
            # 序列化并生成hash
            import json
            data_str = json.dumps(cache_data, sort_keys=True)
            cache_key = hashlib.md5(data_str.encode('utf-8')).hexdigest()
            
            step_name = step_config["name"]
            return f"step_cache:{step_name}:{cache_key}"
            
        except Exception as e:
            self.log_error("生成步骤缓存键失败", error=str(e))
            # 如果生成缓存键失败，返回一个基于时间的键（不会命中缓存）
            step_name = step_config.get("name", "unknown")
            return f"step_cache:{step_name}:no_cache_{int(time.time())}"
    
    def _get_data_hash(self, step_name: str) -> str:
        """
        获取步骤数据的hash值
        
        Args:
            step_name: 步骤名称
            
        Returns:
            数据hash值
        """
        try:
            if step_name not in self.step_data:
                return "no_data"
            
            import json
            data_str = json.dumps(self.step_data[step_name], sort_keys=True)
            return hashlib.md5(data_str.encode('utf-8')).hexdigest()
            
        except Exception:
            return "hash_error"
    
    def _parse_ttl(self, ttl_str: str) -> int:
        """
        解析TTL字符串
        
        Args:
            ttl_str: TTL字符串 (如: "1h", "30m", "3600s")
            
        Returns:
            TTL秒数
        """
        try:
            if isinstance(ttl_str, int):
                return ttl_str
            
            if not isinstance(ttl_str, str):
                return 3600  # 默认1小时
            
            ttl_str = ttl_str.lower().strip()
            
            # 解析时间单位
            if ttl_str.endswith('s'):
                return int(ttl_str[:-1])
            elif ttl_str.endswith('m'):
                return int(ttl_str[:-1]) * 60
            elif ttl_str.endswith('h'):
                return int(ttl_str[:-1]) * 3600
            elif ttl_str.endswith('d'):
                return int(ttl_str[:-1]) * 86400
            else:
                # 假设是秒数
                return int(ttl_str)
                
        except (ValueError, TypeError):
            self.log_warning(f"无法解析TTL字符串: {ttl_str}，使用默认值3600秒")
            return 3600
