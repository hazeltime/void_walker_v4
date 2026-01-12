"""
FINAL COMPREHENSIVE VALIDATION
Tests all fixed bugs end-to-end with the actual exe
"""
import subprocess
import os
import time

os.chdir(r"c:\Users\behro\scripts\void_walker_v4")

print("="*70)
print("  FINAL COMPREHENSIVE VALIDATION")
print("  Testing all fixed bugs with VoidWalker.exe")
print("="*70)

tests_passed = 0
tests_failed = 0

def run_test(name, cmd, expected_in_output=None, should_fail=False, timeout=10):
    global tests_passed, tests_failed
    
    print(f"\n[TEST] {name}")
    print(f"  CMD: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = result.stdout + result.stderr
        has_error = "error:" in output.lower() or result.returncode != 0
        
        # Check expectations
        if should_fail:
            if has_error:
                print(f"  [OK] Correctly failed as expected")
                tests_passed += 1
            else:
                print(f"  [FAIL] Should have failed but didn't")
                tests_failed += 1
        else:
            if expected_in_output and expected_in_output not in output:
                print(f"  [FAIL] Expected text not found: {expected_in_output}")
                print(f"  Output: {output[:200]}")
                tests_failed += 1
            elif has_error:
                print(f"  [FAIL] Unexpected error")
                print(f"  Output: {output[:200]}")
                tests_failed += 1
            else:
                print(f"  [OK] Success")
                tests_passed += 1
                
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] Command took longer than {timeout}s")
        tests_failed += 1
    except Exception as e:
        print(f"  [ERROR] {e}")
        tests_failed += 1

print("\n" + "-"*70)
print("  TESTING PATH NORMALIZATION")
print("-"*70)

# Test drive letter normalization
run_test(
    "Drive letter F: normalizes to F:\\",
    ["python", "main.py", "F:", "--disk", "auto", "--strategy", "auto"],
    expected_in_output="Ready! Starting scan from: F:\\"
)

run_test(
    "Drive letter C: normalizes to C:\\",
    ["python", "main.py", "C:", "--disk", "auto", "--strategy", "auto"],
    expected_in_output="Ready! Starting scan from: C:\\"
)

print("\n" + "-"*70)
print("  TESTING RESUME LOGIC")
print("-"*70)

# Test resume without path (should work)
run_test(
    "Resume without path works",
    ["python", "main.py", "--resume"],
    expected_in_output="Loading resume state"
)

# Test resume with path (should fail)
run_test(
    "Resume with path is rejected",
    ["python", "main.py", "F:\\", "--resume"],
    should_fail=True
)

# Test resume from EXE without path
run_test(
    "EXE: Resume without path works",
    [".\\dist\\VoidWalker.exe", "--resume"],
    expected_in_output="Loading resume state"
)

# Test resume from EXE with path (should fail)
run_test(
    "EXE: Resume with path is rejected",
    [".\\dist\\VoidWalker.exe", "F:\\", "--resume"],
    should_fail=True
)

print("\n" + "-"*70)
print("  TESTING NORMAL EXECUTION")
print("-"*70)

# Test normal execution with test directory
run_test(
    "Normal scan of test directory",
    ["python", "main.py", "test_scan_temp", "--disk", "auto", "--strategy", "auto"],
    expected_in_output="Ready! Starting scan"
)

# Test with F:\ drive
run_test(
    "Scan F:\\ drive",
    ["python", "main.py", "F:\\", "--disk", "auto", "--strategy", "auto"],
    expected_in_output="Ready! Starting scan from: F:\\"
)

# Test EXE execution
run_test(
    "EXE: Normal scan works",
    [".\\dist\\VoidWalker.exe", "test_scan_temp", "--disk", "auto", "--strategy", "auto"],
    expected_in_output="Ready! Starting scan"
)

print("\n" + "-"*70)
print("  TESTING ARGUMENT VALIDATION")
print("-"*70)

# Test show-cache
run_test(
    "Show cache flag works",
    ["python", "main.py", "--show-cache"],
    expected_in_output="CACHED SESSIONS"
)

print("\n" + "="*70)
print("  VALIDATION COMPLETE")
print("="*70)
print(f"\n  PASSED: {tests_passed}")
print(f"  FAILED: {tests_failed}")
print(f"\n  Success Rate: {tests_passed}/{tests_passed + tests_failed} " +
      f"({100 * tests_passed / (tests_passed + tests_failed) if tests_passed + tests_failed > 0 else 0:.1f}%)")
print("="*70)

if tests_failed == 0:
    print("\n[SUCCESS] ALL TESTS PASSED! All bugs are fixed.")
else:
    print(f"\n[WARNING] {tests_failed} tests failed. Review output above.")
