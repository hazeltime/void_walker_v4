"""Quick test of path normalization and resume logic"""
import sys
sys.path.insert(0, '.')
from config.settings import Config

class TestArgs:
    def __init__(self, **kwargs):
        self.path = kwargs.get('path')
        self.resume = kwargs.get('resume', False)
        self.delete = kwargs.get('delete', False)
        self.disk = kwargs.get('disk', 'auto')
        self.strategy = kwargs.get('strategy', 'auto')
        self.workers = kwargs.get('workers', 0)
        self.min_depth = kwargs.get('min_depth', 0)
        self.max_depth = kwargs.get('max_depth', 100)
        self.exclude_path = kwargs.get('exclude_path', [])
        self.exclude_name = kwargs.get('exclude_name', [])
        self.include_name = kwargs.get('include_name', [])

print("="*60)
print("PATH NORMALIZATION TESTS")
print("="*60)

tests = [
    ("F:", "F:\\"),
    ("F:\\", "F:\\"),
    ("C:", "C:\\"),
    ("c:\\temp", "c:\\temp"),
]

for input_path, expected in tests:
    try:
        args = TestArgs(path=input_path)
        config = Config(args)
        result = config.root_path
        status = "[OK]" if result.lower() == expected.lower() else "[FAIL]"
        print(f"{status} '{input_path}' -> '{result}' (expected '{expected}')")
    except Exception as e:
        print(f"[ERROR] '{input_path}': {e}")

print("\n" + "="*60)
print("RESUME LOGIC TESTS")
print("="*60)

# Test 1: Resume WITHOUT path should work
try:
    args = TestArgs(resume=True, path=None)
    config = Config(args)
    print("[OK] Resume without path: Success")
except Exception as e:
    print(f"[FAIL] Resume without path: {e}")

# Test 2: Resume WITH path should FAIL
try:
    args = TestArgs(resume=True, path="F:\\")
    config = Config(args)
    print("[FAIL] Resume with path should have raised error!")
except ValueError as e:
    print(f"[OK] Resume with path correctly rejected: {e}")
except Exception as e:
    print(f"[ERROR] Resume with path: unexpected error: {e}")

print("\n" + "="*60)
print("ALL TESTS COMPLETE")
print("="*60)
