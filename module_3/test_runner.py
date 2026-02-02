# -*- coding: utf-8 -*-
"""Simple manual test script"""
import sys
import traceback

def test_imports():
    """Test module imports"""
    print("=" * 60)
    print("Test 1: Module Imports")
    print("=" * 60)
    try:
        from app.collectors.cpu_collector import CPUCollector
        from app.collectors.memory_collector import MemoryCollector
        from app.collectors.disk_collector import DiskCollector
        from app.collectors.network_collector import NetworkCollector
        from app.collectors.process_collector import ProcessCollector
        from app.storage.memory_storage import MemoryStorage
        print("[PASS] All modules imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        traceback.print_exc()
        return False


def test_cpu_collector():
    """Test CPU collector"""
    print("\n" + "=" * 60)
    print("Test 2: CPU Collector")
    print("=" * 60)
    try:
        from app.collectors.cpu_collector import CPUCollector

        collector = CPUCollector()
        print("[PASS] CPU collector created")

        metrics = collector.collect()
        print("[PASS] CPU metrics collected")

        # Check required fields
        required_fields = ['cpu_percent', 'cpu_percent_per_core', 'cpu_count_logical']
        for field in required_fields:
            assert field in metrics, f"Missing field: {field}"
        print(f"[PASS] Required fields verified: {list(metrics.keys())[:5]}...")

        # Check CPU usage range
        assert 0 <= metrics['cpu_percent'] <= 100, f"CPU usage out of range: {metrics['cpu_percent']}"
        print(f"[PASS] CPU usage: {metrics['cpu_percent']:.1f}%")

        # Check metric type
        assert collector.get_metric_type() == "cpu"
        print("[PASS] Metric type verified")

        return True
    except Exception as e:
        print(f"[FAIL] CPU collector test failed: {e}")
        traceback.print_exc()
        return False


def test_memory_collector():
    """Test memory collector"""
    print("\n" + "=" * 60)
    print("Test 3: Memory Collector")
    print("=" * 60)
    try:
        from app.collectors.memory_collector import MemoryCollector

        collector = MemoryCollector()
        print("[PASS] Memory collector created")

        metrics = collector.collect()
        print("[PASS] Memory metrics collected")

        # Check required fields
        required_fields = ['memory_total', 'memory_used', 'memory_percent']
        for field in required_fields:
            assert field in metrics, f"Missing field: {field}"
        print("[PASS] Required fields verified")

        # Check memory values
        assert metrics['memory_total'] >= metrics['memory_used'], "Memory value error"
        assert 0 <= metrics['memory_percent'] <= 100, f"Memory usage out of range: {metrics['memory_percent']}"
        print(f"[PASS] Memory usage: {metrics['memory_percent']:.1f}%")
        print(f"  - Total: {metrics['memory_total'] / (1024**3):.2f} GB")
        print(f"  - Used: {metrics['memory_used'] / (1024**3):.2f} GB")

        return True
    except Exception as e:
        print(f"[FAIL] Memory collector test failed: {e}")
        traceback.print_exc()
        return False


def test_storage():
    """Test storage"""
    print("\n" + "=" * 60)
    print("Test 4: In-Memory Storage")
    print("=" * 60)
    try:
        from app.storage.memory_storage import MemoryStorage
        from datetime import datetime

        storage = MemoryStorage(max_data_points=100)
        print("[PASS] Storage created")

        # Test data save
        test_data = {'cpu_percent': 50.0, 'timestamp': datetime.now()}
        result = storage.save_metric('cpu', test_data)
        assert result == True, "Save failed"
        print("[PASS] Data saved successfully")

        # Test latest data retrieval
        latest = storage.get_latest('cpu')
        assert latest is not None, "Retrieval failed"
        assert latest['cpu_percent'] == 50.0, "Data mismatch"
        print("[PASS] Latest data retrieved successfully")

        # Test multiple saves and range query
        for i in range(10):
            storage.save_metric('cpu', {'value': i, 'timestamp': datetime.now()})

        all_data = storage.get_range('cpu')
        assert len(all_data) == 11, f"Data count error: {len(all_data)}"
        print(f"[PASS] Range query successful: {len(all_data)} data points")

        # Test stats
        stats = storage.get_stats()
        print(f"[PASS] Stats retrieved: {stats}")

        return True
    except Exception as e:
        print(f"[FAIL] Storage test failed: {e}")
        traceback.print_exc()
        return False


def test_all_collectors():
    """Test all collectors"""
    print("\n" + "=" * 60)
    print("Test 5: All Collectors Integration")
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
                print(f"[PASS] {name} collector: {len(data)} processes")
            else:
                data = collector.collect()
                print(f"[PASS] {name} collector: {len(data)} fields")

        return True
    except Exception as e:
        print(f"[FAIL] Integration test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Main test execution"""
    print("\n" + "=" * 60)
    print("System Monitoring API - Manual Tests")
    print("=" * 60 + "\n")

    results = []

    # Run tests
    results.append(("Module Import", test_imports()))
    results.append(("CPU Collector", test_cpu_collector()))
    results.append(("Memory Collector", test_memory_collector()))
    results.append(("Storage", test_storage()))
    results.append(("Integration", test_all_collectors()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")

    print("\n" + "=" * 60)
    print(f"Total: {passed}/{total} passed ({passed/total*100:.1f}%)")
    print("=" * 60)

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n[FAILED] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
