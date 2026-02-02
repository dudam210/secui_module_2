# 시스템 리소스 메트릭 모니터링 시스템 PRD

## 1. 프로젝트 개요

서버의 실시간 시스템 리소스를 수집, 저장, 모니터링하는 시스템을 구축합니다. CPU, 메모리, 디스크, 네트워크 등 핵심 하드웨어 리소스의 사용률을 추적하여 서버 상태를 가시화하고 문제를 조기에 감지합니다.

## 2. 목표

### 2.1 주요 목표
- 실시간 시스템 리소스 모니터링
- 히스토리 데이터 수집 및 저장
- 직관적인 대시보드를 통한 데이터 시각화
- 임계값 기반 알림 시스템 구축

### 2.2 성공 지표
- 메트릭 수집 주기: 1초 ~ 60초 (설정 가능)
- 데이터 정확도: 99% 이상
- 대시보드 응답 시간: 2초 이내
- 시스템 오버헤드: CPU 5% 미만

## 3. 범위

### 3.1 포함 사항 (In Scope)
- ✅ CPU 메트릭 수집
- ✅ 메모리 메트릭 수집
- ✅ 디스크 메트릭 수집
- ✅ 네트워크 메트릭 수집
- ✅ 프로세스별 리소스 모니터링
- ✅ REST API 제공
- ✅ 시계열 데이터 저장
- ✅ 웹 대시보드 구현

### 3.2 제외 사항 (Out of Scope)
- ❌ 분산 시스템 모니터링 (단일 서버만 지원)
- ❌ 애플리케이션 레벨 APM
- ❌ 로그 수집 및 분석
- ❌ 클라우드 서비스 통합

## 4. 기술 스택

### 4.1 백엔드
- **언어**: Python 3.10+
- **메트릭 수집**: psutil
- **웹 프레임워크**: FastAPI
- **데이터베이스**: InfluxDB (시계열 DB) 또는 SQLite (간단한 구현)
- **스케줄링**: APScheduler

### 4.2 프론트엔드
- **대시보드**: Grafana 또는 커스텀 웹 UI (React/Vue)
- **차트 라이브러리**: Chart.js, Plotly

### 4.3 인프라
- **컨테이너화**: Docker
- **배포**: Docker Compose

## 5. 주요 기능

### 5.1 메트릭 수집 기능

#### 5.1.1 CPU 메트릭
| 메트릭 | 설명 | 단위 |
|--------|------|------|
| cpu_usage_total | 전체 CPU 사용률 | % |
| cpu_usage_per_core | 코어별 CPU 사용률 | % |
| cpu_count | CPU 코어 수 | count |
| cpu_frequency | CPU 주파수 (현재/최소/최대) | MHz |
| load_average | 시스템 로드 (1분, 5분, 15분) | - |

#### 5.1.2 메모리 메트릭
| 메트릭 | 설명 | 단위 |
|--------|------|------|
| memory_total | 전체 메모리 | bytes |
| memory_available | 사용 가능한 메모리 | bytes |
| memory_used | 사용 중인 메모리 | bytes |
| memory_percent | 메모리 사용률 | % |
| swap_total | 스왑 메모리 크기 | bytes |
| swap_used | 사용 중인 스왑 메모리 | bytes |
| swap_percent | 스왑 메모리 사용률 | % |

#### 5.1.3 디스크 메트릭
| 메트릭 | 설명 | 단위 |
|--------|------|------|
| disk_total | 전체 디스크 용량 | bytes |
| disk_used | 사용 중인 디스크 용량 | bytes |
| disk_free | 남은 디스크 용량 | bytes |
| disk_percent | 디스크 사용률 | % |
| disk_read_bytes | 디스크 읽기 bytes | bytes/s |
| disk_write_bytes | 디스크 쓰기 bytes | bytes/s |
| disk_read_count | 디스크 읽기 횟수 | count/s |
| disk_write_count | 디스크 쓰기 횟수 | count/s |

#### 5.1.4 네트워크 메트릭
| 메트릭 | 설명 | 단위 |
|--------|------|------|
| net_bytes_sent | 송신 데이터량 | bytes/s |
| net_bytes_recv | 수신 데이터량 | bytes/s |
| net_packets_sent | 송신 패킷 수 | count/s |
| net_packets_recv | 수신 패킷 수 | count/s |
| net_errin | 수신 에러 수 | count/s |
| net_errout | 송신 에러 수 | count/s |
| net_dropin | 수신 드롭 수 | count/s |
| net_dropout | 송신 드롭 수 | count/s |

#### 5.1.5 프로세스 메트릭 (Top N 프로세스)
| 메트릭 | 설명 | 단위 |
|--------|------|------|
| process_name | 프로세스 이름 | string |
| process_pid | 프로세스 ID | number |
| process_cpu_percent | CPU 사용률 | % |
| process_memory_percent | 메모리 사용률 | % |
| process_memory_rss | 실제 메모리 사용량 | bytes |
| process_num_threads | 스레드 수 | count |
| process_status | 프로세스 상태 | string |

### 5.2 데이터 저장 기능
- 시계열 데이터베이스에 메트릭 저장
- 데이터 보관 정책 (retention policy)
  - 1초 해상도: 1일 보관
  - 1분 해상도: 7일 보관
  - 5분 해상도: 30일 보관
  - 1시간 해상도: 1년 보관

### 5.3 API 기능
- `GET /api/v1/metrics/current` - 현재 시스템 메트릭 조회
- `GET /api/v1/metrics/cpu` - CPU 메트릭 시계열 조회
- `GET /api/v1/metrics/memory` - 메모리 메트릭 시계열 조회
- `GET /api/v1/metrics/disk` - 디스크 메트릭 시계열 조회
- `GET /api/v1/metrics/network` - 네트워크 메트릭 시계열 조회
- `GET /api/v1/metrics/processes` - 프로세스 메트릭 조회
- `GET /api/v1/health` - 시스템 상태 확인

### 5.4 대시보드 기능
- 실시간 메트릭 시각화
  - CPU 사용률 차트 (라인 차트)
  - 메모리 사용률 게이지
  - 디스크 사용률 바 차트
  - 네트워크 트래픽 차트
- 히스토리 데이터 조회 (시간 범위 선택)
- Top N 프로세스 테이블
- 알림 상태 표시

### 5.5 알림 기능
- 임계값 설정
  - CPU 사용률 > 80% (5분 지속 시)
  - 메모리 사용률 > 90%
  - 디스크 사용률 > 85%
- 알림 채널
  - 이메일
  - Slack 웹훅
  - 로그 파일

## 6. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Client (Browser)                      │
│                  Dashboard UI (Web)                      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   API Server (FastAPI)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ REST API     │  │ Metrics      │  │ Alert        │  │
│  │ Endpoints    │  │ Collector    │  │ Manager      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Time Series Database (InfluxDB)             │
│                    또는 SQLite                            │
└─────────────────────────────────────────────────────────┘
                     ▲
                     │
┌────────────────────┴────────────────────────────────────┐
│              Metrics Collector (psutil)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │   CPU    │ │  Memory  │ │   Disk   │ │ Network  │   │
│  │ Monitor  │ │ Monitor  │ │ Monitor  │ │ Monitor  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 7. 데이터 모델

### 7.1 메트릭 데이터 스키마 (InfluxDB)

```
measurement: system_metrics
tags:
  - host: hostname
  - metric_type: cpu|memory|disk|network
fields:
  - cpu_percent: float
  - memory_used: integer
  - disk_read_bytes: integer
  - net_bytes_sent: integer
  - ...
timestamp: nanoseconds
```

## 8. API 명세 예시

### 8.1 현재 메트릭 조회

**Request**
```http
GET /api/v1/metrics/current
```

**Response**
```json
{
  "timestamp": "2026-02-02T10:30:00Z",
  "hostname": "server-01",
  "cpu": {
    "usage_percent": 45.2,
    "per_core": [42.1, 48.3, 43.5, 47.0],
    "frequency": {
      "current": 2400,
      "min": 800,
      "max": 3600
    },
    "load_average": [2.5, 2.3, 2.1]
  },
  "memory": {
    "total": 17179869184,
    "available": 8589934592,
    "used": 8589934592,
    "percent": 50.0,
    "swap": {
      "total": 4294967296,
      "used": 1073741824,
      "percent": 25.0
    }
  },
  "disk": {
    "total": 536870912000,
    "used": 322122547200,
    "free": 214748364800,
    "percent": 60.0,
    "io": {
      "read_bytes_per_sec": 1048576,
      "write_bytes_per_sec": 524288,
      "read_count_per_sec": 100,
      "write_count_per_sec": 50
    }
  },
  "network": {
    "bytes_sent_per_sec": 1048576,
    "bytes_recv_per_sec": 2097152,
    "packets_sent_per_sec": 1000,
    "packets_recv_per_sec": 1500,
    "errors_in": 0,
    "errors_out": 0
  }
}
```

## 9. 구현 계획

### Phase 1: 기본 메트릭 수집 (Week 1)
- psutil 기반 메트릭 수집 모듈 구현
- CPU, 메모리, 디스크, 네트워크 메트릭 수집
- SQLite 기반 데이터 저장

### Phase 2: API 서버 구축 (Week 2)
- FastAPI 서버 구현
- REST API 엔드포인트 개발
- 스케줄러를 통한 주기적 메트릭 수집

### Phase 3: 대시보드 구현 (Week 3)
- 웹 기반 대시보드 UI 개발
- 실시간 차트 및 그래프 구현
- 히스토리 데이터 조회 기능

### Phase 4: 알림 시스템 (Week 4)
- 임계값 기반 알림 로직 구현
- 이메일/Slack 알림 통합
- 알림 설정 UI

### Phase 5: 최적화 및 배포 (Week 5)
- 성능 최적화
- Docker 컨테이너화
- 문서화 및 배포

## 10. 비기능 요구사항

### 10.1 성능
- 메트릭 수집 오버헤드: CPU 5% 미만
- API 응답 시간: 평균 200ms 이하
- 동시 접속자: 최소 100명 지원

### 10.2 확장성
- 플러그인 아키텍처로 새로운 메트릭 추가 가능
- 다중 서버 모니터링 확장 가능한 구조

### 10.3 신뢰성
- 메트릭 수집 실패 시 재시도 로직
- 데이터베이스 장애 시 로컬 캐시
- 시스템 오류 로깅

### 10.4 보안
- API 인증 및 인가 (JWT)
- HTTPS 통신
- Rate limiting

## 11. 테스트 계획

### 11.1 단위 테스트
- 각 메트릭 수집 함수 테스트
- API 엔드포인트 테스트
- 데이터 저장/조회 테스트

### 11.2 통합 테스트
- 전체 파이프라인 테스트
- API → DB → 대시보드 통합 테스트

### 11.3 부하 테스트
- 장기간 메트릭 수집 안정성 테스트
- API 동시 요청 처리 테스트

## 12. 향후 확장 계획

- 분산 시스템 모니터링 지원
- 머신러닝 기반 이상 탐지
- 커스텀 메트릭 정의 기능
- Prometheus 호환 exporter
- 클라우드 서비스 (AWS CloudWatch, Azure Monitor) 연동
- 모바일 앱 지원

## 13. 참고 자료

- [psutil Documentation](https://psutil.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Grafana Documentation](https://grafana.com/docs/)

---

**문서 버전**: 1.0
**최종 수정일**: 2026-02-02
**작성자**: Development Team
