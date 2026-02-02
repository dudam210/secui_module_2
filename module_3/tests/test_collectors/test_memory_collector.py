"""메모리 수집기 테스트"""
import pytest
from app.collectors.memory_collector import MemoryCollector


class TestMemoryCollector:
    """메모리 수집기 테스트 클래스"""

    def test_collector_initialization(self):
        """수집기가 정상적으로 초기화되는지 테스트"""
        collector = MemoryCollector()
        assert collector is not None

    def test_collect_returns_dict(self):
        """collect() 메서드가 딕셔너리를 반환하는지 테스트"""
        collector = MemoryCollector()
        metrics = collector.collect()
        assert isinstance(metrics, dict)

    def test_collect_has_required_fields(self):
        """수집된 메트릭이 필수 필드를 포함하는지 테스트"""
        collector = MemoryCollector()
        metrics = collector.collect()

        required_fields = [
            'memory_total',
            'memory_available',
            'memory_used',
            'memory_percent',
            'swap_total',
            'swap_used',
            'swap_percent'
        ]

        for field in required_fields:
            assert field in metrics, f"Missing required field: {field}"

    def test_memory_values_non_negative(self):
        """메모리 값들이 음수가 아닌지 테스트"""
        collector = MemoryCollector()
        metrics = collector.collect()

        assert metrics['memory_total'] >= 0
        assert metrics['memory_available'] >= 0
        assert metrics['memory_used'] >= 0

    def test_memory_percent_range(self):
        """메모리 사용률이 올바른 범위(0-100)에 있는지 테스트"""
        collector = MemoryCollector()
        metrics = collector.collect()

        assert 0 <= metrics['memory_percent'] <= 100

    def test_memory_total_greater_than_used(self):
        """전체 메모리가 사용 중인 메모리보다 크거나 같은지 테스트"""
        collector = MemoryCollector()
        metrics = collector.collect()

        assert metrics['memory_total'] >= metrics['memory_used']

    def test_get_metric_type(self):
        """get_metric_type()이 올바른 타입을 반환하는지 테스트"""
        collector = MemoryCollector()
        assert collector.get_metric_type() == "memory"
