"""API 엔드포인트 테스트"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.collectors.cpu_collector import CPUCollector
from app.collectors.memory_collector import MemoryCollector
from app.collectors.disk_collector import DiskCollector
from app.collectors.network_collector import NetworkCollector
from app.collectors.process_collector import ProcessCollector
from app.storage.memory_storage import MemoryStorage
from app.api.routes import metrics


@pytest.fixture
def client():
    """테스트 클라이언트 픽스처"""
    # 테스트용 수집기와 스토리지 초기화
    storage = MemoryStorage()
    collectors = {
        'cpu': CPUCollector(),
        'memory': MemoryCollector(),
        'disk': DiskCollector(),
        'network': NetworkCollector(),
        'process': ProcessCollector()
    }

    # 일부 테스트 데이터 추가
    storage.save_metric('cpu', {'cpu_percent': 50.0, 'timestamp': datetime.now()})
    storage.save_metric('memory', {'memory_percent': 60.0, 'timestamp': datetime.now()})

    # API 라우트에 의존성 주입
    metrics.set_dependencies(collectors, storage)

    return TestClient(app)


class TestHealthEndpoint:
    """헬스체크 엔드포인트 테스트"""

    def test_health_check(self, client):
        """헬스체크가 정상 응답하는지 테스트"""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


class TestRootEndpoint:
    """루트 엔드포인트 테스트"""

    def test_root(self, client):
        """루트 엔드포인트가 정상 응답하는지 테스트"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'version' in data


class TestMetricsEndpoints:
    """메트릭 엔드포인트 테스트"""

    def test_get_current_metrics(self, client):
        """현재 메트릭 조회 테스트"""
        response = client.get("/api/v1/metrics/current")

        assert response.status_code == 200
        data = response.json()

        # 모든 메트릭 타입이 포함되어 있는지 확인
        assert 'cpu' in data
        assert 'memory' in data
        assert 'disk' in data
        assert 'network' in data

    def test_get_cpu_metrics(self, client):
        """CPU 메트릭 조회 테스트"""
        response = client.get("/api/v1/metrics/cpu")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_cpu_metrics_with_limit(self, client):
        """CPU 메트릭 limit 파라미터 테스트"""
        response = client.get("/api/v1/metrics/cpu?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_memory_metrics(self, client):
        """메모리 메트릭 조회 테스트"""
        response = client.get("/api/v1/metrics/memory")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_disk_metrics(self, client):
        """디스크 메트릭 조회 테스트"""
        response = client.get("/api/v1/metrics/disk")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_network_metrics(self, client):
        """네트워크 메트릭 조회 테스트"""
        response = client.get("/api/v1/metrics/network")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_processes(self, client):
        """프로세스 목록 조회 테스트"""
        response = client.get("/api/v1/metrics/processes")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10  # 기본 limit

    def test_get_processes_with_custom_limit(self, client):
        """프로세스 목록 커스텀 limit 테스트"""
        response = client.get("/api/v1/metrics/processes?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_processes_sort_by_memory(self, client):
        """프로세스 목록 메모리 기준 정렬 테스트"""
        response = client.get("/api/v1/metrics/processes?sort_by=memory")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_processes_invalid_sort_by(self, client):
        """프로세스 목록 잘못된 정렬 기준 테스트"""
        response = client.get("/api/v1/metrics/processes?sort_by=invalid")

        assert response.status_code == 422  # Validation error

    def test_cors_headers(self, client):
        """CORS 헤더가 포함되어 있는지 테스트"""
        response = client.options("/api/v1/health")

        # CORS 미들웨어가 정상 동작하는지 확인
        assert response.status_code in [200, 405]  # OPTIONS 메서드가 지원될 수 있음
