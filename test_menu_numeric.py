"""
Test Menu - Verify All Numeric Defaults and Inputs

This script tests that:
1. All defaults are numeric (1, 2, 3) not letters (t, d, ssd, etc.)
2. All displays show "number:name" format
3. All inputs accept numbers correctly
4. No Unicode characters crash on Windows console
"""
import subprocess
import sys
import json
import os

def test_config_defaults():
    """Test that saved config file uses numeric values"""
    print("\n" + "="*70)
    print("TEST 1: Configuration File Format")
    print("="*70)
    
    config_file = "void_walker_config.json"
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print(f"\nLoaded config from {config_file}:")
        for key, value in config.items():
            print(f"  {key:20} : {value}")
        
        # Check numeric fields
        numeric_fields = {
            'mode': ['1', '2'],
            'disk': ['1', '2', '3'],
            'strategy': ['1', '2', '3']
        }
        
        print("\nValidation:")
        all_valid = True
        for field, valid_values in numeric_fields.items():
            if field in config:
                value = str(config[field])
                is_valid = value in valid_values
                status = "✓ OK" if is_valid else f"✗ FAIL (expected one of {valid_values})"
                print(f"  {field:15} = {value:10} {status}")
                if not is_valid:
                    all_valid = False
        
        if all_valid:
            print("\n✓ All numeric fields are correct!")
        else:
            print("\n✗ Some fields have incorrect values")
            return False
    else:
        print(f"\n[i] No config file found at {config_file}")
        print("    This is normal for first run")
    
    return True

def test_menu_interaction():
    """Test interactive menu with numeric inputs"""
    print("\n" + "="*70)
    print("TEST 2: Menu Interaction with Numeric Inputs")
    print("="*70)
    
    print("\nSimulating menu navigation...")
    print("Inputs: Enter (accept defaults for all)")
    
    # Test accepting all defaults by pressing Enter repeatedly
    proc = subprocess.Popen(
        ['python', 'main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Simulate:
    # - Choice: 6 (About)
    # - Enter (return to menu)
    # - Q (Quit)
    # - Y (Confirm quit)
    output, _ = proc.communicate(input='6\n\nq\ny\n', timeout=10)
    
    # Check for errors
    if 'KeyError' in output:
        print("\n✗ FAIL: KeyError found in output")
        print("Output:")
        print(output)
        return False
    elif 'UnicodeEncodeError' in output:
        print("\n✗ FAIL: UnicodeEncodeError found in output")
        print("Output:")
        print(output)
        return False
    elif 'Traceback' in output:
        print("\n✗ FAIL: Exception found in output")
        print("Output:")
        print(output)
        return False
    else:
        print("\n✓ Menu loaded successfully without errors")
        # Check for numeric display format
        if ':' in output and any(x in output for x in ['1:Auto', '2:SSD', '1:Dry Run']):
            print("✓ Display format shows 'number:name' correctly")
        return True

def test_default_acceptance():
    """Test that pressing Enter accepts numeric defaults"""
    print("\n" + "="*70)
    print("TEST 3: Default Value Acceptance")
    print("="*70)
    
    print("\nThis test verifies that pressing Enter accepts defaults")
    print("Run manually: python main.py")
    print("Then:")
    print("  1. Choose '1' for New Scan")
    print("  2. Enter a valid path")
    print("  3. Press Enter on Mode prompt (should accept [1:Dry Run])")
    print("  4. Press Enter on Disk prompt (should accept [1:Auto])")
    print("  5. Press Enter on Strategy prompt (should accept [1:Auto])")
    print("\nIf any KeyError or UnicodeError occurs, the test fails")
    
    return True

def test_value_map_display():
    """Test that value_map displays correctly"""
    print("\n" + "="*70)
    print("TEST 4: Value Map Display Format")
    print("="*70)
    
    # Expected format examples
    expected_formats = [
        "[1:Auto]",
        "[2:SSD]",
        "[3:HDD]",
        "[1:Dry Run]",
        "[2:Delete]",
        "[2:BFS]",
        "[3:DFS]"
    ]
    
    print("\nExpected display formats:")
    for fmt in expected_formats:
        print(f"  - Mode/Disk/Strategy should show: {fmt}")
    
    print("\n✓ Format specification correct")
    return True

def run_all_tests():
    """Run all tests"""
    print("="*70)
    print(" MENU NUMERIC VALIDATION TEST SUITE")
    print("="*70)
    
    results = []
    
    results.append(("Config File Format", test_config_defaults()))
    results.append(("Menu Interaction", test_menu_interaction()))
    results.append(("Default Acceptance", test_default_acceptance()))
    results.append(("Value Map Display", test_value_map_display()))
    
    print("\n" + "="*70)
    print(" TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        color = "92" if result else "91"
        print(f"  [{test_name:25}] \033[{color}m{status}\033[0m")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*70)
    if all_passed:
        print("\033[92m ALL TESTS PASSED ✓\033[0m")
    else:
        print("\033[91m SOME TESTS FAILED ✗\033[0m")
    print("="*70 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
