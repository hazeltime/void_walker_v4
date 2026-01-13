"""Tests for config.settings module"""
import unittest
import argparse
import os
from config.settings import Config


class MockArgs:
    """Mock argparse.Namespace for testing"""
    def __init__(self, **kwargs):
        self.path = kwargs.get('path', os.getcwd())
        self.delete = kwargs.get('delete', False)
        self.resume = kwargs.get('resume', False)
        self.disk = kwargs.get('disk', 'hdd')  # Changed default to avoid PowerShell queries in tests
        self.strategy = kwargs.get('strategy', 'dfs')  # Added strategy parameter
        self.workers = kwargs.get('workers', 0)
        self.min_depth = kwargs.get('min_depth', 0)
        self.max_depth = kwargs.get('max_depth', 100)
        self.exclude_path = kwargs.get('exclude_path', [])
        self.exclude_name = kwargs.get('exclude_name', [])
        self.include_name = kwargs.get('include_name', [])


class TestConfig(unittest.TestCase):
    """Test configuration initialization"""
    
    def test_default_config(self):
        """Test default configuration values"""
        args = MockArgs()
        config = Config(args)
        
        self.assertEqual(config.min_depth, 0)
        self.assertEqual(config.max_depth, 100)
        self.assertFalse(config.delete_mode)
        self.assertFalse(config.resume_mode)
        self.assertIn(".git", config.exclude_names)
        self.assertIn("$RECYCLE.BIN", config.exclude_names)
    
    def test_delete_mode(self):
        """Test delete mode configuration"""
        args = MockArgs(delete=True)
        config = Config(args)
        
        self.assertTrue(config.delete_mode)
    
    def test_resume_mode(self):
        """Test resume mode configuration requires resume flag without path"""
        # Test that resume with path raises error
        args = MockArgs(resume=True, path="C:\\test")
        with self.assertRaises(ValueError) as cm:
            Config(args)
        self.assertIn("Cannot specify path with --resume", str(cm.exception))
    
    def test_ssd_disk_type(self):
        """Test SSD disk type configuration"""
        args = MockArgs(disk='ssd', strategy='auto')  # Let strategy auto-derive from disk
        config = Config(args)
        
        self.assertEqual(config.disk_type, 'ssd')
        self.assertEqual(config.strategy, 'BFS')
        self.assertEqual(config.workers, 16)
    
    def test_hdd_disk_type(self):
        """Test HDD disk type configuration"""
        args = MockArgs(disk='hdd', strategy='auto')  # Let strategy auto-derive from disk
        config = Config(args)
        
        self.assertEqual(config.disk_type, 'hdd')
        self.assertEqual(config.strategy, 'DFS')
        self.assertEqual(config.workers, 4)
    
    def test_manual_worker_override(self):
        """Test manual worker count override"""
        args = MockArgs(workers=8)
        config = Config(args)
        
        self.assertEqual(config.workers, 8)
    
    def test_depth_limits(self):
        """Test depth configuration"""
        args = MockArgs(min_depth=2, max_depth=10)
        config = Config(args)
        
        self.assertEqual(config.min_depth, 2)
        self.assertEqual(config.max_depth, 10)
    
    def test_exclude_patterns(self):
        """Test exclude pattern configuration"""
        args = MockArgs(
            exclude_path=['*System32*'],
            exclude_name=['node_modules', '*.tmp']
        )
        config = Config(args)
        
        self.assertIn('*System32*', config.exclude_paths)
        self.assertIn('node_modules', config.exclude_names)
        self.assertIn('*.tmp', config.exclude_names)
    
    def test_include_patterns(self):
        """Test include pattern configuration"""
        args = MockArgs(include_name=['target', 'build'])
        config = Config(args)
        
        self.assertIn('target', config.include_names)
        self.assertIn('build', config.include_names)
    
    def test_session_id_generation(self):
        """Test session ID is generated"""
        args = MockArgs()
        config = Config(args)
        
        self.assertTrue(config.session_id.startswith('session_'))
        self.assertIsNotNone(config.timestamp)


if __name__ == '__main__':
    unittest.main()
