"""
Common constants and enumerations for Void Walker v4.
Centralizes magic strings, numbers, and configuration values.
"""
from enum import Enum


# =============================================================================
# VERSION AND METADATA
# =============================================================================
APP_NAME = "VOID WALKER"
APP_VERSION = "4.1.1"
APP_DESCRIPTION = "Enterprise Empty Folder Detection & Cleanup Tool"
APP_TAGLINE = "Optimized for SSD/HDD with concurrent scanning & intelligent filtering"
REPOSITORY_URL = "github.com/hazeltime/void_walker_v4"
RELEASE_DATE = "January 2026"


# =============================================================================
# ENUMERATIONS
# =============================================================================
class OperationMode(Enum):
    """Execution mode for folder operations"""
    DRY_RUN = "t"  # Test mode, no actual deletions
    DELETE = "d"   # Actually delete empty folders


class DiskType(Enum):
    """Disk hardware type for optimization"""
    AUTO = "auto"
    SSD = "ssd"
    HDD = "hdd"


class ScanStrategy(Enum):
    """Folder traversal strategy"""
    AUTO = "auto"  # Match disk type
    BFS = "bfs"    # Breadth-first search (best for SSD)
    DFS = "dfs"    # Depth-first search (best for HDD)


class FolderStatus(Enum):
    """Database status for scanned folders"""
    PENDING = "PENDING"
    SCANNED = "SCANNED"
    ERROR = "ERROR"
    DELETED = "DELETED"
    WOULD_DELETE = "WOULD_DELETE"


class EnginePhase(Enum):
    """Current execution phase"""
    INIT = "INIT"
    SCANNING = "SCANNING"
    CLEANING = "CLEANING"
    COMPLETE = "COMPLETE"


# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DEFAULT_DB_PATH = "void_walker_history.db"
DB_COMMIT_INTERVAL = 10  # seconds between automatic commits
DB_WAL_MODE = True


# =============================================================================
# CONCURRENCY CONFIGURATION
# =============================================================================
WORKERS_SSD = 16
WORKERS_HDD = 4
MIN_WORKERS = 1
MAX_WORKERS = 32
QUEUE_BATCH_SIZE = 2  # Multiple of workers for queue processing


# =============================================================================
# DEPTH LIMITS
# =============================================================================
DEFAULT_MIN_DEPTH = 0
DEFAULT_MAX_DEPTH = 10000  # Default maximum traversal depth
ABSOLUTE_MAX_DEPTH = 100000  # Safety limit for extreme cases


# =============================================================================
# DEFAULT EXCLUSIONS
# =============================================================================
DEFAULT_EXCLUDE_NAMES = [
    ".git",
    "$RECYCLE.BIN",
    "System Volume Information",
    "Recovery",
    "Boot",
    "Windows",
    "Program Files",
    "Program Files (x86)",
]


# =============================================================================
# FILE PATTERNS
# =============================================================================
CONFIG_FILE = "void_walker_config.json"
LOG_DIRECTORY = "logs"
CACHE_DIRECTORY = ".cache"


# =============================================================================
# UI CONFIGURATION
# =============================================================================
TERMINAL_MIN_WIDTH = 60
TERMINAL_MAX_WIDTH = 120
DASHBOARD_REFRESH_RATE = 0.2  # seconds (5 FPS)
SPINNER_CHARS = ["|", "/", "-", "\\"]


# =============================================================================
# ENGINE PERFORMANCE TUNING
# =============================================================================
ENGINE_COMMIT_INTERVAL = 10  # Seconds between database commits
ENGINE_PROGRESS_UPDATE_INTERVAL = 50  # Items processed between progress updates
ENGINE_WORKER_CAPACITY_MULTIPLIER = 2  # Futures queue = workers * multiplier
ENGINE_QUEUE_POLL_SLEEP = 0.01  # Seconds between queue checks


# =============================================================================
# CONTROLLER SETTINGS
# =============================================================================
CONTROLLER_POLL_INTERVAL = 0.25  # Seconds between keyboard polls (60% less CPU than 0.1s)
CONTROLLER_PAUSE_CHECK_INTERVAL = 0.5  # Seconds between pause state checks


# =============================================================================
# ANSI COLOR CODES
# =============================================================================
class Color:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Text formatting
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"


# =============================================================================
# POWERSHELL CONFIGURATION
# =============================================================================
POWERSHELL_TIMEOUT = 2  # seconds for disk detection
POWERSHELL_DISK_QUERY = (
    "Get-PhysicalDisk | Where-Object {{$_.DeviceID -eq "
    "(Get-Partition -DriveLetter {drive_letter}).DiskNumber}} | "
    "Select-Object -ExpandProperty MediaType"
)


# =============================================================================
# ERROR MESSAGES
# =============================================================================
class ErrorMessage:
    """Standard error messages"""
    PATH_NOT_FOUND = "Directory not found: {path}"
    PATH_NOT_DIR = "Path is not a directory: {path}"
    PATH_EMPTY = "Path cannot be empty"
    CONFIG_LOAD_FAILED = "Failed to load configuration: {error}"
    CONFIG_SAVE_FAILED = "Failed to save configuration: {error}"
    DB_CONNECTION_FAILED = "Database connection failed: {error}"
    PERMISSION_DENIED = "Access denied: {path}"
    INVALID_CHOICE = "Invalid choice. Please select from: {options}"
    WORKER_COUNT_INVALID = "Worker count must be between {min} and {max}"


# =============================================================================
# SUCCESS MESSAGES
# =============================================================================
class SuccessMessage:
    """Standard success messages"""
    CONFIG_SAVED = "Configuration saved to {file}"
    CONFIG_LOADED = "Configuration loaded from {file}"
    SCAN_COMPLETE = "Scan complete: {scanned} folders processed"
    FOLDERS_DELETED = "{count} empty folders deleted"
    STATE_SAVED = "Progress saved: {scanned} folders scanned, {pending} pending"


# =============================================================================
# MENU LABELS
# =============================================================================
class MenuLabel:
    """Menu option labels"""
    NEW_SCAN = "New Scan"
    LOAD_RUN = "Load & Run"
    RESUME = "Resume Session"
    VIEW_CACHE = "View Cache"
    HELP = "Help"
    ABOUT = "About"
    QUIT = "Quit"
    
    MAIN_MENU_OPTIONS = [
        (1, NEW_SCAN, "Configure and run a new folder scan"),
        (2, LOAD_RUN, "Load saved config and execute immediately"),
        (3, RESUME, "Continue a previously interrupted scan"),
        (4, VIEW_CACHE, "Show previous scan sessions and statistics"),
        (5, HELP, "Comprehensive guide to all options"),
        (6, ABOUT, "Application info, version, and features"),
    ]
