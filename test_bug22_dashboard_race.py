"""
Test: Bug #22 - Dashboard Stats Race Condition
===============================================

BEFORE THE FIX:
--------------
Dashboard stats dictionary was accessed from multiple worker threads without
proper locking, causing:
1. Lost increment updates (stats['scanned'] += 1 without lock)
2. Data corruption in shared dictionary
3. Inaccurate metrics (undercounting errors, scanned folders, etc.)

THE FIX:
--------
Added thread-safe methods to Dashboard class:
- increment_scanned(scan_start_time): Thread-safe scan counter with rate calc
- increment_empty(): Thread-safe empty folder counter
- increment_errors(): Thread-safe error counter
- increment_deleted(): Thread-safe deleted counter
- set_queue_depth(depth): Thread-safe queue depth update

All methods acquire dashboard.lock before mutating stats dictionary.

VALIDATION TEST:
---------------
Simulates 100 concurrent workers all incrementing the same counter.
Without proper locking, final count would be < 100 due to lost updates.
With proper locking, final count must equal exactly 100.
"""

import threading
import time
from ui.dashboard import Dashboard

class MockConfig:
    """Minimal config for dashboard testing"""
    def __init__(self):
        self.workers = 4

def test_concurrent_increments():
    """Test that concurrent increments don't lose updates"""
    print("\n" + "="*70)
    print("TEST: Dashboard Stats Race Condition (Bug #22)")
    print("="*70)
    
    config = MockConfig()
    dashboard = Dashboard(config)
    
    # Start the dashboard (but don't display - just test the locking)
    # We won't call dashboard.start() to avoid the display loop
    
    NUM_WORKERS = 100
    INCREMENTS_PER_WORKER = 10
    EXPECTED_TOTAL = NUM_WORKERS * INCREMENTS_PER_WORKER
    
    print(f"\n[*] Starting {NUM_WORKERS} workers, each incrementing {INCREMENTS_PER_WORKER} times")
    print(f"    Expected final count: {EXPECTED_TOTAL}")
    
    def worker_increment_scanned():
        """Simulates a worker thread incrementing scanned counter"""
        for _ in range(INCREMENTS_PER_WORKER):
            dashboard.increment_scanned(time.time())
            time.sleep(0.001)  # Small delay to increase contention
    
    def worker_increment_errors():
        """Simulates a worker thread incrementing error counter"""
        for _ in range(INCREMENTS_PER_WORKER):
            dashboard.increment_errors()
            time.sleep(0.001)
    
    def worker_increment_empty():
        """Simulates a worker thread incrementing empty counter"""
        for _ in range(INCREMENTS_PER_WORKER):
            dashboard.increment_empty()
            time.sleep(0.001)
    
    # Test 1: Scanned counter
    print("\n[TEST 1] Testing increment_scanned()...")
    dashboard.stats['scanned'] = 0
    threads = []
    for i in range(NUM_WORKERS):
        t = threading.Thread(target=worker_increment_scanned)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    scanned_count = dashboard.stats['scanned']
    print(f"    Result: {scanned_count}/{EXPECTED_TOTAL} increments")
    if scanned_count == EXPECTED_TOTAL:
        print(f"    \033[92m✓ PASS - No lost updates!\033[0m")
    else:
        print(f"    \033[91m✗ FAIL - Lost {EXPECTED_TOTAL - scanned_count} updates!\033[0m")
        return False
    
    # Test 2: Error counter
    print("\n[TEST 2] Testing increment_errors()...")
    dashboard.stats['errors'] = 0
    threads = []
    for i in range(NUM_WORKERS):
        t = threading.Thread(target=worker_increment_errors)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    error_count = dashboard.stats['errors']
    print(f"    Result: {error_count}/{EXPECTED_TOTAL} increments")
    if error_count == EXPECTED_TOTAL:
        print(f"    \033[92m✓ PASS - No lost updates!\033[0m")
    else:
        print(f"    \033[91m✗ FAIL - Lost {EXPECTED_TOTAL - error_count} updates!\033[0m")
        return False
    
    # Test 3: Empty counter
    print("\n[TEST 3] Testing increment_empty()...")
    dashboard.stats['empty'] = 0
    threads = []
    for i in range(NUM_WORKERS):
        t = threading.Thread(target=worker_increment_empty)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    empty_count = dashboard.stats['empty']
    print(f"    Result: {empty_count}/{EXPECTED_TOTAL} increments")
    if empty_count == EXPECTED_TOTAL:
        print(f"    \033[92m✓ PASS - No lost updates!\033[0m")
    else:
        print(f"    \033[91m✗ FAIL - Lost {EXPECTED_TOTAL - empty_count} updates!\033[0m")
        return False
    
    # Test 4: Concurrent mixed operations
    print("\n[TEST 4] Testing mixed concurrent operations...")
    dashboard.stats['scanned'] = 0
    dashboard.stats['errors'] = 0
    dashboard.stats['empty'] = 0
    
    def worker_mixed():
        """Worker that does mixed operations"""
        for _ in range(INCREMENTS_PER_WORKER):
            dashboard.increment_scanned(time.time())
            dashboard.increment_errors()
            dashboard.increment_empty()
            dashboard.set_queue_depth(100)
            time.sleep(0.001)
    
    threads = []
    for i in range(NUM_WORKERS):
        t = threading.Thread(target=worker_mixed)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    scanned = dashboard.stats['scanned']
    errors = dashboard.stats['errors']
    empty = dashboard.stats['empty']
    
    print(f"    Scanned: {scanned}/{EXPECTED_TOTAL}")
    print(f"    Errors:  {errors}/{EXPECTED_TOTAL}")
    print(f"    Empty:   {empty}/{EXPECTED_TOTAL}")
    
    all_correct = (scanned == EXPECTED_TOTAL and 
                   errors == EXPECTED_TOTAL and 
                   empty == EXPECTED_TOTAL)
    
    if all_correct:
        print(f"    \033[92m✓ PASS - All counters accurate!\033[0m")
    else:
        print(f"    \033[91m✗ FAIL - Some counters lost updates!\033[0m")
        return False
    
    print("\n" + "="*70)
    print("\033[92m[OK] ALL TESTS PASSED - Dashboard is thread-safe!\033[0m")
    print("="*70 + "\n")
    return True

if __name__ == "__main__":
    success = test_concurrent_increments()
    exit(0 if success else 1)
