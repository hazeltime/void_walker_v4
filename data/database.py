import sqlite3
import json
import threading
import sys

class Database:
    def __init__(self, db_path, session_id):
        self.path = db_path
        self.session_id = session_id
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()
        self.error_count = 0
        self.last_error = None

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

    def add_folder(self, path, depth):
        try:
            with self.lock:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO folders (path, session_id, depth) VALUES (?, ?, ?)",
                    (path, self.session_id, depth)
                )
            return True
        except sqlite3.Error as e:
            self._record_error("add_folder", e, path)
            return False
        except Exception as e:
            self._record_error("add_folder", e, path)
            return False

    def update_folder_stats(self, path, file_count):
        try:
            with self.lock:
                self.cursor.execute(
                    "UPDATE folders SET file_count=?, status='SCANNED' WHERE path=? AND session_id=?",
                    (file_count, path, self.session_id)
                )
        except sqlite3.Error as e:
            self._record_error("update_folder_stats", e, path)
        except Exception as e:
            self._record_error("update_folder_stats", e, path)
        # Commit periodically in engine, or here

    def log_error(self, path, msg):
        try:
            with self.lock:
                self.cursor.execute(
                    "UPDATE folders SET status='ERROR', error_msg=? WHERE path=? AND session_id=?",
                    (msg, path, self.session_id)
                )
        except sqlite3.Error as e:
            self._record_error("log_error", e, path)
        except Exception as e:
            self._record_error("log_error", e, path)

    def mark_deleted(self, path):
        try:
            with self.lock:
                self.cursor.execute(
                    "UPDATE folders SET status='DELETED' WHERE path=? AND session_id=?",
                    (path, self.session_id)
                )
        except sqlite3.Error as e:
            self._record_error("mark_deleted", e, path)
        except Exception as e:
            self._record_error("mark_deleted", e, path)

    def mark_would_delete(self, path):
        try:
            with self.lock:
                self.cursor.execute(
                    "UPDATE folders SET status='WOULD_DELETE' WHERE path=? AND session_id=?",
                    (path, self.session_id)
                )
        except sqlite3.Error as e:
            self._record_error("mark_would_delete", e, path)
        except Exception as e:
            self._record_error("mark_would_delete", e, path)

    def get_pending(self):
        with self.lock:
            self.cursor.execute(
                "SELECT path, depth FROM folders WHERE status='PENDING' AND session_id=? ORDER BY depth ASC",
                (self.session_id,)
            )
            return self.cursor.fetchall()

    def get_empty_candidates(self, min_depth):
        # We want folders processed, with 0 files, ordered deep to shallow
        with self.lock:
            self.cursor.execute("""
                SELECT path FROM folders
                WHERE session_id=? AND status='SCANNED' AND file_count=0 AND depth >= ?
                ORDER BY depth DESC
            """, (self.session_id, min_depth))
            return [r[0] for r in self.cursor.fetchall()]

    def get_errors(self):
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
    def get_last_incomplete_session(db_path):
        """Get the most recent incomplete session for resume"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, config, root_path, timestamp
            FROM sessions
            WHERE completed=0
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        conn.close()

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
