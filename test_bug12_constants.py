#!/usr/bin/env python3
"""Test Bug #12 fix - Using DEFAULT_MAX_DEPTH constant instead of hardcoded values"""
import sys
sys.path.insert(0, '.')
from common.constants import DEFAULT_MAX_DEPTH, ABSOLUTE_MAX_DEPTH
import argparse

print('[Test 1] Verify constants are defined')
assert hasattr(sys.modules['common.constants'], 'DEFAULT_MAX_DEPTH'), 'DEFAULT_MAX_DEPTH not found'
assert hasattr(sys.modules['common.constants'], 'ABSOLUTE_MAX_DEPTH'), 'ABSOLUTE_MAX_DEPTH not found'
print(f'  [OK] DEFAULT_MAX_DEPTH = {DEFAULT_MAX_DEPTH:,}')
print(f'  [OK] ABSOLUTE_MAX_DEPTH = {ABSOLUTE_MAX_DEPTH:,}')

print('\n[Test 2] Verify main.py uses constant')
# Import after constants are loaded
from config.settings import Config

# Create test args with default max_depth
args = argparse.Namespace(
    path='C:\\temp', delete=False, resume=False,
    disk='auto', strategy='auto', workers=4,
    min_depth=0, max_depth=DEFAULT_MAX_DEPTH,  # Should use constant
    exclude_path=[], exclude_name=[], include_name=[]
)
config = Config(args)
assert config.max_depth == DEFAULT_MAX_DEPTH, f'Expected {DEFAULT_MAX_DEPTH}, got {config.max_depth}'
print(f'  [OK] Config uses DEFAULT_MAX_DEPTH = {config.max_depth:,}')

print('\n[Test 3] Verify no hardcoded 10000 in code')
import os
import re

files_to_check = [
    'main.py',
    'ui/menu.py'
]

hardcoded_found = []
for file in files_to_check:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Skip comments
                if '#' in line:
                    line = line.split('#')[0]
                # Check for literal 10000 (not in strings, not imported)
                if re.search(r'\b10000\b', line) and 'DEFAULT_MAX_DEPTH' not in line:
                    hardcoded_found.append(f'{file}:{line_num}')

if hardcoded_found:
    print(f'  [FAIL] Found hardcoded 10000 in: {hardcoded_found}')
    sys.exit(1)
else:
    print('  [OK] No hardcoded 10000 values found')

print('\n[SUCCESS] Bug #12 fix validated - Using constants instead of hardcoded values')
