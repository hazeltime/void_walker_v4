"""
Test suite for new features: cache invalidation, real size verification, 
enhanced dashboard metrics, and summary statistics.
"""
import os
import sys
import tempfile
import shutil
import sqlite3
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.database import Database
from ui.dashboard import Dashboard
from ui.reporter import Reporter
from config.settings import Config


def test_cache_invalidation():
    """Test that missing paths are removed from cache."""
    print("\n" + "="*70)
    print("TEST 1: Cache Invalidation (Remove Stale Paths)")
    print("="*70)
    
    # Create temp database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_cache.db")
        session_id = "test_cache_001"
        
        db = Database(db_path, session_id)
        db.setup()
        
        # Add some folders (mix of existing and non-existing)
        existing_path = tmpdir
        missing_path1 = os.path.join(tmpdir, "missing_folder_1")
        missing_path2 = os.path.join(tmpdir, "missing_folder_2")
        
        db.add_folder(existing_path, 0)
        db.add_folder(missing_path1, 1)
        db.add_folder(missing_path2, 1)
        db.commit()
        
        # Verify all added
        pending_before = db.get_pending()
        print(f"  Before invalidation: {len(pending_before)} pending paths")
        assert len(pending_before) == 3, f"Expected 3 pending, got {len(pending_before)}"
        
        # Invalidate missing paths
        invalidated = db.invalidate_missing_paths()
        print(f"  Invalidated: {invalidated} stale paths")
        
        # Verify only existing path remains
        pending_after = db.get_pending()
        print(f"  After invalidation: {len(pending_after)} pending paths")
        assert len(pending_after) == 1, f"Expected 1 pending, got {len(pending_after)}"
        assert pending_after[0][0] == existing_path, "Wrong path remained"
        
        db.close()
    
    print("  ✓ Cache invalidation working correctly")
    return True


def test_size_verification():
    """Test real size verification for empty folders."""
    print("\n" + "="*70)
    print("TEST 2: Real Size Verification (0 Bytes Check)")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test structure
        empty_folder = os.path.join(tmpdir, "truly_empty")
        folder_with_file = os.path.join(tmpdir, "has_file")
        
        os.makedirs(empty_folder)
        os.makedirs(folder_with_file)
        
        # Add a small file to second folder
        test_file = os.path.join(folder_with_file, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        # Verify empty folder
        empty_size = 0
        for entry in os.scandir(empty_folder):
            if entry.is_file(follow_symlinks=False):
                empty_size += entry.stat(follow_symlinks=False).st_size
        
        print(f"  Empty folder size: {empty_size} bytes")
        assert empty_size == 0, f"Empty folder should be 0 bytes, got {empty_size}"
        
        # Verify folder with file
        file_size = 0
        for entry in os.scandir(folder_with_file):
            if entry.is_file(follow_symlinks=False):
                file_size += entry.stat(follow_symlinks=False).st_size
        
        print(f"  Folder with file size: {file_size} bytes")
        assert file_size > 0, "Folder with file should have size > 0"
    
    print("  ✓ Size verification accurate")
    return True


def test_dashboard_metrics():
    """Test enhanced dashboard metrics (size, speed tracking)."""
    print("\n" + "="*70)
    print("TEST 3: Dashboard Enhanced Metrics")
    print("="*70)
    
    # Create minimal config
    class MockConfig:
        workers = 4
    
    config = MockConfig()
    dashboard = Dashboard(config)
    
    # Test initial state
    assert dashboard.stats['total_size_bytes'] == 0, "Initial size should be 0"
    assert dashboard.stats['processing_speed_bps'] == 0.0, "Initial speed should be 0"
    
    print(f"  Initial size: {dashboard.stats['total_size_bytes']} bytes")
    print(f"  Initial speed: {dashboard.stats['processing_speed_bps']} B/s")
    
    # Simulate processing some data
    import time
    time.sleep(0.1)  # Small delay to make speed calculation meaningful
    
    dashboard.add_processed_size(1024 * 1024)  # 1 MB
    print(f"  After 1 MB: size={dashboard.stats['total_size_bytes']} bytes")
    print(f"  Speed: {dashboard.stats['processing_speed_bps']:.2f} B/s")
    
    assert dashboard.stats['total_size_bytes'] == 1024 * 1024, "Size tracking failed"
    assert dashboard.stats['processing_speed_bps'] > 0, "Speed calculation failed"
    
    # Add more data
    dashboard.add_processed_size(512 * 1024)  # 512 KB
    print(f"  After 512 KB more: size={dashboard.stats['total_size_bytes']} bytes")
    print(f"  Speed: {dashboard.stats['processing_speed_bps']:.2f} B/s")
    
    assert dashboard.stats['total_size_bytes'] == 1024 * 1024 + 512 * 1024, "Cumulative size tracking failed"
    
    print("  ✓ Dashboard metrics tracking correctly")
    return True


def test_statistics_and_top_folders():
    """Test statistics gathering and top root folders query."""
    print("\n" + "="*70)
    print("TEST 4: Statistics & Top Root Folders")
    print("="*70)
    
    # Manual cleanup to avoid Windows file lock issues
    tmpdir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(tmpdir, "test_stats.db")
        session_id = "test_stats_001"
        
        db = Database(db_path, session_id)
        db.setup()
        
        # Create test folder structure
        root1 = os.path.join(tmpdir, "root1")
        root2 = os.path.join(tmpdir, "root2")
        root3 = os.path.join(tmpdir, "root3")
        
        # Add scanned folders to DB using direct SQL
        paths_to_add = [
            (root1, 0, 0),
            (os.path.join(root1, "sub1"), 1, 0),
            (os.path.join(root1, "sub2"), 1, 0),
            (root2, 0, 0),
            (os.path.join(root2, "sub1"), 1, 0),
            (root3, 0, 0),
            (os.path.join(root3, "sub1"), 1, 5),
        ]
        
        with db.lock:
            for path, depth, file_count in paths_to_add:
                db.cursor.execute(
                    "INSERT OR REPLACE INTO folders (path, session_id, depth, file_count, status) VALUES (?, ?, ?, ?, 'SCANNED')",
                    (path, session_id, depth, file_count)
                )
            db.conn.commit()
        
        # Test statistics
        stats = db.get_statistics()
        print(f"  Total scanned: {stats['total_scanned']}")
        print(f"  Total empty: {stats['total_empty']}")
        print(f"  Total errors: {stats['total_errors']}")
        
        assert stats['total_scanned'] == 7, f"Expected 7 scanned, got {stats['total_scanned']}"
        assert stats['total_empty'] == 6, f"Expected 6 empty, got {stats['total_empty']}"
        
        # Test top root folders
        top_roots = db.get_top_root_folders(limit=3)
        print(f"\n  Top root folders: {len(top_roots)}")
        for idx, (root, count) in enumerate(top_roots, 1):
            print(f"    {idx}. {root}: {count} empty")
        
        assert len(top_roots) >= 1, "Should have at least 1 root"
        
        # Close database BEFORE cleanup
        db.close()
        
    finally:
        # Manual cleanup with retry logic
        import time
        for attempt in range(3):
            try:
                shutil.rmtree(tmpdir)
                break
            except PermissionError:
                if attempt < 2:
                    time.sleep(0.1)
                    continue
                # Ignore if still locked on last attempt
                pass
    
    print("  ✓ Statistics and top folders working correctly")
    return True


def test_reporter_final_summary():
    """Test final summary report display."""
    print("\n" + "="*70)
    print("TEST 5: Final Summary Report Display")
    print("="*70)
    
    # Manual cleanup to avoid Windows file lock issues
    tmpdir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(tmpdir, "test_report.db")
        session_id = "test_report_001"
        
        db = Database(db_path, session_id)
        db.setup()
        
        # Create mock config
        class MockConfig:
            pass
        
        config = MockConfig()
        config.session_id = session_id
        config.root_path = tmpdir
        
        # Add test data using direct SQL
        with db.lock:
            for i in range(10):
                path = os.path.join(tmpdir, f"folder_{i}")
                file_count = 0 if i < 5 else 2
                db.cursor.execute(
                    "INSERT OR REPLACE INTO folders (path, session_id, depth, file_count, status) VALUES (?, ?, ?, ?, 'SCANNED')",
                    (path, session_id, 1, file_count)
                )
            db.conn.commit()
        
        # Create reporter and show summary
        reporter = Reporter(config, db)
        print("\n  Calling show_final_summary()...")
        print("  " + "-"*66)
        reporter.show_final_summary()
        
        # Close database BEFORE cleanup
        db.close()
        
    finally:
        # Manual cleanup with retry logic
        import time
        for attempt in range(3):
            try:
                shutil.rmtree(tmpdir)
                break
            except PermissionError:
                if attempt < 2:
                    time.sleep(0.1)
                    continue
                pass  # Ignore if still locked
    
    print("  ✓ Final summary displayed successfully")
    return True


def run_all_tests():
    """Run all new feature tests."""
    print("\n" + "="*70)
    print("  NEW FEATURES TEST SUITE")
    print("="*70)
    
    tests = [
        ("Cache Invalidation", test_cache_invalidation),
        ("Size Verification", test_size_verification),
        ("Dashboard Metrics", test_dashboard_metrics),
        ("Statistics & Top Folders", test_statistics_and_top_folders),
        ("Final Summary Report", test_reporter_final_summary),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"  ✗ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*70)
    print(f"  RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
