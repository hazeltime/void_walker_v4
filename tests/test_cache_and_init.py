"""
Test suite for cache error handling and initialization
"""
import unittest
import sqlite3
import os
import tempfile
import shutil
from data.database import Database
from config.settings import Config
import argparse


class TestCacheErrorHandling(unittest.TestCase):
    """Test database error handling"""
    
    def setUp(self):
        """Create temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        
    def tearDown(self):
        """Cleanup temporary files"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_database_setup_creates_tables(self):
        """Test that database setup creates required tables"""
        db = Database(self.db_path, "test_session")
        db.setup()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check sessions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
        self.assertIsNotNone(cursor.fetchone())
        
        # Check folders table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='folders'")
        self.assertIsNotNone(cursor.fetchone())
        
        conn.close()
    
    def test_empty_session_statistics(self):
        """Test stats retrieval with empty session"""
        db = Database(self.db_path, "empty_session")
        db.setup()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status='SCANNED' THEN 1 ELSE 0 END) as scanned,
                SUM(CASE WHEN status='PENDING' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status='ERROR' THEN 1 ELSE 0 END) as errors,
                SUM(CASE WHEN status='DELETED' THEN 1 ELSE 0 END) as deleted,
                SUM(CASE WHEN status='WOULD_DELETE' THEN 1 ELSE 0 END) as would_delete
            FROM folders WHERE session_id=?
        """, ("empty_session",))
        
        stats = cursor.fetchone()
        
        # Verify null coalescing works
        total = stats[0] or 0
        scanned = stats[1] or 0
        pending = stats[2] or 0
        
        self.assertEqual(total, 0)
        self.assertEqual(scanned, 0)
        self.assertEqual(pending, 0)
        
        conn.close()
    
    def test_add_and_retrieve_folders(self):
        """Test adding folders and retrieving pending list"""
        db = Database(self.db_path, "test_session")
        db.setup()
        
        db.add_folder("/test/path1", 0)
        db.add_folder("/test/path2", 1)
        db.conn.commit()
        
        pending = db.get_pending()
        self.assertEqual(len(pending), 2)
        self.assertEqual(pending[0][0], "/test/path1")
        self.assertEqual(pending[1][0], "/test/path2")
    
    def test_session_count(self):
        """Test that session count increments correctly"""
        db1 = Database(self.db_path, "session_1")
        db1.setup()
        
        db2 = Database(self.db_path, "session_2")
        db2.setup()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sessions")
        count = cursor.fetchone()[0]
        
        self.assertEqual(count, 2)
        conn.close()


class TestConfigInitialization(unittest.TestCase):
    """Test configuration initialization"""
    
    def test_config_default_workers(self):
        """Test worker count defaults based on disk type"""
        # SSD config
        args = argparse.Namespace(
            path="/test",
            delete=False,
            resume=False,
            disk="ssd",
            workers=0,
            min_depth=0,
            max_depth=100,
            exclude_path=[],
            exclude_name=[],
            include_name=[],
            strategy="auto"
        )
        
        config = Config(args)
        self.assertEqual(config.workers, 16)  # SSD default
    
    def test_config_manual_workers(self):
        """Test manual worker override"""
        args = argparse.Namespace(
            path="/test",
            delete=False,
            resume=False,
            disk="auto",
            workers=8,
            min_depth=0,
            max_depth=100,
            exclude_path=[],
            exclude_name=[],
            include_name=[],
            strategy="auto"
        )
        
        config = Config(args)
        self.assertEqual(config.workers, 8)  # Manual override
    
    def test_config_default_exclusions(self):
        """Test that default exclusions are always added"""
        args = argparse.Namespace(
            path="/test",
            delete=False,
            resume=False,
            disk="auto",
            workers=0,
            min_depth=0,
            max_depth=100,
            exclude_path=[],
            exclude_name=["temp"],
            include_name=[],
            strategy="auto"
        )
        
        config = Config(args)
        
        # Check default exclusions are present
        self.assertIn(".git", config.exclude_names)
        self.assertIn("$RECYCLE.BIN", config.exclude_names)
        self.assertIn("System Volume Information", config.exclude_names)
        self.assertIn("temp", config.exclude_names)  # User-provided


if __name__ == '__main__':
    unittest.main()
