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
            self.thread.join(timeout=1.0)

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
        while self.active:
            cols = shutil.get_terminal_size().columns
            
            s = spin[i % 4]
            path = self.current_path
            max_path_len = max(40, cols - 80)
            if len(path) > max_path_len:
                path = "..." + path[-(max_path_len-3):]
            
            # Calculate runtime and ETA
            elapsed = time.time() - self.start_time
            elapsed_str = str(timedelta(seconds=int(elapsed)))
            
            # Build status line with metrics
            with self.lock:
                rate = self.stats.get('scan_rate', 0)
                scanned = self.stats.get('scanned', 0)
                errors = self.stats.get('errors', 0)
                queue = self.stats.get('queue_depth', 0)
            
            # Main status line
            line1 = f"\r[{s}] {self.phase} | {self.status} | Workers: {self.config.workers}"
            
            # Metrics line
            line2 = f"\n{path}"
            line3 = f"\nScanned: {scanned} | Rate: {rate:.1f}/s | Queue: {queue} | Errors: {errors} | Time: {elapsed_str}"
            
            # Combine and fit to width
            full_output = line1 + line2 + line3
            
            # Move cursor up and clear lines
            sys.stdout.write(f"\r{' ' * (cols-1)}")
            sys.stdout.write("\r" + line1[:cols-1])
            sys.stdout.write(line2[:cols-1])
            sys.stdout.write(line3[:cols-1])
            sys.stdout.flush()
            
            i += 1
            time.sleep(0.2)
        
        sys.stdout.write("\n")
