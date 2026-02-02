"""CPU 메트릭 수집기"""
import psutil
from typing import Dict, Any


class CPUCollector:
    """CPU 사용률 및 관련 메트릭을 수집하는 클래스"""

    def __init__(self):
        """CPU 수집기 초기화"""
        # 첫 호출 시 interval을 설정하기 위해 한 번 호출
        psutil.cpu_percent(interval=None)

    def collect(self) -> Dict[str, Any]:
        """
        현재 CPU 메트릭을 수집합니다.

        Returns:
            Dict[str, Any]: CPU 메트릭 딕셔너리
                - cpu_percent: 전체 CPU 사용률 (%)
                - cpu_percent_per_core: 코어별 CPU 사용률 (%)
                - cpu_count_logical: 논리 CPU 코어 수
                - cpu_count_physical: 물리 CPU 코어 수
                - cpu_freq_current: 현재 CPU 주파수 (MHz)
                - cpu_freq_min: 최소 CPU 주파수 (MHz)
                - cpu_freq_max: 최대 CPU 주파수 (MHz)
        """
        metrics = {}

        # 전체 CPU 사용률
        metrics['cpu_percent'] = psutil.cpu_percent(interval=1)

        # 코어별 CPU 사용률
        metrics['cpu_percent_per_core'] = psutil.cpu_percent(interval=None, percpu=True)

        # CPU 코어 수
        metrics['cpu_count_logical'] = psutil.cpu_count(logical=True)
        metrics['cpu_count_physical'] = psutil.cpu_count(logical=False)

        # CPU 주파수 정보 (지원되는 경우)
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                metrics['cpu_freq_current'] = cpu_freq.current
                metrics['cpu_freq_min'] = cpu_freq.min
                metrics['cpu_freq_max'] = cpu_freq.max
        except (AttributeError, NotImplementedError):
            # 일부 플랫폼에서는 지원되지 않음
            metrics['cpu_freq_current'] = None
            metrics['cpu_freq_min'] = None
            metrics['cpu_freq_max'] = None

        return metrics

    def get_metric_type(self) -> str:
        """메트릭 타입 반환"""
        return "cpu"
