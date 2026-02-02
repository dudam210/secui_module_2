"""메트릭 데이터 모델"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CPUMetrics(BaseModel):
    """CPU 메트릭 모델"""
    timestamp: datetime = Field(default_factory=datetime.now)
    cpu_percent: float
    cpu_percent_per_core: List[float]
    cpu_count_logical: int
    cpu_count_physical: Optional[int]
    cpu_freq_current: Optional[float]
    cpu_freq_min: Optional[float]
    cpu_freq_max: Optional[float]


class MemoryMetrics(BaseModel):
    """메모리 메트릭 모델"""
    timestamp: datetime = Field(default_factory=datetime.now)
    memory_total: int
    memory_available: int
    memory_used: int
    memory_percent: float
    memory_free: int
    swap_total: int
    swap_used: int
    swap_free: int
    swap_percent: float


class DiskPartition(BaseModel):
    """디스크 파티션 정보"""
    device: str
    mountpoint: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float


class DiskMetrics(BaseModel):
    """디스크 메트릭 모델"""
    timestamp: datetime = Field(default_factory=datetime.now)
    partitions: List[DiskPartition]
    io_read_bytes: Optional[int]
    io_write_bytes: Optional[int]
    io_read_count: Optional[int]
    io_write_count: Optional[int]
    io_read_time: Optional[int] = None
    io_write_time: Optional[int] = None


class NetworkMetrics(BaseModel):
    """네트워크 메트릭 모델"""
    timestamp: datetime = Field(default_factory=datetime.now)
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int
    interfaces: Dict[str, Dict[str, int]]


class ProcessInfo(BaseModel):
    """프로세스 정보 모델"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_info_rss: int
    status: str
    username: Optional[str]
    create_time: float


class ProcessMetrics(BaseModel):
    """프로세스 메트릭 모델"""
    timestamp: datetime = Field(default_factory=datetime.now)
    processes: List[ProcessInfo]
    sort_by: str
    limit: int


class AllMetrics(BaseModel):
    """모든 메트릭을 포함하는 모델"""
    timestamp: datetime = Field(default_factory=datetime.now)
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    network: Dict[str, Any]


class HealthCheck(BaseModel):
    """헬스체크 응답 모델"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
