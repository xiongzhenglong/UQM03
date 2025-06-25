"""
查询结果缓存管理模块
支持内存缓存和Redis缓存
"""

import json
import pickle
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
from functools import lru_cache

import redis
from src.config.settings import get_settings
from src.utils.logging import LoggerMixin
from src.utils.exceptions import CacheError


class BaseCacheManager(ABC, LoggerMixin):
    """缓存管理器基类"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存数据"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存数据"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """清空所有缓存"""
        pass
    
    @abstractmethod
    async def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        pass


class MemoryCacheManager(BaseCacheManager):
    """内存缓存管理器"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        初始化内存缓存管理器
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认TTL(秒)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.stats_data = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0
        }
    
    async def initialize(self) -> None:
        """初始化缓存管理器"""
        self.log_info("内存缓存管理器初始化完成", max_size=self.max_size)
    
    async def close(self) -> None:
        """关闭缓存管理器"""
        await self.clear()
        self.log_info("内存缓存管理器已关闭")
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        try:
            if key not in self.cache:
                self.stats_data["misses"] += 1
                return None
            
            cache_item = self.cache[key]
            
            # 检查是否过期
            if self._is_expired(cache_item):
                await self.delete(key)
                self.stats_data["misses"] += 1
                return None
            
            # 更新访问时间
            self.access_times[key] = time.time()
            self.stats_data["hits"] += 1
            
            # 反序列化数据
            return self._deserialize_data(cache_item["data"])
            
        except Exception as e:
            self.log_error("获取缓存数据失败", key=key, error=str(e))
            raise CacheError(f"获取缓存数据失败: {e}")
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存数据"""
        try:
            # 如果缓存已满，清理过期项或移除最久未访问的项
            if len(self.cache) >= self.max_size and key not in self.cache:
                await self._cleanup_expired()
                
                if len(self.cache) >= self.max_size:
                    await self._remove_oldest()
            
            # 序列化数据
            serialized_data = self._serialize_data(value)
            
            # 设置缓存项
            expire_time = time.time() + (ttl or self.default_ttl)
            self.cache[key] = {
                "data": serialized_data,
                "expire_time": expire_time,
                "created_time": time.time()
            }
            
            self.access_times[key] = time.time()
            self.stats_data["sets"] += 1
            
            return True
            
        except Exception as e:
            self.log_error("设置缓存数据失败", key=key, error=str(e))
            raise CacheError(f"设置缓存数据失败: {e}")
    
    async def delete(self, key: str) -> bool:
        """删除缓存数据"""
        try:
            if key in self.cache:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                self.stats_data["deletes"] += 1
                return True
            return False
            
        except Exception as e:
            self.log_error("删除缓存数据失败", key=key, error=str(e))
            raise CacheError(f"删除缓存数据失败: {e}")
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        if key not in self.cache:
            return False
        
        cache_item = self.cache[key]
        if self._is_expired(cache_item):
            await self.delete(key)
            return False
        
        return True
    
    async def clear(self) -> bool:
        """清空所有缓存"""
        try:
            self.cache.clear()
            self.access_times.clear()
            self.log_info("内存缓存已清空")
            return True
            
        except Exception as e:
            self.log_error("清空缓存失败", error=str(e))
            raise CacheError(f"清空缓存失败: {e}")
    
    async def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.stats_data["hits"] + self.stats_data["misses"]
        hit_rate = self.stats_data["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "type": "memory",
            "total_items": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": hit_rate,
            **self.stats_data
        }
    
    def _is_expired(self, cache_item: Dict[str, Any]) -> bool:
        """检查缓存项是否过期"""
        return time.time() > cache_item["expire_time"]
    
    async def _cleanup_expired(self) -> None:
        """清理过期的缓存项"""
        expired_keys = []
        current_time = time.time()
        
        for key, cache_item in self.cache.items():
            if current_time > cache_item["expire_time"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            await self.delete(key)
        
        if expired_keys:
            self.log_info("清理过期缓存项", count=len(expired_keys))
    
    async def _remove_oldest(self) -> None:
        """移除最久未访问的缓存项"""
        if not self.access_times:
            return
        
        # 找到最久未访问的键
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        await self.delete(oldest_key)
        self.stats_data["evictions"] += 1
        
        self.log_info("移除最久未访问的缓存项", key=oldest_key)
    
    def _serialize_data(self, data: Any) -> bytes:
        """序列化缓存数据"""
        try:
            return pickle.dumps(data)
        except Exception as e:
            self.log_error("序列化数据失败", error=str(e))
            raise CacheError(f"序列化数据失败: {e}")
    
    def _deserialize_data(self, data: bytes) -> Any:
        """反序列化缓存数据"""
        try:
            return pickle.loads(data)
        except Exception as e:
            self.log_error("反序列化数据失败", error=str(e))
            raise CacheError(f"反序列化数据失败: {e}")


class RedisCacheManager(BaseCacheManager):
    """Redis缓存管理器"""
    
    def __init__(self, redis_url: str, default_ttl: int = 3600):
        """
        初始化Redis缓存管理器
        
        Args:
            redis_url: Redis连接URL
            default_ttl: 默认TTL(秒)
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.redis_client: Optional[redis.Redis] = None
        self.stats_data = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    async def initialize(self) -> None:
        """初始化Redis连接"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=False,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            
            # 测试连接
            await self._ping()
            
            self.log_info("Redis缓存管理器初始化完成", redis_url=self.redis_url)
            
        except Exception as e:
            self.log_error("Redis缓存管理器初始化失败", error=str(e))
            raise CacheError(f"Redis缓存管理器初始化失败: {e}")
    
    async def close(self) -> None:
        """关闭Redis连接"""
        if self.redis_client:
            await self.redis_client.close()
            self.log_info("Redis缓存管理器已关闭")
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        try:
            if not self.redis_client:
                raise CacheError("Redis客户端未初始化")
            
            data = self.redis_client.get(key)
            
            if data is None:
                self.stats_data["misses"] += 1
                return None
            
            self.stats_data["hits"] += 1
            return self._deserialize_data(data)
            
        except Exception as e:
            self.log_error("获取Redis缓存数据失败", key=key, error=str(e))
            raise CacheError(f"获取Redis缓存数据失败: {e}")
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存数据"""
        try:
            if not self.redis_client:
                raise CacheError("Redis客户端未初始化")
            
            serialized_data = self._serialize_data(value)
            
            success = self.redis_client.setex(
                key, 
                ttl or self.default_ttl, 
                serialized_data
            )
            
            if success:
                self.stats_data["sets"] += 1
            
            return bool(success)
            
        except Exception as e:
            self.log_error("设置Redis缓存数据失败", key=key, error=str(e))
            raise CacheError(f"设置Redis缓存数据失败: {e}")
    
    async def delete(self, key: str) -> bool:
        """删除缓存数据"""
        try:
            if not self.redis_client:
                raise CacheError("Redis客户端未初始化")
            
            result = self.redis_client.delete(key)
            
            if result > 0:
                self.stats_data["deletes"] += 1
                return True
            
            return False
            
        except Exception as e:
            self.log_error("删除Redis缓存数据失败", key=key, error=str(e))
            raise CacheError(f"删除Redis缓存数据失败: {e}")
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            if not self.redis_client:
                raise CacheError("Redis客户端未初始化")
            
            return bool(self.redis_client.exists(key))
            
        except Exception as e:
            self.log_error("检查Redis缓存存在性失败", key=key, error=str(e))
            raise CacheError(f"检查Redis缓存存在性失败: {e}")
    
    async def clear(self) -> bool:
        """清空所有缓存"""
        try:
            if not self.redis_client:
                raise CacheError("Redis客户端未初始化")
            
            # 注意：这将清空整个Redis数据库，生产环境需要谨慎使用
            self.redis_client.flushdb()
            self.log_info("Redis缓存已清空")
            return True
            
        except Exception as e:
            self.log_error("清空Redis缓存失败", error=str(e))
            raise CacheError(f"清空Redis缓存失败: {e}")
    
    async def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            if not self.redis_client:
                raise CacheError("Redis客户端未初始化")
            
            info = self.redis_client.info()
            total_requests = self.stats_data["hits"] + self.stats_data["misses"]
            hit_rate = self.stats_data["hits"] / total_requests if total_requests > 0 else 0
            
            return {
                "type": "redis",
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "hit_rate": hit_rate,
                **self.stats_data
            }
            
        except Exception as e:
            self.log_error("获取Redis统计信息失败", error=str(e))
            return {
                "type": "redis",
                "error": str(e),
                **self.stats_data
            }
    
    async def _ping(self) -> None:
        """测试Redis连接"""
        if not self.redis_client:
            raise CacheError("Redis客户端未初始化")
        
        result = self.redis_client.ping()
        if not result:
            raise CacheError("Redis连接测试失败")
    
    def _serialize_data(self, data: Any) -> bytes:
        """序列化缓存数据"""
        try:
            return pickle.dumps(data)
        except Exception as e:
            self.log_error("序列化数据失败", error=str(e))
            raise CacheError(f"序列化数据失败: {e}")
    
    def _deserialize_data(self, data: bytes) -> Any:
        """反序列化缓存数据"""
        try:
            return pickle.loads(data)
        except Exception as e:
            self.log_error("反序列化数据失败", error=str(e))
            raise CacheError(f"反序列化数据失败: {e}")


# 全局缓存管理器实例
_cache_manager: Optional[BaseCacheManager] = None


@lru_cache()
def get_cache_manager() -> BaseCacheManager:
    """获取缓存管理器实例(单例模式)"""
    global _cache_manager
    
    if _cache_manager is None:
        settings = get_settings()
        cache_config = settings.get_cache_config()
        
        if cache_config["type"].lower() == "redis":
            _cache_manager = RedisCacheManager(
                redis_url=cache_config["redis_url"],
                default_ttl=cache_config["default_timeout"]
            )
        else:
            _cache_manager = MemoryCacheManager(
                max_size=cache_config["max_size"],
                default_ttl=cache_config["default_timeout"]
            )
    
    return _cache_manager
