"""메모리 스토리지 테스트"""
import pytest
from datetime import datetime, timedelta
from app.storage.memory_storage import MemoryStorage


class TestMemoryStorage:
    """메모리 스토리지 테스트 클래스"""

    def test_storage_initialization(self):
        """스토리지가 정상적으로 초기화되는지 테스트"""
        storage = MemoryStorage()
        assert storage is not None

    def test_save_metric(self):
        """메트릭 저장이 정상 동작하는지 테스트"""
        storage = MemoryStorage()
        data = {'cpu_percent': 50.0, 'timestamp': datetime.now()}

        result = storage.save_metric('cpu', data)
        assert result is True

    def test_save_invalid_metric_type(self):
        """잘못된 메트릭 타입 저장 시 False 반환하는지 테스트"""
        storage = MemoryStorage()
        data = {'value': 100}

        result = storage.save_metric('invalid_type', data)
        assert result is False

    def test_get_latest(self):
        """최신 메트릭 조회가 정상 동작하는지 테스트"""
        storage = MemoryStorage()
        data = {'cpu_percent': 50.0, 'timestamp': datetime.now()}

        storage.save_metric('cpu', data)
        latest = storage.get_latest('cpu')

        assert latest is not None
        assert latest['cpu_percent'] == 50.0

    def test_get_latest_empty(self):
        """데이터가 없을 때 None을 반환하는지 테스트"""
        storage = MemoryStorage()
        latest = storage.get_latest('cpu')

        assert latest is None

    def test_get_range(self):
        """시간 범위 조회가 정상 동작하는지 테스트"""
        storage = MemoryStorage()

        # 여러 개의 데이터 저장
        for i in range(10):
            data = {
                'cpu_percent': float(i * 10),
                'timestamp': datetime.now() + timedelta(seconds=i)
            }
            storage.save_metric('cpu', data)

        # 전체 데이터 조회
        all_data = storage.get_range('cpu')
        assert len(all_data) == 10

    def test_get_range_with_limit(self):
        """limit을 적용한 조회가 정상 동작하는지 테스트"""
        storage = MemoryStorage()

        # 10개의 데이터 저장
        for i in range(10):
            data = {'cpu_percent': float(i * 10)}
            storage.save_metric('cpu', data)

        # 최근 5개만 조회
        limited_data = storage.get_range('cpu', limit=5)
        assert len(limited_data) == 5

    def test_get_range_with_time_filter(self):
        """시간 필터링이 정상 동작하는지 테스트"""
        storage = MemoryStorage()

        now = datetime.now()
        # 시간 간격을 두고 데이터 저장
        for i in range(5):
            data = {
                'cpu_percent': float(i * 10),
                'timestamp': now + timedelta(seconds=i)
            }
            storage.save_metric('cpu', data)

        # 특정 시간 이후 데이터만 조회
        filtered_data = storage.get_range(
            'cpu',
            start=now + timedelta(seconds=2)
        )
        assert len(filtered_data) <= 3  # 2, 3, 4초 데이터

    def test_get_all_latest(self):
        """모든 메트릭 타입의 최신 데이터 조회 테스트"""
        storage = MemoryStorage()

        # 각 메트릭 타입에 데이터 저장
        storage.save_metric('cpu', {'cpu_percent': 50.0})
        storage.save_metric('memory', {'memory_percent': 60.0})

        all_latest = storage.get_all_latest()

        assert 'cpu' in all_latest
        assert 'memory' in all_latest
        assert all_latest['cpu']['cpu_percent'] == 50.0
        assert all_latest['memory']['memory_percent'] == 60.0

    def test_clear_specific_metric(self):
        """특정 메트릭 타입의 데이터 삭제 테스트"""
        storage = MemoryStorage()

        storage.save_metric('cpu', {'cpu_percent': 50.0})
        storage.save_metric('memory', {'memory_percent': 60.0})

        storage.clear('cpu')

        assert storage.get_latest('cpu') is None
        assert storage.get_latest('memory') is not None

    def test_clear_all(self):
        """전체 데이터 삭제 테스트"""
        storage = MemoryStorage()

        storage.save_metric('cpu', {'cpu_percent': 50.0})
        storage.save_metric('memory', {'memory_percent': 60.0})

        storage.clear()

        assert storage.get_latest('cpu') is None
        assert storage.get_latest('memory') is None

    def test_get_stats(self):
        """통계 조회 테스트"""
        storage = MemoryStorage()

        # 데이터 저장
        for i in range(5):
            storage.save_metric('cpu', {'cpu_percent': float(i)})
        for i in range(3):
            storage.save_metric('memory', {'memory_percent': float(i)})

        stats = storage.get_stats()

        assert stats['cpu'] == 5
        assert stats['memory'] == 3

    def test_max_data_points(self):
        """최대 데이터 포인트 제한 테스트"""
        storage = MemoryStorage(max_data_points=10)

        # 15개의 데이터 저장 (최대 10개로 제한됨)
        for i in range(15):
            storage.save_metric('cpu', {'value': i})

        all_data = storage.get_range('cpu')
        assert len(all_data) == 10  # 최대 10개만 유지

    def test_thread_safety(self):
        """스레드 안전성 기본 테스트"""
        import threading

        storage = MemoryStorage()
        errors = []

        def save_data(thread_id):
            try:
                for i in range(100):
                    storage.save_metric('cpu', {'value': thread_id * 100 + i})
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=save_data, args=(i,)) for i in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # 오류가 발생하지 않았는지 확인
        assert len(errors) == 0

        # 데이터가 정상적으로 저장되었는지 확인
        all_data = storage.get_range('cpu')
        assert len(all_data) > 0
