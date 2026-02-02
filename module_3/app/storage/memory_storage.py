"""인메모리 스토리지 구현"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
import threading


class MemoryStorage:
    """
    시계열 메트릭을 메모리에 저장하는 간단한 스토리지.
    Level 1 (최소 구성)용으로 설계됨.
    """

    def __init__(self, max_data_points: int = 3600):
        """
        Args:
            max_data_points: 메트릭 타입당 최대 저장 데이터 포인트 수 (기본값: 3600)
        """
        self._data: Dict[str, deque] = {
            'cpu': deque(maxlen=max_data_points),
            'memory': deque(maxlen=max_data_points),
            'disk': deque(maxlen=max_data_points),
            'network': deque(maxlen=max_data_points),
            'process': deque(maxlen=max_data_points)
        }
        self._lock = threading.Lock()

    def save_metric(self, metric_type: str, data: Dict[str, Any]) -> bool:
        """
        메트릭 데이터를 저장합니다.

        Args:
            metric_type: 메트릭 타입 (cpu, memory, disk, network, process)
            data: 저장할 메트릭 데이터

        Returns:
            bool: 저장 성공 여부
        """
        if metric_type not in self._data:
            return False

        # 타임스탬프 추가 (없는 경우)
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now()

        with self._lock:
            self._data[metric_type].append(data)

        return True

    def get_latest(self, metric_type: str) -> Optional[Dict[str, Any]]:
        """
        특정 메트릭 타입의 최신 데이터를 반환합니다.

        Args:
            metric_type: 메트릭 타입

        Returns:
            Optional[Dict[str, Any]]: 최신 메트릭 데이터 또는 None
        """
        if metric_type not in self._data:
            return None

        with self._lock:
            if len(self._data[metric_type]) == 0:
                return None
            return dict(self._data[metric_type][-1])

    def get_range(
        self,
        metric_type: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        특정 메트릭 타입의 시간 범위 데이터를 반환합니다.

        Args:
            metric_type: 메트릭 타입
            start: 시작 시간 (None이면 처음부터)
            end: 종료 시간 (None이면 끝까지)
            limit: 최대 반환 개수 (None이면 제한 없음)

        Returns:
            List[Dict[str, Any]]: 메트릭 데이터 리스트
        """
        if metric_type not in self._data:
            return []

        with self._lock:
            data_list = list(self._data[metric_type])

        # 시간 범위 필터링
        if start or end:
            filtered = []
            for item in data_list:
                timestamp = item.get('timestamp')
                if not timestamp:
                    continue

                if start and timestamp < start:
                    continue
                if end and timestamp > end:
                    continue

                filtered.append(item)
            data_list = filtered

        # 제한 적용
        if limit and limit > 0:
            data_list = data_list[-limit:]

        return data_list

    def get_all_latest(self) -> Dict[str, Any]:
        """
        모든 메트릭 타입의 최신 데이터를 반환합니다.

        Returns:
            Dict[str, Any]: 메트릭 타입별 최신 데이터
        """
        result = {}
        for metric_type in self._data.keys():
            latest = self.get_latest(metric_type)
            if latest:
                result[metric_type] = latest

        return result

    def clear(self, metric_type: Optional[str] = None):
        """
        저장된 데이터를 삭제합니다.

        Args:
            metric_type: 삭제할 메트릭 타입 (None이면 전체 삭제)
        """
        with self._lock:
            if metric_type:
                if metric_type in self._data:
                    self._data[metric_type].clear()
            else:
                for key in self._data.keys():
                    self._data[key].clear()

    def get_stats(self) -> Dict[str, int]:
        """
        저장된 데이터 통계를 반환합니다.

        Returns:
            Dict[str, int]: 메트릭 타입별 데이터 포인트 수
        """
        with self._lock:
            return {
                metric_type: len(data)
                for metric_type, data in self._data.items()
            }
