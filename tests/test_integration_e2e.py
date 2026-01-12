"""
End-to-end integration tests with mock filesystem
SAFETY: All tests use dry_run mode only - no actual deletions
"""
import unittest
import os
import sys
import tempfile
import shutil
import sqlite3
from pathlib import Path
from io import StringIO

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config
from core.engine import Engine
from data.database import Database
from utils.logger import setup_logger
import argparse


class TestEndToEndDryRun(unittest.TestCase):
    """End-to-end tests in DRY RUN mode only (safe, no deletions)"""
    
    def setUp(self):
        """Create mock folder structure and suppress console output"""
        # Suppress stdout/stderr to avoid Unicode errors
        self.held_stdout = sys.stdout
        self.held_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        
        # Create test structure
        # root/
        #   empty1/
        #   empty2/
        #   has_files/
        #     file1.txt
        #   nested/
        #     empty3/
        #     has_file/
        #       file2.txt
        
        self.root = Path(self.temp_dir) / "scan_root"
        self.root.mkdir()
        
        (self.root / "empty1").mkdir()
        (self.root / "empty2").mkdir()
        
        has_files = self.root / "has_files"
        has_files.mkdir()
        (has_files / "file1.txt").write_text("content")
        
        nested = self.root / "nested"
        nested.mkdir()
        (nested / "empty3").mkdir()
        
        has_file = nested / "has_file"
        has_file.mkdir()
        (has_file / "file2.txt").write_text("content")
        
        # SAFETY: Create folder with hidden file to test detection
        hidden_content = self.root / "has_hidden"
        hidden_content.mkdir()
        (hidden_content / ".hidden").write_text("hidden content")
    
    def tearDown(self):
        """Cleanup test files and restore stdout/stderr"""
        sys.stdout = self.held_stdout
        sys.stderr = self.held_stderr
        # SAFETY: Only delete temporary test directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_dry_run_identifies_empty_folders(self):
        """Test dry run mode identifies all empty folders WITHOUT deleting anything"""
        # SAFETY: Record initial state
        initial_folders = set()
        for root, dirs, files in os.walk(self.root):
            for d in dirs:
                initial_folders.add(os.path.join(root, d))
        
        args = argparse.Namespace(
            path=str(self.root),
            delete=False,  # CRITICAL: DRY RUN ONLY
            resume=False,
            disk="auto",
            strategy="bfs",
            workers=2,
            min_depth=0,
            max_depth=10,
            exclude_path=[],
            exclude_name=[],
            include_name=[]
        )
        
        config = Config(args)
        config.db_path = self.db_path
        logger = setup_logger(config.session_id)
        
        engine = Engine(config, logger)
        engine.start()
        
        # Check database for would_delete entries
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM folders WHERE status='WOULD_DELETE'")
        empty_count = cursor.fetchone()[0]
        conn.close()
        
        # Should find: empty1, empty2, nested/empty3
        self.assertEqual(empty_count, 3)
        
        # SAFETY VERIFICATION: ALL folders still exist (dry run doesn't delete)
        self.assertTrue((self.root / "empty1").exists(), "Dry run deleted empty1!")
        self.assertTrue((self.root / "empty2").exists(), "Dry run deleted empty2!")
        self.assertTrue((self.root / "nested" / "empty3").exists(), "Dry run deleted nested/empty3!")
        
        # Verify no folders were deleted
        final_folders = set()
        for root, dirs, files in os.walk(self.root):
            for d in dirs:
                final_folders.add(os.path.join(root, d))
        
        deleted = initial_folders - final_folders
        self.assertEqual(len(deleted), 0, f"Dry run deleted folders: {deleted}")
        
        # CRITICAL: Verify folders with content are NEVER marked for deletion
        cursor = conn.cursor()
        cursor.execute("SELECT path, file_count FROM folders WHERE status='WOULD_DELETE'")
        would_delete = cursor.fetchall()
        conn.close()
        
        for path, file_count in would_delete:
            self.assertEqual(file_count, 0, f"Marked non-empty folder for deletion: {path} has {file_count} files!")
            # Double-check physical state
            actual_contents = os.listdir(path) if os.path.exists(path) else []
            self.assertEqual(len(actual_contents), 0, f"Folder {path} has {len(actual_contents)} items!")
    
    def test_depth_filtering(self):
        """Test min/max depth filtering in dry run"""
        args = argparse.Namespace(
            path=str(self.root),
            delete=False,
            resume=False,
            disk="auto",
            strategy="bfs",
            workers=2,
            min_depth=2,  # Only delete depth 2+
            max_depth=10,
            exclude_path=[],
            exclude_name=[],
            include_name=[]
        )
        
        config = Config(args)
        config.db_path = self.db_path
        logger = setup_logger(config.session_id)
        
        engine = Engine(config, logger)
        engine.start()
        
        # Check candidates
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM folders WHERE status='WOULD_DELETE'")
        deleted = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Should only include nested/empty3 (depth 2)
        # Should NOT include empty1, empty2 (depth 1)
        self.assertEqual(len(deleted), 1)
        self.assertTrue(any("empty3" in p for p in deleted))
    
    def test_exclude_patterns(self):
        """Test folder exclusion patterns"""
        # Add excluded folder
        excluded = self.root / "excluded_dir"
        excluded.mkdir()
        
        args = argparse.Namespace(
            path=str(self.root),
            delete=False,
            resume=False,
            disk="auto",
            strategy="bfs",
            workers=2,
            min_depth=0,
            max_depth=10,
            exclude_path=[],
            exclude_name=["excluded_*"],
            include_name=[]
        )
        
        config = Config(args)
        config.db_path = self.db_path
        logger = setup_logger(config.session_id)
        
        engine = Engine(config, logger)
        engine.start()
        
        # Check that excluded_dir was not scanned
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM folders WHERE path LIKE ?", (f"%excluded_dir%",))
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 0)
    
    def test_worker_count_configuration(self):
        """Test different worker counts work correctly"""
        for workers in [1, 2, 4, 8]:
            with self.subTest(workers=workers):
                args = argparse.Namespace(
                    path=str(self.root),
                    delete=False,
                    resume=False,
                    disk="auto",
                    strategy="bfs",
                    workers=workers,
                    min_depth=0,
                    max_depth=10,
                    exclude_path=[],
                    exclude_name=[],
                    include_name=[]
                )
                
                config = Config(args)
                config.db_path = os.path.join(self.temp_dir, f"test_w{workers}.db")
                logger = setup_logger(f"test_{workers}")
                
                engine = Engine(config, logger)
                engine.start()
                
                # Verify scan completed
                conn = sqlite3.connect(config.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM folders WHERE status='SCANNED'")
                scanned = cursor.fetchone()[0]
                conn.close()
                
                self.assertGreater(scanned, 0)


class TestStrategySelection(unittest.TestCase):
    """Test scan strategy selection logic"""
    
    def setUp(self):
        """Suppress console output"""
        self.held_stdout = sys.stdout
        self.held_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
    
    def tearDown(self):
        """Restore stdout/stderr"""
        sys.stdout = self.held_stdout
        sys.stderr = self.held_stderr
    
    def test_bfs_strategy(self):
        """Test BFS strategy configuration"""
        args = argparse.Namespace(
            path="/test",
            delete=False,
            resume=False,
            disk="ssd",
            strategy="bfs",
            workers=0,
            min_depth=0,
            max_depth=100,
            exclude_path=[],
            exclude_name=[],
            include_name=[]
        )
        
        config = Config(args)
        self.assertEqual(config.strategy, "BFS")
        self.assertEqual(config.workers, 16)  # SSD default
    
    def test_dfs_strategy(self):
        """Test DFS strategy configuration"""
        args = argparse.Namespace(
            path="/test",
            delete=False,
            resume=False,
            disk="hdd",
            strategy="dfs",
            workers=0,
            min_depth=0,
            max_depth=100,
            exclude_path=[],
            exclude_name=[],
            include_name=[]
        )
        
        config = Config(args)
        self.assertEqual(config.strategy, "DFS")
        self.assertEqual(config.workers, 4)  # HDD default
    
    def test_auto_strategy_ssd(self):
        """Test auto strategy selects BFS for SSD"""
        args = argparse.Namespace(
            path="/test",
            delete=False,
            resume=False,
            disk="ssd",
            strategy="auto",
            workers=0,
            min_depth=0,
            max_depth=100,
            exclude_path=[],
            exclude_name=[],
            include_name=[]
        )
        
        config = Config(args)
        self.assertEqual(config.strategy, "BFS")
    
    def test_auto_strategy_hdd(self):
        """Test auto strategy selects DFS for HDD"""
        args = argparse.Namespace(
            path="/test",
            delete=False,
            resume=False,
            disk="hdd",
            strategy="auto",
            workers=0,
            min_depth=0,
            max_depth=100,
            exclude_path=[],
            exclude_name=[],
            include_name=[]
        )
        
        config = Config(args)
        self.assertEqual(config.strategy, "DFS")


if __name__ == '__main__':
    unittest.main()
