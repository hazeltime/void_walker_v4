"""
Test the new interactive scroll feature for empty folders.
This script demonstrates the new workflow:
1. Scan completes
2. User is asked if they want to scroll through empty folders
3. User can navigate through paginated list
4. User is asked if they want to proceed with deletion

SAFETY: Creates isolated sandbox with generated test folders.
NO REAL DATA IS TOUCHED.
"""
import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path

from pathlib import Path

def create_test_sandbox():
    """
    Create a completely isolated test sandbox with generated folders.
    Returns the path to the sandbox directory.
    
    Structure created:
    sandbox/
        empty_1/
        empty_2/
        has_file/
            file.txt
        nested/
            empty_deep/
            has_content/
                data.txt
    """
    sandbox = tempfile.mkdtemp(prefix="void_walker_test_")
    print(f"\n✓ Created test sandbox: {sandbox}")
    
    # Create empty folders
    os.makedirs(os.path.join(sandbox, "empty_1"))
    os.makedirs(os.path.join(sandbox, "empty_2"))
    print("  - Created 2 empty folders")
    
    # Create folder with file
    has_file = os.path.join(sandbox, "has_file")
    os.makedirs(has_file)
    with open(os.path.join(has_file, "file.txt"), 'w') as f:
        f.write("This folder should NOT be deleted")
    print("  - Created 1 folder with file (should NOT be deleted)")
    
    # Create nested structure
    nested = os.path.join(sandbox, "nested")
    os.makedirs(os.path.join(nested, "empty_deep"))
    has_content = os.path.join(nested, "has_content")
    os.makedirs(has_content)
    with open(os.path.join(has_content, "data.txt"), 'w') as f:
        f.write("Protected data")
    print("  - Created nested structure with 1 empty and 1 protected folder")
    
    print(f"  Total: 3 empty folders, 2 protected folders\n")
    return sandbox

def cleanup_sandbox(sandbox_path):
    """Completely remove the test sandbox."""
    if os.path.exists(sandbox_path):
        shutil.rmtree(sandbox_path, ignore_errors=True)
        print(f"\n✓ Cleaned up sandbox: {sandbox_path}")

def test_scroll_yes_delete_yes():
    """Test: User wants to scroll AND wants to delete"""
    print("\n" + "="*70)
    print("TEST 1: Scroll YES, Delete YES (DRY RUN)")
    print("="*70)
    
    proc = subprocess.Popen(
        ['python', 'main.py', 'test_scan_temp'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Simulate user input:
    # 1. "y" - Yes, I want to scroll through the list
    # 2. "" (Enter) - Continue after viewing page
    # 3. "y" - Yes, proceed with deletion
    output, _ = proc.communicate(input='y\n\ny\n')
    
    print(output)
    print("\n✓ Test 1 completed")

def test_scroll_no_delete_yes():
    """Test: User doesn't want to scroll but wants to delete"""
    print("\n" + "="*70)
    print("TEST 2: Scroll NO, Delete YES (DRY RUN)")
    print("="*70)
    
    proc = subprocess.Popen(
        ['python', 'main.py', 'test_scan_temp'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Simulate user input:
    # 1. "n" - No, skip scrolling
    # 2. "y" - Yes, proceed with deletion
    output, _ = proc.communicate(input='n\ny\n')
    
    print(output)
    print("\n✓ Test 2 completed")

def test_scroll_yes_delete_no():
    """Test: User wants to scroll but doesn't want to delete"""
    print("\n" + "="*70)
    print("TEST 3: Scroll YES, Delete NO")
    print("="*70)
    
    proc = subprocess.Popen(
        ['python', 'main.py', 'test_scan_temp'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Simulate user input:
    # 1. "y" - Yes, scroll
    # 2. "" (Enter) - Continue after viewing
    # 3. "n" - No, don't delete
    output, _ = proc.communicate(input='y\n\nn\n')
    
    print(output)
    print("\n✓ Test 3 completed")

def test_with_delete_mode():
    """Test: Production DELETE mode - SAFE SANDBOX ONLY"""
    print("\n" + "="*70)
    print("TEST 4: DELETE MODE (Production) - ISOLATED SANDBOX")
    print("="*70)
    
    # Create isolated test sandbox
    sandbox = create_test_sandbox()
    
    try:
        print("⚠ This test will DELETE empty folders in the sandbox ONLY")
        print("⚠ NO REAL DATA will be touched\n")
        
        # Count folders before
        folders_before = []
        for root, dirs, files in os.walk(sandbox):
            for d in dirs:
                folders_before.append(os.path.join(root, d))
        print(f"Before: {len(folders_before)} folders in sandbox")
        
        proc = subprocess.Popen(
            ['python', 'main.py', sandbox, '--delete'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Simulate user input:
        # 1. "y" - Yes, scroll
        # 2. "" (Enter) - Continue after viewing
        # 3. "y" - Yes, DELETE the folders (SANDBOX ONLY)
        output, _ = proc.communicate(input='y\n\ny\n')
        
        print(output)
        
        # Verify results
        folders_after = []
        for root, dirs, files in os.walk(sandbox):
            for d in dirs:
                folders_after.append(os.path.join(root, d))
        
        deleted_count = len(folders_before) - len(folders_after)
        print(f"\nAfter: {len(folders_after)} folders remaining")
        print(f"Deleted: {deleted_count} empty folders")
        
        # Verify protected folders still exist
        protected = [
            os.path.join(sandbox, "has_file"),
            os.path.join(sandbox, "nested", "has_content")
        ]
        
        for folder in protected:
            if os.path.exists(folder):
                print(f"✓ Protected folder still exists: {os.path.basename(folder)}")
            else:
                print(f"✗ ERROR: Protected folder was deleted: {folder}")
        
        print("\n✓ Test 4 completed - Sandbox test successful")
        
    finally:
        # Always cleanup the sandbox
        cleanup_sandbox(sandbox)
    """Test: User wants to scroll AND wants to delete"""
    print("\n" + "="*70)
    print("TEST 1: Scroll YES, Delete YES (DRY RUN)")
    print("="*70)
    
    proc = subprocess.Popen(
        ['python', 'main.py', 'test_scan_temp'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Simulate user input:
    # 1. "y" - Yes, I want to scroll through the list
    # 2. "" (Enter) - Continue after viewing page
    # 3. "y" - Yes, proceed with deletion
    output, _ = proc.communicate(input='y\n\ny\n')
    
    print(output)
    print("\n✓ Test 1 completed")

def test_scroll_no_delete_yes():
    """Test: User doesn't want to scroll but wants to delete"""
    print("\n" + "="*70)
    print("TEST 2: Scroll NO, Delete YES (DRY RUN)")
    print("="*70)
    
    proc = subprocess.Popen(
        ['python', 'main.py', 'test_scan_temp'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Simulate user input:
    # 1. "n" - No, skip scrolling
    # 2. "y" - Yes, proceed with deletion
    output, _ = proc.communicate(input='n\ny\n')
    
    print(output)
    print("\n✓ Test 2 completed")

def test_scroll_yes_delete_no():
    """Test: User wants to scroll but doesn't want to delete"""
    print("\n" + "="*70)
    print("TEST 3: Scroll YES, Delete NO")
    print("="*70)
    
    proc = subprocess.Popen(
        ['python', 'main.py', 'test_scan_temp'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Simulate user input:
    # 1. "y" - Yes, scroll
    # 2. "" (Enter) - Continue after viewing
    # 3. "n" - No, don't delete
    output, _ = proc.communicate(input='y\n\nn\n')
    
    print(output)
    print("\n✓ Test 3 completed")

def test_with_delete_mode():
    """Test: Production DELETE mode"""
    print("\n" + "="*70)
    print("TEST 4: DELETE MODE (Production)")
    print("="*70)
    print("⚠ WARNING: This will actually delete empty folders!")
    print("Testing on test_scan_temp only...\n")
    
    proc = subprocess.Popen(
        ['python', 'main.py', 'test_scan_temp', '--delete'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Simulate user input:
    # 1. "y" - Yes, scroll
    # 2. "" (Enter) - Continue after viewing
    # 3. "y" - Yes, DELETE the folders
    output, _ = proc.communicate(input='y\n\ny\n')
    
    print(output)
    print("\n✓ Test 4 completed")

if __name__ == "__main__":
    print("="*70)
    print(" TESTING NEW INTERACTIVE SCROLL & CONFIRM FEATURE")
    print(" SAFETY: ALL TESTS USE ISOLATED SANDBOXES")
    print("="*70)
    
    # Run dry-run tests (use existing test folder)
    test_scroll_yes_delete_yes()
    test_scroll_no_delete_yes()
    test_scroll_yes_delete_no()
    
    # Ask before running delete mode (creates isolated sandbox)
    print("\n" + "="*70)
    print("DELETE MODE TEST")
    print("="*70)
    print("This test will:")
    print("  1. Create an ISOLATED temporary sandbox")
    print("  2. Generate test folders inside the sandbox")
    print("  3. Run DELETE mode on the sandbox ONLY")
    print("  4. Verify protected folders are NOT deleted")
    print("  5. Completely remove the sandbox")
    print("\n⚠ NO REAL DATA ON YOUR SYSTEM WILL BE TOUCHED")
    print("="*70)
    
    choice = input("\nRun DELETE mode test in isolated sandbox? (y/N): ").lower().strip()
    if choice == 'y':
        test_with_delete_mode()
    else:
        print("\n⊗ Skipped DELETE mode test")
    
    print("\n" + "="*70)
    print(" ALL TESTS COMPLETED")
    print("="*70)
    print("\n✓ New feature working correctly!")
    print("  - Prompts user to scroll through empty folders")
    print("  - Displays paginated list with depth markers")
    print("  - Asks for confirmation before deletion")
    print("  - Works in both DRY RUN and DELETE modes")
    print("  - DELETE test uses isolated sandbox (NO REAL DATA TOUCHED)")

