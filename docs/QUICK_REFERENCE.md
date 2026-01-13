# Void Walker v4.1 - Quick Reference Card

## 🚀 Quick Start

### View Previous Sessions
```powershell
python main.py --show-cache
```

### Dry Run (Safe Mode)
```powershell
python main.py "E:\Data"
```

### Delete Mode
```powershell
python main.py "E:\Data" --delete
```

### Resume Interrupted Session
```powershell
python main.py "E:\Data" --resume
```

---

## ⌨️ Runtime Keyboard Controls

| Key | Action | Description |
|-----|--------|-------------|
| **P** | Pause/Resume | Toggle scan pause |
| **S** | Save State | Manual checkpoint |
| **Q** | Quit | Graceful exit with save |
| **H** | Help | Show command menu |
| **C** | Config | Display current settings |
| **D** | Dashboard | Toggle display on/off |
| **V** | Verbose | Toggle verbose mode |

---

## 🔧 Common CLI Patterns

### SSD Optimization
```powershell
python main.py "C:\Projects" --disk ssd --workers 32
```

### HDD Optimization
```powershell
python main.py "E:\Archive" --disk hdd --workers 4
```

### Filter by Depth
```powershell
python main.py "C:\Temp" --min-depth 2 --max-depth 5
```

### Exclude Patterns
```powershell
python main.py "C:\Code" `
    --exclude-name "node_modules" ".git" "*.log" `
    --exclude-path "*Windows*" "*System32*"
```

### Include Only Specific Folders
```powershell
python main.py "C:\Projects" --include-name "temp" "cache" "build"
```

---

## 📊 Dashboard Metrics Explained

```
[/] SCANNING | RUNNING | Workers: 16
E:\Projects\old_projects\temp_data\cache
Scanned: 1247 | Rate: 124.7/s | Queue: 342 | Errors: 3 | Time: 0:00:10
```

- **Spinner**: [/ - \ |] indicates activity
- **Phase**: SCANNING or CLEANING
- **Status**: RUNNING, PAUSED, or SAVED
- **Workers**: Active thread count
- **Current Path**: Folder being processed
- **Scanned**: Total folders scanned
- **Rate**: Folders per second
- **Queue**: Pending folders
- **Errors**: Permission/system errors
- **Time**: Elapsed runtime

---

## 🎯 Disk Type Strategy

| Type | Strategy | Workers | Best For |
|------|----------|---------|----------|
| **SSD** | BFS | 16 | Fast random access, parallel I/O |
| **HDD** | DFS | 4 | Sequential access, minimize seeks |
| **Auto** | Detect | Auto | Let system decide |

---

## 📁 Default Exclusions

These folders are ALWAYS excluded:
- `.git`
- `$RECYCLE.BIN`
- `System Volume Information`

Add more with `--exclude-name`

---

## 🔍 Troubleshooting

### "Permission Denied" Errors
```powershell
# Run as Administrator OR exclude paths
python main.py "C:\Windows" --exclude-path "*System32*"
```

### Scan Too Fast/Slow
```powershell
# Override worker count
python main.py "E:\Data" --workers 8
```

### Resume Not Working
```powershell
# Check session exists
python main.py --show-cache

# Ensure same path
python main.py "E:\Data" --resume
```

### SSD Not Detected
```powershell
# Force SSD mode
python main.py "C:\Data" --disk ssd
```

---

## 🧪 Testing

### Run All Tests
```powershell
python tests/run_tests.py
```

### Full Validation
```powershell
python validate.py
```

### Individual Test Module
```powershell
python -m unittest tests.test_config
```

---

## 📝 Log Files

- **Session Logs**: `logs/session_{timestamp}.log`
- **Database**: `void_walker_history.db`
- **Config**: `last_run_config.json`

---

## 🆘 Help

### CLI Help
```powershell
python main.py --help
```

### Interactive Wizard
```powershell
python main.py
# (no arguments launches menu)
```

---

## ⚡ Performance Tips

1. **Use SSD mode** for solid-state drives
2. **Increase workers** for faster systems (--workers 32)
3. **Set max-depth** to limit traversal
4. **Exclude large folders** early (node_modules)
5. **Save state often** with [S] key
6. **Monitor queue depth** to gauge progress

---

## 🔒 Safety Checklist

- [ ] Run **dry run** first (no --delete)
- [ ] Check `--show-cache` for previous results
- [ ] Set `--min-depth` to protect root
- [ ] Add exclusions for important folders
- [ ] Monitor errors in dashboard
- [ ] Review session log before cleanup
- [ ] Have backups of critical data

---

## 📊 Example Session Flow

```powershell
# 1. View cache
python main.py --show-cache

# 2. Dry run with filters
python main.py "E:\Projects" `
    --disk auto `
    --exclude-name "node_modules" ".git" `
    --min-depth 2

# During scan: Press [S] to save state
# During scan: Press [C] to view config
# During scan: Press [P] to pause

# 3. Review results
# Check: logs/session_{timestamp}.log

# 4. If happy, run delete mode
python main.py "E:\Projects" --delete --resume

# 5. Verify
python main.py --show-cache
```

---

**Quick Ref Version**: 4.1.0  
**Last Updated**: January 12, 2026

---

For full documentation, see [README.md](README.md)
