"""CPU 수집기 테스트"""
import pytest
from app.collectors.cpu_collector import CPUCollector


class TestCPUCollector:
    """CPU 수집기 테스트 클래스"""

    def test_collector_initialization(self):
        """수집기가 정상적으로 초기화되는지 테스트"""
        collector = CPUCollector()
        assert collector is not None

    def test_collect_returns_dict(self):
        """collect() 메서드가 딕셔너리를 반환하는지 테스트"""
        collector = CPUCollector()
        metrics = collector.collect()
        assert isinstance(metrics, dict)

    def test_collect_has_required_fields(self):
        """수집된 메트릭이 필수 필드를 포함하는지 테스트"""
        collector = CPUCollector()
        metrics = collector.collect()

        required_fields = [
            'cpu_percent',
            'cpu_percent_per_core',
            'cpu_count_logical',
            'cpu_count_physical'
        ]

        for field in required_fields:
            assert field in metrics, f"Missing required field: {field}"

    def test_cpu_percent_range(self):
        """CPU 사용률이 올바른 범위(0-100)에 있는지 테스트"""
        collector = CPUCollector()
        metrics = collector.collect()

        assert 0 <= metrics['cpu_percent'] <= 100, \
            f"CPU percent out of range: {metrics['cpu_percent']}"

    def test_cpu_percent_per_core_is_list(self):
        """코어별 CPU 사용률이 리스트인지 테스트"""
        collector = CPUCollector()
        metrics = collector.collect()

        assert isinstance(metrics['cpu_percent_per_core'], list)
        assert len(metrics['cpu_percent_per_core']) > 0

    def test_cpu_count_logical_positive(self):
        """논리 CPU 코어 수가 양수인지 테스트"""
        collector = CPUCollector()
        metrics = collector.collect()

        assert metrics['cpu_count_logical'] > 0

    def test_get_metric_type(self):
        """get_metric_type()이 올바른 타입을 반환하는지 테스트"""
        collector = CPUCollector()
        assert collector.get_metric_type() == "cpu"

    def test_multiple_collections(self):
        """여러 번 수집해도 정상 동작하는지 테스트"""
        collector = CPUCollector()

        metrics1 = collector.collect()
        metrics2 = collector.collect()

        assert isinstance(metrics1, dict)
        assert isinstance(metrics2, dict)
        assert 'cpu_percent' in metrics1
        assert 'cpu_percent' in metrics2
