"""Tests for filtering logic in Engine"""
import unittest
import os
import tempfile
from unittest.mock import Mock
from core.engine import Engine
from tests.test_config import MockArgs
from config.settings import Config
from utils.logger import setup_logger


class TestFiltering(unittest.TestCase):
    """Test path and folder filtering logic"""
    
    def setUp(self):
        """Create test engine with mock config"""
        self.test_dir = tempfile.mkdtemp()
        args = MockArgs(
            path=self.test_dir,
            exclude_path=['*System32*', '*Windows*'],
            exclude_name=['node_modules', '.git', '*.tmp'],
            max_depth=5
        )
        self.config = Config(args)
        self.logger = Mock()
        self.engine = Engine(self.config, self.logger)
    
    def test_filter_by_name(self):
        """Test filtering by folder name"""
        # Should be filtered
        self.assertTrue(self._is_filtered_helper("C:\\Test\\node_modules", "node_modules", 2))
        self.assertTrue(self._is_filtered_helper("C:\\Test\\.git", ".git", 2))
        
        # Should NOT be filtered
        self.assertFalse(self._is_filtered_helper("C:\\Test\\src", "src", 2))
    
    def test_filter_by_path(self):
        """Test filtering by full path pattern"""
        # Should be filtered
        self.assertTrue(self._is_filtered_helper("C:\\Windows\\System32", "System32", 2))
        self.assertTrue(self._is_filtered_helper("C:\\Windows\\Temp", "Temp", 2))
        
        # Should NOT be filtered
        self.assertFalse(self._is_filtered_helper("C:\\Users\\Test", "Test", 2))
    
    def test_filter_by_depth(self):
        """Test filtering by max depth"""
        # Should be filtered (exceeds max_depth)
        self.assertTrue(self._is_filtered_helper("C:\\Test\\Deep", "Deep", 6))
        
        # Should NOT be filtered
        self.assertFalse(self._is_filtered_helper("C:\\Test\\Shallow", "Shallow", 3))
    
    def test_wildcard_pattern(self):
        """Test wildcard pattern matching"""
        args = MockArgs(
            path=self.test_dir,
            exclude_name=['temp*', '*.log']
        )
        config = Config(args)
        engine = Engine(config, self.logger)
        
        # Should be filtered
        self.assertTrue(engine._is_filtered("C:\\Test\\temp_files", "temp_files", 2))
        self.assertTrue(engine._is_filtered("C:\\Test\\debug.log", "debug.log", 2))
        
        # Should NOT be filtered
        self.assertFalse(engine._is_filtered("C:\\Test\\data", "data", 2))
    
    def test_default_exclusions(self):
        """Test that default exclusions are applied"""
        # Config should automatically add default exclusions
        self.assertIn('.git', self.config.exclude_names)
        self.assertIn('$RECYCLE.BIN', self.config.exclude_names)
        self.assertIn('System Volume Information', self.config.exclude_names)
    
    def _is_filtered_helper(self, path, name, depth):
        """Helper to test filtering"""
        return self.engine._is_filtered(path, name, depth)


if __name__ == '__main__':
    unittest.main()
