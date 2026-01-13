import sys
import shutil
import time
import threading
from datetime import timedelta

class Dashboard:
    # Display constants
    SPINNER_CHARS = ["|", "/", "-", "\\"]
    DEFAULT_TERMINAL_WIDTH = 120
    MIN_PATH_LENGTH = 40
    DASHBOARD_LINES = 4  # Number of lines used by dashboard display
    UPDATE_INTERVAL = 0.2  # Seconds between dashboard refreshes
    
    def __init__(self, config):
        self.config = config
        self.active = False
        self.lock = threading.Lock()
        self.current_path = "Initializing..."
        self.status = "STARTING"
        self.phase = "INIT"
        
        # Enhanced metrics
        self.stats = {
            "scanned": 0,
            "empty": 0,
            "deleted": 0,
            "errors": 0,
            "scan_rate": 0.0,
            "queue_depth": 0,
            "active_workers": 0
        }
        self.start_time = time.time()

    def start(self):
        self.active = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.active = False
        if hasattr(self, 'thread') and self.thread is not None:
            self.thread.join(timeout=1.0)
            # Verify thread actually stopped
            if self.thread.is_alive():
                print("\n[!] Warning: Dashboard thread did not stop cleanly", file=sys.stderr)
                # Thread will be terminated when program exits (daemon=True)
        # Clear dashboard area - move cursor to start of dashboard lines and clear
        sys.stdout.write(f"\033[{self.DASHBOARD_LINES}A")  # Move up N lines
        sys.stdout.write("\033[J")   # Clear from cursor to end
        sys.stdout.write("\n")       # Add newline for clean separation
        sys.stdout.flush()
    def update_current(self, path):
        with self.lock:
            self.current_path = path

    def set_status(self, msg):
        with self.lock:
            self.status = msg
            
    def set_phase(self, phase):
        with self.lock:
            self.phase = phase
    
    def increment_scanned(self, scan_start_time):
        """Thread-safe increment of scanned counter with rate calculation"""
        with self.lock:
            self.stats['scanned'] += 1
            elapsed = time.time() - scan_start_time
            if elapsed > 0:
                self.stats['scan_rate'] = self.stats['scanned'] / elapsed
    
    def increment_empty(self):
        """Thread-safe increment of empty folder counter"""
        with self.lock:
            self.stats['empty'] += 1
    
    def increment_errors(self):
        """Thread-safe increment of error counter"""
        with self.lock:
            self.stats['errors'] += 1
    
    def increment_deleted(self):
        """Thread-safe increment of deleted counter"""
        with self.lock:
            self.stats['deleted'] += 1
    
    def set_queue_depth(self, depth):
        """Thread-safe update of queue depth"""
        with self.lock:
            self.stats['queue_depth'] = depth

    def _loop(self):
        i = 0
        first_run = True
        
        while self.active:
            try:
                cols = shutil.get_terminal_size().columns
            except OSError:
                cols = self.DEFAULT_TERMINAL_WIDTH
            
            s = self.SPINNER_CHARS[i % len(self.SPINNER_CHARS)]
            
            with self.lock:
                path = self.current_path
                rate = self.stats.get('scan_rate', 0)
                scanned = self.stats.get('scanned', 0)
                errors = self.stats.get('errors', 0)
                queue = self.stats.get('queue_depth', 0)
                empty = self.stats.get('empty', 0)
                deleted = self.stats.get('deleted', 0)
            
            # Truncate path if too long
            max_path_len = max(self.MIN_PATH_LENGTH, cols - 20)
            if len(path) > max_path_len:
                path = "..." + path[-(max_path_len-3):]
            
            # Calculate runtime
            elapsed = time.time() - self.start_time
            elapsed_str = str(timedelta(seconds=int(elapsed)))
            
            # Build output lines
            line1 = f"[{s}] {self.phase} | {self.status} | Workers: {self.config.workers}"
            line2 = f"{path}"
            line3 = f"Scanned: {scanned} | Rate: {rate:.1f}/s | Queue: {queue} | Empty: {empty} | Deleted: {deleted} | Errors: {errors} | Time: {elapsed_str}"
            line4 = "-" * min(60, cols)
            
            # Clear and rewrite (move cursor up on subsequent runs)
            if not first_run:
                # Move cursor up and clear
                sys.stdout.write(f"\033[{self.DASHBOARD_LINES}A")  # Move up N lines
                sys.stdout.write("\033[J")   # Clear from cursor to end of screen
            else:
                first_run = False
            
            # Write all lines
            sys.stdout.write(line1 + "\n")
            sys.stdout.write(line2 + "\n")
            sys.stdout.write(line3 + "\n")
            sys.stdout.write(line4 + "\n")
            sys.stdout.flush()
            
            i += 1
            time.sleep(self.UPDATE_INTERVAL)
        
        # Final newline for clean exit
        sys.stdout.write("\n")
