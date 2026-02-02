/**
 * 시스템 모니터링 메인 로직
 */

class SystemMonitor {
    constructor() {
        this.refreshInterval = 1000; // 1초
        this.apiEndpoint = '/api/stats'; // 백엔드 API 엔드포인트
        this.isConnected = false;
        this.dataPointCount = 0;
        this.useSimulation = true; // true: 시뮬레이션 모드, false: 실제 API 호출

        // DOM 요소
        this.elements = {
            statusDot: document.getElementById('statusDot'),
            statusText: document.getElementById('statusText'),
            cpuValue: document.getElementById('cpuValue'),
            cpuProgress: document.getElementById('cpuProgress'),
            memValue: document.getElementById('memValue'),
            memProgress: document.getElementById('memProgress'),
            memUsed: document.getElementById('memUsed'),
            memTotal: document.getElementById('memTotal'),
            diskValue: document.getElementById('diskValue'),
            diskProgress: document.getElementById('diskProgress'),
            diskUsed: document.getElementById('diskUsed'),
            diskTotal: document.getElementById('diskTotal'),
            netDown: document.getElementById('netDown'),
            netUp: document.getElementById('netUp'),
            hostname: document.getElementById('hostname'),
            os: document.getElementById('os'),
            uptime: document.getElementById('uptime'),
            lastUpdate: document.getElementById('lastUpdate'),
            processTable: document.getElementById('processTable'),
            refreshRate: document.getElementById('refreshRate'),
            dataPoints: document.getElementById('dataPoints')
        };

        // 차트 초기화
        this.initCharts();

        // 모니터링 시작
        this.start();
    }

    initCharts() {
        // CPU 차트
        window.cpuChart = new SimpleChart('cpuChart', {
            color: '#667eea',
            fillColor: 'rgba(102, 126, 234, 0.2)',
            max: 100,
            min: 0
        });

        // 네트워크 차트 (업로드/다운로드)
        window.networkChart = new MultiLineChart('networkChart', {
            datasets: [
                {
                    data: [],
                    color: '#10b981',
                    fillColor: 'rgba(16, 185, 129, 0.2)',
                    lineWidth: 2
                },
                {
                    data: [],
                    color: '#3b82f6',
                    fillColor: 'rgba(59, 130, 246, 0.2)',
                    lineWidth: 2
                }
            ],
            max: 1000,
            min: 0
        });
    }

    start() {
        console.log('System monitor started');
        this.elements.refreshRate.textContent = this.refreshInterval / 1000;

        // 초기 데이터 로드
        this.fetchData();

        // 주기적 업데이트
        this.intervalId = setInterval(() => {
            this.fetchData();
        }, this.refreshInterval);
    }

    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }
    }

    async fetchData() {
        try {
            let data;

            if (this.useSimulation) {
                // 시뮬레이션 데이터 생성
                data = this.generateSimulatedData();
            } else {
                // 실제 API 호출
                const response = await fetch(this.apiEndpoint);
                if (!response.ok) {
                    throw new Error('API request failed');
                }
                data = await response.json();
            }

            this.updateUI(data);
            this.updateStatus(true);
            this.dataPointCount++;
            this.elements.dataPoints.textContent = this.dataPointCount;

        } catch (error) {
            console.error('Failed to fetch data:', error);
            this.updateStatus(false, error.message);
        }
    }

    generateSimulatedData() {
        // 시뮬레이션 데이터 생성 (데모용)
        const now = Date.now();
        const cpuBase = 30 + Math.sin(now / 10000) * 20;
        const memBase = 60;
        const diskBase = 45;

        return {
            cpu: {
                usage: Math.max(0, Math.min(100, cpuBase + Math.random() * 15))
            },
            memory: {
                total: 16,
                used: memBase / 100 * 16 + Math.random() * 2,
                percent: memBase + Math.random() * 5
            },
            disk: {
                total: 500,
                used: diskBase / 100 * 500 + Math.random() * 10,
                percent: diskBase + Math.random() * 3
            },
            network: {
                download: Math.random() * 500 + 100,
                upload: Math.random() * 200 + 50
            },
            system: {
                hostname: 'demo-server-01',
                os: 'Linux Ubuntu 22.04 LTS',
                uptime: Date.now() - (Math.random() * 86400000)
            },
            processes: this.generateSimulatedProcesses()
        };
    }

    generateSimulatedProcesses() {
        const processNames = [
            'node', 'nginx', 'mysql', 'redis', 'python',
            'docker', 'systemd', 'chrome', 'code', 'bash'
        ];

        return processNames.slice(0, 5).map((name, i) => ({
            pid: 1000 + Math.floor(Math.random() * 9000),
            name: name,
            cpu: (20 - i * 3 + Math.random() * 5).toFixed(1),
            memory: ((200 - i * 30) + Math.random() * 50).toFixed(0) + ' MB'
        }));
    }

    updateUI(data) {
        // CPU 업데이트
        if (data.cpu) {
            const cpuPercent = data.cpu.usage.toFixed(1);
            this.elements.cpuValue.textContent = cpuPercent + '%';
            this.elements.cpuProgress.style.width = cpuPercent + '%';
            this.updateProgressColor(this.elements.cpuProgress, cpuPercent);
            window.cpuChart.addData(parseFloat(cpuPercent));
        }

        // 메모리 업데이트
        if (data.memory) {
            const memPercent = data.memory.percent.toFixed(1);
            this.elements.memValue.textContent = memPercent + '%';
            this.elements.memProgress.style.width = memPercent + '%';
            this.elements.memUsed.textContent = data.memory.used.toFixed(1) + ' GB';
            this.elements.memTotal.textContent = data.memory.total.toFixed(0) + ' GB';
            this.updateProgressColor(this.elements.memProgress, memPercent);
        }

        // 디스크 업데이트
        if (data.disk) {
            const diskPercent = data.disk.percent.toFixed(1);
            this.elements.diskValue.textContent = diskPercent + '%';
            this.elements.diskProgress.style.width = diskPercent + '%';
            this.elements.diskUsed.textContent = data.disk.used.toFixed(0) + ' GB';
            this.elements.diskTotal.textContent = data.disk.total.toFixed(0) + ' GB';
            this.updateProgressColor(this.elements.diskProgress, diskPercent);
        }

        // 네트워크 업데이트
        if (data.network) {
            this.elements.netDown.textContent = this.formatSpeed(data.network.download);
            this.elements.netUp.textContent = this.formatSpeed(data.network.upload);
            window.networkChart.addData(0, data.network.download);
            window.networkChart.addData(1, data.network.upload);
        }

        // 시스템 정보 업데이트
        if (data.system) {
            this.elements.hostname.textContent = data.system.hostname || '-';
            this.elements.os.textContent = data.system.os || '-';
            if (data.system.uptime) {
                this.elements.uptime.textContent = this.formatUptime(data.system.uptime);
            }
        }

        // 프로세스 목록 업데이트
        if (data.processes && data.processes.length > 0) {
            this.updateProcessTable(data.processes);
        }

        // 마지막 업데이트 시간
        this.elements.lastUpdate.textContent = new Date().toLocaleTimeString('ko-KR');
    }

    updateProgressColor(element, percent) {
        element.classList.remove('warning', 'danger');
        if (percent > 80) {
            element.classList.add('danger');
        } else if (percent > 60) {
            element.classList.add('warning');
        }
    }

    updateProcessTable(processes) {
        const tbody = this.elements.processTable;
        tbody.innerHTML = '';

        processes.forEach(proc => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${proc.pid}</td>
                <td>${proc.name}</td>
                <td>${proc.cpu}%</td>
                <td>${proc.memory}</td>
            `;
            tbody.appendChild(row);
        });
    }

    updateStatus(connected, errorMsg = '') {
        this.isConnected = connected;

        if (connected) {
            this.elements.statusDot.className = 'status-dot connected';
            this.elements.statusText.textContent = '연결됨';
        } else {
            this.elements.statusDot.className = 'status-dot error';
            this.elements.statusText.textContent = errorMsg || '연결 실패';
        }
    }

    formatSpeed(kbps) {
        if (kbps < 1024) {
            return kbps.toFixed(1) + ' KB/s';
        } else {
            return (kbps / 1024).toFixed(2) + ' MB/s';
        }
    }

    formatUptime(timestamp) {
        const uptime = Date.now() - timestamp;
        const days = Math.floor(uptime / 86400000);
        const hours = Math.floor((uptime % 86400000) / 3600000);
        const minutes = Math.floor((uptime % 3600000) / 60000);

        if (days > 0) {
            return `${days}일 ${hours}시간 ${minutes}분`;
        } else if (hours > 0) {
            return `${hours}시간 ${minutes}분`;
        } else {
            return `${minutes}분`;
        }
    }

    setRefreshInterval(seconds) {
        this.refreshInterval = seconds * 1000;
        this.elements.refreshRate.textContent = seconds;

        // 인터벌 재시작
        this.stop();
        this.start();
    }

    toggleSimulation(enabled) {
        this.useSimulation = enabled;
        console.log('Simulation mode:', enabled ? 'ON' : 'OFF');
    }
}

// 페이지 로드 시 모니터 시작
document.addEventListener('DOMContentLoaded', () => {
    window.monitor = new SystemMonitor();

    // 콘솔 명령어 안내
    console.log('%c시스템 모니터링 대시보드', 'font-size: 20px; font-weight: bold; color: #667eea;');
    console.log('%c사용 가능한 명령어:', 'font-size: 14px; font-weight: bold;');
    console.log('  monitor.setRefreshInterval(초) - 갱신 주기 변경');
    console.log('  monitor.toggleSimulation(true/false) - 시뮬레이션 모드 전환');
    console.log('  monitor.stop() - 모니터링 중지');
    console.log('  monitor.start() - 모니터링 시작');
});
