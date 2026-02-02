"""디스크 메트릭 수집기"""
import psutil
from typing import Dict, Any, List


class DiskCollector:
    """디스크 사용률 및 I/O 메트릭을 수집하는 클래스"""

    def __init__(self):
        """디스크 수집기 초기화"""
        # 초기 I/O 카운터 읽기 (델타 계산을 위해)
        self._last_io_counters = psutil.disk_io_counters()

    def collect(self) -> Dict[str, Any]:
        """
        현재 디스크 메트릭을 수집합니다.

        Returns:
            Dict[str, Any]: 디스크 메트릭 딕셔너리
                - partitions: 파티션별 사용률 정보 리스트
                - io_read_bytes: 읽은 바이트 수
                - io_write_bytes: 쓴 바이트 수
                - io_read_count: 읽기 횟수
                - io_write_count: 쓰기 횟수
        """
        metrics = {}

        # 파티션별 사용률
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except PermissionError:
                # 접근 권한이 없는 파티션은 건너뛰기
                continue

        metrics['partitions'] = partitions

        # 디스크 I/O 카운터
        try:
            io_counters = psutil.disk_io_counters()
            if io_counters:
                metrics['io_read_bytes'] = io_counters.read_bytes
                metrics['io_write_bytes'] = io_counters.write_bytes
                metrics['io_read_count'] = io_counters.read_count
                metrics['io_write_count'] = io_counters.write_count
                metrics['io_read_time'] = io_counters.read_time
                metrics['io_write_time'] = io_counters.write_time
        except (AttributeError, RuntimeError):
            # 일부 플랫폼에서는 지원되지 않음
            metrics['io_read_bytes'] = None
            metrics['io_write_bytes'] = None
            metrics['io_read_count'] = None
            metrics['io_write_count'] = None

        return metrics

    def get_metric_type(self) -> str:
        """메트릭 타입 반환"""
        return "disk"
