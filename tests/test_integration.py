"""
Integration tests with mock filesystem
"""
import unittest
import tempfile
import shutil
import os
from pathlib import Path


class MockFilesystem:
    """Create and manage mock filesystem for testing"""
    
    def __init__(self):
        self.root = None
        
    def create(self):
        """Create comprehensive test filesystem"""
        self.root = tempfile.mkdtemp(prefix="void_walker_test_")
        
        # Structure:
        # root/
        #   empty1/
        #   empty2/
        #   with_file/
        #     file.txt
        #   nested/
        #     empty_deep/
        #     with_file_deep/
        #       data.dat
        #   multi_level/
        #     level1/
        #       level2/
        #         level3/
        #           empty_deep_nested/
        
        # Empty folders
        os.makedirs(os.path.join(self.root, "empty1"))
        os.makedirs(os.path.join(self.root, "empty2"))
        
        # Folder with file
        with_file = os.path.join(self.root, "with_file")
        os.makedirs(with_file)
        Path(os.path.join(with_file, "file.txt")).write_text("content")
        
        # Nested structure
        empty_deep = os.path.join(self.root, "nested", "empty_deep")
        os.makedirs(empty_deep)
        
        with_file_deep = os.path.join(self.root, "nested", "with_file_deep")
        os.makedirs(with_file_deep)
        Path(os.path.join(with_file_deep, "data.dat")).write_bytes(b"binary")
        
        # Multi-level nesting
        deep_empty = os.path.join(self.root, "multi_level", "level1", "level2", "level3", "empty_deep_nested")
        os.makedirs(deep_empty)
        
        return self.root
    
    def cleanup(self):
        """Remove mock filesystem"""
        if self.root and os.path.exists(self.root):
            shutil.rmtree(self.root, ignore_errors=True)
    
    def get_empty_folders(self):
        """Return list of expected empty folders"""
        return [
            os.path.join(self.root, "empty1"),
            os.path.join(self.root, "empty2"),
            os.path.join(self.root, "nested", "empty_deep"),
            os.path.join(self.root, "multi_level", "level1", "level2", "level3", "empty_deep_nested"),
        ]


class TestEngineIntegration(unittest.TestCase):
    """Integration tests with real filesystem operations"""
    
    def setUp(self):
        """Setup mock filesystem"""
        self.fs = MockFilesystem()
        self.test_root = self.fs.create()
        
    def tearDown(self):
        """Cleanup mock filesystem"""
        self.fs.cleanup()
    
    def test_scan_detects_all_empty_folders(self):
        """Test engine scans and identifies all empty folders"""
        import argparse
        from config.settings import Config
        from core.engine import Engine
        from utils.logger import setup_logger
        
        args = argparse.Namespace(
            path=self.test_root,
            delete=False,
            resume=False,
            disk="auto",
            strategy="auto",
            workers=2,
            min_depth=0,
            max_depth=100,
            exclude_path=[],
            exclude_name=[],
            include_name=[]
        )
        
        config = Config(args)
        logger = setup_logger("test_integration")
        engine = Engine(config, logger)
        
        # Mock dashboard to avoid output
        engine.dashboard.active = False
        
        # Run scan
        engine.db.setup()
        engine.queue.append((self.test_root, 0))
        engine.db.add_folder(self.test_root, 0)
        engine._process_queue()
        
        # Get empty candidates
        empty_folders = engine.db.get_empty_candidates(0)
        expected_empty = self.fs.get_empty_folders()
        
        # Verify all expected empty folders were found
        self.assertEqual(len(empty_folders), len(expected_empty))
        for folder in expected_empty:
            self.assertIn(folder, empty_folders)
    
    def test_delete_mode_removes_empty_folders(self):
        """Test delete mode actually removes empty folders"""
        import argparse
        from config.settings import Config
        from core.engine import Engine
        from utils.logger import setup_logger
        
        args = argparse.Namespace(
            path=self.test_root,
            delete=True,
            resume=False,
            disk="auto",
            strategy="dfs",
            workers=2,
            min_depth=0,
            max_depth=100,
            exclude_path=[],
            exclude_name=[],
            include_name=[]
        )
        
        config = Config(args)
        logger = setup_logger("test_delete")
        engine = Engine(config, logger)
        
        engine.dashboard.active = False
        
        # Run full workflow
        engine.db.setup()
        engine.queue.append((self.test_root, 0))
        engine.db.add_folder(self.test_root, 0)
        engine._process_queue()
        engine._process_cleanup()
        
        # Verify empty folders were deleted
        expected_empty = self.fs.get_empty_folders()
        for folder in expected_empty:
            self.assertFalse(os.path.exists(folder), f"Folder should be deleted: {folder}")
    
    def test_depth_filtering(self):
        """Test min/max depth filtering"""
        import argparse
        from config.settings import Config
        from core.engine import Engine
        from utils.logger import setup_logger
        
        args = argparse.Namespace(
            path=self.test_root,
            delete=False,
            resume=False,
            disk="auto",
            strategy="bfs",
            workers=2,
            min_depth=3,  # Only delete folders at depth 3+
            max_depth=5,
            exclude_path=[],
            exclude_name=[],
            include_name=[]
        )
        
        config = Config(args)
        logger = setup_logger("test_depth")
        engine = Engine(config, logger)
        
        engine.dashboard.active = False
        
        engine.db.setup()
        engine.queue.append((self.test_root, 0))
        engine.db.add_folder(self.test_root, 0)
        engine._process_queue()
        
        # Get candidates with min_depth=3
        empty_folders = engine.db.get_empty_candidates(3)
        
        # Should only include deep nested folder
        deep_folder = os.path.join(self.test_root, "multi_level", "level1", "level2", "level3", "empty_deep_nested")
        self.assertIn(deep_folder, empty_folders)
        
        # Should not include shallow folders
        shallow1 = os.path.join(self.test_root, "empty1")
        self.assertNotIn(shallow1, empty_folders)
    
    def test_concurrent_workers(self):
        """Test multiple workers process folders correctly"""
        import argparse
        from config.settings import Config
        from core.engine import Engine
        from utils.logger import setup_logger
        
        for worker_count in [1, 2, 4, 8]:
            with self.subTest(workers=worker_count):
                args = argparse.Namespace(
                    path=self.test_root,
                    delete=False,
                    resume=False,
                    disk="ssd",
                    strategy="bfs",
                    workers=worker_count,
                    min_depth=0,
                    max_depth=100,
                    exclude_path=[],
                    exclude_name=[],
                    include_name=[]
                )
                
                config = Config(args)
                logger = setup_logger(f"test_workers_{worker_count}")
                engine = Engine(config, logger)
                
                engine.dashboard.active = False
                
                engine.db.setup()
                engine.queue.append((self.test_root, 0))
                engine.db.add_folder(self.test_root, 0)
                engine._process_queue()
                
                empty_folders = engine.db.get_empty_candidates(0)
                expected_empty = self.fs.get_empty_folders()
                
                self.assertEqual(len(empty_folders), len(expected_empty))


class TestConfigEndToEnd(unittest.TestCase):
    """Test all configuration options end-to-end"""
    
    def test_disk_type_ssd(self):
        """Test SSD configuration"""
        import argparse
        from config.settings import Config
        
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
        self.assertEqual(config.disk_type, "ssd")
        self.assertEqual(config.workers, 16)
        self.assertEqual(config.strategy, "BFS")
    
    def test_disk_type_hdd(self):
        """Test HDD configuration"""
        import argparse
        from config.settings import Config
        
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
        self.assertEqual(config.disk_type, "hdd")
        self.assertEqual(config.workers, 4)
        self.assertEqual(config.strategy, "DFS")
    
    def test_manual_worker_override(self):
        """Test manual worker count override"""
        import argparse
        from config.settings import Config
        
        for workers in [1, 4, 8, 16, 32]:
            with self.subTest(workers=workers):
                args = argparse.Namespace(
                    path="/test",
                    delete=False,
                    resume=False,
                    disk="auto",
                    strategy="auto",
                    workers=workers,
                    min_depth=0,
                    max_depth=100,
                    exclude_path=[],
                    exclude_name=[],
                    include_name=[]
                )
                
                config = Config(args)
                self.assertEqual(config.workers, workers)
    
    def test_strategy_override(self):
        """Test scan strategy override"""
        import argparse
        from config.settings import Config
        
        for strategy in ["bfs", "dfs"]:
            with self.subTest(strategy=strategy):
                args = argparse.Namespace(
                    path="/test",
                    delete=False,
                    resume=False,
                    disk="auto",
                    strategy=strategy,
                    workers=0,
                    min_depth=0,
                    max_depth=100,
                    exclude_path=[],
                    exclude_name=[],
                    include_name=[]
                )
                
                config = Config(args)
                self.assertEqual(config.strategy, strategy.upper())
    
    def test_exclusion_patterns(self):
        """Test path and name exclusions"""
        import argparse
        from config.settings import Config
        
        args = argparse.Namespace(
            path="/test",
            delete=False,
            resume=False,
            disk="auto",
            strategy="auto",
            workers=0,
            min_depth=0,
            max_depth=100,
            exclude_path=["*Windows*", "*.tmp*"],
            exclude_name=["node_modules", ".git"],
            include_name=[]
        )
        
        config = Config(args)
        self.assertIn("*Windows*", config.exclude_paths)
        self.assertIn("*.tmp*", config.exclude_paths)
        self.assertIn("node_modules", config.exclude_names)
        self.assertIn(".git", config.exclude_names)


if __name__ == '__main__':
    unittest.main()
