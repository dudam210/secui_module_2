# 시스템 모니터링 대시보드

JavaScript 기반 실시간 시스템 모니터링 웹 애플리케이션

## 기능

- **실시간 모니터링**
  - CPU 사용률 + 실시간 차트
  - 메모리 사용량
  - 디스크 사용량
  - 네트워크 트래픽 (업로드/다운로드)

- **시스템 정보**
  - 호스트명, OS, 가동시간
  - 상위 프로세스 목록 (CPU 기준)

- **시각화**
  - 실시간 라인 차트
  - 프로그레스 바
  - 반응형 대시보드

## 파일 구조

```
module_1/
├── index.html          # 메인 HTML
├── style.css           # 스타일시트
├── chart.js            # 차트 렌더링 라이브러리
├── monitor.js          # 모니터링 로직
├── server.js           # Node.js 백엔드 서버
└── README.md           # 문서
```

## 실행 방법

### 방법 1: 시뮬레이션 모드 (백엔드 없이)

HTML 파일을 직접 브라우저에서 열면 시뮬레이션 데이터로 작동합니다.

```bash
# 브라우저에서 index.html 열기
start index.html    # Windows
open index.html     # macOS
xdg-open index.html # Linux
```

### 방법 2: 실제 시스템 데이터 (Node.js 서버)

Node.js 서버를 실행하여 실제 시스템 정보를 수집합니다.

```bash
# Node.js 서버 시작
node server.js

# 브라우저에서 접속
http://localhost:3000
```

그 다음 `monitor.js`에서 시뮬레이션 모드 비활성화:

```javascript
// monitor.js 파일에서
this.useSimulation = false;  // true -> false로 변경
```

## API 명세

### GET /api/stats

시스템 통계 조회

**응답 예시:**
```json
{
  "cpu": {
    "usage": 45.2
  },
  "memory": {
    "total": 16,
    "used": 8.5,
    "percent": 53.1
  },
  "disk": {
    "total": 500,
    "used": 250,
    "percent": 50
  },
  "network": {
    "download": 450.5,
    "upload": 120.3
  },
  "system": {
    "hostname": "server-01",
    "os": "Linux 5.15.0",
    "uptime": 1643723400000
  },
  "processes": [
    {
      "pid": 1234,
      "name": "node",
      "cpu": "15.3",
      "memory": "250 MB"
    }
  ]
}
```

## 브라우저 콘솔 명령어

개발자 도구 콘솔에서 다음 명령어 사용 가능:

```javascript
// 갱신 주기 변경 (초 단위)
monitor.setRefreshInterval(2)

// 시뮬레이션 모드 전환
monitor.toggleSimulation(true)   // 시뮬레이션 ON
monitor.toggleSimulation(false)  // 실제 API 호출

// 모니터링 제어
monitor.stop()   // 중지
monitor.start()  // 시작
```

## 커스터마이징

### 차트 색상 변경

`monitor.js`에서 차트 초기화 부분 수정:

```javascript
window.cpuChart = new SimpleChart('cpuChart', {
    color: '#your-color',           // 선 색상
    fillColor: 'rgba(r, g, b, 0.2)', // 영역 색상
    max: 100,
    min: 0
});
```

### 갱신 주기 변경

`monitor.js`에서:

```javascript
this.refreshInterval = 2000; // 2초 (밀리초 단위)
```

### 최대 데이터 포인트 변경

`chart.js`에서:

```javascript
this.maxDataPoints = 120; // 기본 60 -> 120
```

## 확장 아이디어

- [ ] 알림 기능 (임계값 초과 시)
- [ ] 히스토리 데이터 저장 (DB)
- [ ] 다중 서버 모니터링
- [ ] 로그 조회 기능
- [ ] WebSocket 실시간 통신
- [ ] Docker 컨테이너 모니터링
- [ ] 데이터 내보내기 (CSV, JSON)

## 필요한 패키지 (고급 기능)

실제 시스템 정보를 더 정확하게 가져오려면:

```bash
npm install systeminformation   # 시스템 정보
npm install express             # 웹 프레임워크
npm install ws                  # WebSocket
```

## 라이센스

MIT

## 주의사항

- 시뮬레이션 모드는 데모용입니다
- 실제 프로덕션 환경에서는 인증/권한 체크 필요
- 네트워크 트래픽 등 일부 정보는 OS별 추가 구현 필요
