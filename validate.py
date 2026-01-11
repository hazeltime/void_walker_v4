"""
Integration validation script for Void Walker v4.1
Tests all major features and ensures consistency
"""
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_imports():
    """Test that all modules can be imported"""
    print_section("Testing Module Imports")
    
    try:
        from config.settings import Config
        print("✓ config.settings")
        
        from core.engine import Engine
        print("✓ core.engine")
        
        from core.controller import Controller
        print("✓ core.controller")
        
        from data.database import Database
        print("✓ data.database")
        
        from ui.dashboard import Dashboard
        from ui.menu import Menu
        from ui.reporter import Reporter
        print("✓ ui modules")
        
        from utils.logger import setup_logger
        from utils.validators import normalize_path, validate_target_path
        print("✓ utils modules")
        
        print("\n✅ All imports successful")
        return True
    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        return False

def test_unit_tests():
    """Run the complete test suite"""
    print_section("Running Unit Tests")
    
    result = subprocess.run(
        [sys.executable, "tests/run_tests.py"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("\n✅ All unit tests passed")
        return True
    else:
        print("\n❌ Some tests failed")
        return False

def test_cli_arguments():
    """Test CLI argument parsing"""
    print_section("Testing CLI Argument Parsing")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        # Test --help
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if "--show-cache" in result.stdout:
            print("✓ --show-cache argument registered")
        else:
            print("❌ --show-cache argument missing")
            return False
        
        if "--disk" in result.stdout:
            print("✓ --disk argument registered")
        else:
            print("❌ --disk argument missing")
            return False
        
        # Test --show-cache execution
        result = subprocess.run(
            [sys.executable, "main.py", "--show-cache"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✓ --show-cache executes without error")
        else:
            print(f"❌ --show-cache failed: {result.stderr}")
            return False
        
        print("\n✅ CLI arguments validated")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ CLI test timeout")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

def test_disk_detection():
    """Test SSD/HDD detection logic"""
    print_section("Testing Disk Detection")
    
    try:
        from config.settings import Config
        from tests.test_config import MockArgs
        
        # Test auto detection
        args = MockArgs(disk='auto')
        config = Config(args)
        print(f"✓ Auto-detection result: {config.disk_type}")
        
        # Test manual override
        args_ssd = MockArgs(disk='ssd')
        config_ssd = Config(args_ssd)
        if config_ssd.disk_type == 'ssd':
            print("✓ Manual SSD override works")
        else:
            print("❌ Manual override failed")
            return False
        
        # Test worker count adjustment
        if config_ssd.workers == 16:
            print(f"✓ SSD worker count: {config_ssd.workers}")
        else:
            print(f"❌ Expected 16 workers for SSD, got {config_ssd.workers}")
            return False
        
        args_hdd = MockArgs(disk='hdd')
        config_hdd = Config(args_hdd)
        if config_hdd.workers == 4:
            print(f"✓ HDD worker count: {config_hdd.workers}")
        else:
            print(f"❌ Expected 4 workers for HDD, got {config_hdd.workers}")
            return False
        
        print("\n✅ Disk detection validated")
        return True
        
    except Exception as e:
        print(f"❌ Disk detection test failed: {e}")
        return False

def test_concurrent_engine():
    """Test that ThreadPoolExecutor is properly integrated"""
    print_section("Testing Concurrent Engine")
    
    try:
        from core.engine import Engine
        from config.settings import Config
        from tests.test_config import MockArgs
        from unittest.mock import Mock
        
        # Create test config
        test_dir = tempfile.mkdtemp()
        args = MockArgs(path=test_dir, workers=4)
        config = Config(args)
        logger = Mock()
        
        # Create engine
        engine = Engine(config, logger)
        
        # Check attributes
        if hasattr(engine, 'executor'):
            print("✓ Engine has executor attribute")
        else:
            print("❌ Engine missing executor attribute")
            return False
        
        if hasattr(engine, 'commit_interval'):
            print(f"✓ Auto-commit interval: {engine.commit_interval}s")
        else:
            print("❌ Engine missing commit_interval")
            return False
        
        if hasattr(engine, 'save_state'):
            print("✓ Engine has save_state method")
        else:
            print("❌ Engine missing save_state method")
            return False
        
        print("\n✅ Concurrent engine validated")
        return True
        
    except Exception as e:
        print(f"❌ Concurrent engine test failed: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

def test_dashboard_metrics():
    """Test dashboard has enhanced metrics"""
    print_section("Testing Dashboard Metrics")
    
    try:
        from ui.dashboard import Dashboard
        from config.settings import Config
        from tests.test_config import MockArgs
        
        args = MockArgs()
        config = Config(args)
        dashboard = Dashboard(config)
        
        # Check enhanced metrics
        required_metrics = ['scanned', 'empty', 'deleted', 'errors', 'scan_rate', 'queue_depth', 'active_workers']
        
        for metric in required_metrics:
            if metric in dashboard.stats:
                print(f"✓ Metric '{metric}' exists")
            else:
                print(f"❌ Metric '{metric}' missing")
                return False
        
        print("\n✅ Dashboard metrics validated")
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_controller_features():
    """Test enhanced controller keyboard commands"""
    print_section("Testing Controller Features")
    
    try:
        from core.controller import Controller
        from core.engine import Engine
        from config.settings import Config
        from tests.test_config import MockArgs
        from unittest.mock import Mock
        
        args = MockArgs()
        config = Config(args)
        logger = Mock()
        engine = Engine(config, logger)
        controller = Controller(engine)
        
        # Check methods exist
        if hasattr(controller, '_show_help'):
            print("✓ Help method exists")
        else:
            print("❌ Help method missing")
            return False
        
        if hasattr(controller, '_show_config'):
            print("✓ Config display method exists")
        else:
            print("❌ Config display method missing")
            return False
        
        if hasattr(controller, 'verbose'):
            print("✓ Verbose attribute exists")
        else:
            print("❌ Verbose attribute missing")
            return False
        
        print("\n✅ Controller features validated")
        return True
        
    except Exception as e:
        print(f"❌ Controller test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("\n" + "="*60)
    print(" VOID WALKER v4.1 - INTEGRATION VALIDATION")
    print("="*60)
    
    results = {
        "Module Imports": test_imports(),
        "Unit Tests": test_unit_tests(),
        "CLI Arguments": test_cli_arguments(),
        "Disk Detection": test_disk_detection(),
        "Concurrent Engine": test_concurrent_engine(),
        "Dashboard Metrics": test_dashboard_metrics(),
        "Controller Features": test_controller_features()
    }
    
    print_section("VALIDATION SUMMARY")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f" {status} - {test_name}")
    
    print(f"\n Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL VALIDATION TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
