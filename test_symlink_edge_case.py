"""
Test: Can folders with ONLY symlinks be deleted?
"""
import os
import tempfile
import shutil

print("Testing symlink-only folder deletion behavior...")
print("="*60)

# Create test structure
test_dir = tempfile.mkdtemp(prefix="symlink_test_")
print(f"Test directory: {test_dir}")

try:
    # Create a folder with only a symlink
    symlink_folder = os.path.join(test_dir, "has_only_symlink")
    os.makedirs(symlink_folder)
    
    # Create a target file
    target_file = os.path.join(test_dir, "target.txt")
    with open(target_file, 'w') as f:
        f.write("target content")
    
    # Create symlink in the folder
    symlink_path = os.path.join(symlink_folder, "link_to_target.txt")
    
    if os.name == 'nt':  # Windows
        # On Windows, need admin for symlinks OR use junctions/hardlinks
        try:
            os.symlink(target_file, symlink_path)
            print("✓ Created symlink (Windows)")
        except OSError as e:
            print(f"⚠ Cannot create symlink on Windows without admin: {e}")
            print("  Creating hardlink instead...")
            os.link(target_file, symlink_path)
            print("✓ Created hardlink (Windows fallback)")
    else:  # Unix/Linux
        os.symlink(target_file, symlink_path)
        print("✓ Created symlink (Unix)")
    
    # Check with os.scandir (what the code uses)
    print("\nChecking with os.scandir():")
    count = 0
    for entry in os.scandir(symlink_folder):
        print(f"  Found: {entry.name}")
        print(f"    is_file(): {entry.is_file()}")
        print(f"    is_dir(): {entry.is_dir()}")
        print(f"    is_symlink(): {entry.is_symlink()}")
        if entry.is_symlink():
            print("    → SKIPPED (symlink)")
            continue
        if entry.is_file() or entry.is_dir():
            count += 1
    
    print(f"\nEntry count (code logic): {count}")
    
    # Check with os.listdir
    print(f"\nos.listdir() result: {os.listdir(symlink_folder)}")
    listdir_count = len(os.listdir(symlink_folder))
    print(f"os.listdir() count: {listdir_count}")
    
    # Try to delete with os.rmdir
    print("\nAttempting os.rmdir()...")
    if count == 0:
        print("  Entry count is 0, folder would be candidate for deletion")
        print(f"  BUT os.listdir() count is {listdir_count}")
        
        if listdir_count > 0:
            print("\n  ✅ SAFE: Guard 4 (os.listdir) would catch this!")
            print(f"     contents = os.listdir(path)  # Returns: {os.listdir(symlink_folder)}")
            print(f"     if len(contents) > 0: continue  # {listdir_count} > 0, SKIP!")
        else:
            print(f"\n  ⚠ POTENTIAL ISSUE: Both checks return 0")
            try:
                # Try the actual deletion
                test_copy = os.path.join(test_dir, "test_delete")
                shutil.copytree(symlink_folder, test_copy, symlinks=True)
                os.rmdir(test_copy)
                print("  ✗ DELETED: os.rmdir() succeeded on symlink-only folder!")
            except OSError as e:
                print(f"  ✓ SAFE: os.rmdir() failed: {e}")
    
finally:
    # Cleanup
    shutil.rmtree(test_dir, ignore_errors=True)
    print(f"\n✓ Cleaned up test directory")

print("\n" + "="*60)
print("CONCLUSION:")
print("="*60)
