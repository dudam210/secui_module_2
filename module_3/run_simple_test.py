"""간단한 수동 테스트 스크립트"""
import sys
import traceback

def test_imports():
    """모듈 임포트 테스트"""
    print("=" * 60)
    print("테스트 1: 모듈 임포트")
    print("=" * 60)
    try:
        from app.collectors.cpu_collector import CPUCollector
        from app.collectors.memory_collector import MemoryCollector
        from app.collectors.disk_collector import DiskCollector
        from app.collectors.network_collector import NetworkCollector
        from app.collectors.process_collector import ProcessCollector
        from app.storage.memory_storage import MemoryStorage
        print("✓ 모든 모듈 임포트 성공")
        return True
    except Exception as e:
        print(f"✗ 임포트 실패: {e}")
        traceback.print_exc()
        return False


def test_cpu_collector():
    """CPU 수집기 테스트"""
    print("\n" + "=" * 60)
    print("테스트 2: CPU 수집기")
    print("=" * 60)
    try:
        from app.collectors.cpu_collector import CPUCollector

        collector = CPUCollector()
        print("✓ CPU 수집기 생성 성공")

        metrics = collector.collect()
        print("✓ CPU 메트릭 수집 성공")

        # 필수 필드 확인
        required_fields = ['cpu_percent', 'cpu_percent_per_core', 'cpu_count_logical']
        for field in required_fields:
            assert field in metrics, f"필드 누락: {field}"
        print(f"✓ 필수 필드 확인 완료: {list(metrics.keys())}")

        # CPU 사용률 범위 확인
        assert 0 <= metrics['cpu_percent'] <= 100, f"CPU 사용률 범위 오류: {metrics['cpu_percent']}"
        print(f"✓ CPU 사용률: {metrics['cpu_percent']:.1f}%")

        # 메트릭 타입 확인
        assert collector.get_metric_type() == "cpu"
        print("✓ 메트릭 타입 확인 완료")

        return True
    except Exception as e:
        print(f"✗ CPU 수집기 테스트 실패: {e}")
        traceback.print_exc()
        return False


def test_memory_collector():
    """메모리 수집기 테스트"""
    print("\n" + "=" * 60)
    print("테스트 3: 메모리 수집기")
    print("=" * 60)
    try:
        from app.collectors.memory_collector import MemoryCollector

        collector = MemoryCollector()
        print("✓ 메모리 수집기 생성 성공")

        metrics = collector.collect()
        print("✓ 메모리 메트릭 수집 성공")

        # 필수 필드 확인
        required_fields = ['memory_total', 'memory_used', 'memory_percent']
        for field in required_fields:
            assert field in metrics, f"필드 누락: {field}"
        print(f"✓ 필수 필드 확인 완료")

        # 메모리 값 확인
        assert metrics['memory_total'] >= metrics['memory_used'], "메모리 값 오류"
        assert 0 <= metrics['memory_percent'] <= 100, f"메모리 사용률 범위 오류: {metrics['memory_percent']}"
        print(f"✓ 메모리 사용률: {metrics['memory_percent']:.1f}%")
        print(f"  - 전체: {metrics['memory_total'] / (1024**3):.2f} GB")
        print(f"  - 사용: {metrics['memory_used'] / (1024**3):.2f} GB")

        return True
    except Exception as e:
        print(f"✗ 메모리 수집기 테스트 실패: {e}")
        traceback.print_exc()
        return False


def test_storage():
    """스토리지 테스트"""
    print("\n" + "=" * 60)
    print("테스트 4: 인메모리 스토리지")
    print("=" * 60)
    try:
        from app.storage.memory_storage import MemoryStorage
        from datetime import datetime

        storage = MemoryStorage(max_data_points=100)
        print("✓ 스토리지 생성 성공")

        # 데이터 저장 테스트
        test_data = {'cpu_percent': 50.0, 'timestamp': datetime.now()}
        result = storage.save_metric('cpu', test_data)
        assert result == True, "저장 실패"
        print("✓ 데이터 저장 성공")

        # 최신 데이터 조회 테스트
        latest = storage.get_latest('cpu')
        assert latest is not None, "조회 실패"
        assert latest['cpu_percent'] == 50.0, "데이터 불일치"
        print("✓ 최신 데이터 조회 성공")

        # 여러 데이터 저장 및 범위 조회
        for i in range(10):
            storage.save_metric('cpu', {'value': i, 'timestamp': datetime.now()})

        all_data = storage.get_range('cpu')
        assert len(all_data) == 11, f"데이터 개수 오류: {len(all_data)}"  # 초기 1개 + 10개
        print(f"✓ 범위 조회 성공: {len(all_data)}개 데이터")

        # 통계 확인
        stats = storage.get_stats()
        print(f"✓ 통계 조회 성공: {stats}")

        return True
    except Exception as e:
        print(f"✗ 스토리지 테스트 실패: {e}")
        traceback.print_exc()
        return False


def test_all_collectors():
    """모든 수집기 테스트"""
    print("\n" + "=" * 60)
    print("테스트 5: 모든 수집기 통합 테스트")
    print("=" * 60)
    try:
        from app.collectors.cpu_collector import CPUCollector
        from app.collectors.memory_collector import MemoryCollector
        from app.collectors.disk_collector import DiskCollector
        from app.collectors.network_collector import NetworkCollector
        from app.collectors.process_collector import ProcessCollector

        collectors = {
            'CPU': CPUCollector(),
            'Memory': MemoryCollector(),
            'Disk': DiskCollector(),
            'Network': NetworkCollector(),
            'Process': ProcessCollector()
        }

        for name, collector in collectors.items():
            if name == 'Process':
                data = collector.collect(limit=5)
                print(f"✓ {name} 수집기: {len(data)}개 프로세스")
            else:
                data = collector.collect()
                print(f"✓ {name} 수집기: {len(data)}개 필드")

        return True
    except Exception as e:
        print(f"✗ 통합 테스트 실패: {e}")
        traceback.print_exc()
        return False


def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 60)
    print("System Monitoring API - 수동 테스트")
    print("=" * 60 + "\n")

    results = []

    # 테스트 실행
    results.append(("모듈 임포트", test_imports()))
    results.append(("CPU 수집기", test_cpu_collector()))
    results.append(("메모리 수집기", test_memory_collector()))
    results.append(("스토리지", test_storage()))
    results.append(("통합 테스트", test_all_collectors()))

    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 통과" if result else "✗ 실패"
        print(f"{status}: {name}")

    print("\n" + "=" * 60)
    print(f"전체: {passed}/{total} 통과 ({passed/total*100:.1f}%)")
    print("=" * 60)

    if passed == total:
        print("\n[SUCCESS] 모든 테스트 통과!")
        return 0
    else:
        print(f"\n[FAILED] {total - passed}개 테스트 실패")
        return 1


if __name__ == "__main__":
    sys.exit(main())
