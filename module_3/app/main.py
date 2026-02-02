"""FastAPI 메인 애플리케이션"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from app.collectors.cpu_collector import CPUCollector
from app.collectors.memory_collector import MemoryCollector
from app.collectors.disk_collector import DiskCollector
from app.collectors.network_collector import NetworkCollector
from app.collectors.process_collector import ProcessCollector
from app.storage.memory_storage import MemoryStorage
from app.api.routes import metrics

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 전역 변수
scheduler = None
storage = None
collectors = None


def collect_metrics():
    """주기적으로 메트릭을 수집하여 스토리지에 저장"""
    try:
        # CPU 메트릭 수집 및 저장
        cpu_data = collectors['cpu'].collect()
        storage.save_metric('cpu', cpu_data)

        # 메모리 메트릭 수집 및 저장
        memory_data = collectors['memory'].collect()
        storage.save_metric('memory', memory_data)

        # 디스크 메트릭 수집 및 저장
        disk_data = collectors['disk'].collect()
        storage.save_metric('disk', disk_data)

        # 네트워크 메트릭 수집 및 저장
        network_data = collectors['network'].collect()
        storage.save_metric('network', network_data)

        logger.debug("Metrics collected successfully")

    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    global scheduler, storage, collectors

    logger.info("Starting System Monitoring Application...")

    # 스토리지 초기화
    storage = MemoryStorage(max_data_points=3600)  # 1시간 데이터 (1초당 1개)
    logger.info("Storage initialized")

    # 수집기 초기화
    collectors = {
        'cpu': CPUCollector(),
        'memory': MemoryCollector(),
        'disk': DiskCollector(),
        'network': NetworkCollector(),
        'process': ProcessCollector()
    }
    logger.info("Collectors initialized")

    # API 라우트에 의존성 주입
    metrics.set_dependencies(collectors, storage)

    # 스케줄러 시작
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        collect_metrics,
        'interval',
        seconds=5,  # 5초마다 수집
        id='metric_collection',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started (collecting every 5 seconds)")

    # 첫 번째 메트릭 수집 (즉시)
    collect_metrics()

    yield

    # 종료 시 정리
    logger.info("Shutting down...")
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


# FastAPI 애플리케이션 생성
app = FastAPI(
    title="System Monitoring API",
    description="실시간 시스템 리소스 모니터링 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Level 1에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(metrics.router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "System Monitoring API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
