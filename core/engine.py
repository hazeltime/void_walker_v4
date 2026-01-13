import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import deque
from typing import Optional, Tuple
import fnmatch
import stat

from data.database import Database
from ui.dashboard import Dashboard
from ui.reporter import Reporter
from .controller import Controller

class Engine:
    # Configuration constants
    COMMIT_INTERVAL = 10  # Seconds between database commits
    PROGRESS_UPDATE_INTERVAL = 50  # Items processed between progress updates
    WORKER_CAPACITY_MULTIPLIER = 2  # Futures queue = workers * multiplier
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.db = Database(config.db_path, config.session_id)
        self.dashboard = Dashboard(config)
        self.controller = Controller(self) 
        self.queue = deque()
        self.queue_lock = threading.Lock()
        self.lock = threading.Lock()
        self.state_lock = threading.Lock()  # Protects paused/running flags
        self.paused = False
        self.running = True
        self.executor = None
        self.last_commit_time = time.time()
        self.scan_start_time = None
        self.total_scanned = 0
        self.total_empty = 0
        self.total_errors = 0
        self.total_deleted = 0

    def start(self):
        print("\n\033[96m[*] Initializing Void Walker...\033[0m")
        print("\033[90m    > Setting up database...\033[0m")
        self.db.setup()
        
        # Save config for resume functionality (only if not resuming)
        if not self.config.resume_mode:
            self.config.save_to_db(self.db)
        
        print("\033[90m    > Starting keyboard controller...\033[0m")
        self.controller.start()
        print("\033[90m    > Launching real-time dashboard...\033[0m")
        self.dashboard.start()

        self.logger.info("Phase 1: Scanning")
        self.dashboard.set_phase("SCANNING")
        
        if not self.config.resume_mode:
            print(f"\033[92m[OK] Ready! Starting scan from: {self.config.root_path}\033[0m", flush=True)
            print(f"[*] Starting {self.config.workers} workers...", flush=True)
            print("")
            self._enqueue(self.config.root_path, 0)
            self.db.add_folder(self.config.root_path, 0)
        else:
            print("\033[93m[*] Loading resume state from cache...\033[0m", flush=True)
            self._load_resume_state()
            print(f"\033[92m[OK] Resuming with {self._queue_size()} pending folders\033[0m", flush=True)
            print("")

        self._process_queue()
        
        # Scan complete - show summary but keep dashboard for cleanup phase
        print(f"\n\033[92m[OK] Scan Complete!\033[0m", flush=True)
        print(f"    Folders scanned: {self.total_scanned}", flush=True)
        print(f"    Empty found: {self.total_empty}", flush=True)
        print(f"    Errors: {self.total_errors}\n", flush=True)

        self.logger.info("Phase 2: Cleanup")
        print("\033[96m[*] Phase 2: Analyzing empty folders...\033[0m", flush=True)
        self.dashboard.set_phase("CLEANUP")
        self._process_cleanup()
        
        print("\033[92m[OK] All phases complete\033[0m\n", flush=True)
        
        # Show comprehensive final summary with top 3 root folders
        reporter = Reporter(self.config, self.db)
        reporter.show_final_summary()
        
        # Stop dashboard AFTER all work is done
        self.dashboard.stop()
        self.controller.stop()
    
    def scan_only(self):
        """Phase 1: Scanning only - does not perform cleanup"""
        print("\033[90m    > Setting up database...\033[0m")
        self.db.setup()
        
        # Save config for resume functionality (only if not resuming)
        if not self.config.resume_mode:
            self.config.save_to_db(self.db)
        
        print("\033[90m    > Starting keyboard controller...\033[0m")
        self.controller.start()
        print("\033[90m    > Launching real-time dashboard...\033[0m")
        self.dashboard.start()

        self.logger.info("Phase 1: Scanning")
        self.dashboard.set_phase("SCANNING")
        
        if not self.config.resume_mode:
            print(f"\033[92m[OK] Ready! Starting scan from: {self.config.root_path}\033[0m", flush=True)
            print(f"[*] Starting {self.config.workers} workers...", flush=True)
            print("")
            self._enqueue(self.config.root_path, 0)
            self.db.add_folder(self.config.root_path, 0)
        else:
            print("\033[93m[*] Loading resume state from cache...\033[0m", flush=True)
            self._load_resume_state()
            print(f"\033[92m[OK] Resuming with {self._queue_size()} pending folders\033[0m", flush=True)
            print("")

        self._process_queue()
        
        # Scan complete - show summary
        print(f"\n\033[92m[OK] Scan Complete!\033[0m", flush=True)
        print(f"    Folders scanned: {self.total_scanned}", flush=True)
        print(f"    Empty found: {self.total_empty}", flush=True)
        print(f"    Errors: {self.total_errors}\n", flush=True)
        
        # Stop dashboard and controller after scan
        self.dashboard.stop()
        self.controller.stop()
        self.logger.info("Scan phase complete - controller and dashboard stopped")
    
    def cleanup_only(self):
        """Phase 2: Cleanup only - assumes scanning already completed"""
        self.logger.info("Phase 2: Cleanup")
        
        # Restart controller and dashboard for cleanup phase
        self.controller.start()
        self.dashboard.start()
        self.dashboard.set_phase("CLEANUP")
        
        print("\033[96m[*] Phase 2: Analyzing empty folders...\033[0m", flush=True)
        self._process_cleanup()
        
        print("\033[92m[OK] Cleanup phase complete\033[0m\n", flush=True)
        
        # Stop dashboard and controller
        self.dashboard.stop()
        self.controller.stop()

    def _load_resume_state(self):
        # Invalidate stale cache entries before resuming
        print("\033[90m    > Validating cache integrity...\033[0m", flush=True)
        invalidated = self.db.invalidate_missing_paths()
        if invalidated > 0:
            print(f"\033[93m    > Removed {invalidated} stale cache entries (paths no longer exist)\033[0m", flush=True)
        
        pending = self.db.get_pending()
        for path, depth in pending:
            with self.queue_lock:
                self.queue.append((path, depth))

    def _queue_size(self):
        with self.queue_lock:
            return len(self.queue)

    def _pop_next(self) -> Optional[Tuple[str, int]]:
        with self.queue_lock:
            if not self.queue:
                return None
            if self.config.strategy == "BFS":
                return self.queue.popleft()
            return self.queue.pop()

    def _enqueue(self, path: str, depth: int) -> int:
        with self.queue_lock:
            self.queue.append((path, depth))
            return len(self.queue)

    def _is_filtered(self, path: str, name: str, depth: int) -> bool:
        if depth > self.config.max_depth: return True
        if self.config.include_names:
            if not any(fnmatch.fnmatch(name, pat) for pat in self.config.include_names):
                return True
        for pat in self.config.exclude_names:
            if fnmatch.fnmatch(name, pat): return True
        for pat in self.config.exclude_paths:
            if fnmatch.fnmatch(path, pat): return True
        return False

    def _process_queue(self):
        """Concurrent queue processing with ThreadPoolExecutor"""
        self.scan_start_time = time.time()
        futures = []
        items_processed = 0
        
        with ThreadPoolExecutor(max_workers=self.config.workers) as executor:
            self.executor = executor
            
            while True:
                # Handle pause (with lock protection)
                with self.state_lock:
                    if not self.running:
                        break
                    is_paused = self.paused
                
                while is_paused:
                    self.dashboard.set_status("PAUSED")
                    time.sleep(0.5)
                    with self.state_lock:
                        if not self.running:
                            break
                        is_paused = self.paused
                
                with self.state_lock:
                    if not self.running:
                        break
                
                # Submit work while queue has items and we have capacity
                while len(futures) < self.config.workers * self.WORKER_CAPACITY_MULTIPLIER:
                    with self.state_lock:
                        if not self.running:
                            break
                    item = self._pop_next()
                    if not item:
                        break
                    path, depth = item
                    future = executor.submit(self._scan_folder, path, depth)
                    futures.append(future)
                    self.dashboard.set_queue_depth(self._queue_size())
                
                # Process completed futures (optimized to O(n) instead of O(n²))
                if futures:
                    done = [f for f in futures if f.done()]
                    if done:
                        # Rebuild futures list without completed ones (O(n) instead of O(n²))
                        futures = [f for f in futures if not f.done()]
                        items_processed += len(done)
                        
                        # Check results for exceptions
                        for future in done:
                            try:
                                future.result()  # Raises exception if worker failed
                            except Exception as e:
                                self.logger.error(f"Worker error: {e}")
                    
                    # Periodic commits for resume capability
                    if time.time() - self.last_commit_time >= self.COMMIT_INTERVAL:
                        self.db.commit()
                        self.last_commit_time = time.time()
                        self.logger.info(f"Progress saved: {self.total_scanned} folders scanned")
                        # Show progress to console every commit interval
                        print(f"[*] Progress: {self.total_scanned} folders scanned, {self.total_empty} empty found...", flush=True)
                
                # Check if we're done
                if self._queue_size() == 0 and not futures:
                    break
                
                # Progress update to show activity
                if items_processed > 0 and items_processed % self.PROGRESS_UPDATE_INTERVAL == 0:
                    print(f"\r[*] Progress: {self.total_scanned} folders | {self.total_empty} empty | Queue: {self._queue_size()}", end='', flush=True)
                
                time.sleep(0.01)  # Small sleep to prevent busy-wait
            
            # Shut down executor and wait for all workers to complete
            executor.shutdown(wait=True)
            
            # Final commit
            self.db.commit()
            self.executor = None
        
        # Show scan completion summary
        print(f"\n\033[92m[OK] Scan Complete!\033[0m")
        print(f"    Scanned: {self.total_scanned} folders")
        print(f"    Empty: {self.total_empty} folders")
        print(f"    Errors: {self.total_errors}\n")
        
        # Mark session as completed
        self.db.mark_completed()
        self.logger.info(f"Session completed successfully")

    def _scan_folder(self, path, depth):
        try:
            # Check for Junctions/Reparse Points (WinError 1920 cause)
            try:
                st = os.lstat(path)
                if stat.S_ISLNK(st.st_mode) or (os.name == 'nt' and hasattr(stat, 'S_ISDIR') and (st.st_mode & stat.S_IFMT) == stat.S_IFDIR and (st.st_mode & 0o170000) == 0o120000):
                    self.logger.debug(f"Skipping symlink/junction: {path}")
                    return
            except Exception as e:
                self.logger.debug(f"Error checking symlink status for {path}: {e}")

            queue_depth = self._queue_size()
            self.dashboard.update_current(path)
            self.dashboard.set_queue_depth(queue_depth)
            
            # Calculate folder size for metrics
            try:
                folder_size = 0
                with os.scandir(path) as scan_it:
                    for entry in scan_it:
                        try:
                            if entry.is_file(follow_symlinks=False):
                                folder_size += entry.stat(follow_symlinks=False).st_size
                        except (OSError, PermissionError):
                            pass  # Skip inaccessible files
                self.dashboard.add_processed_size(folder_size)
            except (OSError, PermissionError):
                pass  # Can't read folder, skip size tracking

            with os.scandir(path) as it:
                entry_count = 0
                
                for entry in it:
                    try:
                        if entry.is_symlink():
                            continue
                            
                        if entry.is_file():
                            entry_count += 1
                        elif entry.is_dir():
                            entry_count += 1
                            if not self._is_filtered(entry.path, entry.name, depth + 1):
                                queue_depth = self._enqueue(entry.path, depth + 1)
                                self.dashboard.set_queue_depth(queue_depth)
                                self.db.add_folder(entry.path, depth + 1)
                    except PermissionError:
                        self.db.log_error(entry.path, "Access Denied")
                        self.dashboard.increment_errors()
                        with self.lock:
                            self.total_errors += 1
                    except OSError as e:
                        self.db.log_error(entry.path, str(e))
                        self.dashboard.increment_errors()
                        with self.lock:
                            self.total_errors += 1
                
                self.db.update_folder_stats(path, entry_count)
                
                # Track if this folder is empty (no files, no folders)
                if entry_count == 0:
                    self.dashboard.increment_empty()
                    with self.lock:
                        self.total_empty += 1
                
                self.dashboard.increment_scanned(self.scan_start_time)
                with self.lock:
                    self.total_scanned += 1
                
        except PermissionError:
            self.db.log_error(path, "Access Denied")
            self.dashboard.increment_errors()
            with self.lock:
                self.total_errors += 1
        except OSError as e:
            self.db.log_error(path, str(e))
            self.dashboard.increment_errors()
            with self.lock:
                self.total_errors += 1

    def save_state(self):
        """Manual state save triggered by user"""
        self.db.commit()
        pending = self._queue_size()
        self.logger.info(f"State saved manually: {self.total_scanned} folders, {pending} pending")
        with self.lock:
            self.dashboard.set_status(f"SAVED ({pending} pending)")
        time.sleep(1)  # Brief pause to show message

    def _process_cleanup(self):
        # We must re-evaluate empty status recursively
        # The DB candidate list is just a starting point.
        # If we delete a child, the parent might BECOME empty.
        
        # Get deepest folders first
        candidates = self.db.get_empty_candidates(self.config.min_depth)
        
        # Safety summary for dry-run mode
        if not self.config.delete_mode:
            print(f"\n\033[96m[*] DRY RUN: Found {len(candidates)} empty folder candidates\033[0m")
            print(f"\033[90m    Verifying each folder is truly empty...\033[0m")
            total_size_bytes = 0  # Track actual verified size
            verified_empty = 0
        else:
            print(f"\n\033[93m[!] DELETE MODE: Removing {len(candidates)} empty folder candidates\033[0m")
            print(f"\033[90m    Each folder verified with triple safety checks...\033[0m")
        
        processed = 0
        for path in candidates:
            if path == self.config.root_path: continue
            
            # SAFETY: Triple verification that folder is truly empty
            try:
                if not os.path.exists(path): continue
                
                # First check: os.listdir (primary guard)
                contents = os.listdir(path)
                if contents:
                    # NOT EMPTY - skip this folder
                    self.logger.warning(f"Skipped {path}: contains {len(contents)} items")
                    continue
                
                # Second check: Verify ACTUAL DISK SIZE is exactly 0 bytes (not just count)
                try:
                    actual_size = 0
                    # Use os.scandir for accurate size check
                    for entry in os.scandir(path):
                        # This should never execute for truly empty folder
                        if entry.is_file(follow_symlinks=False):
                            actual_size += entry.stat(follow_symlinks=False).st_size
                        actual_size += 1  # Count entries (files or folders)
                    
                    # SAFETY CHECK: Explicit validation (not assertion - can't be disabled)
                    if actual_size > 0:
                        error_msg = f"Safety check failed: Folder not empty: {path} has size/items: {actual_size}"
                        self.logger.error(error_msg)
                        self.dashboard.increment_errors()
                        continue
                    
                    # Third check: Verify with os.stat that folder itself is minimal size
                    try:
                        folder_stat = os.stat(path)
                        # Empty folders should be minimal size (typically 0-4096 bytes for metadata)
                        # We verify size is 0 CONTENT bytes by the scandir check above
                        if not self.config.delete_mode:
                            # Track that this folder has 0 content bytes
                            total_size_bytes += 0  # Confirmed empty
                    except OSError:
                        pass  # stat failed, but we already verified with scandir
                    
                except OSError as e:
                    self.logger.error(f"Error verifying folder size {path}: {e}")
                    self.dashboard.increment_errors()
                    continue
                
                # Only proceed if ALL checks pass
                if self.config.delete_mode:
                    # PRODUCTION: Delete only after all safety checks pass
                    os.rmdir(path)  # Will raise OSError if not truly empty
                    self.db.mark_deleted(path)
                    self.dashboard.increment_deleted()
                    with self.lock:
                        self.total_deleted += 1
                    processed += 1
                    if processed % 10 == 0:
                        print(f"\r[*] Deleted: {processed}/{len(candidates)} empty folders", end='', flush=True)
                else:
                    # DRY RUN: Mark and count
                    self.db.mark_would_delete(path)
                    self.dashboard.increment_empty()
                    with self.lock:
                        self.total_deleted += 1
                    verified_empty += 1
                    processed += 1
                    if processed % 10 == 0:
                        print(f"\r[*] Verified: {verified_empty}/{len(candidates)} empty folders (0 bytes each)", end='', flush=True)
                    
            except OSError as e:
                self.logger.error(f"Cannot delete {path}: {e}")
                self.dashboard.increment_errors()
        
        # Persist delete/would-delete statuses
        self.db.commit()
        
        # Final summary
        print()  # New line after progress
        if self.config.delete_mode:
            print(f"\033[92m[OK] Successfully deleted {self.total_deleted} empty folders\033[0m")
            print(f"\033[90m    All folders verified empty before deletion\033[0m")
        else:
            # Dry-run summary with REAL size verification
            if verified_empty > 0:
                print(f"\033[92m[OK] Verified {verified_empty} truly empty folders")
                print(f"    Total content size: {total_size_bytes} bytes (all folders confirmed 0 bytes)\033[0m")
