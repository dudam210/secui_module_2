# -*- coding: utf-8 -*-
"""API endpoint test script"""
import time
import sys

def test_api():
    """Test API endpoints"""
    try:
        import httpx
    except ImportError:
        print("[ERROR] httpx not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "httpx"])
        import httpx

    base_url = "http://localhost:8000"

    print("=" * 60)
    print("Testing API Endpoints")
    print("=" * 60)

    # Wait for server to start
    print("\nWaiting for server to start...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = httpx.get(f"{base_url}/api/v1/health", timeout=2.0)
            if response.status_code == 200:
                print("[OK] Server is running!")
                break
        except Exception:
            if i < max_retries - 1:
                print(f"  Retry {i+1}/{max_retries}...")
                time.sleep(1)
            else:
                print("[ERROR] Server not responding")
                return False

    tests_passed = 0
    tests_total = 0

    # Test 1: Health check
    print("\n" + "-" * 60)
    print("Test 1: Health Check Endpoint")
    print("-" * 60)
    tests_total += 1
    try:
        response = httpx.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Status Code: {response.status_code}")
            print(f"  Response: {data}")
            tests_passed += 1
        else:
            print(f"[FAIL] Status Code: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

    # Test 2: Root endpoint
    print("\n" + "-" * 60)
    print("Test 2: Root Endpoint")
    print("-" * 60)
    tests_total += 1
    try:
        response = httpx.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Status Code: {response.status_code}")
            print(f"  Message: {data.get('message')}")
            print(f"  Version: {data.get('version')}")
            tests_passed += 1
        else:
            print(f"[FAIL] Status Code: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

    # Test 3: Current metrics
    print("\n" + "-" * 60)
    print("Test 3: Current Metrics Endpoint")
    print("-" * 60)
    tests_total += 1
    try:
        response = httpx.get(f"{base_url}/api/v1/metrics/current")
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Status Code: {response.status_code}")
            print(f"  CPU Usage: {data['cpu']['cpu_percent']:.1f}%")
            print(f"  Memory Usage: {data['memory']['memory_percent']:.1f}%")
            print(f"  Disk Partitions: {len(data['disk']['partitions'])}")
            print(f"  Network Interfaces: {len(data['network']['interfaces'])}")
            tests_passed += 1
        else:
            print(f"[FAIL] Status Code: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

    # Test 4: CPU metrics
    print("\n" + "-" * 60)
    print("Test 4: CPU Metrics Endpoint")
    print("-" * 60)
    tests_total += 1
    try:
        response = httpx.get(f"{base_url}/api/v1/metrics/cpu?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Status Code: {response.status_code}")
            print(f"  Data points returned: {len(data)}")
            if len(data) > 0:
                print(f"  Latest CPU: {data[-1].get('cpu_percent', 'N/A'):.1f}%")
            tests_passed += 1
        else:
            print(f"[FAIL] Status Code: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

    # Test 5: Memory metrics
    print("\n" + "-" * 60)
    print("Test 5: Memory Metrics Endpoint")
    print("-" * 60)
    tests_total += 1
    try:
        response = httpx.get(f"{base_url}/api/v1/metrics/memory?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Status Code: {response.status_code}")
            print(f"  Data points returned: {len(data)}")
            if len(data) > 0:
                print(f"  Latest Memory: {data[-1].get('memory_percent', 'N/A'):.1f}%")
            tests_passed += 1
        else:
            print(f"[FAIL] Status Code: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

    # Test 6: Processes
    print("\n" + "-" * 60)
    print("Test 6: Processes Endpoint")
    print("-" * 60)
    tests_total += 1
    try:
        response = httpx.get(f"{base_url}/api/v1/metrics/processes?limit=5&sort_by=cpu")
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Status Code: {response.status_code}")
            print(f"  Processes returned: {len(data)}")
            if len(data) > 0:
                top_process = data[0]
                print(f"  Top process: {top_process['name']} (CPU: {top_process['cpu_percent']:.1f}%)")
            tests_passed += 1
        else:
            print(f"[FAIL] Status Code: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Passed: {tests_passed}/{tests_total} ({tests_passed/tests_total*100:.1f}%)")
    print("=" * 60)

    if tests_passed == tests_total:
        print("\n[SUCCESS] All API tests passed!")
        return True
    else:
        print(f"\n[FAILED] {tests_total - tests_passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
