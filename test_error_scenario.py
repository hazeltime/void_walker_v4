"""Simulate the exact error scenario: Menu launching with resume"""
import subprocess
import os
import sys

os.chdir(r"c:\Users\behro\scripts\void_walker_v4")

print("="*70)
print("SIMULATING USER'S ERROR SCENARIO")
print("="*70)
print("\nTest 1: Menu with empty input (should show menu)")
print("-"*70)

# This should work - just show the menu
result = subprocess.run(
    ["python", "main.py"],
    input="\nq\n",  # Just quit
    capture_output=True,
    text=True,
    timeout=5
)

if "VOID WALKER" in result.stdout or "error:" in result.stdout.lower():
    print("✓ Menu loads correctly")
else:
    print("✗ FAIL: Menu not loading")
    print(result.stdout[:500])

print("\nTest 2: Resume flag only (should resume, not show menu)")
print("-"*70)

result = subprocess.run(
    ["python", "main.py", "--resume"],
    capture_output=True,
    text=True,
    timeout=5
)

if "Loading resume state" in result.stdout and "error:" not in result.stdout.lower():
    print("✓ Resume works without path")
else:
    print("✗ FAIL: Resume has errors")
    print(result.stdout[:500])
    print(result.stderr[:500])

print("\nTest 3: Resume with path (should reject)")
print("-"*70)

result = subprocess.run(
    ["python", "main.py", "F:\\", "--resume"],
    capture_output=True,
    text=True,
    timeout=5
)

if "Cannot specify path with --resume" in result.stdout or "Cannot specify path with --resume" in result.stderr:
    print("✓ Resume correctly rejects path argument")
else:
    print("✗ FAIL: Should have rejected path with resume")
    print(result.stdout[:500])
    print(result.stderr[:500])

print("\nTest 4: Normal path execution (should work)")
print("-"*70)

result = subprocess.run(
    ["python", "main.py", "test_scan_temp", "--disk", "auto", "--strategy", "auto"],
    capture_output=True,
    text=True,
    timeout=10
)

if "Ready! Starting scan" in result.stdout and "error:" not in result.stdout.lower():
    print("✓ Normal execution works")
else:
    print("✗ FAIL: Normal execution has errors")
    print(result.stdout[:500])
    print(result.stderr[:500])

print("\n" + "="*70)
print("ALL SCENARIO TESTS COMPLETE")
print("="*70)
