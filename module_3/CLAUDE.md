# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 저장소의 코드를 작업할 때 참고하는 가이드입니다.

## 프로젝트 개요

시스템 리소스 메트릭 모니터링 시스템 - 단일 서버의 실시간 시스템 리소스 메트릭(CPU, 메모리, 디스크, 네트워크)을 수집, 저장 및 시각화하는 서버 모니터링 시스템입니다.

**기술 스택:**

이 프로젝트는 5단계의 기술 스택 레벨을 지원하며, 각 레벨은 특정 사용 사례와 규모에 맞게 설계되었습니다:

- **Level 1**: 최소 구성 (로컬 개발/학습) - 1-10명 사용자
- **Level 2**: 기본 프로덕션 (소규모 배포) - 10-50명 사용자
- **Level 3**: 중급 (모니터링/로깅 추가) - 50-500명 사용자
- **Level 4**: 고급 (고가용성/확장성) - 500-5K명 사용자
- **Level 5**: 엔터프라이즈급 (완전한 관측성) - 5K+명 사용자

각 레벨의 상세 내용은 아래 "기술 스택 상세" 섹션을 참조하세요.

**기본 코어 스택 (모든 레벨 공통):**
- 언어: Python 3.11+
- 메트릭 수집: psutil 7.2.2
- 웹 프레임워크: FastAPI 0.109+
- 스케줄러: APScheduler 3.10U
- 데이터베이스: InfluxDB 2.7+ 또는 VictoriaMetrics (시계열)

## Skills
   **Git commit**
   - 사용자가 Git commit을 요청 할때 `C:\Users\student\Desktop\vibe_coding\module_3\.claude\skills\git-commit\SKILL.md`를 참고하여 Git commit을 수행한다.
   **Code review**
- 사용자가 Python코드 리뷰를 요청 할때 `C:\Users\student\Desktop\vibe_coding\module_3\.claude\skills\code-review\SKILL.md`를 참고하여 코드 리뷰를 수행한다.

## 기술 스택 상세

### Level 1: 최소 구성 (로컬 개발/학습)

**목적:** 로컬 개발, 프로토타이핑, 학습 환경에 적합한 최소 구성

**핵심 컴포넌트:**
- **백엔드:** Python 3.11+, FastAPI 0.109+, psutil 7.2.2, APScheduler 3.10+, uvicorn
- **데이터베이스:** SQLite (Python 내장) 또는 InfluxDB 2.7 OSS
- **프론트엔드:** 없음 (API만) 또는 간단한 HTML + Chart.js
- **배포:** 로컬 프로세스 (uvicorn)
- **개발 도구:** pytest 7.4+, black 24.1+, ruff 0.1+

**모니터링/로깅:**
- 기본 Python logging 모듈
- 콘솔 출력

**보안:**
- 없음 (로컬 전용)

**리소스 요구사항:**
- CPU: 1 코어
- 메모리: 512MB RAM
- 디스크: 1GB
- 네트워크: 로컬호스트만

**사용 시나리오:**
- 개인 학습 및 프로토타이핑
- 로컬 개발 환경
- 개념 증명 (PoC)
- 1-10명 개발자

**예상 설정 시간:** 1시간

---

### Level 2: 기본 프로덕션 (소규모 배포)

**목적:** 소규모 팀이나 스타트업의 초기 프로덕션 환경

**핵심 컴포넌트:**
- **백엔드:** Level 1 + JWT 인증 (python-jose), Rate limiting (slowapi)
- **데이터베이스:**
  - 시계열: InfluxDB 2.7 OSS
  - 관계형: PostgreSQL 14+ (SQLAlchemy 2.0+, asyncpg)
  - 캐싱: Redis 7.2+
- **프론트엔드:** Grafana 10.3+
- **배포:** Docker Compose, Nginx (리버스 프록시)
- **로깅:** loguru 0.7+

**모니터링/로깅:**
- Grafana 대시보드
- 파일 기반 로깅 (JSON 포맷)
- 기본 헬스체크 엔드포인트

**보안:**
- HTTPS (Let's Encrypt)
- JWT 인증
- Rate limiting
- 기본 CORS 정책

**리소스 요구사항:**
- CPU: 2-4 코어
- 메모리: 4-8GB RAM
- 디스크: 50-100GB (SSD 권장)
- 네트워크: 100Mbps+

**사용 시나리오:**
- 스타트업 MVP
- 소규모 팀 (2-5명)
- 단일 서버 배포
- 10-50명 사용자

**예상 설정 시간:** 1일

---

### Level 3: 중급 (모니터링/로깅)

**목적:** 관측성(Observability)이 중요한 중규모 환경

**핵심 컴포넌트:**
- **백엔드:** Level 2 + OpenTelemetry, Celery (비동기 작업)
- **데이터베이스:**
  - 시계열: VictoriaMetrics (InfluxDB 대안, 더 높은 성능)
  - 관계형: PostgreSQL 14+ (연결 풀링)
  - 캐싱: Redis 7.2+
  - 메시지 큐: Redis (Celery 백엔드)
- **프론트엔드:** Grafana 10.3+ (고급 대시보드)
- **배포:** Docker Compose 또는 소규모 Kubernetes

**모니터링/로깅:**
- **메트릭:** Prometheus 2.49+, VictoriaMetrics
- **로그:** Loki 2.9+, Promtail
- **추적:** OpenTelemetry (선택사항)
- **알림:** Alertmanager 0.26+
- **에러 트래킹:** Sentry
- **시스템 메트릭:** Node Exporter 1.7+

**보안:**
- Level 2의 모든 기능
- 역할 기반 접근 제어 (RBAC)
- 감사 로그
- 데이터베이스 연결 암호화

**리소스 요구사항:**
- CPU: 8-16 코어
- 메모리: 16-32GB RAM
- 디스크: 200-500GB (SSD 필수)
- 네트워크: 1Gbps+

**사용 시나리오:**
- 성장 중인 회사
- 중규모 팀 (5-10명)
- 관측성이 중요한 환경
- 50-500명 사용자
- 95%+ 가동시간 요구

**예상 설정 시간:** 1주

---

### Level 4: 고급 (고가용성/확장성)

**목적:** 고가용성과 수평 확장이 필요한 대규모 환경

**핵심 컴포넌트:**
- **백엔드:** Level 3 + 멀티 인스턴스, 로드 밸런싱
- **데이터베이스:**
  - 시계열: VictoriaMetrics Cluster
  - 관계형: PostgreSQL HA (Patroni 3.2+), 읽기 복제본
  - 캐싱: Redis Cluster (HA)
  - 메시지 큐: RabbitMQ Cluster (Celery 백엔드)
- **프론트엔드:** Grafana HA
- **배포:** Kubernetes, Helm Charts
- **로드 밸런서:** HAProxy 또는 Nginx Plus

**모니터링/로깅:**
- Level 3의 모든 기능
- **장기 저장:** Thanos (Prometheus 장기 저장)
- **분산 추적:** OpenTelemetry + Jaeger/Tempo
- **시크릿 관리:** HashiCorp Vault
- **인프라 모니터링:** Kubernetes 메트릭, cAdvisor

**보안:**
- Level 3의 모든 기능
- Vault 기반 시크릿 관리
- 네트워크 정책 (Kubernetes NetworkPolicy)
- Pod Security Standards
- 데이터베이스 암호화 (at-rest, in-transit)
- 정기 백업 및 재해 복구 계획

**리소스 요구사항:**
- CPU: 32-64 코어 (클러스터 전체)
- 메모리: 64-128GB RAM
- 디스크: 1-5TB (SSD 필수, NVMe 권장)
- 네트워크: 10Gbps+

**사용 시나리오:**
- 중견 기업
- 대규모 팀 (10-20명)
- 미션 크리티컬 서비스
- 500-5K명 사용자
- 99.9%+ 가동시간 요구
- 수평 확장 필요

**예상 설정 시간:** 2-4주

---

### Level 5: 엔터프라이즈급 (완전한 관측성)

**목적:** 대기업, 금융, 의료 등 규제 준수가 필요한 글로벌 환경

**핵심 컴포넌트:**
- **백엔드:** Level 4 + Service Mesh, 멀티 리전
- **데이터베이스:**
  - 시계열: VictoriaMetrics Enterprise Cluster
  - 관계형: CockroachDB (글로벌 분산) 또는 PostgreSQL 멀티 리전
  - 캐싱: Redis Enterprise
  - 메시지 큐: Apache Kafka (멀티 클러스터)
- **프론트엔드:** Grafana Enterprise
- **배포:** 멀티 클러스터 Kubernetes, GitOps (ArgoCD)
- **Service Mesh:** Istio 또는 Linkerd

**모니터링/로깅 (LGTM Stack):**
- **L**oki: 분산 로그 집계
- **G**rafana: 통합 관측성 플랫폼
- **T**empo: 분산 추적
- **M**imir: Prometheus 장기 저장 및 멀티테넌시
- **추가:** OpenTelemetry Collector, SIEM 통합 (Splunk/ELK)

**보안:**
- Level 4의 모든 기능
- Zero Trust 아키텍처
- SIEM 통합
- 규정 준수 도구 (SOC 2, HIPAA, PCI-DSS)
- 고급 위협 탐지
- 자동화된 보안 스캔 (SAST, DAST)
- 감사 로그 장기 보관 (7년+)

**고급 기능:**
- 멀티 리전 배포
- 자동 페일오버 및 재해 복구
- 카나리 배포, 블루-그린 배포
- A/B 테스트 인프라
- 자동 스케일링 (HPA, VPA, Cluster Autoscaler)

**리소스 요구사항:**
- CPU: 100+ 코어 (글로벌 클러스터)
- 메모리: 256GB+ RAM
- 디스크: 10TB+ (NVMe SSD, 분산 스토리지)
- 네트워크: 100Gbps+, 멀티 리전

**사용 시나리오:**
- 대기업 (Fortune 500)
- 글로벌 운영 (멀티 리전)
- 금융, 의료, 정부 기관
- 5K+명 사용자
- 99.99%+ 가동시간 요구 (연간 다운타임 <1시간)
- 규제 준수 필수

**예상 설정 시간:** 1-3개월

---

## 기술 스택 선택 가이드

### 레벨 비교 테이블

| 요소 | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
|------|---------|---------|---------|---------|---------|
| **사용자 수** | 1-10 | 10-50 | 50-500 | 500-5K | 5K+ |
| **가동시간** | 낮음 | 90%+ | 95%+ | 99.9%+ | 99.99%+ |
| **팀 규모** | 1-2명 | 2-5명 | 5-10명 | 10-20명 | 20+명 |
| **예산** | 무료 | 낮음 | 중간 | 높음 | 매우 높음 |
| **복잡도** | 매우 낮음 | 낮음 | 중간 | 높음 | 매우 높음 |
| **설정 시간** | 1시간 | 1일 | 1주 | 2-4주 | 1-3개월 |
| **인프라** | 단일 프로세스 | 단일 서버 | 다중 컨테이너 | 클러스터 | 멀티 클러스터 |
| **데이터베이스** | SQLite | PostgreSQL | PostgreSQL | PostgreSQL HA | CockroachDB |
| **시계열 DB** | SQLite/InfluxDB | InfluxDB | VictoriaMetrics | VM Cluster | VM Enterprise |
| **캐싱** | 없음 | Redis | Redis | Redis Cluster | Redis Enterprise |
| **인증** | 없음 | JWT | JWT + RBAC | JWT + RBAC | Zero Trust |
| **모니터링** | 로그만 | Grafana | Prometheus+Grafana | Prometheus+Thanos | LGTM Stack |
| **로깅** | 콘솔 | 파일 | Loki | Loki | Loki + SIEM |
| **배포** | 로컬 | Docker Compose | Docker/K8s | Kubernetes | 멀티 K8s |

### 권장 시작 레벨

**다음 기준에 따라 적절한 레벨을 선택하세요:**

- **학습/프로토타입:** Level 1
  - 빠르게 시작하고 개념을 이해하는 것이 목표
  - 로컬 환경에서만 실행
  - 최소 의존성, 빠른 설정

- **스타트업 MVP:** Level 2
  - 실제 사용자에게 배포할 준비가 됨
  - 단일 서버로 충분
  - 기본 보안 및 인증 필요
  - 비용 효율적

- **성장 중인 회사:** Level 3
  - 사용자 증가로 관측성 필요
  - 문제 발생 시 빠른 진단 필요
  - 모니터링 및 알림 인프라 구축
  - SLA 준수 시작

- **중견 기업:** Level 4
  - 고가용성 필수
  - 서비스 중단 시 비즈니스 영향 큼
  - 수평 확장 필요
  - 전문 운영 팀 보유

- **대기업/금융/의료:** Level 5
  - 글로벌 운영
  - 규제 준수 필수 (SOC 2, HIPAA 등)
  - 99.99% 가동시간 요구
  - 대규모 엔지니어링 팀

### 마이그레이션 경로

프로젝트가 성장함에 따라 단계적으로 레벨을 높일 수 있습니다:

**Level 1 → 2:**
- Docker Compose로 컨테이너화
- PostgreSQL 및 Redis 추가
- JWT 인증 구현
- HTTPS 설정

**Level 2 → 3:**
- Prometheus 및 Grafana 추가
- Loki로 로그 집계
- OpenTelemetry 계측
- Celery로 비동기 작업 분리

**Level 3 → 4:**
- Kubernetes로 마이그레이션
- 데이터베이스 HA 구성
- Redis Cluster 설정
- Vault로 시크릿 관리

**Level 4 → 5:**
- LGTM Stack 구현
- 멀티 리전 배포
- Service Mesh 추가
- SIEM 통합 및 규정 준수

## 개발 명령어

### 환경 설정 (레벨별)

#### Level 1: 최소 구성
```bash
# 가상 환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 의존성 설치
pip install -r requirements-level1.txt

# 개발 모드로 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API 테스트
curl http://localhost:8000/api/v1/health
```

#### Level 2: 기본 프로덕션
```bash
# 의존성 설치
pip install -r requirements-level2.txt

# Docker Compose로 전체 스택 실행
docker-compose -f docker-compose-level2.yml up -d

# 서비스 확인
docker-compose -f docker-compose-level2.yml ps

# 로그 확인
docker-compose -f docker-compose-level2.yml logs -f app

# 접속 정보
# - API: http://localhost:8000
# - Grafana: http://localhost:3000 (admin/admin)
# - InfluxDB: http://localhost:8086
```

#### Level 3: 중급 (모니터링/로깅)
```bash
# 의존성 설치
pip install -r requirements-level3.txt

# Docker Compose로 전체 관측성 스택 실행
docker-compose -f docker-compose-level3.yml up -d

# 서비스 확인
docker-compose -f docker-compose-level3.yml ps

# 접속 정보
# - API: http://localhost:8000
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
# - Loki: http://localhost:3100
# - Alertmanager: http://localhost:9093
```

#### Level 4-5: Kubernetes 배포
```bash
# Helm을 사용한 배포
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install monitoring ./helm-charts/monitoring

# 배포 상태 확인
kubectl get pods -n monitoring
kubectl get services -n monitoring

# 로그 확인
kubectl logs -f -n monitoring deployment/monitoring-app

# 포트 포워딩으로 로컬 접속
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

### 환경 설정 (공통)
```bash
# 의존성 설치 (기본 - Level 1)
pip install -r requirements-level1.txt

# 개발 모드로 실행
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 테스트
```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_metrics_collector.py

# 커버리지와 함께 실행
pytest --cov=app tests/
```

### Docker
```bash
# Docker Compose로 빌드 및 실행
docker-compose up --build

# 백그라운드 모드로 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

## 아키텍처

시스템은 세 가지 주요 컴포넌트로 구성된 계층 구조를 따릅니다:

### 1. 메트릭 수집 레이어 (`app/collectors/`)
- `psutil`을 사용한 CPU, 메모리, 디스크, 네트워크 메트릭 개별 수집기
- 상위 N개 리소스 소비 프로세스 추적용 프로세스 모니터
- 각 수집기는 독립적이며 플러그인 아키텍처를 통해 확장 가능

### 2. API 서버 레이어 (`app/api/`)
- REST 엔드포인트를 제공하는 FastAPI 애플리케이션
- APScheduler가 주기적 메트릭 수집 관리 (1-60초 설정 가능)
- 엔드포인트 패턴: `/api/v1/metrics/{resource_type}`

### 3. 스토리지 레이어 (`app/storage/`)
- 시계열 데이터베이스 추상화 (InfluxDB 또는 SQLite)
- 데이터 보관 정책 구현:
  - 1초 해상도: 1일
  - 1분 해상도: 7일
  - 5분 해상도: 30일
  - 1시간 해상도: 1년

### 4. 알림 관리자 (`app/alerts/`)
- 임계값 기반 알림 로직
- 이메일 및 Slack 웹훅 알림 지원
- 기본 임계값: CPU >80% (5분), 메모리 >90%, 디스크 >85%

## 주요 API 엔드포인트

- `GET /api/v1/metrics/current` - 모든 메트릭의 현재 스냅샷
- `GET /api/v1/metrics/cpu?start=<timestamp>&end=<timestamp>` - CPU 시계열 데이터
- `GET /api/v1/metrics/memory?start=<timestamp>&end=<timestamp>` - 메모리 시계열 데이터
- `GET /api/v1/metrics/disk?start=<timestamp>&end=<timestamp>` - 디스크 시계열 데이터
- `GET /api/v1/metrics/network?start=<timestamp>&end=<timestamp>` - 네트워크 시계열 데이터
- `GET /api/v1/metrics/processes?limit=10` - 리소스 사용량 기준 상위 N개 프로세스
- `GET /api/v1/health` - 헬스체크 엔드포인트

## 데이터 모델

### InfluxDB 스키마
```
measurement: system_metrics
tags:
  - host: 호스트명
  - metric_type: cpu|memory|disk|network
fields:
  - cpu_percent: float
  - memory_used: integer
  - disk_read_bytes: integer
  - net_bytes_sent: integer
  - (메트릭별 추가 필드)
timestamp: 나노초
```

## 성능 요구사항

- 메트릭 수집 오버헤드: CPU <5%
- API 응답 시간: 평균 <200ms
- 시스템은 100개 이상의 동시 연결 지원
- 메트릭 수집 주기: 1-60초 (설정 가능)

## 설정

`config/config.yaml`을 통해 설정 관리:
- 데이터베이스 연결 설정
- 메트릭 수집 주기
- 알림 임계값 및 알림 채널
- 데이터 보관 정책

## 테스트 전략

- **단위 테스트**: 각 메트릭 수집기 함수를 독립적으로 테스트
- **통합 테스트**: API → DB → 응답 파이프라인 테스트
- **부하 테스트**: 메트릭 수집을 위한 장기 실행 안정성 테스트
- 플랫폼 의존성을 피하기 위해 테스트에서 `psutil` 호출 모킹

## 새로운 메트릭 추가하기

새로운 메트릭 유형을 추가하려면:
1. 기본 수집기 인터페이스를 따라 `app/collectors/`에 새 수집기 생성
2. `app/main.py`의 스케줄러에 수집기 추가
3. `app/api/routes/`에 해당 API 엔드포인트 생성
4. InfluxDB 측정값을 사용하는 경우 데이터베이스 스키마 업데이트
5. `tests/test_collectors/`에 테스트 추가

## 프로젝트 범위

**범위 내:**
- 단일 서버 모니터링
- CPU, 메모리, 디스크, 네트워크, 프로세스 메트릭
- REST API 및 웹 대시보드
- 시계열 데이터 저장

**범위 외:**
- 분산 시스템 모니터링
- 애플리케이션 레벨 APM
- 로그 수집 및 분석
- 클라우드 서비스 통합 (향후 계획)
