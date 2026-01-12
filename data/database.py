import sqlite3
import json

class Database:
    def __init__(self, db_path, session_id):
        self.path = db_path
        self.session_id = session_id
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def setup(self):
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
        self.cursor.execute("INSERT OR IGNORE INTO sessions (id, timestamp) VALUES (?, datetime('now'))", (self.session_id,))
        self.conn.commit()
        
        # Count existing sessions for user info
        self.cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = self.cursor.fetchone()[0]
        print(f"\033[90m       Database ready ({total_sessions} total sessions)\033[0m")

    def add_folder(self, path, depth):
        try:
            self.cursor.execute(
                "INSERT OR IGNORE INTO folders (path, session_id, depth) VALUES (?, ?, ?)", 
                (path, self.session_id, depth)
            )
        except: pass

    def update_folder_stats(self, path, file_count):
        self.cursor.execute(
            "UPDATE folders SET file_count=?, status='SCANNED' WHERE path=? AND session_id=?", 
            (file_count, path, self.session_id)
        )
        # Commit periodically in engine, or here
        
    def log_error(self, path, msg):
        self.cursor.execute(
            "UPDATE folders SET status='ERROR', error_msg=? WHERE path=? AND session_id=?", 
            (msg, path, self.session_id)
        )

    def mark_deleted(self, path):
        self.cursor.execute("UPDATE folders SET status='DELETED' WHERE path=? AND session_id=?", (path, self.session_id))

    def mark_would_delete(self, path):
        self.cursor.execute("UPDATE folders SET status='WOULD_DELETE' WHERE path=? AND session_id=?", (path, self.session_id))

    def get_pending(self):
        self.cursor.execute("SELECT path, depth FROM folders WHERE status='PENDING' AND session_id=? ORDER BY depth ASC", (self.session_id,))
        return self.cursor.fetchall()

    def get_empty_candidates(self, min_depth):
        # We want folders processed, with 0 files, ordered deep to shallow
        self.cursor.execute("""
            SELECT path FROM folders 
            WHERE session_id=? AND status='SCANNED' AND file_count=0 AND depth >= ?
            ORDER BY depth DESC
        """, (self.session_id, min_depth))
        return [r[0] for r in self.cursor.fetchall()]

    def get_errors(self):
        self.cursor.execute("SELECT path, error_msg FROM folders WHERE status='ERROR' AND session_id=?", (self.session_id,))
        return self.cursor.fetchall()

    def save_config(self, config_dict, root_path):
        """Save session configuration for resume functionality"""
        self.cursor.execute(
            "UPDATE sessions SET config=?, root_path=? WHERE id=?",
            (json.dumps(config_dict), root_path, self.session_id)
        )
        self.conn.commit()

    def mark_completed(self):
        """Mark session as completed"""
        self.cursor.execute(
            "UPDATE sessions SET completed=1 WHERE id=?",
            (self.session_id,)
        )
        self.conn.commit()

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
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()
