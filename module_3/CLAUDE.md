# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

시스템 리소스 메트릭 모니터링 시스템 - A server monitoring system that collects, stores, and visualizes real-time system resource metrics (CPU, memory, disk, network) for a single server.

**Tech Stack:**
- Backend: Python 3.10+, FastAPI, psutil, APScheduler
- Database: InfluxDB (time-series) or SQLite (simple implementation)
- Frontend: Grafana or custom web UI (React/Vue)
- Deployment: Docker, Docker Compose

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_metrics_collector.py

# Run with coverage
pytest --cov=app tests/
```

### Docker
```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Architecture

The system follows a layered architecture with three main components:

### 1. Metrics Collector Layer (`app/collectors/`)
- Individual collectors for CPU, memory, disk, network metrics using `psutil`
- Process monitor for tracking top N resource-consuming processes
- Each collector is independent and can be extended through a plugin architecture

### 2. API Server Layer (`app/api/`)
- FastAPI application serving REST endpoints
- APScheduler manages periodic metric collection (configurable 1-60 seconds)
- Endpoints follow pattern: `/api/v1/metrics/{resource_type}`

### 3. Storage Layer (`app/storage/`)
- Time-series database abstraction (InfluxDB or SQLite)
- Implements retention policies:
  - 1-second resolution: 1 day
  - 1-minute resolution: 7 days
  - 5-minute resolution: 30 days
  - 1-hour resolution: 1 year

### 4. Alert Manager (`app/alerts/`)
- Threshold-based alert logic
- Supports email and Slack webhook notifications
- Default thresholds: CPU >80% (5min), Memory >90%, Disk >85%

## Key API Endpoints

- `GET /api/v1/metrics/current` - Current snapshot of all metrics
- `GET /api/v1/metrics/cpu?start=<timestamp>&end=<timestamp>` - CPU time-series data
- `GET /api/v1/metrics/memory?start=<timestamp>&end=<timestamp>` - Memory time-series data
- `GET /api/v1/metrics/disk?start=<timestamp>&end=<timestamp>` - Disk time-series data
- `GET /api/v1/metrics/network?start=<timestamp>&end=<timestamp>` - Network time-series data
- `GET /api/v1/metrics/processes?limit=10` - Top N processes by resource usage
- `GET /api/v1/health` - Health check endpoint

## Data Model

### InfluxDB Schema
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
  - (additional metric-specific fields)
timestamp: nanoseconds
```

## Performance Requirements

- Metric collection overhead: <5% CPU
- API response time: <200ms average
- System supports 100+ concurrent connections
- Metric collection interval: 1-60 seconds (configurable)

## Configuration

Configuration is managed through `config/config.yaml`:
- Database connection settings
- Metric collection intervals
- Alert thresholds and notification channels
- Retention policies

## Testing Strategy

- **Unit tests**: Test each metric collector function independently
- **Integration tests**: Test API → DB → response pipeline
- **Load tests**: Long-running stability tests for metric collection
- Mock `psutil` calls in tests to avoid platform dependencies

## Adding New Metrics

To add a new metric type:
1. Create a new collector in `app/collectors/` following the base collector interface
2. Add the collector to the scheduler in `app/main.py`
3. Create corresponding API endpoint in `app/api/routes/`
4. Update database schema if using InfluxDB measurements
5. Add tests in `tests/test_collectors/`

## Project Scope

**In Scope:**
- Single server monitoring
- CPU, memory, disk, network, process metrics
- REST API and web dashboard
- Time-series data storage

**Out of Scope:**
- Distributed system monitoring
- Application-level APM
- Log collection and analysis
- Cloud service integrations (future)
