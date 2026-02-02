"""프로세스 메트릭 수집기"""
import psutil
from typing import Dict, Any, List


class ProcessCollector:
    """상위 프로세스 정보를 수집하는 클래스"""

    def collect(self, limit: int = 10, sort_by: str = 'cpu') -> List[Dict[str, Any]]:
        """
        리소스 사용량 기준 상위 N개 프로세스를 수집합니다.

        Args:
            limit: 반환할 프로세스 수 (기본값: 10)
            sort_by: 정렬 기준 ('cpu' 또는 'memory', 기본값: 'cpu')

        Returns:
            List[Dict[str, Any]]: 프로세스 정보 리스트
                각 프로세스는 다음 정보를 포함:
                - pid: 프로세스 ID
                - name: 프로세스 이름
                - cpu_percent: CPU 사용률 (%)
                - memory_percent: 메모리 사용률 (%)
                - memory_info_rss: RSS 메모리 (bytes)
                - status: 프로세스 상태
                - username: 프로세스 소유자
                - create_time: 프로세스 생성 시간 (timestamp)
        """
        processes = []

        # 모든 프로세스 정보 수집
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent',
                                         'memory_info', 'status', 'username', 'create_time']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': pinfo['cpu_percent'] or 0,
                    'memory_percent': pinfo['memory_percent'] or 0,
                    'memory_info_rss': pinfo['memory_info'].rss if pinfo['memory_info'] else 0,
                    'status': pinfo['status'],
                    'username': pinfo['username'],
                    'create_time': pinfo['create_time']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # 프로세스가 종료되었거나 접근 권한이 없는 경우 건너뛰기
                continue

        # 정렬 기준에 따라 정렬
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)

        # 상위 N개만 반환
        return processes[:limit]

    def get_metric_type(self) -> str:
        """메트릭 타입 반환"""
        return "process"
