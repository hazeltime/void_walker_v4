#!/usr/bin/env python3
"""Test Bug #4 fix - Type normalization in config loading"""
import sys
import json
import os
sys.path.insert(0, '.')
from ui.menu import Menu

def test_type_normalization():
    """Test that config values are normalized to strings"""
    test_file = 'test_config_types_temp.json'
    
    test_cases = [
        {
            'name': 'String values (already correct)',
            'input': {'mode': '2', 'disk': '2', 'strategy': '2'},
            'expected': {'mode': '2', 'disk': '2', 'strategy': '2'}
        },
        {
            'name': 'Integer values (need normalization)',
            'input': {'mode': 2, 'disk': 2, 'strategy': 2},
            'expected': {'mode': '2', 'disk': '2', 'strategy': '2'}
        },
        {
            'name': 'Old letter values (need migration)',
            'input': {'mode': 't', 'disk': 'ssd', 'strategy': 'bfs'},
            'expected': {'mode': '1', 'disk': '2', 'strategy': '2'}
        },
        {
            'name': 'Mixed types',
            'input': {'mode': 1, 'disk': 'auto', 'strategy': 3},
            'expected': {'mode': '1', 'disk': '1', 'strategy': '3'}
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test['name']}")
        print(f"  Input: {test['input']}")
        
        # Write test config
        with open(test_file, 'w') as f:
            json.dump(test['input'], f)
        
        # Load config
        menu = Menu()
        menu.config_file = test_file
        loaded = menu.load_config()
        
        # Check results
        passed = True
        for key in ['mode', 'disk', 'strategy']:
            actual_value = loaded[key]
            expected_value = test['expected'][key]
            actual_type = type(actual_value).__name__
            
            if actual_value != expected_value:
                print(f"  ✗ FAIL: {key} = {actual_value} (expected {expected_value})")
                passed = False
                all_passed = False
            elif not isinstance(actual_value, str):
                print(f"  ✗ FAIL: {key} type = {actual_type} (expected str)")
                passed = False
                all_passed = False
        
        if passed:
            print(f"  ✓ PASS: All values correct and normalized to strings")
            print(f"    mode='{loaded['mode']}', disk='{loaded['disk']}', strategy='{loaded['strategy']}'")
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("\n" + "="*70)
    if all_passed:
        print("[SUCCESS] All tests passed - Bug #4 fix validated!")
        print("Config values are properly normalized to strings")
        return 0
    else:
        print("[FAILURE] Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(test_type_normalization())
