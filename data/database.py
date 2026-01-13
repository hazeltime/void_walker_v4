import sqlite3
import json
import threading
import sys
from typing import Optional, List, Tuple, Dict, Any, Callable, TypeVar

# Type variable for generic database operation
T = TypeVar('T')

class Database:
    def __init__(self, db_path, session_id):
        self.path = db_path
        self.session_id = session_id
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()
        self.error_count = 0
        self.last_error = None
    
    def _execute_safe(self, operation_name: str, func: Callable[[], T], path: Optional[str] = None) -> Optional[T]:
        """Execute database operation with comprehensive error handling."""
        try:
            return func()
        except sqlite3.Error as e:
            self._record_error(operation_name, e, path)
            return None
        except Exception as e:
            self._record_error(operation_name, e, path)
            return None

    def _record_error(self, action, error, path=None):
        self.error_count += 1
        msg = f"[DB] {action} failed"
        if path:
            msg += f" ({path})"
        msg += f": {error}"
        self.last_error = msg
        try:
            print(msg, file=sys.stderr)
        except (OSError, IOError) as print_error:
            # If stderr print fails, try to log to a fallback error file
            try:
                import os
                error_log = os.path.join(os.getcwd(), "database_errors.log")
                with open(error_log, "a", encoding="utf-8") as f:
                    f.write(f"{msg}\n")
            except Exception:
                # Last resort: store in memory for retrieval
                if not hasattr(self, '_fallback_errors'):
                    self._fallback_errors = []
                self._fallback_errors.append(msg)

    def setup(self):
        with self.lock:
            self.cursor.execute("PRAGMA journal_mode=WAL;")

            # Table: Sessions
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    config TEXT,
                    root_path TEXT,
                    completed INTEGER DEFAULT 0
                )
            """)

            # Table: Folders (Linked to Session)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS folders (
                    path TEXT,
                    session_id TEXT,
                    depth INTEGER,
                    file_count INTEGER DEFAULT -1,
                    status TEXT DEFAULT 'PENDING',
                    error_msg TEXT,
                    PRIMARY KEY (path, session_id)
                )
            """)

            # Register Session
            self.cursor.execute(
                "INSERT OR IGNORE INTO sessions (id, timestamp) VALUES (?, datetime('now'))",
                (self.session_id,)
            )
            self.conn.commit()

            # Count existing sessions for user info
            self.cursor.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = self.cursor.fetchone()[0]
        print(f"\033[90m       Database ready ({total_sessions} total sessions)\033[0m")

    def add_folder(self, path: str, depth: int) -> bool:
        """Add folder to database with error handling."""
        def execute():
            with self.lock:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO folders (path, session_id, depth) VALUES (?, ?, ?)",
                    (path, self.session_id, depth)
                )
            return True
        
        result = self._execute_safe("add_folder", execute, path)
        return result if result is not None else False
    
    def add_folders_batch(self, folders: List[Tuple[str, int]]) -> int:
        """
        Add multiple folders in a single transaction for performance.
        
        Args:
            folders: List of (path, depth) tuples to insert
            
        Returns:
            Number of folders successfully inserted (0 if error)
        """
        if not folders:
            return 0
            
        def execute():
            with self.lock:
                # Prepare batch data with session_id
                batch_data = [(path, self.session_id, depth) for path, depth in folders]
                self.cursor.executemany(
                    "INSERT OR IGNORE INTO folders (path, session_id, depth) VALUES (?, ?, ?)",
                    batch_data
                )
                return len(folders)
        
        result = self._execute_safe("add_folders_batch", execute)
        return result if result is not None else 0

    def update_folder_stats(self, path, file_count):
        def execute():
            with self.lock:
                self.cursor.execute(
                    "UPDATE folders SET file_count=?, status='SCANNED' WHERE path=? AND session_id=?",
                    (file_count, path, self.session_id)
                )
        return self._execute_safe("update_folder_stats", execute, path)
        # Commit periodically in engine, or here

    def log_error(self, path, msg):
        def execute():
            with self.lock:
                self.cursor.execute(
                    "UPDATE folders SET status='ERROR', error_msg=? WHERE path=? AND session_id=?",
                    (msg, path, self.session_id)
                )
        return self._execute_safe("log_error", execute, path)

    def mark_deleted(self, path):
        def execute():
            with self.lock:
                self.cursor.execute(
                    "UPDATE folders SET status='DELETED' WHERE path=? AND session_id=?",
                    (path, self.session_id)
                )
        return self._execute_safe("mark_deleted", execute, path)

    def mark_would_delete(self, path):
        def execute():
            with self.lock:
                self.cursor.execute(
                    "UPDATE folders SET status='WOULD_DELETE' WHERE path=? AND session_id=?",
                    (path, self.session_id)
                )
        return self._execute_safe("mark_would_delete", execute, path)

    def get_pending(self) -> List[Tuple[str, int]]:
        with self.lock:
            self.cursor.execute(
                "SELECT path, depth FROM folders WHERE status='PENDING' AND session_id=? ORDER BY depth ASC",
                (self.session_id,)
            )
            return self.cursor.fetchall()

    def get_empty_candidates(self, min_depth: int) -> List[str]:
        # We want folders processed, with 0 files, ordered deep to shallow
        with self.lock:
            self.cursor.execute("""
                SELECT path FROM folders
                WHERE session_id=? AND status='SCANNED' AND file_count=0 AND depth >= ?
                ORDER BY depth DESC
            """, (self.session_id, min_depth))
            return [r[0] for r in self.cursor.fetchall()]

    def get_errors(self) -> List[Tuple[str, str]]:
        with self.lock:
            self.cursor.execute(
                "SELECT path, error_msg FROM folders WHERE status='ERROR' AND session_id=?",
                (self.session_id,)
            )
            return self.cursor.fetchall()

    def save_config(self, config_dict, root_path):
        """Save session configuration for resume functionality"""
        try:
            with self.lock:
                self.cursor.execute(
                    "UPDATE sessions SET config=?, root_path=? WHERE id=?",
                    (json.dumps(config_dict), root_path, self.session_id)
                )
                self.conn.commit()
        except sqlite3.Error as e:
            self._record_error("save_config", e, root_path)
        except Exception as e:
            self._record_error("save_config", e, root_path)

    def invalidate_missing_paths(self) -> int:
        """Remove cached entries for paths that no longer exist. Returns count of invalidated entries."""
        try:
            with self.lock:
                # Get all pending paths for this session
                self.cursor.execute(
                    "SELECT path FROM folders WHERE session_id=? AND status='PENDING'",
                    (self.session_id,)
                )
                pending_paths = [row[0] for row in self.cursor.fetchall()]
                
                # Check which paths no longer exist
                import os
                invalid_count = 0
                for path in pending_paths:
                    if not os.path.exists(path):
                        self.cursor.execute(
                            "DELETE FROM folders WHERE path=? AND session_id=?",
                            (path, self.session_id)
                        )
                        invalid_count += 1
                
                if invalid_count > 0:
                    self.conn.commit()
                return invalid_count
        except Exception as e:
            self._record_error("invalidate_missing_paths", e)
            return 0
    
    def mark_completed(self):
        """Mark session as completed"""
        try:
            with self.lock:
                self.cursor.execute(
                    "UPDATE sessions SET completed=1 WHERE id=?",
                    (self.session_id,)
                )
                self.conn.commit()
        except sqlite3.Error as e:
            self._record_error("mark_completed", e)
        except Exception as e:
            self._record_error("mark_completed", e)

    @staticmethod
    def get_last_incomplete_session(db_path: str) -> Optional[Dict[str, Any]]:
        """Get the most recent incomplete session for resume"""
        # Use context manager to ensure connection is closed even if exception occurs
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, config, root_path, timestamp
                FROM sessions
                WHERE completed=0
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            result = cursor.fetchone()

            if result:
                session_id, config_json, root_path, timestamp = result
                config = json.loads(config_json) if config_json else {}
                return {
                    'session_id': session_id,
                    'config': config,
                    'root_path': root_path,
                    'timestamp': timestamp
                }
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get session statistics including counts and sizes."""
        try:
            with self.lock:
                # Count total scanned and empty folders
                self.cursor.execute(
                    "SELECT COUNT(*) FROM folders WHERE session_id=? AND status='SCANNED'",
                    (self.session_id,)
                )
                total_scanned = self.cursor.fetchone()[0]
                
                self.cursor.execute(
                    "SELECT COUNT(*) FROM folders WHERE session_id=? AND status='SCANNED' AND file_count=0",
                    (self.session_id,)
                )
                total_empty = self.cursor.fetchone()[0]
                
                self.cursor.execute(
                    "SELECT COUNT(*) FROM folders WHERE session_id=? AND status='ERROR'",
                    (self.session_id,)
                )
                total_errors = self.cursor.fetchone()[0]
                
                return {
                    'total_scanned': total_scanned,
                    'total_empty': total_empty,
                    'total_errors': total_errors
                }
        except Exception as e:
            self._record_error("get_statistics", e)
            return {'total_scanned': 0, 'total_empty': 0, 'total_errors': 0}
    
    def get_top_root_folders(self, limit: int = 3) -> List[Tuple[str, int]]:
        """Get top N root folders with most empty subfolders.
        
        Returns:
            List of (root_folder, empty_count) tuples sorted by count descending.
        """
        try:
            with self.lock:
                # Get all empty folder paths and extract top-level directories
                self.cursor.execute("""
                    SELECT path FROM folders
                    WHERE session_id=? AND status='SCANNED' AND file_count=0
                """, (self.session_id,))
                
                empty_paths = [row[0] for row in self.cursor.fetchall()]
                
                # Count empty folders under each root (first level directory)
                import os
                from collections import Counter
                root_counts = Counter()
                
                for path in empty_paths:
                    # Extract root folder (first directory component)
                    parts = os.path.normpath(path).split(os.sep)
                    if len(parts) >= 2:
                        # For absolute paths like C:\Users\..., root is C:\Users
                        # For relative paths, root is first directory
                        if os.name == 'nt' and parts[0].endswith(':'):
                            # Windows: C:\folder1 -> root is C:\folder1
                            root = os.sep.join(parts[:2]) if len(parts) > 1 else parts[0]
                        else:
                            # Unix or relative: /folder1 or folder1
                            root = parts[0] if parts[0] else os.sep.join(parts[:2])
                        root_counts[root] += 1
                
                # Return top N
                return root_counts.most_common(limit)
        except Exception as e:
            self._record_error("get_top_root_folders", e)
            return []
    
    def commit(self):
        try:
            with self.lock:
                self.conn.commit()
        except sqlite3.Error as e:
            self._record_error("commit", e)
        except Exception as e:
            self._record_error("commit", e)

    def close(self):
        try:
            with self.lock:
                self.conn.commit()
                self.conn.close()
        except sqlite3.Error as e:
            self._record_error("close", e)
        except Exception as e:
            self._record_error("close", e)
