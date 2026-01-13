"""
Comprehensive automated testing for all bugs, errors, and inconsistencies
Tests parsing, paths, arguments, resume logic, and menu flows
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def run_with_timeout(cmd, timeout=10, input_text=None):
    """Run command with timeout and optional input"""
    try:
        result = subprocess.run(
            cmd,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"TIMEOUT after {timeout}s"
    except Exception as e:
        return -2, "", str(e)

def test_argument_parsing():
    """Test all argument parsing scenarios"""
    print("\n" + "="*60)
    print("TEST SUITE: Argument Parsing")
    print("="*60)
    
    tests = [
        ("No arguments", ["python", "main.py"], None, True),
        ("Path only", ["python", "main.py", "c:\\temp"], None, True),
        ("Path with spaces", ["python", "main.py", "c:\\Program Files"], None, True),
        ("Drive letter", ["python", "main.py", "F:\\"], None, True),
        ("Drive letter no slash", ["python", "main.py", "F:"], None, True),
        ("Relative path", ["python", "main.py", "."], None, True),
        ("Resume flag only", ["python", "main.py", "--resume"], None, True),
        ("Resume with path", ["python", "main.py", "--resume", "F:\\"], None, False),  # Should fail
        ("Show cache", ["python", "main.py", "--show-cache"], None, True),
        ("All args", ["python", "main.py", "c:\\temp", "--disk", "auto", "--strategy", "bfs"], None, True),
    ]
    
    passed = 0
    failed = 0
    
    for name, cmd, input_data, should_succeed in tests:
        print(f"\n[TEST] {name}")
        print(f"  Command: {' '.join(cmd)}")
        
        code, stdout, stderr = run_with_timeout(cmd, timeout=5, input_text=input_data)
        
        has_error = "error:" in stdout.lower() or "error:" in stderr.lower() or code < 0
        
        if should_succeed and not has_error:
            print(f"  ✓ PASS")
            passed += 1
        elif not should_succeed and has_error:
            print(f"  ✓ PASS (expected to fail)")
            passed += 1
        else:
            print(f"  ✗ FAIL")
            if has_error:
                print(f"    Error: {stderr[:200]}")
            failed += 1
    
    print(f"\nArgument Parsing: {passed} passed, {failed} failed")
    return failed == 0

def test_path_normalization():
    """Test path normalization and validation"""
    print("\n" + "="*60)
    print("TEST SUITE: Path Normalization")
    print("="*60)
    
    from config.settings import Config
    
    test_cases = [
        ("c:\\temp", "c:\\temp"),
        ("C:\\TEMP", "c:\\temp"),
        ("c:/temp", "c:\\temp"),
        ("F:\\", "F:\\"),
        ("F:", "F:\\"),
        (".", os.getcwd()),
    ]
    
    passed = 0
    failed = 0
    
    for input_path, expected in test_cases:
        print(f"\n[TEST] Normalize: {input_path}")
        
        class Args:
            path = input_path
            delete = False
            resume = False
            disk = "auto"
            strategy = "auto"
            workers = 0
            min_depth = 0
            max_depth = 100
            exclude_path = []
            exclude_name = []
            include_name = []
        
        try:
            config = Config(Args())
            normalized = config.root_path.lower()
            expected_norm = expected.lower()
            
            if normalized == expected_norm:
                print(f"  ✓ PASS: {config.root_path}")
                passed += 1
            else:
                print(f"  ✗ FAIL: got {config.root_path}, expected {expected}")
                failed += 1
        except Exception as e:
            print(f"  ✗ FAIL: {e}")
            failed += 1
    
    print(f"\nPath Normalization: {passed} passed, {failed} failed")
    return failed == 0

def test_resume_logic():
    """Test resume session logic"""
    print("\n" + "="*60)
    print("TEST SUITE: Resume Logic")
    print("="*60)
    
    # Check if resume creates duplicate path arguments
    print("\n[TEST] Resume doesn't add duplicate path argument")
    
    # This simulates what happens when menu launches with resume
    from ui.menu import Menu
    
    # Check launch_engine method
    import inspect
    source = inspect.getsource(Menu.launch_engine)
    
    has_duplicate_path = "args.append(path)" in source and "--resume" in source
    
    if has_duplicate_path:
        print("  ✗ FAIL: Resume logic may append path when it shouldn't")
        return False
    else:
        print("  ✓ PASS: Resume logic looks correct")
        return True

def test_menu_config_loading():
    """Test menu configuration loading"""
    print("\n" + "="*60)
    print("TEST SUITE: Menu Config Loading")
    print("="*60)
    
    from ui.menu import Menu
    
    # Test loading config
    menu = Menu()
    
    # Create test config
    test_config = {
        "path": "F:\\",
        "delete_mode": False,
        "disk_type": "auto",
        "strategy": "auto",
        "workers": 16
    }
    
    import json
    config_file = "void_walker_config.json"
    
    try:
        with open(config_file, 'w') as f:
            json.dump(test_config, f)
        
        loaded = menu.load_config()
        
        if loaded and loaded.get("path") == "F:\\":
            print("  ✓ PASS: Config loaded correctly")
            return True
        else:
            print(f"  ✗ FAIL: Config not loaded correctly: {loaded}")
            return False
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False

def test_unicode_handling():
    """Test Unicode character handling"""
    print("\n" + "="*60)
    print("TEST SUITE: Unicode Handling")
    print("="*60)
    
    # Check all Python files for Unicode issues
    unicode_chars = ['→', '✓', '⚠', '✗', '•']
    issues = []
    
    for root, dirs, files in os.walk('.'):
        # Skip venv, __pycache__, etc
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'build', 'dist']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for char in unicode_chars:
                            if char in content:
                                issues.append((filepath, char))
                except (UnicodeDecodeError, PermissionError, OSError) as e:
                    # Skip files that can't be read (binary, no permission, etc.)
                    print(f"  [i] Skipped {filepath}: {type(e).__name__}", file=sys.stderr)
                    continue
    
    if issues:
        print(f"  ✗ FAIL: Found {len(issues)} Unicode issues:")
        for path, char in issues[:10]:  # Show first 10
            print(f"    {path}: {char}")
        return False
    else:
        print("  ✓ PASS: No Unicode issues found")
        return True

def test_database_concurrent_access():
    """Test database handles concurrent access"""
    print("\n" + "="*60)
    print("TEST SUITE: Database Concurrent Access")
    print("="*60)
    
    from data.database import Database
    import threading
    
    db_path = "test_concurrent.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = Database(db_path, "test_session")
    db.setup()
    
    errors = []
    
    def worker(worker_id):
        try:
            for i in range(10):
                db.add_folder(f"/test/{worker_id}/{i}", i)
            db.commit()
        except Exception as e:
            errors.append(f"Worker {worker_id}: {e}")
    
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    
    db.close()
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    if errors:
        print(f"  ✗ FAIL: Database concurrent access errors:")
        for err in errors:
            print(f"    {err}")
        return False
    else:
        print("  ✓ PASS: Database handles concurrent access")
        return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  COMPREHENSIVE BUG DETECTION AND TESTING SUITE")
    print("="*70)
    print("\nFinding ALL bugs, errors, inconsistencies, and incomplete code...")
    print("Using timeouts, automation, and systematic testing\n")
    
    results = {}
    
    # Run all test suites
    results['Argument Parsing'] = test_argument_parsing()
    results['Path Normalization'] = test_path_normalization()
    results['Resume Logic'] = test_resume_logic()
    results['Menu Config'] = test_menu_config_loading()
    results['Unicode Handling'] = test_unicode_handling()
    results['Database Concurrency'] = test_database_concurrent_access()
    
    # Summary
    print("\n" + "="*70)
    print("  TEST RESULTS SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    print("="*70)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
