# Void Walker v4.1.1

**Enterprise Empty Folder Detection & Cleanup Tool**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-33%2F33%20passing-brightgreen.svg)](./tests/)

> Optimized for SSD/HDD with concurrent scanning, intelligent filtering, and resume capability.

---

## 🚀 Quick Start

### Windows
```bash
# Using batch file (easiest)
void_walker.bat

# Or directly with Python
python main.py
```

### Command Line
```bash
# Dry run (safe preview)
python main.py F:\

# Delete mode
python main.py F:\ --delete

# With filters
python main.py F:\ --exclude-name node_modules .git --min-depth 2
```

---

## ✨ Features

### Core Capabilities
- **Concurrent Scanning**: ThreadPoolExecutor with up to 32 workers
- **Hardware Optimization**: Auto-detects SSD/HDD, optimizes strategy
- **Resume Capability**: Continue interrupted scans from SQLite cache
- **Real-time Dashboard**: Live metrics at 5 FPS (scan rate, queue, errors)
- **Dry Run Mode**: Safe preview before deletion
- **Pattern Filtering**: Include/exclude paths and names with glob patterns

### Performance
| Hardware | Strategy | Workers | Speed Boost |
|----------|----------|---------|-------------|
| SSD      | BFS      | 16      | 10-12x      |
| HDD      | DFS      | 4       | 3-4x        |

**Average scan rate**: 200-500 folders/second on SSD

---

## 📋 Menu Interface

```
═══ MAIN MENU ═══

[1] New Scan         - Configure and run a new folder scan
[2] Load & Run       - Load saved config and execute immediately
[3] Resume Session   - Continue a previously interrupted scan
[4] View Cache       - Show previous scan sessions
[5] Help             - Comprehensive guide to all options
[6] About            - Application info and features
[Q] Quit             - Exit with confirmation
```

---

## 🏗️ Architecture

```
void_walker_v4/
├── main.py                 # Entry point & CLI
├── void_walker.bat         # Windows launcher
├── requirements.txt        # No dependencies!
│
├── config/
│   └── settings.py        # Hardware detection & config
│
├── core/
│   ├── engine.py          # ThreadPoolExecutor scanning
│   └── controller.py      # Keyboard controls
│
├── data/
│   └── database.py        # SQLite persistence
│
├── ui/
│   ├── menu.py            # Interactive wizard
│   ├── dashboard.py       # Real-time display
│   └── reporter.py        # Post-scan reports
│
├── utils/
│   ├── logger.py          # Logging setup
│   └── validators.py      # Path validation
│
└── tests/                 # 33 tests, 100% passing
    ├── test_config.py     # 10 tests
    ├── test_database.py   # 9 tests  
    ├── test_filtering.py  # 4 tests
    └── test_validators.py # 10 tests
```

---

## 🧪 Testing

```bash
python tests/run_tests.py
# Ran 33 tests in 0.079s - OK
```

---

## ⚙️ Configuration

**File**: `void_walker_config.json`

```json
{
    "path": "F:\\",
    "mode": "t",
    "disk": "s",
    "strategy": "bfs",
    "workers": 16,
    "min_depth": 2,
    "max_depth": 50,
    "exclude_paths": ["*.tmp*"],
    "exclude_names": ["node_modules", ".git"],
    "include_names": []
}
```

---

## 🎮 Keyboard Controls

| Key | Action |
|-----|--------|
| **P** | Pause/Resume |
| **S** | Save Progress |
| **H** | Show Help |
| **C** | Show Config |
| **Q** | Quit |

---

## 🔧 Requirements

- **Python 3.8+** (3.14 recommended)
- **OS**: Windows, Linux, Mac
- **Dependencies**: None (stdlib only)

---

## 📦 Installation

```bash
git clone https://github.com/hazeltime/void_walker_v4.git
cd void_walker_v4
python main.py --help
```

---

## 🛡️ Safety

1. ✅ Dry run default
2. ✅ Min depth protection
3. ✅ Pattern exclusions
4. ✅ Quit confirmation
5. ✅ Auto-save every 10s

---

## 📝 License

MIT License

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/hazeltime/void_walker_v4/issues)
- **Repository**: [hazeltime/void_walker_v4](https://github.com/hazeltime/void_walker_v4)

---

**Made with ❤️ for enterprise-scale folder cleanup**
