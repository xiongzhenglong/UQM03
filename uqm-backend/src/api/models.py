"""
Pydantic数据模型定义
定义API请求和响应的数据结构
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator


class StepType(str, Enum):
    """步骤类型枚举"""
    QUERY = "query"
    ENRICH = "enrich"
    PIVOT = "pivot"
    UNPIVOT = "unpivot"
    UNION = "union"
    ASSERT = "assert"


class JobStatus(str, Enum):
    """异步任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Parameter(BaseModel):
    """参数定义模型"""
    name: str = Field(..., description="参数名称")
    type: str = Field(..., description="参数类型")
    default: Optional[Any] = Field(None, description="默认值")
    required: bool = Field(True, description="是否必需")
    description: Optional[str] = Field(None, description="参数描述")


class Metadata(BaseModel):
    """元数据模型"""
    name: str = Field(..., description="查询名称")
    description: Optional[str] = Field(None, description="查询描述")
    version: Optional[str] = Field("1.0", description="版本号")
    author: Optional[str] = Field(None, description="作者")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")


class StepResult(BaseModel):
    """单个步骤执行结果模型"""
    step_name: str = Field(..., description="步骤名称")
    step_type: StepType = Field(..., description="步骤类型")
    status: str = Field(..., description="执行状态")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="步骤结果数据")
    row_count: int = Field(0, description="结果行数")
    execution_time: float = Field(0.0, description="执行时间(秒)")
    cache_hit: bool = Field(False, description="是否命中缓存")
    error: Optional[str] = Field(None, description="错误信息")


class ValidationError(BaseModel):
    """验证错误详情模型"""
    field: str = Field(..., description="错误字段")
    message: str = Field(..., description="错误信息")
    value: Optional[Any] = Field(None, description="错误值")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: Dict[str, Any] = Field(..., description="错误详情")
    
    class Config:
        schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "数据验证失败",
                    "details": {}
                }
            }
        }


class UQMRequest(BaseModel):
    """UQM请求数据模型"""
    uqm: Dict[str, Any] = Field(..., description="UQM JSON定义")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="查询参数")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="执行选项")
    
    @validator('uqm')
    def validate_uqm(cls, v):
        """验证UQM结构"""
        if not isinstance(v, dict):
            raise ValueError("UQM必须是一个JSON对象")
        
        required_fields = ['metadata', 'steps']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"UQM缺少必需字段: {field}")
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "uqm": {
                    "metadata": {
                        "name": "示例查询",
                        "description": "这是一个示例UQM查询"
                    },
                    "steps": [
                        {
                            "name": "step1",
                            "type": "query",
                            "config": {
                                "data_source": "users",
                                "dimensions": ["id", "name"],
                                "metrics": [],
                                "filters": []
                            }
                        }
                    ],
                    "output": "step1"
                },
                "parameters": {
                    "limit": 100
                },
                "options": {
                    "cache_enabled": True,
                    "timeout": 300
                }
            }
        }


class UQMResponse(BaseModel):
    """UQM响应数据模型"""
    success: bool = Field(..., description="执行是否成功")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="查询结果数据")
    metadata: Optional[Metadata] = Field(None, description="查询元数据")
    execution_info: Dict[str, Any] = Field(default_factory=dict, description="执行信息")
    step_results: Optional[List[StepResult]] = Field(None, description="步骤执行结果")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": [
                    {"id": 1, "name": "张三"},
                    {"id": 2, "name": "李四"}
                ],
                "metadata": {
                    "name": "示例查询",
                    "description": "这是一个示例UQM查询"
                },
                "execution_info": {
                    "total_time": 1.23,
                    "row_count": 2,
                    "cache_hit": False
                },
                "step_results": [
                    {
                        "step_name": "step1",
                        "step_type": "query",
                        "status": "completed",
                        "row_count": 2,
                        "execution_time": 1.23,
                        "cache_hit": False
                    }
                ]
            }
        }


class ValidationRequest(BaseModel):
    """验证请求模型"""
    uqm: Dict[str, Any] = Field(..., description="要验证的UQM JSON定义")
    
    class Config:
        schema_extra = {
            "example": {
                "uqm": {
                    "metadata": {
                        "name": "示例查询"
                    },
                    "steps": [
                        {
                            "name": "step1",
                            "type": "query",
                            "config": {}
                        }
                    ],
                    "output": "step1"
                }
            }
        }


class ValidationResponse(BaseModel):
    """验证响应模型"""
    valid: bool = Field(..., description="是否验证通过")
    errors: Optional[List[ValidationError]] = Field(None, description="验证错误列表")
    warnings: Optional[List[str]] = Field(None, description="警告信息列表")
    
    class Config:
        schema_extra = {
            "example": {
                "valid": True,
                "errors": None,
                "warnings": ["建议添加查询描述"]
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(..., description="检查时间")
    version: str = Field(..., description="服务版本")
    uptime: float = Field(..., description="运行时间(秒)")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2023-12-01T10:00:00Z",
                "version": "0.1.0",
                "uptime": 3600.0
            }
        }


class MetricsResponse(BaseModel):
    """指标响应模型"""
    total_requests: int = Field(..., description="总请求数")
    successful_requests: int = Field(..., description="成功请求数")
    failed_requests: int = Field(..., description="失败请求数")
    average_response_time: float = Field(..., description="平均响应时间(秒)")
    active_connections: int = Field(..., description="活跃连接数")
    cache_hit_rate: float = Field(..., description="缓存命中率")
    
    class Config:
        schema_extra = {
            "example": {
                "total_requests": 1000,
                "successful_requests": 950,
                "failed_requests": 50,
                "average_response_time": 1.5,
                "active_connections": 10,
                "cache_hit_rate": 0.75
            }
        }


class AsyncJobRequest(BaseModel):
    """异步任务请求模型"""
    uqm: Dict[str, Any] = Field(..., description="UQM JSON定义")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="查询参数")
    callback_url: Optional[str] = Field(None, description="结果回调URL")
    
    class Config:
        schema_extra = {
            "example": {
                "uqm": {
                    "metadata": {"name": "异步查询"},
                    "steps": [{"name": "step1", "type": "query", "config": {}}],
                    "output": "step1"
                },
                "parameters": {},
                "callback_url": "https://example.com/callback"
            }
        }


class AsyncJobResponse(BaseModel):
    """异步任务响应模型"""
    job_id: str = Field(..., description="任务ID")
    status: JobStatus = Field(..., description="任务状态")
    created_at: datetime = Field(..., description="创建时间")
    estimated_completion: Optional[datetime] = Field(None, description="预计完成时间")
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": "job_123456",
                "status": "pending",
                "created_at": "2023-12-01T10:00:00Z",
                "estimated_completion": "2023-12-01T10:05:00Z"
            }
        }


class JobStatusResponse(BaseModel):
    """任务状态响应模型"""
    job_id: str = Field(..., description="任务ID")
    status: JobStatus = Field(..., description="任务状态")
    created_at: datetime = Field(..., description="创建时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    progress: Optional[float] = Field(None, description="进度百分比")
    result: Optional[UQMResponse] = Field(None, description="执行结果")
    error: Optional[str] = Field(None, description="错误信息")
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": "job_123456",
                "status": "completed",
                "created_at": "2023-12-01T10:00:00Z",
                "started_at": "2023-12-01T10:00:01Z",
                "completed_at": "2023-12-01T10:02:30Z",
                "progress": 100.0,
                "result": {
                    "success": True,
                    "data": [{"id": 1, "name": "张三"}]
                }
            }
        }
