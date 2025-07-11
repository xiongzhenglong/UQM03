"""
REST API路由定义
定义所有API端点和处理逻辑
"""

import time
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import math
import numpy as np
import pandas as pd
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import JSONResponse, FileResponse

from src.api.models import (
    UQMRequest, UQMResponse, ValidationRequest, ValidationResponse,
    HealthResponse, MetricsResponse, ErrorResponse,
    AsyncJobRequest, AsyncJobResponse, JobStatusResponse,
    JobStatus, AIGenerateRequest, AIGenerateResponse,
    AIGenerateVisualizationRequest, AIGenerateVisualizationResponse
)
from src.core.engine import get_uqm_engine
from src.core.cache import get_cache_manager
from src.services.ai_service import get_ai_service
from src.utils.logging import get_logger
from src.utils.exceptions import (
    ValidationError, ExecutionError, TimeoutError
)
from src.config.settings import get_settings

# 创建路由实例
router = APIRouter()
logger = get_logger(__name__)

# 服务启动时间
START_TIME = time.time()

# 异步任务存储（生产环境应使用Redis或数据库）
async_jobs: Dict[str, Dict[str, Any]] = {}

# 指标统计
metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_response_time": 0.0,
    "active_connections": 0,
    "cache_hits": 0,
    "cache_misses": 0
}


def update_metrics(success: bool, response_time: float, cache_hit: bool = False) -> None:
    """更新指标统计"""
    metrics["total_requests"] += 1
    metrics["total_response_time"] += response_time
    
    if success:
        metrics["successful_requests"] += 1
    else:
        metrics["failed_requests"] += 1
    
    if cache_hit:
        metrics["cache_hits"] += 1
    else:
        metrics["cache_misses"] += 1


def clean_nan(obj, _path=None):
    if _path is None:
        _path = []
    # float('nan')
    if isinstance(obj, float) and math.isnan(obj):
        print(f"[NaN found] path={_path} type=float value={obj}")
        return None
    # numpy.nan
    if isinstance(obj, np.floating) and np.isnan(obj):
        print(f"[NaN found] path={_path} type=numpy.nan value={obj}")
        return None
    # pandas.NA
    if obj is pd.NA:
        print(f"[NaN found] path={_path} type=pandas.NA value={obj}")
        return None
    # pandas.NaT
    if obj is pd.NaT:
        print(f"[NaN found] path={_path} type=pandas.NaT value={obj}")
        return None
    # None 直接返回
    if obj is None:
        return None
    # dict 递归
    if isinstance(obj, dict):
        return {k: clean_nan(v, _path+['.'+str(k)]) for k, v in obj.items()}
    # list 递归
    if isinstance(obj, list):
        return [clean_nan(v, _path+[f'[{i}]']) for i, v in enumerate(obj)]
    # tuple 递归
    if isinstance(obj, tuple):
        return tuple(clean_nan(v, _path+[f'({i})']) for i, v in enumerate(obj))
    # set 递归
    if isinstance(obj, set):
        return {clean_nan(v, _path+[f'{{{i}}}']) for i, v in enumerate(obj)}
    # Pydantic/BaseModel 递归
    if isinstance(obj, BaseModel):
        print(f"[BaseModel found] path={_path} type={type(obj)} value={obj}")
        return clean_nan(obj.dict(), _path+['.dict'])
    # 其它对象，尝试递归 __dict__
    if hasattr(obj, '__dict__'):
        print(f"[__dict__ found] path={_path} type={type(obj)} value={obj}")
        return clean_nan(vars(obj), _path+['.__dict__'])
    # 打印所有未处理类型
    if not isinstance(obj, (str, int, bool)):
        print(f"[Unhandled type] path={_path} type={type(obj)} value={obj}")
    return obj


@router.post(
    "/execute",
    response_model=UQMResponse,
    summary="执行UQM查询",
    description="执行UQM查询并返回结果",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"}
    }
)
async def execute_uqm(request: UQMRequest) -> UQMResponse:
    """
    执行UQM查询的主要端点
    
    Args:
        request: UQM请求数据
        
    Returns:
        UQM执行结果
    """
    start_time = time.time()
    
    try:
        logger.info(
            "开始执行UQM查询",
            uqm_name=request.uqm.get("metadata", {}).get("name", "未命名"),
            parameters=request.parameters
        )
        
        # 获取UQM引擎实例
        engine = get_uqm_engine()
        
        # 执行查询
        result = await engine.process(
            uqm_data=request.uqm,
            parameters=request.parameters,
            options=request.options
        )
        # 只递归清理 result.data，保持 result 类型不变
        if hasattr(result, 'data'):
            result.data = clean_nan(result.data)
        else:
            print('[ERROR] result has no .data attribute, type:', type(result))
        
        response_time = time.time() - start_time
        update_metrics(success=True, response_time=response_time)
        
        logger.info(
            "UQM查询执行完成",
            execution_time=response_time,
            row_count=len(result.data) if result.data else 0
        )
        
        return result
        
    except ValidationError as e:
        response_time = time.time() - start_time
        update_metrics(success=False, response_time=response_time)
        
        logger.error(
            "UQM查询验证失败",
            error=str(e),
            execution_time=response_time
        )
        
        raise HTTPException(
            status_code=400,
            detail={
                "code": "VALIDATION_ERROR",
                "message": str(e),
                "details": e.details
            }
        )
        
    except ExecutionError as e:
        response_time = time.time() - start_time
        update_metrics(success=False, response_time=response_time)
        
        logger.error(
            "UQM查询执行失败",
            error=str(e),
            execution_time=response_time
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "code": "EXECUTION_ERROR",
                "message": str(e),
                "details": e.details
            }
        )
        
    except TimeoutError as e:
        response_time = time.time() - start_time
        update_metrics(success=False, response_time=response_time)
        
        logger.error(
            "UQM查询执行超时",
            error=str(e),
            execution_time=response_time
        )
        
        raise HTTPException(
            status_code=408,
            detail={
                "code": "TIMEOUT_ERROR",
                "message": str(e),
                "details": e.details
            }
        )
        
    except Exception as e:
        response_time = time.time() - start_time
        update_metrics(success=False, response_time=response_time)
        
        logger.error(
            "UQM查询执行出现未知错误",
            error=str(e),
            execution_time=response_time,
            exc_info=True
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误",
                "details": {}
            }
        )


@router.post(
    "/validate",
    response_model=ValidationResponse,
    summary="验证UQM定义",
    description="验证UQM定义的有效性",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"}
    }
)
async def validate_uqm(request: ValidationRequest) -> ValidationResponse:
    """
    验证UQM定义有效性
    
    Args:
        request: 验证请求数据
        
    Returns:
        验证结果
    """
    try:
        logger.info(
            "开始验证UQM定义",
            uqm_name=request.uqm.get("metadata", {}).get("name", "未命名")
        )
        
        # 获取UQM引擎实例
        engine = get_uqm_engine()
        
        # 验证UQM定义
        validation_result = await engine.validate_query(request.uqm)
        
        logger.info(
            "UQM定义验证完成",
            valid=validation_result.valid,
            error_count=len(validation_result.errors) if validation_result.errors else 0
        )
        
        return validation_result
        
    except Exception as e:
        logger.error(
            "UQM定义验证出现错误",
            error=str(e),
            exc_info=True
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "验证过程出现错误",
                "details": {"error": str(e)}
            }
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="健康检查",
    description="检查服务健康状态"
)
async def health_check() -> HealthResponse:
    """
    健康检查端点
    
    Returns:
        服务健康状态
    """
    uptime = time.time() - START_TIME
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="0.1.0",
        uptime=uptime
    )


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="获取系统指标",
    description="获取系统运行指标和统计信息"
)
async def get_metrics() -> MetricsResponse:
    """
    获取系统指标
    
    Returns:
        系统指标数据
    """
    # 计算缓存命中率
    total_cache_requests = metrics["cache_hits"] + metrics["cache_misses"]
    cache_hit_rate = (
        metrics["cache_hits"] / total_cache_requests 
        if total_cache_requests > 0 else 0.0
    )
    
    # 计算平均响应时间
    avg_response_time = (
        metrics["total_response_time"] / metrics["total_requests"]
        if metrics["total_requests"] > 0 else 0.0
    )
    
    return MetricsResponse(
        total_requests=metrics["total_requests"],
        successful_requests=metrics["successful_requests"],
        failed_requests=metrics["failed_requests"],
        average_response_time=avg_response_time,
        active_connections=metrics["active_connections"],
        cache_hit_rate=cache_hit_rate
    )


async def execute_async_job(job_id: str, uqm_data: Dict[str, Any], 
                          parameters: Dict[str, Any], callback_url: str = None) -> None:
    """
    执行异步任务
    
    Args:
        job_id: 任务ID
        uqm_data: UQM数据
        parameters: 查询参数
        callback_url: 回调URL
    """
    try:
        # 更新任务状态为运行中
        async_jobs[job_id].update({
            "status": JobStatus.RUNNING,
            "started_at": datetime.utcnow(),
            "progress": 0.0
        })
        
        logger.info(f"开始执行异步任务: {job_id}")
        
        # 获取UQM引擎实例
        engine = get_uqm_engine()
        
        # 执行查询
        result = await engine.process(
            uqm_data=uqm_data,
            parameters=parameters
        )
        
        # 更新任务状态为完成
        async_jobs[job_id].update({
            "status": JobStatus.COMPLETED,
            "completed_at": datetime.utcnow(),
            "progress": 100.0,
            "result": result
        })
        
        logger.info(f"异步任务执行完成: {job_id}")
        
        # 如果有回调URL，发送结果（这里简化处理）
        if callback_url:
            logger.info(f"发送回调通知: {callback_url}")
        
    except Exception as e:
        # 更新任务状态为失败
        async_jobs[job_id].update({
            "status": JobStatus.FAILED,
            "completed_at": datetime.utcnow(),
            "error": str(e)
        })
        
        logger.error(f"异步任务执行失败: {job_id}", error=str(e), exc_info=True)


@router.post(
    "/execute-async",
    response_model=AsyncJobResponse,
    summary="异步执行UQM查询",
    description="异步执行UQM查询，返回任务ID",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"}
    }
)
async def execute_async(request: AsyncJobRequest, background_tasks: BackgroundTasks) -> AsyncJobResponse:
    """
    异步执行UQM查询
    
    Args:
        request: 异步任务请求
        background_tasks: 后台任务
        
    Returns:
        异步任务响应
    """
    try:
        # 生成任务ID
        job_id = str(uuid.uuid4())
        
        # 创建任务记录
        created_at = datetime.utcnow()
        async_jobs[job_id] = {
            "job_id": job_id,
            "status": JobStatus.PENDING,
            "created_at": created_at,
            "uqm_data": request.uqm,
            "parameters": request.parameters,
            "callback_url": request.callback_url
        }
        
        # 添加后台任务
        background_tasks.add_task(
            execute_async_job,
            job_id=job_id,
            uqm_data=request.uqm,
            parameters=request.parameters,
            callback_url=request.callback_url
        )
        
        logger.info(f"创建异步任务: {job_id}")
        
        return AsyncJobResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            created_at=created_at,
            estimated_completion=created_at + timedelta(minutes=5)
        )
        
    except Exception as e:
        logger.error("创建异步任务失败", error=str(e), exc_info=True)
        
        raise HTTPException(
            status_code=500,
            detail={
                "code": "ASYNC_JOB_ERROR",
                "message": "创建异步任务失败",
                "details": {"error": str(e)}
            }
        )


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="获取异步任务状态",
    description="获取指定任务的执行状态和结果",
    responses={
        404: {"model": ErrorResponse, "description": "任务不存在"}
    }
)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    获取异步任务状态
    
    Args:
        job_id: 任务ID
        
    Returns:
        任务状态信息
    """
    if job_id not in async_jobs:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "JOB_NOT_FOUND",
                "message": f"任务不存在: {job_id}",
                "details": {}
            }
        )
    
    job_info = async_jobs[job_id]
    
    return JobStatusResponse(
        job_id=job_id,
        status=job_info["status"],
        created_at=job_info["created_at"],
        started_at=job_info.get("started_at"),
        completed_at=job_info.get("completed_at"),
        progress=job_info.get("progress"),
        result=job_info.get("result"),
        error=job_info.get("error")
    )


@router.delete(
    "/jobs/{job_id}",
    summary="取消异步任务",
    description="取消指定的异步任务",
    responses={
        404: {"model": ErrorResponse, "description": "任务不存在"}
    }
)
async def cancel_job(job_id: str) -> Dict[str, str]:
    """
    取消异步任务
    
    Args:
        job_id: 任务ID
        
    Returns:
        取消结果
    """
    if job_id not in async_jobs:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "JOB_NOT_FOUND",
                "message": f"任务不存在: {job_id}",
                "details": {}
            }
        )
    
    job_info = async_jobs[job_id]
    
    if job_info["status"] in [JobStatus.COMPLETED, JobStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "JOB_ALREADY_FINISHED",
                "message": f"任务已完成，无法取消: {job_id}",
                "details": {}
            }
        )
    
    # 更新任务状态为已取消
    async_jobs[job_id].update({
        "status": JobStatus.CANCELLED,
        "completed_at": datetime.utcnow()
    })
    
    logger.info(f"取消异步任务: {job_id}")
    
    return {"message": f"任务已取消: {job_id}"}

# ================== 报表管理API ==================
import os, json
from fastapi import Request
from fastapi.responses import FileResponse

REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../reports'))
INDEX_FILE = os.path.join(REPORTS_DIR, 'index.json')

class ReportBlock(BaseModel):
    id: str
    type: str  # 'table' | 'chart'
    title: str
    description: str
    uqmConfig: dict = {} # UQM 查询配置
    config: dict
    order: int = 0

class ReportModel(BaseModel):
    id: str
    title: str
    description: str
    createdAt: str
    updatedAt: str
    blocks: list[ReportBlock]

# 获取报表列表
@router.get('/reports')
def get_reports():
    try:
        if not os.path.exists(INDEX_FILE):
            return []
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
            return report_data
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果文件不存在或解析失败，返回空列表是更合理的行为
        return []

# 获取单个报表详情
@router.get('/reports/{report_id}')
def get_report(report_id: str):
    file_path = os.path.join(REPORTS_DIR, f'{report_id}.json')
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail='Report not found')
        with open(file_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
            # 确保旧数据兼容
            for block in report_data.get("blocks", []):
                if "uqmConfig" not in block:
                    block["uqmConfig"] = {}
            return report_data
    except (FileNotFoundError, json.JSONDecodeError):
        return None

# 新建报表
@router.post('/reports')
def create_report(report: ReportModel):
    # 生成唯一ID和时间
    import uuid, datetime
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    if not report.id:
        report.id = str(uuid.uuid4())
    report.createdAt = now
    report.updatedAt = now

    # 确保目录存在
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # 保存报表文件
    file_path = os.path.join(REPORTS_DIR, f'{report.id}.json')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(report.dict(), f, ensure_ascii=False, indent=2)

    # 更新index.json
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = []
    # 检查是否已存在
    found = False
    for item in index:
        if item['id'] == report.id:
            item['title'] = report.title
            item['description'] = report.description
            item['updatedAt'] = now
            found = True
            break
    if not found:
        index.append({
            'id': report.id,
            'title': report.title,
            'description': report.description,
            'createdAt': now,
            'updatedAt': now,
            'filename': f'{report.id}.json'
        })
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return {'success': True, 'id': report.id}


# 删除报表
@router.delete('/reports/{report_id}')
def delete_report(report_id: str):
    try:
        # 检查报表文件是否存在
        file_path = os.path.join(REPORTS_DIR, f'{report_id}.json')
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail='Report not found')
        
        # 删除报表文件
        os.remove(file_path)
        
        # 从index.json中移除记录
        if os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                index = json.load(f)
            
            # 过滤掉要删除的报表
            index = [item for item in index if item['id'] != report_id]
            
            # 写回index.json
            with open(INDEX_FILE, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
        
        logger.info(f"报表删除成功: {report_id}")
        return {'success': True, 'message': f'报表 {report_id} 已删除'}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除报表失败: {report_id}", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DELETE_ERROR",
                "message": "删除报表失败",
                "details": {"error": str(e)}
            }
        )


# ================== AI生成API ==================

@router.post(
    "/generate",
    response_model=AIGenerateResponse,
    summary="AI生成UQM Schema",
    description="根据自然语言描述生成UQM JSON Schema",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"}
    }
)
async def generate_uqm_schema(request: AIGenerateRequest) -> AIGenerateResponse:
    """
    根据自然语言查询生成UQM JSON Schema
    
    Args:
        request: AI生成请求数据
        
    Returns:
        AI生成的UQM Schema
    """
    start_time = time.time()
    
    try:
        logger.info(
            "开始AI生成UQM Schema",
            query=request.query[:100] + "..." if len(request.query) > 100 else request.query
        )
        
        # 获取AI服务实例
        ai_service = get_ai_service()
        
        # 生成Schema
        schema = await ai_service.generate_uqm_schema(request.query)
        
        generation_time = time.time() - start_time
        
        if schema:
            logger.info(
                "AI生成UQM Schema成功",
                generation_time=generation_time,
                query_length=len(request.query)
            )
            
            # 调试：打印schema结构
            logger.info(f"AI返回的schema结构: {json.dumps(schema, ensure_ascii=False, indent=2)}")
            
            # 确保返回的数据符合AIGenerateResponse模型
            response_data = {
                "uqm": schema.get("uqm", {}),
                "parameters": schema.get("parameters", {}),
                "options": schema.get("options", {})
            }
            
            logger.info(f"构造的响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            return AIGenerateResponse(**response_data)
        else:
            logger.error(
                "AI生成UQM Schema失败",
                generation_time=generation_time
            )
            
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "AI_GENERATION_FAILED",
                    "message": "AI生成失败，请检查查询描述或重试",
                    "details": {}
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        generation_time = time.time() - start_time
        
        logger.error(
            "AI生成UQM Schema异常",
            error=str(e),
            generation_time=generation_time,
            exc_info=True
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "code": "AI_GENERATION_ERROR",
                "message": "AI生成失败",
                "details": {"error": str(e)}
            }
        )


@router.post(
    "/generate-and-execute",
    response_model=UQMResponse,
    summary="AI生成并执行UQM查询",
    description="根据自然语言描述生成UQM Schema并立即执行",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"}
    }
)
async def generate_and_execute(request: AIGenerateRequest) -> UQMResponse:
    """
    AI生成并执行UQM查询
    
    Args:
        request: AI生成请求
        
    Returns:
        UQM执行结果
    """
    start_time = time.time()
    
    try:
        logger.info("开始AI生成并执行查询", query=request.query)
        
        # 获取AI服务实例
        ai_service = get_ai_service()
        
        # 生成Schema
        schema = await ai_service.generate_uqm_schema(request.query)
        if not schema:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "AI_GENERATION_FAILED",
                    "message": "AI生成Schema失败"
                }
            )
        
        # 获取UQM引擎实例
        engine = get_uqm_engine()
        
        # 执行查询
        result = await engine.process(
            uqm_data=schema,
            parameters=request.options or {},
            options=request.options or {}
        )
        
        # 清理NaN值
        if hasattr(result, 'data'):
            result.data = clean_nan(result.data)
        
        response_time = time.time() - start_time
        update_metrics(success=True, response_time=response_time)
        
        logger.info(
            "AI生成并执行查询完成",
            execution_time=response_time,
            row_count=len(result.data) if result.data else 0
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        response_time = time.time() - start_time
        update_metrics(success=False, response_time=response_time)
        
        logger.error(
            "AI生成并执行查询失败",
            error=str(e),
            execution_time=response_time
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": f"服务器内部错误: {str(e)}"
            }
        )


@router.post(
    "/generate-visualization",
    response_model=AIGenerateVisualizationResponse,
    summary="AI生成可视化代码",
    description="根据查询结果和用户需求生成表格或图表代码",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"}
    }
)
async def generate_visualization(request: AIGenerateVisualizationRequest) -> AIGenerateVisualizationResponse:
    """
    AI生成可视化代码
    
    Args:
        request: 可视化生成请求
        
    Returns:
        生成的可视化配置
    """
    start_time = time.time()
    
    try:
        logger.info(
            "开始AI生成可视化代码",
            data_rows=len(request.data),
            query=request.query,
            visualization_type=request.visualization_type
        )
        
        # 获取AI服务实例
        ai_service = get_ai_service()
        
        # 生成可视化配置
        result = await ai_service.generate_visualization_code(
            data=request.data,
            query=request.query,
            visualization_type=request.visualization_type
        )
        
        if not result or result.get("error"):
            raise HTTPException(
                status_code=500,
                detail={"message": result.get("error") if result else "AI服务返回空结果"}
            )

        return AIGenerateVisualizationResponse(
            success=True,
            visualization_type=result.get("visualization_type", "table"),
            config=result.get("config"),
            error=None
        )
        
    except Exception as e:
        response_time = time.time() - start_time
        update_metrics(success=False, response_time=response_time)
        
        logger.error(
            "AI生成可视化代码失败",
            error=str(e),
            execution_time=response_time
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": f"服务器内部错误: {str(e)}"
            }
        )
