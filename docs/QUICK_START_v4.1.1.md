# Void Walker v4.1.1 - Quick Start Guide

## 🚀 Running the Application

### Interactive Menu (Recommended)
```cmd
python main.py
```

### Direct Scan
```cmd
python main.py F:\
```

### Resume Previous Session
```cmd
python main.py --resume
```

### View Cached Sessions
```cmd
python main.py --show-cache
```

### Build Standalone .exe
```powershell
.\build_exe.ps1
# Creates: VoidWalker.exe
```

### Run Coverage Report
```powershell
.\run_coverage.ps1
# Creates: htmlcov/index.html
```

---

## 📋 New Features (January 2026 Update)

### 1. Windows System Folder Exclusions

When configuring a scan, you'll see:

```
7. WINDOWS SYSTEM FOLDERS (Quick Exclusions)
   Select common folders to automatically exclude:

   [A] All system folders (recommended)
   [C] Custom selection
   [N] None (skip)

   Your choice [A]: 
```

**Options:**
- **[A]** - Exclude all 6 system folders automatically
- **[C]** - Pick specific folders by number (e.g., `1,3,5`)
- **[N]** - Skip (you can add manual exclusions later)

**Protected Folders:**
1. Windows
2. Program Files
3. Program Files (x86)
4. ProgramData
5. Users
6. $RECYCLE.BIN

### 2. Initialization Progress

You'll now see:
```
[*] Initializing Void Walker...
    → Setting up database...
       Database ready (5 total sessions)
    → Starting keyboard controller...
    → Launching real-time dashboard...
[✓] Ready! Starting scan from: C:\path
```

### 3. Improved Default Values

Default values are now **bold bright yellow** and easier to distinguish:

**Before:**
```
Path []: 
```

**After:**
```
Path [C:\Users\Documents]:  ← (bold bright yellow)
      ^^^^^^^^^^^^^^^^^^^^
```

### 4. .exe Compilation

**Build executable:**
```powershell
.\build_exe.ps1
```

**Run standalone:**
```cmd
VoidWalker.exe
VoidWalker.exe C:\path
VoidWalker.exe --help
```

**Benefits:**
- ✅ No Python required
- ✅ Single file (~12 MB)
- ✅ Can run while editing code
- ✅ Share with others easily

---

## 🧪 Testing

### Run All Tests
```cmd
python tests/run_tests.py
```

**Expected Output:**
```
Ran 70 tests in 0.158s
OK
```

### Run with Coverage
```powershell
.\run_coverage.ps1
```

**Output:**
- Terminal: Coverage percentages
- HTML: `htmlcov/index.html` (open in browser)

---

## 🐛 Bug Fixes

### Cache Error Fixed
**Before:** `'>' not supported between instances of 'NoneType' and 'int'`

**After:** Null coalescing handles empty sessions gracefully

### Default Path Fixed
**Before:** Empty string (confusing)

**After:** Current working directory (obvious default)

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| **Tests** | 70 passing |
| **Test Runtime** | 0.158s |
| **Code Coverage** | Use `run_coverage.ps1` |
| **Executable Size** | ~12 MB (UPX compressed) |
| **Backward Compatible** | ✅ Yes |

---

## 🎮 Workflow Examples

### Safe Scan (Dry Run)
```cmd
python main.py
# Choose [1] New Scan
# Choose [T] for Dry Run
# Select [A] for Windows exclusions
# Review results without deleting
```

### Production Delete
```cmd
python main.py F:\ --delete --disk ssd
# Direct deletion on F: drive
# SSD optimized (16 workers, BFS)
```

### Resume Interrupted Scan
```cmd
python main.py --resume
# Continues from last checkpoint
# Uses saved configuration
```

### Build for Distribution
```powershell
.\build_exe.ps1
# Share VoidWalker.exe with team
# No Python installation needed
```

---

## 🔧 Configuration

**Default Config File:** `void_walker_config.json`

**Example:**
```json
{
    "path": "F:\\",
    "mode": "t",
    "disk": "s",
    "strategy": "bfs",
    "workers": 16,
    "min_depth": 2,
    "max_depth": 50,
    "exclude_paths": [
        "*:\\Windows*",
        "*:\\Program Files*"
    ],
    "exclude_names": ["node_modules", ".git"],
    "include_names": [],
    "windows_exclusions": []
}
```

**Load Saved Config:**
```
Choose [2] Load & Run from main menu
```

---

## 🎯 Best Practices

### Safety First
1. **Always test with Dry Run first** (`[T]` mode)
2. **Use Windows exclusions** (`[A]` recommended)
3. **Set min_depth ≥ 2** to protect drive roots
4. **Review cache status** before delete mode

### Performance
1. **SSD drives:** Auto-selects 16 workers + BFS
2. **HDD drives:** Auto-selects 4 workers + DFS
3. **Manual override:** `--workers 8` if needed

### Resume Safety
1. **Auto-saves every 10 seconds** during scan
2. **Press S** to manually save progress
3. **Use --resume** to continue interrupted scans

---

## 📞 Support

**Documentation:**
- [README.md](../README.md) - Full documentation
- [UPDATE_SUMMARY_JAN2026.md](UPDATE_SUMMARY_JAN2026.md) - Detailed changes
- [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md) - Architecture details

**GitHub:**
- Repository: `hazeltime/void_walker_v4`
- Issues: Report bugs via GitHub Issues
- Latest: Commit 53cfc83

**Tests:**
- 70 tests covering all modules
- Run: `python tests/run_tests.py`
- Coverage: `.\run_coverage.ps1`

---

## ⚡ Quick Commands Cheat Sheet

| Command | Action |
|---------|--------|
| `python main.py` | Interactive menu |
| `python main.py C:\path` | Direct scan |
| `python main.py --delete` | Enable deletion |
| `python main.py --resume` | Resume last session |
| `python main.py --show-cache` | View history |
| `.\build_exe.ps1` | Build .exe |
| `.\run_coverage.ps1` | Test coverage |
| `python tests/run_tests.py` | Run tests |

**During Scan:**
- `P` - Pause/Resume
- `S` - Save progress
- `Q` - Quit safely

---

**Version:** 4.1.1
**Last Updated:** January 12, 2026
**Tests:** 70/70 passing
**Status:** Production Ready
