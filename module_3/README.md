# System Monitoring API (Module 3)

Python FastAPI 기반 시스템 리소스 모니터링 백엔드 API

## 특징

- **실시간 메트릭 수집**: CPU, 메모리, 디스크, 네트워크, 프로세스 정보 수집
- **RESTful API**: FastAPI 기반의 고성능 REST API
- **자동 수집**: APScheduler를 이용한 주기적 메트릭 수집
- **시계열 저장**: 인메모리 스토리지로 시계열 데이터 저장
- **테스트 완비**: 단위 테스트 및 통합 테스트 포함

## 기술 스택 (Level 1)

- **언어**: Python 3.11+
- **웹 프레임워크**: FastAPI 0.109+
- **메트릭 수집**: psutil 7.2.2
- **스케줄러**: APScheduler 3.10+
- **테스트**: pytest 7.4+
- **ASGI 서버**: uvicorn

## 설치 및 실행

### 1. 의존성 설치

```bash
# 가상 환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 의존성 설치
pip install -r requirements-level1.txt
```

### 2. 개발 모드로 실행

```bash
# 방법 1: Python 모듈로 실행
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 방법 2: 메인 파일 직접 실행
python app/main.py
```

### 3. API 문서 확인

서버 실행 후 브라우저에서 다음 URL로 접속:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 엔드포인트

### 기본

- `GET /` - API 정보
- `GET /api/v1/health` - 헬스체크

### 메트릭

- `GET /api/v1/metrics/current` - 모든 메트릭의 현재 스냅샷
- `GET /api/v1/metrics/cpu` - CPU 시계열 데이터
- `GET /api/v1/metrics/memory` - 메모리 시계열 데이터
- `GET /api/v1/metrics/disk` - 디스크 시계열 데이터
- `GET /api/v1/metrics/network` - 네트워크 시계열 데이터
- `GET /api/v1/metrics/processes` - 상위 프로세스 목록

### 쿼리 파라미터

#### 시계열 메트릭 (CPU, 메모리, 디스크, 네트워크)

- `start`: 시작 시간 (ISO 8601 형식)
- `end`: 종료 시간 (ISO 8601 형식)
- `limit`: 최대 반환 개수 (기본값: 100, 최대: 1000)

예시:
```bash
curl "http://localhost:8000/api/v1/metrics/cpu?limit=50"
```

#### 프로세스

- `limit`: 반환할 프로세스 수 (기본값: 10, 최대: 100)
- `sort_by`: 정렬 기준 (cpu 또는 memory, 기본값: cpu)

예시:
```bash
curl "http://localhost:8000/api/v1/metrics/processes?limit=20&sort_by=memory"
```

## 테스트

### 모든 테스트 실행

```bash
pytest
```

### 커버리지와 함께 실행

```bash
pytest --cov=app tests/
```

### 특정 테스트 파일 실행

```bash
pytest tests/test_collectors/test_cpu_collector.py
```

### 특정 테스트 클래스/함수 실행

```bash
pytest tests/test_collectors/test_cpu_collector.py::TestCPUCollector::test_collect_returns_dict
```

## 프로젝트 구조

```
module_3/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── metrics.py      # API 라우트
│   ├── collectors/
│   │   ├── cpu_collector.py    # CPU 메트릭 수집기
│   │   ├── memory_collector.py # 메모리 메트릭 수집기
│   │   ├── disk_collector.py   # 디스크 메트릭 수집기
│   │   ├── network_collector.py# 네트워크 메트릭 수집기
│   │   └── process_collector.py# 프로세스 메트릭 수집기
│   ├── models/
│   │   └── metrics.py          # Pydantic 데이터 모델
│   ├── storage/
│   │   └── memory_storage.py   # 인메모리 스토리지
│   └── main.py                 # FastAPI 메인 애플리케이션
├── tests/
│   ├── test_collectors/        # 수집기 단위 테스트
│   ├── test_storage/           # 스토리지 단위 테스트
│   └── test_api/               # API 통합 테스트
├── requirements-level1.txt     # Level 1 의존성
└── pytest.ini                  # pytest 설정
```

## 아키텍처

시스템은 3개의 주요 레이어로 구성됩니다:

### 1. 메트릭 수집 레이어 (app/collectors/)

- `psutil`을 사용하여 시스템 메트릭 수집
- 각 수집기는 독립적으로 동작
- 플러그인 아키텍처로 쉽게 확장 가능

### 2. API 서버 레이어 (app/api/)

- FastAPI 기반 REST 엔드포인트 제공
- APScheduler가 주기적 메트릭 수집 관리 (기본 5초)
- CORS 지원으로 프론트엔드 통합 가능

### 3. 스토리지 레이어 (app/storage/)

- 인메모리 시계열 데이터 저장
- 스레드 안전
- 최대 데이터 포인트 수 제한 (기본 3600개)

## 설정

### 메트릭 수집 주기 변경

`app/main.py`에서 스케줄러 설정을 수정:

```python
scheduler.add_job(
    collect_metrics,
    'interval',
    seconds=5,  # 원하는 초 단위로 변경
    id='metric_collection',
    replace_existing=True
)
```

### 저장 데이터 포인트 수 변경

`app/main.py`에서 스토리지 초기화 시 변경:

```python
storage = MemoryStorage(max_data_points=3600)  # 원하는 개수로 변경
```

## 성능

- **메트릭 수집 오버헤드**: <5% CPU
- **API 응답 시간**: <200ms 평균
- **동시 연결**: 100개 이상 지원
- **수집 주기**: 1-60초 설정 가능

## 다음 단계 (Level 2로 확장)

Level 1에서 Level 2로 확장 시 추가될 기능:

- InfluxDB 시계열 데이터베이스 통합
- PostgreSQL 관계형 데이터베이스
- Redis 캐싱
- JWT 인증
- Rate limiting
- Docker Compose 배포
- Grafana 대시보드 통합

자세한 내용은 `CLAUDE.md`를 참조하세요.

## 문제 해결

### 포트가 이미 사용 중인 경우

```bash
# 다른 포트로 실행
uvicorn app.main:app --port 8001
```

### psutil 설치 오류 (Windows)

Visual C++ Build Tools가 필요할 수 있습니다:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

### 권한 오류

일부 시스템 메트릭은 관리자 권한이 필요할 수 있습니다:

```bash
# Windows (관리자 권한으로 실행)
# Linux/Mac
sudo python app/main.py
```

## 라이선스

이 프로젝트는 학습 목적으로 제작되었습니다.
