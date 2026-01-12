"""
Direct test of core scanning functionality with timeout
Tests the most basic scan operations without UI/dashboard interference
"""
import os
import sys
import time
from pathlib import Path
from collections import deque
from threading import Thread

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import Config
from utils.logger import setup_logger

class TimeoutError(Exception):
    pass

def test_basic_scan_with_timeout(root_path, timeout_seconds=10):
    """Test basic scanning functionality with timeout"""
    print(f"\n{'='*60}")
    print(f"CORE SCAN TEST: {root_path}")
    print(f"Timeout: {timeout_seconds}s")
    print(f"{'='*60}\n")
    
    # Create minimal config
    class Args:
        path = root_path
        delete = False
        resume = False
        disk = "auto"
        strategy = "bfs"
        workers = 1  # Single thread for predictable testing
        min_depth = 0
        max_depth = 100
        exclude_path = []
        exclude_name = []
        include_name = []
    
    config = Config(Args())
    logger = setup_logger(config.session_id)
    
    # Test 1: Basic folder scanning
    print("[TEST 1] Checking os.scandir() on test folders...")
    folders_found = []
    try:
        with os.scandir(root_path) as it:
            for entry in it:
                if entry.is_dir(follow_symlinks=False):
                    folders_found.append(entry.name)
                    print(f"  Found folder: {entry.name}")
    except Exception as e:
        print(f"  ERROR: {e}")
        return False
    
    print(f"  Result: {len(folders_found)} folders found\n")
    
    # Test 2: Check which folders are empty
    print("[TEST 2] Checking which folders are empty...")
    empty_folders = []
    for folder_name in folders_found:
        folder_path = os.path.join(root_path, folder_name)
        try:
            contents = os.listdir(folder_path)
            is_empty = len(contents) == 0
            print(f"  {folder_name}: {'EMPTY' if is_empty else f'has {len(contents)} items'}")
            if is_empty:
                empty_folders.append(folder_name)
        except Exception as e:
            print(f"  {folder_name}: ERROR - {e}")
    
    print(f"  Result: {len(empty_folders)} empty folders\n")
    
    # Test 3: Test Engine initialization
    print("[TEST 3] Testing Engine initialization...")
    from core.engine import Engine
    
    try:
        # Disable dashboard for testing
        original_dashboard_init = None
        
        engine = Engine(config, logger)
        print(f"  Engine created successfully")
        print(f"  Queue initialized: {len(engine.queue)} items")
        print(f"  Workers: {engine.config.workers}")
        
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"  Result: Engine initialized OK\n")
    
    # Test 4: Manual queue processing test
    print("[TEST 4] Testing manual queue processing...")
    print(f"  Adding root to queue: {root_path}")
    
    test_queue = deque()
    test_queue.append((root_path, 0))
    scanned_count = 0
    found_empty = []
    
    result_container = {'completed': False, 'error': None}
    
    def scan_worker():
        nonlocal scanned_count
        try:
            while test_queue:
                path, depth = test_queue.popleft()
                print(f"  Scanning: {path}")
                scanned_count += 1
                
                try:
                    with os.scandir(path) as it:
                        has_content = False
                        for entry in it:
                            if entry.is_dir(follow_symlinks=False):
                                has_content = True
                                subpath = entry.path
                                print(f"    Queueing subfolder: {entry.name}")
                                test_queue.append((subpath, depth + 1))
                            elif entry.is_file():
                                has_content = True
                        
                        if not has_content:
                            print(f"    -> EMPTY FOLDER FOUND: {path}")
                            found_empty.append(path)
                            
                except Exception as e:
                    print(f"    ERROR scanning {path}: {e}")
            
            result_container['completed'] = True
            
        except Exception as e:
            result_container['error'] = e
            import traceback
            traceback.print_exc()
    
    # Run with timeout
    worker_thread = Thread(target=scan_worker, daemon=True)
    worker_thread.start()
    worker_thread.join(timeout=timeout_seconds)
    
    if worker_thread.is_alive():
        print(f"  TIMEOUT: Scan did not complete in {timeout_seconds}s")
        return False
    
    if result_container['error']:
        print(f"  ERROR: {result_container['error']}")
        return False
    
    print(f"\n  Result: Scanned {scanned_count} folders, found {len(found_empty)} empty")
    print(f"  Empty folders: {[os.path.basename(p) for p in found_empty]}\n")
    
    # Test 5: Full engine scan with timeout
    print("[TEST 5] Testing full Engine.start() with timeout...")
    
    # Create fresh engine
    engine = Engine(config, logger)
    engine_result = {'completed': False, 'error': None, 'stats': {}}
    
    def engine_worker():
        try:
            # Disable dashboard output
            engine.dashboard.running = False
            engine.queue.append((root_path, 0))
            engine._process_queue()
            
            engine_result['completed'] = True
            engine_result['stats'] = {
                'scanned': engine.total_scanned,
                'empty': engine.total_empty,
                'errors': engine.total_errors
            }
        except Exception as e:
            engine_result['error'] = e
            import traceback
            traceback.print_exc()
    
    engine_thread = Thread(target=engine_worker, daemon=True)
    start_time = time.time()
    engine_thread.start()
    engine_thread.join(timeout=timeout_seconds)
    elapsed = time.time() - start_time
    
    if engine_thread.is_alive():
        print(f"  TIMEOUT: Engine did not complete in {timeout_seconds}s")
        engine.running = False  # Signal to stop
        return False
    
    if engine_result['error']:
        print(f"  ERROR: {engine_result['error']}")
        return False
    
    stats = engine_result['stats']
    print(f"  Result: Scanned {stats['scanned']} folders in {elapsed:.2f}s")
    print(f"  Found: {stats['empty']} empty folders")
    print(f"  Errors: {stats['errors']}\n")
    
    print(f"{'='*60}")
    print(f"ALL TESTS PASSED")
    print(f"Expected empty folders: empty1, empty_child")
    print(f"Found {len(found_empty)} empty folders in manual test")
    print(f"Found {stats['empty']} empty folders in engine test")
    print(f"{'='*60}\n")
    
    return True

if __name__ == "__main__":
    test_path = sys.argv[1] if len(sys.argv) > 1 else "c:\\Users\\behro\\scripts\\void_walker_v4\\test_scan_temp"
    
    if not os.path.exists(test_path):
        print(f"ERROR: Test path does not exist: {test_path}")
        sys.exit(1)
    
    success = test_basic_scan_with_timeout(test_path, timeout_seconds=10)
    sys.exit(0 if success else 1)
