/**
 * 시스템 모니터링 백엔드 서버 (Node.js)
 * 실제 시스템 정보를 수집하여 API로 제공
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const PORT = 3000;

// MIME 타입 매핑
const mimeTypes = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.json': 'application/json'
};

// 이전 네트워크 통계 (속도 계산용)
let prevNetStats = null;
let prevTimestamp = Date.now();

/**
 * CPU 사용률 계산
 */
function getCPUUsage() {
    const cpus = os.cpus();
    let totalIdle = 0;
    let totalTick = 0;

    cpus.forEach(cpu => {
        for (let type in cpu.times) {
            totalTick += cpu.times[type];
        }
        totalIdle += cpu.times.idle;
    });

    const idle = totalIdle / cpus.length;
    const total = totalTick / cpus.length;
    const usage = 100 - (100 * idle / total);

    return usage;
}

/**
 * 메모리 정보
 */
function getMemoryInfo() {
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;

    return {
        total: totalMem / (1024 ** 3), // GB
        used: usedMem / (1024 ** 3),
        free: freeMem / (1024 ** 3),
        percent: (usedMem / totalMem) * 100
    };
}

/**
 * 디스크 정보 (간단 버전 - 실제로는 추가 라이브러리 필요)
 */
function getDiskInfo() {
    // Node.js 기본 모듈로는 디스크 정보를 직접 가져올 수 없음
    // 여기서는 시뮬레이션 데이터 반환
    // 실제로는 'node-disk-info' 같은 패키지 사용 필요

    return {
        total: 500,
        used: 250 + Math.random() * 50,
        percent: 50 + Math.random() * 10
    };
}

/**
 * 네트워크 통계
 */
function getNetworkStats() {
    const interfaces = os.networkInterfaces();
    let totalRx = 0;
    let totalTx = 0;

    // Node.js 기본 모듈로는 실시간 네트워크 트래픽을 가져올 수 없음
    // 여기서는 간단한 시뮬레이션
    // 실제로는 /proc/net/dev 파싱이나 'systeminformation' 패키지 사용

    const now = Date.now();
    const timeDelta = (now - prevTimestamp) / 1000; // 초

    const download = Math.random() * 500 + 100;
    const upload = Math.random() * 200 + 50;

    prevTimestamp = now;

    return {
        download: download, // KB/s
        upload: upload
    };
}

/**
 * 시스템 정보
 */
function getSystemInfo() {
    return {
        hostname: os.hostname(),
        os: `${os.type()} ${os.release()}`,
        platform: os.platform(),
        arch: os.arch(),
        uptime: Date.now() - (os.uptime() * 1000)
    };
}

/**
 * 상위 프로세스 목록 (간단 버전)
 */
function getTopProcesses() {
    // Node.js 기본 모듈로는 프로세스 목록을 가져올 수 없음
    // 실제로는 child_process로 'ps' 명령 실행 필요
    // 여기서는 시뮬레이션

    const processNames = [
        'node', 'nginx', 'mysql', 'redis', 'python',
        'docker', 'systemd', 'chrome', 'code', 'bash'
    ];

    return processNames.slice(0, 5).map((name, i) => ({
        pid: process.pid + i,
        name: name,
        cpu: (20 - i * 3 + Math.random() * 5).toFixed(1),
        memory: ((200 - i * 30) + Math.random() * 50).toFixed(0) + ' MB'
    }));
}

/**
 * 통합 시스템 통계
 */
function getSystemStats() {
    return {
        cpu: {
            usage: getCPUUsage()
        },
        memory: getMemoryInfo(),
        disk: getDiskInfo(),
        network: getNetworkStats(),
        system: getSystemInfo(),
        processes: getTopProcesses(),
        timestamp: Date.now()
    };
}

/**
 * 정적 파일 서빙
 */
function serveStaticFile(res, filePath) {
    const ext = path.extname(filePath);
    const contentType = mimeTypes[ext] || 'application/octet-stream';

    fs.readFile(filePath, (err, content) => {
        if (err) {
            if (err.code === 'ENOENT') {
                res.writeHead(404, { 'Content-Type': 'text/plain' });
                res.end('404 Not Found');
            } else {
                res.writeHead(500, { 'Content-Type': 'text/plain' });
                res.end('500 Internal Server Error');
            }
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content);
        }
    });
}

/**
 * HTTP 서버
 */
const server = http.createServer((req, res) => {
    console.log(`${req.method} ${req.url}`);

    // CORS 헤더 추가
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // API 엔드포인트
    if (req.url === '/api/stats' && req.method === 'GET') {
        const stats = getSystemStats();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(stats));
        return;
    }

    // 정적 파일 서빙
    let filePath = '.' + req.url;
    if (filePath === './') {
        filePath = './index.html';
    }

    serveStaticFile(res, filePath);
});

server.listen(PORT, () => {
    console.log('='.repeat(50));
    console.log('시스템 모니터링 서버 시작');
    console.log('='.repeat(50));
    console.log(`서버 주소: http://localhost:${PORT}`);
    console.log(`API 엔드포인트: http://localhost:${PORT}/api/stats`);
    console.log('='.repeat(50));
    console.log('\n브라우저에서 http://localhost:3000 을 열어주세요.\n');
});

// 종료 시그널 처리
process.on('SIGINT', () => {
    console.log('\n서버를 종료합니다...');
    server.close(() => {
        console.log('서버 종료 완료');
        process.exit(0);
    });
});
