"""네트워크 메트릭 수집기"""
import psutil
from typing import Dict, Any


class NetworkCollector:
    """네트워크 I/O 메트릭을 수집하는 클래스"""

    def __init__(self):
        """네트워크 수집기 초기화"""
        # 초기 I/O 카운터 읽기 (델타 계산을 위해)
        self._last_io_counters = psutil.net_io_counters()

    def collect(self) -> Dict[str, Any]:
        """
        현재 네트워크 메트릭을 수집합니다.

        Returns:
            Dict[str, Any]: 네트워크 메트릭 딕셔너리
                - bytes_sent: 송신한 바이트 수
                - bytes_recv: 수신한 바이트 수
                - packets_sent: 송신한 패킷 수
                - packets_recv: 수신한 패킷 수
                - errin: 수신 오류 수
                - errout: 송신 오류 수
                - dropin: 수신 드롭 수
                - dropout: 송신 드롭 수
                - interfaces: 인터페이스별 상세 정보
        """
        metrics = {}

        # 전체 네트워크 I/O 카운터
        io_counters = psutil.net_io_counters()
        metrics['bytes_sent'] = io_counters.bytes_sent
        metrics['bytes_recv'] = io_counters.bytes_recv
        metrics['packets_sent'] = io_counters.packets_sent
        metrics['packets_recv'] = io_counters.packets_recv
        metrics['errin'] = io_counters.errin
        metrics['errout'] = io_counters.errout
        metrics['dropin'] = io_counters.dropin
        metrics['dropout'] = io_counters.dropout

        # 인터페이스별 네트워크 I/O 카운터
        interfaces = {}
        per_nic = psutil.net_io_counters(pernic=True)
        for interface_name, interface_stats in per_nic.items():
            interfaces[interface_name] = {
                'bytes_sent': interface_stats.bytes_sent,
                'bytes_recv': interface_stats.bytes_recv,
                'packets_sent': interface_stats.packets_sent,
                'packets_recv': interface_stats.packets_recv,
                'errin': interface_stats.errin,
                'errout': interface_stats.errout,
                'dropin': interface_stats.dropin,
                'dropout': interface_stats.dropout
            }

        metrics['interfaces'] = interfaces

        return metrics

    def get_metric_type(self) -> str:
        """메트릭 타입 반환"""
        return "network"
