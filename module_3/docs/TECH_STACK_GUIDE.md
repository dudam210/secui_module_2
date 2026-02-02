# 기술 스택 상세 가이드

이 문서는 시스템 리소스 메트릭 모니터링 시스템의 5단계 기술 스택 레벨에 대한 상세 정보를 제공합니다.

## 목차

1. [개요](#개요)
2. [레벨별 상세 비교](#레벨별-상세-비교)
3. [기술 선택 근거](#기술-선택-근거)
4. [마이그레이션 가이드](#마이그레이션-가이드)
5. [성능 튜닝](#성능-튜닝)
6. [보안 베스트 프랙티스](#보안-베스트-프랙티스)
7. [트러블슈팅](#트러블슈팅)

## 개요

이 프로젝트는 5단계의 기술 스택 레벨을 지원하며, 각 레벨은 특정 사용 사례와 규모에 최적화되어 있습니다. 프로젝트는 Level 1에서 시작하여 필요에 따라 단계적으로 상위 레벨로 마이그레이션할 수 있습니다.

### 레벨 요약

- **Level 1**: 로컬 개발/학습 (1-10명)
- **Level 2**: 기본 프로덕션 (10-50명)
- **Level 3**: 중급 - 모니터링/로깅 (50-500명)
- **Level 4**: 고급 - HA/확장성 (500-5K명)
- **Level 5**: 엔터프라이즈급 (5K+명)

## 레벨별 상세 비교

### 데이터베이스 비교

| 레벨 | 시계열 DB | 관계형 DB | 캐싱 | 메시지 큐 |
|------|-----------|-----------|------|-----------|
| Level 1 | SQLite/InfluxDB | SQLite | 없음 | 없음 |
| Level 2 | InfluxDB OSS | PostgreSQL | Redis | 없음 |
| Level 3 | VictoriaMetrics | PostgreSQL | Redis | Redis (Celery) |
| Level 4 | VM Cluster | PostgreSQL HA | Redis Cluster | RabbitMQ Cluster |
| Level 5 | VM Enterprise | CockroachDB | Redis Enterprise | Kafka |

### 관측성 스택 비교

| 레벨 | 메트릭 | 로그 | 추적 | 알림 |
|------|--------|------|------|------|
| Level 1 | 없음 | Python logging | 없음 | 없음 |
| Level 2 | Grafana | loguru (파일) | 없음 | 이메일 |
| Level 3 | Prometheus + Grafana | Loki + Promtail | OpenTelemetry | Alertmanager + Slack |
| Level 4 | Prometheus + Thanos | Loki | OpenTelemetry + Tempo | Alertmanager (HA) |
| Level 5 | LGTM Stack | Loki + SIEM | Tempo (multi-tenant) | PagerDuty + Opsgenie |

### 배포 방식 비교

| 레벨 | 배포 방식 | 오케스트레이션 | 로드 밸런싱 | CI/CD |
|------|-----------|----------------|-------------|-------|
| Level 1 | 로컬 프로세스 | 없음 | 없음 | 없음 |
| Level 2 | Docker Compose | 없음 | Nginx | 기본 |
| Level 3 | Docker Compose | 없음 | Nginx | GitLab CI/GitHub Actions |
| Level 4 | Kubernetes | Kubernetes | Ingress/HAProxy | ArgoCD |
| Level 5 | Multi-cluster K8s | Kubernetes | Service Mesh | ArgoCD + Flux |

## 기술 선택 근거

### 시계열 데이터베이스

#### InfluxDB vs VictoriaMetrics

**InfluxDB (Level 1-2):**
- ✅ 쉬운 시작, 풍부한 문서
- ✅ 통합된 UI 및 관리 도구
- ✅ Flux 쿼리 언어 (강력한 데이터 변환)
- ❌ 높은 리소스 사용량
- ❌ 클러스터링이 엔터프라이즈 버전에만 제공

**VictoriaMetrics (Level 3+):**
- ✅ InfluxDB 대비 20배 빠른 수집 속도
- ✅ 70배 적은 스토리지 사용
- ✅ Prometheus 및 InfluxDB 호환
- ✅ 오픈소스 클러스터링
- ❌ 상대적으로 작은 커뮤니티

**권장:**
- 학습/프로토타입: InfluxDB
- 프로덕션 (Level 3+): VictoriaMetrics

### 관계형 데이터베이스

#### PostgreSQL vs CockroachDB

**PostgreSQL (Level 2-4):**
- ✅ 성숙한 생태계
- ✅ 풍부한 확장 기능
- ✅ 뛰어난 성능
- ❌ 수동 HA 구성 필요 (Patroni)
- ❌ 글로벌 분산에 제한적

**CockroachDB (Level 5):**
- ✅ 자동 샤딩 및 복제
- ✅ 글로벌 분산 지원
- ✅ PostgreSQL 호환 (대부분)
- ❌ 높은 비용
- ❌ 복잡한 운영

### 메시지 큐

#### Redis vs RabbitMQ vs Kafka

**Redis (Level 2-3):**
- ✅ 간단한 설정
- ✅ Celery와 잘 통합
- ✅ 낮은 레이턴시
- ❌ 메시지 지속성 제한적
- ❌ 복잡한 라우팅 불가

**RabbitMQ (Level 4):**
- ✅ 강력한 메시지 라우팅
- ✅ 메시지 지속성 보장
- ✅ HA 클러스터링
- ❌ Redis보다 높은 레이턴시
- ❌ 복잡한 운영

**Kafka (Level 5):**
- ✅ 초당 수백만 메시지 처리
- ✅ 장기 메시지 저장
- ✅ 이벤트 소싱/스트리밍
- ❌ 높은 운영 복잡도
- ❌ 높은 리소스 요구사항

### OpenTelemetry (Level 3+)

**왜 OpenTelemetry?**
- 업계 표준 (CNCF 프로젝트)
- 벤더 중립적
- 메트릭, 로그, 추적 통합
- 다양한 백엔드 지원 (Prometheus, Jaeger, Loki 등)

**대안:**
- Datadog APM (비용 높음, 벤더 종속)
- New Relic (비용 높음, 벤더 종속)
- Jaeger (추적만, 메트릭/로그 불가)

## 마이그레이션 가이드

### Level 1 → Level 2

**목표:** 로컬 개발 환경을 프로덕션 준비 환경으로 전환

**단계:**

1. **Docker 컨테이너화**
   ```bash
   # Dockerfile 생성
   # docker-compose-level2.yml 사용
   docker-compose -f docker-compose-level2.yml up -d
   ```

2. **데이터베이스 마이그레이션**
   - SQLite → PostgreSQL
   - 데이터 덤프 및 복원
   ```bash
   # SQLite 데이터 내보내기
   sqlite3 metrics.db .dump > dump.sql

   # PostgreSQL로 가져오기 (스키마 조정 필요)
   psql -U postgres -d monitoring < dump_converted.sql
   ```

3. **인증 추가**
   - JWT 토큰 발급 엔드포인트 구현
   - 보호된 엔드포인트에 의존성 추가
   ```python
   from fastapi import Depends, HTTPException
   from fastapi.security import OAuth2PasswordBearer

   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

   @app.get("/api/v1/metrics/cpu")
   async def get_cpu_metrics(token: str = Depends(oauth2_scheme)):
       # 토큰 검증
       ...
   ```

4. **HTTPS 설정**
   - Let's Encrypt 인증서 발급
   - Nginx 설정
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /etc/letsencrypt/live/domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/domain.com/privkey.pem;

       location / {
           proxy_pass http://app:8000;
       }
   }
   ```

5. **모니터링 설정**
   - Grafana 대시보드 구성
   - InfluxDB 데이터 소스 추가
   - 기본 대시보드 생성

**예상 소요 시간:** 1-2일

**체크리스트:**
- [ ] Docker Compose 파일 작성 완료
- [ ] 데이터베이스 마이그레이션 성공
- [ ] JWT 인증 구현 및 테스트
- [ ] HTTPS 인증서 발급
- [ ] Grafana 대시보드 생성
- [ ] 프로덕션 환경 변수 설정
- [ ] 백업 스크립트 작성

---

### Level 2 → Level 3

**목표:** 관측성 스택 추가로 시스템 가시성 향상

**단계:**

1. **Prometheus 통합**
   ```bash
   pip install prometheus-fastapi-instrumentator
   ```

   ```python
   from prometheus_fastapi_instrumentator import Instrumentator

   app = FastAPI()
   Instrumentator().instrument(app).expose(app)
   ```

2. **Loki + Promtail 설정**
   - docker-compose-level3.yml 사용
   - Promtail 설정으로 로그 수집
   ```yaml
   # promtail-config.yml
   clients:
     - url: http://loki:3100/loki/api/v1/push

   scrape_configs:
     - job_name: app
       static_configs:
         - targets:
             - localhost
           labels:
             job: monitoring-app
             __path__: /var/log/app/*.log
   ```

3. **OpenTelemetry 계측**
   ```python
   from opentelemetry import trace
   from opentelemetry.sdk.trace import TracerProvider
   from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

   trace.set_tracer_provider(TracerProvider())
   FastAPIInstrumentor.instrument_app(app)
   ```

4. **Celery 비동기 작업 분리**
   - Celery 앱 생성
   - 장기 실행 작업을 Celery 작업으로 이동
   ```python
   from celery import Celery

   celery_app = Celery('monitoring', broker='redis://redis:6379/0')

   @celery_app.task
   def collect_metrics():
       # 메트릭 수집 로직
       pass
   ```

5. **Alertmanager 알림 설정**
   ```yaml
   # alertmanager.yml
   route:
     receiver: 'slack'

   receivers:
     - name: 'slack'
       slack_configs:
         - api_url: 'https://hooks.slack.com/services/...'
           channel: '#alerts'
   ```

**예상 소요 시간:** 1주

**체크리스트:**
- [ ] Prometheus 메트릭 수집 확인
- [ ] Loki로 로그 집계 확인
- [ ] OpenTelemetry 추적 작동 확인
- [ ] Celery 작업 실행 확인
- [ ] Alertmanager 알림 테스트
- [ ] Grafana에 모든 데이터 소스 추가
- [ ] 통합 대시보드 생성

---

### Level 3 → Level 4

**목표:** Kubernetes로 마이그레이션하여 HA 및 확장성 확보

**단계:**

1. **Kubernetes 클러스터 준비**
   ```bash
   # 로컬 테스트: minikube 또는 kind
   minikube start --memory=8192 --cpus=4

   # 프로덕션: AWS EKS, GCP GKE, Azure AKS
   eksctl create cluster --name monitoring --region us-west-2
   ```

2. **Helm 차트 작성**
   ```bash
   helm create monitoring
   ```

   - Deployment, Service, Ingress 정의
   - ConfigMap, Secret 설정
   - PersistentVolumeClaim 구성

3. **PostgreSQL HA 구성 (Patroni)**
   ```bash
   # Helm으로 PostgreSQL HA 설치
   helm install postgres bitnami/postgresql-ha \
     --set postgresql.replicaCount=3 \
     --set postgresql.password=password
   ```

4. **Redis Cluster 구성**
   ```bash
   helm install redis bitnami/redis-cluster \
     --set cluster.nodes=6 \
     --set cluster.replicas=1
   ```

5. **Vault 시크릿 관리**
   ```bash
   helm install vault hashicorp/vault

   # 시크릿 저장
   vault kv put secret/monitoring \
     db_password=secret123 \
     jwt_secret=supersecret
   ```

6. **Ingress 및 로드 밸런싱**
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: monitoring-ingress
   spec:
     rules:
       - host: monitoring.example.com
         http:
           paths:
             - path: /
               pathType: Prefix
               backend:
                 service:
                   name: monitoring-app
                   port:
                     number: 8000
   ```

7. **HPA (Horizontal Pod Autoscaler) 설정**
   ```yaml
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: monitoring-hpa
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: monitoring-app
     minReplicas: 3
     maxReplicas: 10
     metrics:
       - type: Resource
         resource:
           name: cpu
           target:
             type: Utilization
             averageUtilization: 70
   ```

**예상 소요 시간:** 2-4주

**체크리스트:**
- [ ] Kubernetes 클러스터 프로비저닝
- [ ] Helm 차트 작성 완료
- [ ] 데이터베이스 HA 구성 확인
- [ ] Redis Cluster 작동 확인
- [ ] Vault 시크릿 관리 설정
- [ ] Ingress 및 TLS 설정
- [ ] HPA 자동 스케일링 테스트
- [ ] 재해 복구 계획 수립
- [ ] 백업 자동화

---

### Level 4 → Level 5

**목표:** 엔터프라이즈급 관측성 및 글로벌 분산 시스템 구축

**단계:**

1. **LGTM Stack 구현**
   - **Loki**: 분산 로그 집계
   - **Grafana**: 통합 관측성 플랫폼
   - **Tempo**: 분산 추적
   - **Mimir**: Prometheus 장기 저장

   ```bash
   helm install lgtm grafana/lgtm-distributed
   ```

2. **CockroachDB로 마이그레이션**
   ```bash
   # CockroachDB 클러스터 배포
   helm install cockroachdb cockroachdb/cockroachdb \
     --set statefulset.replicas=5

   # 데이터 마이그레이션
   cockroach dump postgresql://... | cockroach sql --database=monitoring
   ```

3. **Kafka 이벤트 스트리밍**
   ```bash
   helm install kafka bitnami/kafka \
     --set replicaCount=5 \
     --set zookeeper.replicaCount=3
   ```

4. **Service Mesh (Istio) 구성**
   ```bash
   istioctl install --set profile=production

   # 자동 사이드카 인젝션
   kubectl label namespace monitoring istio-injection=enabled
   ```

5. **멀티 리전 배포**
   - 각 리전에 Kubernetes 클러스터 배포
   - CockroachDB 글로벌 복제 설정
   - Kafka 멀티 리전 미러링

6. **Zero Trust 보안**
   - mTLS 모든 서비스 간 통신
   - OPA (Open Policy Agent) 정책 엔진
   - Falco 런타임 보안

7. **SIEM 통합**
   ```bash
   # Splunk Forwarder 또는 ELK Stack
   helm install splunk splunk/splunk-connect-for-kubernetes
   ```

**예상 소요 시간:** 1-3개월

**체크리스트:**
- [ ] LGTM Stack 완전히 작동
- [ ] CockroachDB 글로벌 분산 확인
- [ ] Kafka 멀티 리전 설정
- [ ] Service Mesh 트래픽 관리 확인
- [ ] mTLS 모든 통신 암호화
- [ ] SIEM 통합 및 알림 설정
- [ ] 규정 준수 감사 통과
- [ ] 재해 복구 시뮬레이션 성공
- [ ] 글로벌 페일오버 테스트

## 성능 튜닝

### FastAPI 최적화

**Uvicorn Workers 설정:**
```bash
# CPU 코어 수에 따라 조정 (코어 수 * 2 + 1)
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

**Gunicorn + Uvicorn Workers (프로덕션):**
```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --keep-alive 5
```

### 데이터베이스 최적화

**PostgreSQL:**
```sql
-- 인덱스 추가
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp DESC);
CREATE INDEX idx_metrics_type ON metrics(metric_type);

-- 파티셔닝 (시계열 데이터)
CREATE TABLE metrics_2026_01 PARTITION OF metrics
  FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- 연결 풀링 설정
-- max_connections = 200
-- shared_buffers = 4GB
-- effective_cache_size = 12GB
```

**InfluxDB/VictoriaMetrics:**
```bash
# 데이터 보관 정책
influx bucket update \
  --id <bucket-id> \
  --retention 30d

# 다운샘플링
CREATE CONTINUOUS QUERY "cq_1h" ON "monitoring"
BEGIN
  SELECT mean(cpu_percent) AS cpu_percent
  INTO "monitoring"."1h"."system_metrics"
  FROM "monitoring"."autogen"."system_metrics"
  GROUP BY time(1h), *
END
```

### Redis 최적화

```bash
# 메모리 정책
maxmemory 4gb
maxmemory-policy allkeys-lru

# 지속성 설정 (성능 vs 내구성)
save ""  # RDB 스냅샷 비활성화 (성능 우선)
appendonly yes  # AOF 활성화 (내구성 우선)
```

### 캐싱 전략

```python
from functools import lru_cache
import redis

redis_client = redis.Redis(host='redis', port=6379)

@lru_cache(maxsize=128)
def get_system_info():
    """메모리 캐싱 (프로세스 내)"""
    return psutil.cpu_count(), psutil.virtual_memory().total

async def get_metrics(metric_type: str):
    """Redis 캐싱 (분산)"""
    cache_key = f"metrics:{metric_type}:latest"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # 데이터베이스에서 조회
    data = await fetch_from_db(metric_type)

    # 캐시 저장 (60초 TTL)
    redis_client.setex(cache_key, 60, json.dumps(data))

    return data
```

## 보안 베스트 프랙티스

### Level 2+ 보안

**1. 환경 변수로 시크릿 관리**
```bash
# .env 파일 (절대 Git에 커밋하지 말 것!)
SECRET_KEY=<random-256-bit-key>
DATABASE_URL=postgresql://user:password@host/db
INFLUXDB_TOKEN=<secure-token>
```

**2. JWT 토큰 보안**
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

**3. Rate Limiting**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/metrics/cpu")
@limiter.limit("60/minute")
async def get_cpu_metrics(request: Request):
    ...
```

**4. CORS 설정**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://monitoring.example.com"],  # 특정 도메인만
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # 필요한 메서드만
    allow_headers=["Authorization"],
)
```

### Level 4+ 보안

**1. Vault 시크릿 관리**
```python
import hvac

vault_client = hvac.Client(url='http://vault:8200', token='root-token')

# 시크릿 읽기
secret = vault_client.secrets.kv.v2.read_secret_version(
    path='monitoring/database'
)
db_password = secret['data']['data']['password']
```

**2. 네트워크 정책 (Kubernetes)**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: monitoring-network-policy
spec:
  podSelector:
    matchLabels:
      app: monitoring
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: nginx
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
```

**3. Pod Security Standards**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: monitoring-app
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  containers:
    - name: app
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
```

## 트러블슈팅

### 일반적인 문제

**1. 높은 메모리 사용량**

*증상:* 애플리케이션이 메모리를 계속 소비하여 OOM 발생

*원인:*
- psutil 호출 시 프로세스 정보가 누적
- 메트릭 데이터가 메모리에 축적

*해결:*
```python
# 프로세스 정보 정리
import gc

def collect_metrics():
    # 메트릭 수집
    ...
    # 강제 가비지 컬렉션
    gc.collect()
```

**2. 데이터베이스 연결 풀 고갈**

*증상:* "Too many connections" 오류

*원인:*
- 연결이 제대로 닫히지 않음
- 연결 풀 크기가 작음

*해결:*
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,  # 연결 유효성 확인
    pool_recycle=3600,  # 1시간마다 재활용
)
```

**3. Prometheus 메트릭 누락**

*증상:* Grafana 대시보드에 데이터가 표시되지 않음

*원인:*
- 애플리케이션이 /metrics 엔드포인트를 노출하지 않음
- Prometheus가 스크래핑하지 못함

*해결:*
```bash
# /metrics 엔드포인트 확인
curl http://localhost:8000/metrics

# Prometheus 설정 확인
kubectl exec -it prometheus-0 -- cat /etc/prometheus/prometheus.yml

# 타겟 상태 확인
# http://prometheus:9090/targets
```

**4. Loki 로그 수집 실패**

*증상:* Grafana에서 로그를 볼 수 없음

*원인:*
- Promtail이 로그 파일에 접근할 수 없음
- 로그 포맷이 Promtail 설정과 맞지 않음

*해결:*
```yaml
# promtail-config.yml
scrape_configs:
  - job_name: app
    static_configs:
      - targets:
          - localhost
        labels:
          job: monitoring-app
          __path__: /var/log/app/*.log
    pipeline_stages:
      - json:
          expressions:
            timestamp: timestamp
            level: level
            message: message
      - timestamp:
          source: timestamp
          format: RFC3339
```

**5. Kubernetes Pod가 시작하지 않음**

*증상:* Pod가 CrashLoopBackOff 상태

*원인:*
- 컨테이너가 시작 후 즉시 종료
- 헬스체크 실패

*해결:*
```bash
# 로그 확인
kubectl logs -f pod/monitoring-app-xxx

# 이벤트 확인
kubectl describe pod monitoring-app-xxx

# 헬스체크 조정
# deployment.yaml
livenessProbe:
  httpGet:
    path: /api/v1/health
    port: 8000
  initialDelaySeconds: 30  # 시작 시간 늘림
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### 성능 문제

**1. 느린 API 응답**

*진단:*
```python
import time
from functools import wraps

def timeit(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper

@app.get("/api/v1/metrics/cpu")
@timeit
async def get_cpu_metrics():
    ...
```

*최적화:*
- 데이터베이스 쿼리 최적화 (인덱스 추가)
- 캐싱 추가
- 비동기 I/O 사용

**2. 높은 CPU 사용량**

*진단:*
```bash
# 프로파일링
pip install py-spy
py-spy top --pid <process-id>

# 또는 Docker 컨테이너 내부
docker exec -it monitoring-app py-spy top --pid 1
```

*최적화:*
- psutil 호출 빈도 줄이기
- 데이터 집계를 Celery 작업으로 이동
- 더 효율적인 알고리즘 사용

### 데이터 손실 문제

**1. 메트릭 데이터 누락**

*원인:*
- 수집기가 중단됨
- 데이터베이스 연결 실패

*해결:*
```python
# 재시도 로직 추가
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def save_metrics(data):
    await db.save(data)
```

**2. 로그 누락**

*원인:*
- Promtail이 로그 파일을 놓침
- 로그 로테이션 설정 문제

*해결:*
```yaml
# logrotate 설정
/var/log/app/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 app app
    postrotate
        docker kill -s USR1 monitoring-promtail
    endscript
}
```

## 추가 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Prometheus 모범 사례](https://prometheus.io/docs/practices/)
- [Kubernetes 프로덕션 체크리스트](https://kubernetes.io/docs/setup/production-environment/)
- [OpenTelemetry 문서](https://opentelemetry.io/docs/)
- [VictoriaMetrics 가이드](https://docs.victoriametrics.com/)

## 문의 및 지원

문제가 발생하거나 질문이 있으면 다음을 통해 문의하세요:
- GitHub Issues
- Slack 커뮤니티
- 이메일: support@example.com
