"""메모리 메트릭 수집기"""
import psutil
from typing import Dict, Any


class MemoryCollector:
    """메모리 사용률 및 관련 메트릭을 수집하는 클래스"""

    def collect(self) -> Dict[str, Any]:
        """
        현재 메모리 메트릭을 수집합니다.

        Returns:
            Dict[str, Any]: 메모리 메트릭 딕셔너리
                - memory_total: 전체 메모리 (bytes)
                - memory_available: 사용 가능한 메모리 (bytes)
                - memory_used: 사용 중인 메모리 (bytes)
                - memory_percent: 메모리 사용률 (%)
                - memory_free: 여유 메모리 (bytes)
                - swap_total: 전체 스왑 메모리 (bytes)
                - swap_used: 사용 중인 스왑 메모리 (bytes)
                - swap_free: 여유 스왑 메모리 (bytes)
                - swap_percent: 스왑 메모리 사용률 (%)
        """
        metrics = {}

        # 가상 메모리 정보
        vmem = psutil.virtual_memory()
        metrics['memory_total'] = vmem.total
        metrics['memory_available'] = vmem.available
        metrics['memory_used'] = vmem.used
        metrics['memory_percent'] = vmem.percent
        metrics['memory_free'] = vmem.free

        # 스왑 메모리 정보
        swap = psutil.swap_memory()
        metrics['swap_total'] = swap.total
        metrics['swap_used'] = swap.used
        metrics['swap_free'] = swap.free
        metrics['swap_percent'] = swap.percent

        return metrics

    def get_metric_type(self) -> str:
        """메트릭 타입 반환"""
        return "memory"
