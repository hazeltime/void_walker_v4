# Void Walker v4.1 - Enterprise Folder Cleaner

**Ultra-fast, concurrent folder scanner and empty directory remover for Windows**

## 🚀 New Features (v4.1)

### ✅ TRUE Concurrent Scanning
- **ThreadPoolExecutor-based** multi-threaded scanning (previously imported but unused!)
- Auto-tuned worker count based on disk type:
  - **SSD**: 16 workers (BFS strategy)
  - **HDD**: 4 workers (DFS strategy to minimize seeking)
- Real-time concurrency with futures management

### ✅ Enhanced SSD/HDD Detection
- **Automatic detection** via PowerShell `Get-PhysicalDisk` on Windows
- Detects NVMe, SSD, and HDD media types
- Fallback heuristics for virtualized environments
- Manual override with `--disk ssd|hdd|auto`

### ✅ Cache Status Display
- New `--show-cache` command to view all previous sessions
- Displays completion percentage, pending folders, errors
- Resume capability tracking

### ✅ Interactive Runtime Controls
Enhanced keyboard menu during execution:
- **[P]** Pause/Resume toggle
- **[S]** Save state (manual checkpoint)
- **[Q]** Quit gracefully
- **[H]** Help menu
- **[C]** Show current configuration
- **[D]** Toggle dashboard display
- **[V]** Verbose mode toggle

### ✅ Auto-Persistence
- **Automatic commits** every 10 seconds during scan
- Full resume support for interrupted sessions
- Progress tracking in SQLite database

### ✅ Enhanced Dashboard
Real-time metrics display:
- **Scan rate** (folders/second)
- **Queue depth** (pending work)
- **Active workers** count
- **Elapsed time** with ETA estimation
- **Error tracking**
- Dynamic terminal width adjustment

### ✅ Comprehensive Test Suite
- Unit tests for validators, config, database, filtering
- Mock-based testing for isolation
- Test runner: `python tests/run_tests.py`

---

## 📋 Usage

### Basic Dry Run
```powershell
python main.py "E:\Data" --disk auto
```

### Delete Mode with Custom Workers
```powershell
python main.py "E:\Data" --delete --disk ssd --workers 32
```

### Resume Interrupted Session
```powershell
python main.py "E:\Data" --resume
```

### View Cached Sessions
```powershell
python main.py --show-cache
```

### Advanced Filtering
```powershell
python main.py "C:\Projects" `
    --exclude-name "node_modules" ".git" "*.tmp" `
    --exclude-path "*System32*" "*Windows*" `
    --min-depth 2 `
    --max-depth 10
```

---

## 🔧 CLI Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `path` | Target directory to scan | *Required* |
| `--delete` | Enable actual deletion (vs dry run) | `False` |
| `--resume` | Resume previous interrupted session | `False` |
| `--show-cache` | Display session history and exit | - |
| `--disk` | Disk type: `ssd`, `hdd`, `auto` | `auto` |
| `--workers` | Manual thread count override | Auto (16/4) |
| `--min-depth` | Minimum depth to delete | `0` |
| `--max-depth` | Maximum traversal depth | `100` |
| `--exclude-path` | Path glob patterns to exclude | `[]` |
| `--exclude-name` | Folder name patterns to exclude | See defaults |
| `--include-name` | Include ONLY these folder names | `[]` |

### Default Exclusions
- `.git`
- `$RECYCLE.BIN`
- `System Volume Information`

---

## 🎯 Architecture

### Modular Design
```
void_walker_v4/
├── main.py              # CLI entry point
├── config/
│   └── settings.py      # Configuration with SSD detection
├── core/
│   ├── engine.py        # Concurrent scanning engine
│   └── controller.py    # Keyboard controls
├── data/
│   └── database.py      # SQLite persistence
├── ui/
│   ├── menu.py          # Interactive wizard
│   ├── dashboard.py     # Real-time display
│   └── reporter.py      # Session reports
├── utils/
│   ├── logger.py        # Logging setup
│   └── validators.py    # Path validation
└── tests/               # Comprehensive test suite
    ├── test_validators.py
    ├── test_config.py
    ├── test_database.py
    ├── test_filtering.py
    └── run_tests.py
```

### Execution Flow
```
main.py → Config → Engine
              ↓
         Database.setup()
              ↓
     Controller.start() (keyboard listener)
              ↓
     Dashboard.start() (live UI)
              ↓
    ThreadPoolExecutor pool
              ↓
   Concurrent _scan_folder() workers
              ↓
    Periodic auto-commits (10s)
              ↓
         Cleanup phase
              ↓
      Reporter.show_summary()
```

---

## 🧪 Testing

Run the complete test suite:
```powershell
python tests/run_tests.py
```

Individual test modules:
```powershell
python -m unittest tests.test_validators
python -m unittest tests.test_config
python -m unittest tests.test_database
python -m unittest tests.test_filtering
```

---

## 💾 Data Persistence

### Database Schema
**File**: `void_walker_history.db` (SQLite, WAL mode)

**Tables**:
1. `sessions`
   - `id` (session ID)
   - `timestamp` (creation time)
   - `config` (serialized config)

2. `folders`
   - `path` (folder path)
   - `session_id` (foreign key)
   - `depth` (nesting level)
   - `file_count` (files in folder)
   - `status` (PENDING/SCANNED/ERROR/DELETED/WOULD_DELETE)
   - `error_msg` (error details)

### Session Files
- **Logs**: `logs/session_{timestamp}.log`
- **Config**: `last_run_config.json`

---

## ⚡ Performance

### Concurrency Model
- **ThreadPoolExecutor** with configurable workers
- **BFS** (Breadth-First) for SSD: Level-by-level parallel processing
- **DFS** (Depth-First) for HDD: Minimize disk head movement
- **Thread-safe** queue and stats with `threading.Lock`
- **Auto-commit** every 10s for resume capability

### Optimization Strategies
| Disk Type | Strategy | Workers | Rationale |
|-----------|----------|---------|-----------|
| SSD/NVMe | BFS | 16 | Random access, high concurrency |
| HDD | DFS | 4 | Sequential access, minimize seeks |

### Safety Features
- **Symlink/Junction detection** (prevents infinite loops)
- **Permission error handling** (non-fatal, logged)
- **Graceful shutdown** on Ctrl+C
- **State preservation** on interruption

---

## 🔍 Example Session

```powershell
PS> python main.py "E:\Projects" --delete --disk auto

[i] Interactive Controls Enabled: Press 'H' for help

Initializing Void Walker v4 [Session: session_20260112_153045]
Target: E:\Projects | Mode: DELETE
Strategy: BFS | Workers: 16

[/] SCANNING | RUNNING | Workers: 16
E:\Projects\old_projects\temp_data\cache
Scanned: 1247 | Rate: 124.7/s | Queue: 342 | Errors: 3 | Time: 0:00:10

[PHASE: CLEANING]
Deleted: 87 empty folders

SESSION REPORT
==============================================================
 Session:  session_20260112_153045
 Logs:     logs/session_20260112_153045.log
 Errors:   3
--------------------------------------------------------------
```

---

## 📊 Features Comparison

| Feature | v4.0 | v4.1 |
|---------|------|------|
| Concurrent Scanning | ❌ (imported but unused) | ✅ ThreadPoolExecutor |
| SSD Detection | ⚠️ Stub | ✅ PowerShell query |
| Cache Display | ❌ | ✅ --show-cache |
| Runtime Controls | P/R/Q only | ✅ P/S/Q/H/C/D/V |
| Auto-Persistence | ❌ | ✅ Every 10s |
| Dashboard Metrics | Basic | ✅ Rate/Queue/ETA |
| Test Suite | ❌ | ✅ Comprehensive |
| Pattern Matching | fnmatch | ✅ Enhanced glob |

---

## 🛡️ Safety & Error Handling

### Protected Operations
- **Read-only scanning** by default (requires `--delete`)
- **Depth limits** prevent accidental deep deletion
- **Default exclusions** protect system folders
- **Permission errors** logged, not fatal
- **Junctions/Symlinks** automatically skipped

### Error Recovery
- **Automatic state saving** every 10 seconds
- **Resume from checkpoint** with `--resume`
- **Graceful shutdown** preserves progress
- **Error log** in database for analysis

---

## 🔮 Future Enhancements
- [ ] Pattern include/exclude with regex support
- [ ] Network path support (UNC)
- [ ] Size-based filtering (delete folders < X MB)
- [ ] Age-based filtering (modified > N days ago)
- [ ] Export results to CSV/JSON
- [ ] Linux/macOS cross-platform support
- [ ] GUI interface

---

## 📝 Requirements
- **Python 3.8+**
- **Windows 11** (PowerShell 5.1+ for disk detection)
- **No external dependencies** (standard library only)

---

## 📄 License
MIT License - See LICENSE file

---

## 🤝 Contributing
1. Run tests: `python tests/run_tests.py`
2. Ensure all tests pass
3. Follow existing code style
4. Add tests for new features

---

## 🐛 Troubleshooting

### "ThreadPoolExecutor not working"
- Ensure Python 3.8+ is installed
- Check worker count with `--workers` override

### "SSD not detected"
- Run PowerShell as Administrator
- Use `--disk ssd` to force SSD mode

### "Resume not working"
- Check `void_walker_history.db` exists
- Verify session ID in `--show-cache`

### "Permission denied errors"
- Run as Administrator for system folders
- Add paths to `--exclude-path` to skip

---

**Version**: 4.1.0  
**Last Updated**: January 12, 2026  
**Author**: Enterprise Systems Team
