# 레벨 간 마이그레이션 가이드

이 문서는 시스템 리소스 메트릭 모니터링 시스템의 각 기술 스택 레벨 간 마이그레이션을 위한 단계별 가이드를 제공합니다.

## 목차

1. [마이그레이션 원칙](#마이그레이션-원칙)
2. [Level 1 → Level 2](#level-1--level-2)
3. [Level 2 → Level 3](#level-2--level-3)
4. [Level 3 → Level 4](#level-3--level-4)
5. [Level 4 → Level 5](#level-4--level-5)
6. [롤백 절차](#롤백-절차)

## 마이그레이션 원칙

### 다운타임 최소화

모든 마이그레이션은 가능한 한 다운타임을 최소화하도록 설계되어야 합니다:

1. **블루-그린 배포**: 새 환경을 구축한 후 트래픽 전환
2. **카나리 배포**: 일부 트래픽을 새 환경으로 점진적으로 이동
3. **롤링 업데이트**: 한 번에 하나씩 인스턴스 업데이트

### 데이터 무결성

마이그레이션 중 데이터 손실을 방지하기 위해:

1. **전체 백업**: 마이그레이션 전 모든 데이터베이스 백업
2. **검증**: 마이그레이션 후 데이터 무결성 확인
3. **이중 쓰기**: 마이그레이션 중 이전 및 새 시스템 모두에 데이터 쓰기

### 테스트 전략

프로덕션 마이그레이션 전:

1. **스테이징 환경**: 동일한 마이그레이션을 스테이징에서 먼저 수행
2. **부하 테스트**: 새 환경이 예상 부하를 처리할 수 있는지 확인
3. **롤백 연습**: 롤백 절차를 사전에 테스트

---

## Level 1 → Level 2

**목표:** 로컬 개발 환경을 프로덕션 준비 환경으로 전환

**예상 소요 시간:** 1-2일
**다운타임:** 4-8시간 (신규 시스템이므로 허용 가능)

### 사전 준비

**1. 시스템 요구사항 확인**
```bash
# 서버 사양
- CPU: 2-4 코어
- 메모리: 4-8GB
- 디스크: 50-100GB (SSD 권장)
- 네트워크: 100Mbps+

# 소프트웨어 설치
- Docker 20.10+
- Docker Compose 2.0+
- Git
```

**2. 도메인 및 SSL 인증서 준비**
```bash
# Let's Encrypt 인증서 발급
sudo apt install certbot
sudo certbot certonly --standalone -d monitoring.example.com
```

**3. 백업 생성 (기존 SQLite 데이터가 있는 경우)**
```bash
# SQLite 백업
sqlite3 metrics.db .dump > backup_$(date +%Y%m%d).sql
```

### 마이그레이션 단계

**Step 1: Docker 환경 설정**

```bash
# 1. 프로젝트 디렉토리에서 Docker Compose 파일 확인
cd /path/to/monitoring-system
ls -la docker-compose-level2.yml

# 2. 환경 변수 파일 생성
cat > .env << EOF
ENVIRONMENT=production
SECRET_KEY=$(openssl rand -hex 32)
INFLUXDB_TOKEN=$(openssl rand -hex 32)
GRAFANA_PASSWORD=your_secure_password
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/monitoring
EOF

# 3. Nginx 설정 디렉토리 생성
mkdir -p nginx/ssl
mkdir -p grafana/provisioning
```

**Step 2: Nginx 설정 파일 작성**

```bash
# nginx/nginx.conf
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8000;
    }

    upstream grafana {
        server grafana:3000;
    }

    # HTTP → HTTPS 리다이렉트
    server {
        listen 80;
        server_name monitoring.example.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS
    server {
        listen 443 ssl http2;
        server_name monitoring.example.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # API
        location /api/ {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Grafana
        location / {
            proxy_pass http://grafana;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

# SSL 인증서 복사
sudo cp /etc/letsencrypt/live/monitoring.example.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/monitoring.example.com/privkey.pem nginx/ssl/
```

**Step 3: 데이터베이스 마이그레이션 (SQLite → PostgreSQL)**

```bash
# 1. Docker Compose로 PostgreSQL 시작
docker-compose -f docker-compose-level2.yml up -d postgres

# 2. SQLite 데이터를 PostgreSQL 호환 형식으로 변환
# (수동 스키마 조정 필요)
python scripts/migrate_sqlite_to_postgres.py

# 3. PostgreSQL로 데이터 가져오기
docker exec -i monitoring-postgres psql -U postgres -d monitoring < backup_converted.sql
```

**스크립트 예시: `scripts/migrate_sqlite_to_postgres.py`**

```python
import sqlite3
import psycopg2
from datetime import datetime

# SQLite 연결
sqlite_conn = sqlite3.connect('metrics.db')
sqlite_cursor = sqlite_conn.cursor()

# PostgreSQL 연결
pg_conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='monitoring',
    user='postgres',
    password='postgres'
)
pg_cursor = pg_conn.cursor()

# 스키마 생성
pg_cursor.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMPTZ NOT NULL,
        metric_type VARCHAR(50) NOT NULL,
        host VARCHAR(100) NOT NULL,
        value JSONB NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    CREATE INDEX idx_metrics_timestamp ON metrics(timestamp DESC);
    CREATE INDEX idx_metrics_type ON metrics(metric_type);
""")

# 데이터 마이그레이션
sqlite_cursor.execute("SELECT * FROM metrics")
rows = sqlite_cursor.fetchall()

for row in rows:
    pg_cursor.execute(
        "INSERT INTO metrics (timestamp, metric_type, host, value) VALUES (%s, %s, %s, %s)",
        (row[1], row[2], row[3], row[4])
    )

pg_conn.commit()
print(f"Migrated {len(rows)} rows")

sqlite_conn.close()
pg_conn.close()
```

**Step 4: Docker Compose로 전체 스택 시작**

```bash
# 1. 전체 서비스 시작
docker-compose -f docker-compose-level2.yml up -d

# 2. 서비스 상태 확인
docker-compose -f docker-compose-level2.yml ps

# 3. 로그 확인
docker-compose -f docker-compose-level2.yml logs -f

# 4. 헬스체크
curl http://localhost:8000/api/v1/health
curl http://localhost:3000/api/health  # Grafana
```

**Step 5: 인증 구현**

코드 변경이 필요합니다. `app/auth.py` 파일을 생성:

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception
```

API 엔드포인트 보호 (`app/api/routes/metrics.py`):

```python
from fastapi import APIRouter, Depends
from app.auth import get_current_user

router = APIRouter()

@router.get("/cpu")
async def get_cpu_metrics(current_user: str = Depends(get_current_user)):
    # 인증된 사용자만 접근 가능
    ...
```

**Step 6: Grafana 대시보드 설정**

```bash
# 1. Grafana 접속
# http://localhost:3000 (admin / GRAFANA_PASSWORD)

# 2. InfluxDB 데이터 소스 추가
# Configuration > Data Sources > Add data source > InfluxDB
# URL: http://influxdb:8086
# Organization: monitoring
# Token: INFLUXDB_TOKEN
# Bucket: system_metrics

# 3. 대시보드 가져오기
# Dashboards > Import > Upload JSON file
```

**Step 7: 모니터링 및 검증**

```bash
# 1. API 테스트
curl -X POST http://localhost:8000/token \
  -d "username=admin&password=admin"

TOKEN="eyJ..."

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/metrics/cpu

# 2. 메트릭 수집 확인
# InfluxDB UI: http://localhost:8086
# Data Explorer에서 system_metrics 버킷 확인

# 3. Grafana 대시보드 확인
# http://localhost:3000
```

### 마이그레이션 후 작업

**1. 백업 스크립트 설정**

```bash
# /opt/monitoring/backup.sh
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/monitoring/backups"

# PostgreSQL 백업
docker exec monitoring-postgres pg_dump -U postgres monitoring | gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# InfluxDB 백업
docker exec monitoring-influxdb influx backup /backup/$DATE
docker cp monitoring-influxdb:/backup/$DATE $BACKUP_DIR/influxdb_$DATE

# 오래된 백업 삭제 (7일 이상)
find $BACKUP_DIR -type f -mtime +7 -delete

# crontab -e
# 0 2 * * * /opt/monitoring/backup.sh
```

**2. 알림 설정**

```python
# app/alerts/email_alert.py
import aiosmtplib
from email.message import EmailMessage

async def send_alert(subject: str, body: str):
    message = EmailMessage()
    message["From"] = "monitoring@example.com"
    message["To"] = "admin@example.com"
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username="monitoring@example.com",
        password="app_password"
    )
```

**3. 문서화**

- 운영 매뉴얼 작성
- 장애 대응 절차 문서화
- 백업/복구 절차 문서화

---

## Level 2 → Level 3

**목표:** 관측성 스택 추가로 시스템 가시성 향상

**예상 소요 시간:** 1주
**다운타임:** 1-2시간 (서비스 재시작)

### 사전 준비

**1. 리소스 요구사항 확인**
```bash
# 증가된 서버 사양
- CPU: 8-16 코어 (기존: 2-4)
- 메모리: 16-32GB (기존: 4-8GB)
- 디스크: 200-500GB (기존: 50-100GB)
```

**2. Slack 웹훅 설정 (알림용)**
```bash
# Slack에서 Incoming Webhook 생성
# https://api.slack.com/messaging/webhooks
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX"
```

### 마이그레이션 단계

**Step 1: Prometheus 통합**

```bash
# 1. requirements-level3.txt 설치
pip install -r requirements-level3.txt

# 2. Prometheus 설정 파일 생성
mkdir -p prometheus
cat > prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'monitoring-cluster'
    env: 'production'

# Alertmanager 설정
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# 알림 규칙 로드
rule_files:
  - '/etc/prometheus/alerts/*.yml'

# 스크래핑 설정
scrape_configs:
  # FastAPI 앱
  - job_name: 'monitoring-app'
    static_configs:
      - targets:
          - app:8000
    metrics_path: '/metrics'

  # Node Exporter (호스트 메트릭)
  - job_name: 'node-exporter'
    static_configs:
      - targets:
          - node-exporter:9100

  # PostgreSQL Exporter
  - job_name: 'postgres'
    static_configs:
      - targets:
          - postgres-exporter:9187

  # Redis Exporter
  - job_name: 'redis'
    static_configs:
      - targets:
          - redis-exporter:9121
EOF
```

**Step 2: 알림 규칙 설정**

```yaml
# prometheus/alerts/app_alerts.yml
groups:
  - name: application
    interval: 30s
    rules:
      # CPU 사용률 경고
      - alert: HighCPUUsage
        expr: cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is {{ $value }}% (threshold: 80%)"

      # 메모리 사용률 경고
      - alert: HighMemoryUsage
        expr: memory_usage_percent > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is {{ $value }}% (threshold: 90%)"

      # API 응답 시간 경고
      - alert: SlowAPIResponse
        expr: http_request_duration_seconds{quantile="0.99"} > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow API responses"
          description: "99th percentile response time is {{ $value }}s"

      # 에러율 경고
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status=~"5.."}[5m])
          /
          rate(http_requests_total[5m])
          > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"
```

**Step 3: Alertmanager 설정**

```yaml
# alertmanager/alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

# 알림 라우팅
route:
  receiver: 'default'
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  routes:
    # Critical 알림은 즉시 전송
    - match:
        severity: critical
      receiver: 'critical'
      group_wait: 0s
      repeat_interval: 5m

    # Warning 알림은 그룹화
    - match:
        severity: warning
      receiver: 'warning'
      group_wait: 30s

# 수신자 설정
receivers:
  - name: 'default'
    slack_configs:
      - channel: '#monitoring'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'critical'
    slack_configs:
      - channel: '#alerts-critical'
        title: ':fire: CRITICAL: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true

  - name: 'warning'
    slack_configs:
      - channel: '#alerts-warning'
        title: ':warning: Warning: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

# 억제 규칙 (중복 알림 방지)
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'cluster', 'service']
```

**Step 4: Loki + Promtail 설정**

```yaml
# loki/loki-config.yml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-05-15
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 168h

storage_config:
  boltdb:
    directory: /loki/index
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: true
  retention_period: 168h  # 7일
```

```yaml
# promtail/promtail-config.yml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # 애플리케이션 로그
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
            module: module
      - timestamp:
          source: timestamp
          format: RFC3339
      - labels:
          level:
          module:

  # 시스템 로그
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: system
          __path__: /var/log/host/*.log
```

**Step 5: OpenTelemetry 계측**

```python
# app/telemetry.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
import os

def setup_telemetry(app):
    # Tracer Provider 설정
    trace.set_tracer_provider(TracerProvider())

    # OTLP Exporter 설정
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317"),
        insecure=True
    )

    # Span Processor 추가
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(otlp_exporter)
    )

    # FastAPI 자동 계측
    FastAPIInstrumentor.instrument_app(app)

    # Logging 계측
    LoggingInstrumentor().instrument()

# app/main.py에서 호출
from app.telemetry import setup_telemetry

app = FastAPI()
setup_telemetry(app)
```

**Step 6: Celery 설정 (비동기 작업)**

```python
# app/celery_app.py
from celery import Celery
import os

celery_app = Celery(
    'monitoring',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    include=['app.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'app.tasks.collect_metrics': {'queue': 'metrics'},
        'app.tasks.send_alert': {'queue': 'alerts'},
    },
    task_time_limit=300,  # 5분
    task_soft_time_limit=240,  # 4분
)

# app/tasks.py
from app.celery_app import celery_app
import psutil

@celery_app.task(name='app.tasks.collect_metrics')
def collect_metrics():
    """메트릭 수집 작업"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    # 데이터베이스에 저장
    ...

@celery_app.task(name='app.tasks.send_alert')
def send_alert(alert_type: str, message: str):
    """알림 전송 작업"""
    # 이메일 또는 Slack으로 알림 전송
    ...
```

**Step 7: Docker Compose 업데이트 및 재시작**

```bash
# 1. 기존 서비스 중지 (데이터는 유지)
docker-compose -f docker-compose-level2.yml down

# 2. Level 3 서비스 시작
docker-compose -f docker-compose-level3.yml up -d

# 3. 서비스 상태 확인
docker-compose -f docker-compose-level3.yml ps

# 4. 로그 확인
docker-compose -f docker-compose-level3.yml logs -f prometheus
docker-compose -f docker-compose-level3.yml logs -f loki
docker-compose -f docker-compose-level3.yml logs -f celery-worker

# 5. 엔드포인트 확인
curl http://localhost:9090/api/v1/targets  # Prometheus
curl http://localhost:3100/ready  # Loki
curl http://localhost:9093/-/healthy  # Alertmanager
```

**Step 8: Grafana 데이터 소스 추가**

```bash
# Grafana 접속 (http://localhost:3000)

# 1. Prometheus 데이터 소스 추가
# Configuration > Data Sources > Add > Prometheus
# URL: http://prometheus:9090
# Save & Test

# 2. Loki 데이터 소스 추가
# Configuration > Data Sources > Add > Loki
# URL: http://loki:3100
# Save & Test

# 3. 대시보드 가져오기
# Dashboards > Import > ID: 1860 (Node Exporter)
# Dashboards > Import > ID: 7587 (PostgreSQL)
```

### 검증

```bash
# 1. Prometheus 메트릭 확인
curl http://localhost:8000/metrics | grep -E "http_requests_total|cpu_usage_percent"

# 2. Loki 로그 확인
# Grafana > Explore > Loki
# Query: {job="monitoring-app"}

# 3. Alertmanager 알림 테스트
# Alertmanager UI (http://localhost:9093) 에서 Silence 해제 후 테스트 알림 트리거

# 4. Celery 작업 확인
# Flower UI (http://localhost:5555) 에서 작업 실행 상태 확인
```

---

## Level 3 → Level 4

**목표:** Kubernetes로 마이그레이션하여 HA 및 확장성 확보

**예상 소요 시간:** 2-4주
**다운타임:** 0-1시간 (블루-그린 배포 사용 시)

### 사전 준비

**1. Kubernetes 클러스터 프로비저닝**

로컬 테스트:
```bash
# minikube
minikube start --memory=16384 --cpus=8 --disk-size=100g

# kind
kind create cluster --config kind-config.yaml
```

프로덕션:
```bash
# AWS EKS
eksctl create cluster \
  --name monitoring-cluster \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.xlarge \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 10 \
  --managed

# GCP GKE
gcloud container clusters create monitoring-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-4 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10

# Azure AKS
az aks create \
  --resource-group monitoring-rg \
  --name monitoring-cluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 10
```

**2. Helm 및 도구 설치**

```bash
# Helm 설치
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# kubectl 확인
kubectl version
kubectl cluster-info

# kubectl 플러그인
kubectl krew install ctx ns
```

### 마이그레이션 단계

이 섹션은 매우 길어질 수 있으므로, 핵심 단계만 요약합니다. 상세 내용은 `TECH_STACK_GUIDE.md`를 참조하세요.

**Step 1: Helm 차트 생성**

```bash
helm create monitoring
cd monitoring

# values.yaml 편집
# - 이미지 태그
# - 리소스 제한
# - 환경 변수
# - PersistentVolume 설정
```

**Step 2: 데이터베이스 HA 구성**

```bash
# PostgreSQL HA (Patroni)
helm install postgres bitnami/postgresql-ha \
  --namespace monitoring \
  --create-namespace \
  --set postgresql.replicaCount=3 \
  --set postgresql.password=password

# Redis Cluster
helm install redis bitnami/redis-cluster \
  --namespace monitoring \
  --set cluster.nodes=6 \
  --set cluster.replicas=1
```

**Step 3: 애플리케이션 배포**

```bash
# Helm으로 배포
helm install monitoring-app ./monitoring \
  --namespace monitoring \
  --values values-production.yaml

# 배포 상태 확인
kubectl get pods -n monitoring
kubectl get services -n monitoring
```

**Step 4: Ingress 설정**

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: monitoring-ingress
  namespace: monitoring
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - monitoring.example.com
      secretName: monitoring-tls
  rules:
    - host: monitoring.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: monitoring-app
                port:
                  number: 8000
```

**Step 5: 데이터 마이그레이션**

```bash
# 1. Level 3 환경에서 데이터 백업
kubectl exec -it postgres-0 -n monitoring -- pg_dump -U postgres monitoring > backup.sql

# 2. Level 4 환경으로 복원
kubectl exec -i postgres-0 -n monitoring -- psql -U postgres monitoring < backup.sql
```

**Step 6: 트래픽 전환 (블루-그린 배포)**

```bash
# 1. DNS 또는 로드 밸런서에서 트래픽을 Level 4 환경으로 점진적으로 전환
# 2. Level 3 환경 모니터링
# 3. 문제 없으면 완전히 전환
# 4. Level 3 환경 유지 (롤백용)
```

---

## Level 4 → Level 5

**목표:** 엔터프라이즈급 관측성 및 글로벌 분산 시스템 구축

**예상 소요 시간:** 1-3개월
**다운타임:** 0 (완전한 블루-그린 배포)

이 마이그레이션은 매우 복잡하며, 전문 컨설팅 및 아키텍트 팀이 필요합니다. 여기서는 핵심 컴포넌트만 다룹니다.

### 핵심 단계

1. **LGTM Stack 구현**
2. **CockroachDB 글로벌 분산**
3. **Kafka 이벤트 스트리밍**
4. **Service Mesh (Istio) 구성**
5. **멀티 리전 배포**
6. **Zero Trust 보안**
7. **SIEM 통합**

상세 내용은 `TECH_STACK_GUIDE.md`를 참조하세요.

---

## 롤백 절차

모든 마이그레이션에는 롤백 계획이 필요합니다.

### 일반 롤백 원칙

1. **이전 환경 유지**: 마이그레이션 완료 후 최소 1주일간 이전 환경 유지
2. **빠른 DNS 전환**: DNS TTL을 짧게 설정 (예: 60초)
3. **데이터 동기화**: 가능한 경우 양방향 데이터 동기화

### Level 2 → Level 1 롤백

```bash
# 1. Docker Compose 중지
docker-compose -f docker-compose-level2.yml down

# 2. SQLite 백업 복원
cp backup_YYYYMMDD.sql metrics.db

# 3. 로컬 프로세스로 재시작
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Level 3 → Level 2 롤백

```bash
# 1. Level 3 서비스 중지
docker-compose -f docker-compose-level3.yml down

# 2. 데이터베이스 백업 복원 (필요한 경우)
docker exec -i monitoring-postgres psql -U postgres monitoring < backup_pre_migration.sql

# 3. Level 2 서비스 재시작
docker-compose -f docker-compose-level2.yml up -d
```

### Level 4 → Level 3 롤백

```bash
# 1. DNS/로드 밸런서에서 트래픽을 Level 3으로 되돌림
# (Level 3 환경이 여전히 실행 중이라고 가정)

# 2. Kubernetes 배포 삭제
helm uninstall monitoring-app -n monitoring

# 3. 데이터베이스 복원 (필요한 경우)
# Level 3 PostgreSQL로 최신 백업 복원
```

### 긴급 롤백 체크리스트

- [ ] 이전 환경이 여전히 실행 중인지 확인
- [ ] DNS TTL이 짧은지 확인 (< 5분)
- [ ] 데이터베이스 백업 준비
- [ ] 롤백 스크립트 사전 테스트
- [ ] 팀 전체에 롤백 절차 공유
- [ ] 롤백 후 헬스체크 수행

---

## 추가 리소스

- [Kubernetes 프로덕션 체크리스트](https://kubernetes.io/docs/setup/production-environment/)
- [Helm 베스트 프랙티스](https://helm.sh/docs/chart_best_practices/)
- [PostgreSQL HA 가이드](https://patroni.readthedocs.io/)
- [CockroachDB 마이그레이션](https://www.cockroachlabs.com/docs/stable/migration-overview.html)

## 지원

마이그레이션 중 문제가 발생하면:
- GitHub Issues
- Slack: #monitoring-support
- 이메일: support@example.com
