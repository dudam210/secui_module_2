/**
 * 간단한 차트 렌더링 클래스
 */

class SimpleChart {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return;
        }

        this.ctx = this.canvas.getContext('2d');
        this.data = [];
        this.maxDataPoints = options.maxDataPoints || 60;
        this.color = options.color || '#667eea';
        this.fillColor = options.fillColor || 'rgba(102, 126, 234, 0.2)';
        this.lineWidth = options.lineWidth || 2;
        this.max = options.max || 100;
        this.min = options.min || 0;
        this.showGrid = options.showGrid !== false;

        this.init();
    }

    init() {
        // 캔버스 크기 설정
        const rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
    }

    addData(value) {
        this.data.push(value);
        if (this.data.length > this.maxDataPoints) {
            this.data.shift();
        }
        this.render();
    }

    setData(dataArray) {
        this.data = dataArray.slice(-this.maxDataPoints);
        this.render();
    }

    clear() {
        this.data = [];
        this.render();
    }

    render() {
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;
        const padding = 10;

        // 캔버스 초기화
        ctx.clearRect(0, 0, width, height);

        if (this.data.length === 0) {
            return;
        }

        // 그리드 그리기
        if (this.showGrid) {
            ctx.strokeStyle = '#f0f0f0';
            ctx.lineWidth = 1;

            // 수평선
            for (let i = 0; i <= 4; i++) {
                const y = padding + (height - padding * 2) * (i / 4);
                ctx.beginPath();
                ctx.moveTo(padding, y);
                ctx.lineTo(width - padding, y);
                ctx.stroke();
            }
        }

        // 데이터 포인트 계산
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        const stepX = chartWidth / (this.maxDataPoints - 1);

        const points = this.data.map((value, index) => {
            const x = padding + index * stepX;
            const normalizedValue = (value - this.min) / (this.max - this.min);
            const y = padding + chartHeight - (normalizedValue * chartHeight);
            return { x, y, value };
        });

        // 영역 채우기
        ctx.fillStyle = this.fillColor;
        ctx.beginPath();
        ctx.moveTo(points[0].x, height - padding);

        points.forEach(point => {
            ctx.lineTo(point.x, point.y);
        });

        ctx.lineTo(points[points.length - 1].x, height - padding);
        ctx.closePath();
        ctx.fill();

        // 선 그리기
        ctx.strokeStyle = this.color;
        ctx.lineWidth = this.lineWidth;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';

        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);

        points.forEach(point => {
            ctx.lineTo(point.x, point.y);
        });

        ctx.stroke();

        // 포인트 그리기 (마지막 포인트만)
        if (points.length > 0) {
            const lastPoint = points[points.length - 1];
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(lastPoint.x, lastPoint.y, 3, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    resize() {
        this.init();
        this.render();
    }
}

// 다중 데이터셋 차트 (네트워크 업로드/다운로드용)
class MultiLineChart {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return;
        }

        this.ctx = this.canvas.getContext('2d');
        this.datasets = options.datasets || [];
        this.maxDataPoints = options.maxDataPoints || 60;
        this.max = options.max || 100;
        this.min = options.min || 0;
        this.showGrid = options.showGrid !== false;

        this.init();
    }

    init() {
        const rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
    }

    addData(datasetIndex, value) {
        if (!this.datasets[datasetIndex]) {
            console.error(`Dataset ${datasetIndex} not found`);
            return;
        }

        this.datasets[datasetIndex].data.push(value);
        if (this.datasets[datasetIndex].data.length > this.maxDataPoints) {
            this.datasets[datasetIndex].data.shift();
        }

        this.render();
    }

    clear() {
        this.datasets.forEach(ds => {
            ds.data = [];
        });
        this.render();
    }

    render() {
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;
        const padding = 10;

        ctx.clearRect(0, 0, width, height);

        // 그리드
        if (this.showGrid) {
            ctx.strokeStyle = '#f0f0f0';
            ctx.lineWidth = 1;

            for (let i = 0; i <= 4; i++) {
                const y = padding + (height - padding * 2) * (i / 4);
                ctx.beginPath();
                ctx.moveTo(padding, y);
                ctx.lineTo(width - padding, y);
                ctx.stroke();
            }
        }

        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        const stepX = chartWidth / (this.maxDataPoints - 1);

        // 각 데이터셋 그리기
        this.datasets.forEach(dataset => {
            if (dataset.data.length === 0) return;

            const points = dataset.data.map((value, index) => {
                const x = padding + index * stepX;
                const normalizedValue = (value - this.min) / (this.max - this.min);
                const y = padding + chartHeight - (normalizedValue * chartHeight);
                return { x, y };
            });

            // 영역 채우기
            if (dataset.fillColor) {
                ctx.fillStyle = dataset.fillColor;
                ctx.beginPath();
                ctx.moveTo(points[0].x, height - padding);
                points.forEach(point => ctx.lineTo(point.x, point.y));
                ctx.lineTo(points[points.length - 1].x, height - padding);
                ctx.closePath();
                ctx.fill();
            }

            // 선 그리기
            ctx.strokeStyle = dataset.color || '#667eea';
            ctx.lineWidth = dataset.lineWidth || 2;
            ctx.lineJoin = 'round';
            ctx.lineCap = 'round';

            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            points.forEach(point => ctx.lineTo(point.x, point.y));
            ctx.stroke();

            // 마지막 포인트
            if (points.length > 0) {
                const lastPoint = points[points.length - 1];
                ctx.fillStyle = dataset.color || '#667eea';
                ctx.beginPath();
                ctx.arc(lastPoint.x, lastPoint.y, 3, 0, Math.PI * 2);
                ctx.fill();
            }
        });
    }

    resize() {
        this.init();
        this.render();
    }
}

// 윈도우 리사이즈 핸들러
window.addEventListener('resize', () => {
    // 전역 차트 객체들이 있으면 리사이즈
    if (window.cpuChart) window.cpuChart.resize();
    if (window.networkChart) window.networkChart.resize();
});
