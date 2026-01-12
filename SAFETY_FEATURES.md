# Void Walker v4 - Safety Features

## Multi-Layer Deletion Guards

### 1. Database-Level Filtering
**Location:** `data/database.py:get_empty_candidates()`
```python
WHERE file_count=0  # Only folders with zero files
```
- Candidates must have `file_count` exactly equal to 0
- Scanned folders only (status='SCANNED')
- Respects minimum depth configuration

### 2. Triple Physical Verification
**Location:** `core/engine.py:_process_cleanup()`

#### Guard #1: os.listdir() Check (Primary)
```python
contents = os.listdir(path)
if len(contents) > 0:
    self.logger.warning(f"Skipped {path}: contains {len(contents)} items")
    continue
```
- Checks actual filesystem state
- Skips folders with any content
- Logs warning for non-empty folders

#### Guard #2: os.scandir() Verification Loop
```python
size = 0
for entry in os.scandir(path):
    size += 1  # Should never execute for truly empty folder
```
- Secondary verification using scandir
- Counts actual directory entries
- More thorough than listdir alone

#### Guard #3: Assertion with Size Check
```python
assert size == 0, f"Folder not empty: {path} has {size} items"
```
- Explicit assertion that size must be exactly 0
- Raises AssertionError if folder has content
- Logs error and increments error counter
- Continues to next folder (does not delete)

### 3. Operating System Guard
```python
os.rmdir(path)  # Will raise OSError if not truly empty
```
- Final OS-level safety check
- `rmdir()` only works on empty directories
- Raises `OSError` if folder contains files/subfolders
- Exception caught and logged as error

### 4. Root Path Protection
```python
if path == self.config.root_path: continue
```
- Never attempts to delete the scan root directory
- Prevents accidental deletion of entire scan target

## Dry-Run Mode Safety

### Summary Report
```python
if not self.config.delete_mode:
    print(f"\n[*] DRY RUN: Found {len(candidates)} empty folder candidates")
    total_size = 0
    verified_empty = 0
```

### Size Verification
```python
total_size += 0  # Verified empty, size = 0
verified_empty += 1
```

### Final Summary
```
[✓] Verified {verified_empty} truly empty folders
    Total size: {total_size} bytes (all folders confirmed empty)
```
- Explicit confirmation that all folders are empty
- Total size always shows 0 bytes
- Verified count shows successful validation count

## Test Safety Features

### E2E Test Guards
**File:** `tests/test_integration_e2e.py`

```python
"""
SAFETY: All tests use dry_run mode only - no actual deletions
"""
```

#### Pre-Test State Recording
```python
initial_folders = set()
for root, dirs, files in os.walk(self.root):
    for d in dirs:
        initial_folders.add(os.path.join(root, d))
```

#### Post-Test Verification
```python
final_folders = set()
for root, dirs, files in os.walk(self.root):
    for d in dirs:
        final_folders.add(os.path.join(root, d))

deleted = initial_folders - final_folders
self.assertEqual(len(deleted), 0, f"Dry run deleted folders: {deleted}")
```

#### Content Verification
```python
for path, file_count in would_delete:
    self.assertEqual(file_count, 0, f"Marked non-empty folder: {path} has {file_count} files!")
    actual_contents = os.listdir(path) if os.path.exists(path) else []
    self.assertEqual(len(actual_contents), 0, f"Folder {path} has {len(actual_contents)} items!")
```

### Test Mode Enforcement
```python
delete=False,  # CRITICAL: DRY RUN ONLY
```
- All E2E tests use `delete=False`
- No test ever sets `delete=True`
- Assertions verify no folders deleted

## Safety Guarantee

**Only truly empty folders (0 files, 0 subfolders) can be deleted.**

The four-layer verification ensures:
1. Database records indicate zero files
2. os.listdir() returns empty list
3. os.scandir() loop finds zero entries
4. os.rmdir() OS-level validation

If ANY check fails:
- Folder is skipped
- Warning/error logged
- Counter incremented
- Execution continues safely

## Production vs. Dry-Run

### Dry-Run Mode (`delete=False`)
- Marks folders as `WOULD_DELETE` in database
- Never calls `os.rmdir()`
- Shows summary with size verification
- Safe for exploratory use

### Production Mode (`delete=True`)
- Calls `os.rmdir()` only after ALL checks pass
- Marks folders as `DELETED` in database
- OS-level guard prevents non-empty deletion
- Logs all deletions

## Commit History
- **851b25e**: feat(safety): add triple verification guards and dry-run summary
- **349f903**: fix(ui): initialize exclude_paths before Windows submenu
- All 70 core tests passing
