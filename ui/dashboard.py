import sys
import shutil
import time
import threading
from datetime import timedelta

class Dashboard:
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
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)        # Clear dashboard area and move cursor down
        print("\n" * 5, end="", flush=True)
    def update_current(self, path):
        with self.lock:
            self.current_path = path

    def set_status(self, msg):
        with self.lock:
            self.status = msg
            
    def set_phase(self, phase):
        with self.lock:
            self.phase = phase

    def _loop(self):
        spin = ["|", "/", "-", "\\"]
        i = 0
        first_run = True
        
        while self.active:
            try:
                cols = shutil.get_terminal_size().columns
            except:
                cols = 120
            
            s = spin[i % 4]
            
            with self.lock:
                path = self.current_path
                rate = self.stats.get('scan_rate', 0)
                scanned = self.stats.get('scanned', 0)
                errors = self.stats.get('errors', 0)
                queue = self.stats.get('queue_depth', 0)
                empty = self.stats.get('empty', 0)
                deleted = self.stats.get('deleted', 0)
            
            # Truncate path if too long
            max_path_len = max(40, cols - 20)
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
                # Move cursor up 4 lines and clear
                sys.stdout.write("\033[4A")  # Move up 4 lines
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
            time.sleep(0.2)
        
        # Final newline for clean exit
        sys.stdout.write("\n")
