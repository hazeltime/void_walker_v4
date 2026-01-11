"""Tests for utils.validators module"""
import unittest
import os
import tempfile
import shutil
from utils.validators import normalize_path, validate_target_path


class TestPathNormalization(unittest.TestCase):
    """Test path normalization functionality"""
    
    def test_normalize_quoted_path(self):
        """Test removal of quotes from path"""
        self.assertEqual(normalize_path('"C:\\Users"'), 'C:\\Users')
        self.assertEqual(normalize_path("'C:\\Users'"), 'C:\\Users')
    
    def test_normalize_drive_root(self):
        """Test drive root normalization"""
        result = normalize_path("E:")
        self.assertEqual(result, "E:\\")
    
    def test_normalize_slashes(self):
        """Test slash normalization"""
        if os.name == 'nt':
            self.assertEqual(normalize_path("C:/Users/Test"), "C:\\Users\\Test")
    
    def test_normalize_empty_path(self):
        """Test empty path handling"""
        self.assertEqual(normalize_path(""), "")
        self.assertEqual(normalize_path(None), "")
    
    def test_normalize_whitespace(self):
        """Test whitespace stripping"""
        self.assertEqual(normalize_path("  C:\\Users  "), "C:\\Users")


class TestPathValidation(unittest.TestCase):
    """Test path validation functionality"""
    
    def setUp(self):
        """Create temporary directory for testing"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directory"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_validate_existing_directory(self):
        """Test validation of existing directory"""
        valid, msg = validate_target_path(self.test_dir)
        self.assertTrue(valid)
        self.assertEqual(msg, "OK")
    
    def test_validate_nonexistent_path(self):
        """Test validation of non-existent path"""
        fake_path = os.path.join(self.test_dir, "nonexistent")
        valid, msg = validate_target_path(fake_path)
        self.assertFalse(valid)
        self.assertIn("does not exist", msg)
    
    def test_validate_empty_path(self):
        """Test validation of empty path"""
        valid, msg = validate_target_path("")
        self.assertFalse(valid)
        self.assertIn("cannot be empty", msg)
    
    def test_validate_file_not_directory(self):
        """Test validation when target is a file"""
        test_file = os.path.join(self.test_dir, "testfile.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        valid, msg = validate_target_path(test_file)
        self.assertFalse(valid)
        self.assertIn("not a directory", msg)


if __name__ == '__main__':
    unittest.main()
