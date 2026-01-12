"""Tests for common.constants module"""
import unittest
from common.constants import (
    OperationMode, DiskType, ScanStrategy, FolderStatus,
    EnginePhase, Color, ErrorMessage, SuccessMessage,
    APP_VERSION, WORKERS_SSD, WORKERS_HDD
)


class TestEnums(unittest.TestCase):
    """Test enumeration classes"""
    
    def test_operation_mode_values(self):
        """Test OperationMode enum values"""
        self.assertEqual(OperationMode.DRY_RUN.value, "t")
        self.assertEqual(OperationMode.DELETE.value, "d")
    
    def test_disk_type_values(self):
        """Test DiskType enum values"""
        self.assertEqual(DiskType.AUTO.value, "auto")
        self.assertEqual(DiskType.SSD.value, "ssd")
        self.assertEqual(DiskType.HDD.value, "hdd")
    
    def test_scan_strategy_values(self):
        """Test ScanStrategy enum values"""
        self.assertEqual(ScanStrategy.AUTO.value, "auto")
        self.assertEqual(ScanStrategy.BFS.value, "bfs")
        self.assertEqual(ScanStrategy.DFS.value, "dfs")
    
    def test_folder_status_values(self):
        """Test FolderStatus enum values"""
        self.assertEqual(FolderStatus.PENDING.value, "PENDING")
        self.assertEqual(FolderStatus.SCANNED.value, "SCANNED")
        self.assertEqual(FolderStatus.ERROR.value, "ERROR")
        self.assertEqual(FolderStatus.DELETED.value, "DELETED")
        self.assertEqual(FolderStatus.WOULD_DELETE.value, "WOULD_DELETE")
    
    def test_engine_phase_values(self):
        """Test EnginePhase enum values"""
        self.assertEqual(EnginePhase.INIT.value, "INIT")
        self.assertEqual(EnginePhase.SCANNING.value, "SCANNING")
        self.assertEqual(EnginePhase.CLEANING.value, "CLEANING")
        self.assertEqual(EnginePhase.COMPLETE.value, "COMPLETE")


class TestConstants(unittest.TestCase):
    """Test constant values"""
    
    def test_version_format(self):
        """Test version string format"""
        self.assertRegex(APP_VERSION, r'^\d+\.\d+\.\d+$')
    
    def test_worker_counts(self):
        """Test worker configuration"""
        self.assertEqual(WORKERS_SSD, 16)
        self.assertEqual(WORKERS_HDD, 4)
        self.assertGreater(WORKERS_SSD, WORKERS_HDD)
    
    def test_color_codes(self):
        """Test ANSI color codes are strings"""
        self.assertIsInstance(Color.RED, str)
        self.assertIsInstance(Color.GREEN, str)
        self.assertIsInstance(Color.YELLOW, str)
        self.assertIsInstance(Color.CYAN, str)
        self.assertIsInstance(Color.RESET, str)
    
    def test_error_messages_format(self):
        """Test error messages can be formatted"""
        msg = ErrorMessage.PATH_NOT_FOUND.format(path="/test/path")
        self.assertIn("/test/path", msg)
        
        msg = ErrorMessage.INVALID_CHOICE.format(options="1,2,3")
        self.assertIn("1,2,3", msg)
    
    def test_success_messages_format(self):
        """Test success messages can be formatted"""
        msg = SuccessMessage.CONFIG_SAVED.format(file="test.json")
        self.assertIn("test.json", msg)
        
        msg = SuccessMessage.SCAN_COMPLETE.format(scanned=100)
        self.assertIn("100", msg)


if __name__ == '__main__':
    unittest.main()
