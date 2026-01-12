import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque
import fnmatch
import stat
import re
from datetime import datetime

from data.database import Database
from ui.dashboard import Dashboard
from .controller import Controller

class Engine:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.db = Database(config.db_path, config.session_id)
        self.dashboard = Dashboard(config)
        self.controller = Controller(self) 
        self.queue = deque()
        self.lock = threading.Lock()
        self.paused = False
        self.running = True
        self.executor = None
        self.last_commit_time = time.time()
        self.commit_interval = 10  # seconds
        self.scan_start_time = None
        self.total_scanned = 0

    def start(self):
        print("\n\033[96m[*] Initializing Void Walker...\033[0m")
        print("\033[90m    → Setting up database...\033[0m")
        self.db.setup()
        print("\033[90m    → Starting keyboard controller...\033[0m")
        self.controller.start()
        print("\033[90m    → Launching real-time dashboard...\033[0m")
        self.dashboard.start()

        self.logger.info("Phase 1: Scanning")
        self.dashboard.set_phase("SCANNING")
        
        if not self.config.resume_mode:
            print(f"\033[92m[✓] Ready! Starting scan from: {self.config.root_path}\033[0m\n")
            self.queue.append((self.config.root_path, 0))
            self.db.add_folder(self.config.root_path, 0)
        else:
            print("\033[93m[*] Loading resume state from cache...\033[0m")
            self._load_resume_state()
            print(f"\033[92m[✓] Resuming with {len(self.queue)} pending folders\033[0m\n")

        self._process_queue()

        self.logger.info("Phase 2: Cleaning")
        self.dashboard.set_phase("CLEANING")
        self._process_cleanup()
        
        self.controller.stop()
        self.dashboard.stop()

    def _load_resume_state(self):
        pending = self.db.get_pending()
        for path, depth in pending:
            self.queue.append((path, depth))

    def _is_filtered(self, path, name, depth):
        if depth > self.config.max_depth: return True
        for pat in self.config.exclude_names:
            if fnmatch.fnmatch(name, pat): return True
        for pat in self.config.exclude_paths:
            if fnmatch.fnmatch(path, pat): return True
        return False

    def _process_queue(self):
        """Concurrent queue processing with ThreadPoolExecutor"""
        self.scan_start_time = time.time()
        futures = []
        
        with ThreadPoolExecutor(max_workers=self.config.workers) as executor:
            self.executor = executor
            
            while self.running:
                # Handle pause
                while self.paused and self.running:
                    self.dashboard.set_status("PAUSED")
                    time.sleep(0.5)
                
                if not self.running:
                    break
                
                # Submit work while queue has items and we have capacity
                while len(futures) < self.config.workers * 2 and self.queue and self.running:
                    try:
                        if self.config.strategy == "BFS":
                            path, depth = self.queue.popleft()
                        else:
                            path, depth = self.queue.pop()
                        
                        future = executor.submit(self._scan_folder, path, depth)
                        futures.append(future)
                    except IndexError:
                        break
                
                # Process completed futures
                if futures:
                    done = [f for f in futures if f.done()]
                    for future in done:
                        futures.remove(future)
                        try:
                            future.result()  # Raises exception if worker failed
                        except Exception as e:
                            self.logger.error(f"Worker error: {e}")
                    
                    # Periodic commits for resume capability
                    if time.time() - self.last_commit_time >= self.commit_interval:
                        self.db.commit()
                        self.last_commit_time = time.time()
                        self.logger.info(f"Progress saved: {self.total_scanned} folders scanned")
                
                # Check if we're done
                if not self.queue and not futures:
                    break
                
                time.sleep(0.01)  # Small sleep to prevent busy-wait
            
            # Final commit
            self.db.commit()
            self.executor = None

    def _scan_folder(self, path, depth):
        try:
            # Check for Junctions/Reparse Points (WinError 1920 cause)
            try:
                st = os.lstat(path)
                if stat.S_ISLNK(st.st_mode) or (os.name == 'nt' and hasattr(stat, 'S_ISDIR') and (st.st_mode & stat.S_IFMT) == stat.S_IFDIR and (st.st_mode & 0o170000) == 0o120000):
                    return
            except:
                pass

            with self.lock:
                self.dashboard.update_current(path)
                self.dashboard.stats['queue_depth'] = len(self.queue)

            with os.scandir(path) as it:
                file_count = 0
                
                for entry in it:
                    try:
                        if entry.is_symlink():
                            continue
                            
                        if entry.is_file():
                            file_count += 1
                        elif entry.is_dir():
                            if not self._is_filtered(entry.path, entry.name, depth + 1):
                                with self.lock:
                                    self.queue.append((entry.path, depth + 1))
                                self.db.add_folder(entry.path, depth + 1)
                    except PermissionError:
                        pass
                
                self.db.update_folder_stats(path, file_count)
                
                with self.lock:
                    self.dashboard.stats['scanned'] += 1
                    self.total_scanned += 1
                    # Update scan rate
                    elapsed = time.time() - self.scan_start_time
                    if elapsed > 0:
                        self.dashboard.stats['scan_rate'] = self.total_scanned / elapsed
                
        except PermissionError:
            self.db.log_error(path, "Access Denied")
            with self.lock:
                self.dashboard.stats['errors'] += 1
        except OSError as e:
            self.db.log_error(path, str(e))
            with self.lock:
                self.dashboard.stats['errors'] += 1

    def save_state(self):
        """Manual state save triggered by user"""
        self.db.commit()
        self.logger.info(f"State saved manually: {self.total_scanned} folders, {len(self.queue)} pending")
        with self.lock:
            self.dashboard.set_status(f"SAVED ({len(self.queue)} pending)")
        time.sleep(1)  # Brief pause to show message

    def _process_cleanup(self):
        # We must re-evaluate empty status recursively
        # The DB candidate list is just a starting point.
        # If we delete a child, the parent might BECOME empty.
        
        # Get deepest folders first
        candidates = self.db.get_empty_candidates(self.config.min_depth)
        
        for path in candidates:
            if path == self.config.root_path: continue
            
            # Verification: Physically Empty?
            try:
                if not os.path.exists(path): continue
                
                if not os.listdir(path):
                    if self.config.delete_mode:
                        os.rmdir(path)
                        self.db.mark_deleted(path)
                        with self.lock: self.dashboard.stats['deleted'] += 1
                    else:
                        self.db.mark_would_delete(path)
                        with self.lock: self.dashboard.stats['empty'] += 1
            except OSError:
                with self.lock: self.dashboard.stats['errors'] += 1
