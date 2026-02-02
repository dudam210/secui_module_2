"""메트릭 API 라우트"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException

from app.models.metrics import (
    CPUMetrics, MemoryMetrics, DiskMetrics, NetworkMetrics,
    ProcessMetrics, AllMetrics, HealthCheck
)

router = APIRouter(prefix="/api/v1", tags=["metrics"])

# 전역 변수로 수집기와 스토리지 저장 (의존성 주입 대신 간단하게)
_collectors = None
_storage = None


def set_dependencies(collectors, storage):
    """수집기와 스토리지를 설정합니다."""
    global _collectors, _storage
    _collectors = collectors
    _storage = storage


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    헬스체크 엔드포인트
    """
    return HealthCheck(status="healthy")


@router.get("/metrics/current", response_model=AllMetrics)
async def get_current_metrics():
    """
    모든 메트릭의 현재 스냅샷을 반환합니다.
    """
    if not _collectors:
        raise HTTPException(status_code=503, detail="Collectors not initialized")

    return AllMetrics(
        cpu=_collectors['cpu'].collect(),
        memory=_collectors['memory'].collect(),
        disk=_collectors['disk'].collect(),
        network=_collectors['network'].collect()
    )


@router.get("/metrics/cpu")
async def get_cpu_metrics(
    start: Optional[datetime] = Query(None, description="시작 시간"),
    end: Optional[datetime] = Query(None, description="종료 시간"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="최대 반환 개수")
) -> List[Dict[str, Any]]:
    """
    CPU 시계열 메트릭을 반환합니다.
    """
    if not _storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    data = _storage.get_range('cpu', start=start, end=end, limit=limit)
    return data


@router.get("/metrics/memory")
async def get_memory_metrics(
    start: Optional[datetime] = Query(None, description="시작 시간"),
    end: Optional[datetime] = Query(None, description="종료 시간"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="최대 반환 개수")
) -> List[Dict[str, Any]]:
    """
    메모리 시계열 메트릭을 반환합니다.
    """
    if not _storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    data = _storage.get_range('memory', start=start, end=end, limit=limit)
    return data


@router.get("/metrics/disk")
async def get_disk_metrics(
    start: Optional[datetime] = Query(None, description="시작 시간"),
    end: Optional[datetime] = Query(None, description="종료 시간"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="최대 반환 개수")
) -> List[Dict[str, Any]]:
    """
    디스크 시계열 메트릭을 반환합니다.
    """
    if not _storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    data = _storage.get_range('disk', start=start, end=end, limit=limit)
    return data


@router.get("/metrics/network")
async def get_network_metrics(
    start: Optional[datetime] = Query(None, description="시작 시간"),
    end: Optional[datetime] = Query(None, description="종료 시간"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="최대 반환 개수")
) -> List[Dict[str, Any]]:
    """
    네트워크 시계열 메트릭을 반환합니다.
    """
    if not _storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    data = _storage.get_range('network', start=start, end=end, limit=limit)
    return data


@router.get("/metrics/processes")
async def get_processes(
    limit: int = Query(10, ge=1, le=100, description="반환할 프로세스 수"),
    sort_by: str = Query('cpu', regex='^(cpu|memory)$', description="정렬 기준")
) -> List[Dict[str, Any]]:
    """
    리소스 사용량 기준 상위 N개 프로세스를 반환합니다.
    """
    if not _collectors:
        raise HTTPException(status_code=503, detail="Collectors not initialized")

    processes = _collectors['process'].collect(limit=limit, sort_by=sort_by)
    return processes
