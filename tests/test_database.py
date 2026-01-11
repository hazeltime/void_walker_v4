"""Tests for data.database module"""
import unittest
import os
import tempfile
from data.database import Database


class TestDatabase(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Create temporary database for testing"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db_path = self.test_db.name
        self.session_id = "test_session_001"
        self.db = Database(self.db_path, self.session_id)
        self.db.setup()
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_database_setup(self):
        """Test database initialization"""
        # Verify tables exist
        self.db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in self.db.cursor.fetchall()]
        
        self.assertIn('sessions', tables)
        self.assertIn('folders', tables)
    
    def test_add_folder(self):
        """Test adding folder to database"""
        test_path = "C:\\Test\\Path"
        depth = 2
        
        self.db.add_folder(test_path, depth)
        self.db.commit()
        
        self.db.cursor.execute(
            "SELECT path, depth, status FROM folders WHERE path=? AND session_id=?",
            (test_path, self.session_id)
        )
        result = self.db.cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], test_path)
        self.assertEqual(result[1], depth)
        self.assertEqual(result[2], 'PENDING')
    
    def test_update_folder_stats(self):
        """Test updating folder statistics"""
        test_path = "C:\\Test\\Path"
        self.db.add_folder(test_path, 1)
        
        file_count = 5
        self.db.update_folder_stats(test_path, file_count)
        self.db.commit()
        
        self.db.cursor.execute(
            "SELECT file_count, status FROM folders WHERE path=? AND session_id=?",
            (test_path, self.session_id)
        )
        result = self.db.cursor.fetchone()
        
        self.assertEqual(result[0], file_count)
        self.assertEqual(result[1], 'SCANNED')
    
    def test_log_error(self):
        """Test error logging"""
        test_path = "C:\\Test\\Error"
        error_msg = "Access Denied"
        
        self.db.add_folder(test_path, 1)
        self.db.log_error(test_path, error_msg)
        self.db.commit()
        
        self.db.cursor.execute(
            "SELECT status, error_msg FROM folders WHERE path=? AND session_id=?",
            (test_path, self.session_id)
        )
        result = self.db.cursor.fetchone()
        
        self.assertEqual(result[0], 'ERROR')
        self.assertEqual(result[1], error_msg)
    
    def test_mark_deleted(self):
        """Test marking folder as deleted"""
        test_path = "C:\\Test\\Deleted"
        self.db.add_folder(test_path, 1)
        self.db.mark_deleted(test_path)
        self.db.commit()
        
        self.db.cursor.execute(
            "SELECT status FROM folders WHERE path=? AND session_id=?",
            (test_path, self.session_id)
        )
        result = self.db.cursor.fetchone()
        
        self.assertEqual(result[0], 'DELETED')
    
    def test_mark_would_delete(self):
        """Test marking folder as would-delete (dry run)"""
        test_path = "C:\\Test\\WouldDelete"
        self.db.add_folder(test_path, 1)
        self.db.mark_would_delete(test_path)
        self.db.commit()
        
        self.db.cursor.execute(
            "SELECT status FROM folders WHERE path=? AND session_id=?",
            (test_path, self.session_id)
        )
        result = self.db.cursor.fetchone()
        
        self.assertEqual(result[0], 'WOULD_DELETE')
    
    def test_get_pending(self):
        """Test retrieving pending folders"""
        paths = [
            ("C:\\Test\\Path1", 1),
            ("C:\\Test\\Path2", 2),
            ("C:\\Test\\Path3", 1)
        ]
        
        for path, depth in paths:
            self.db.add_folder(path, depth)
        self.db.commit()
        
        pending = self.db.get_pending()
        
        self.assertEqual(len(pending), 3)
        # Should be ordered by depth ASC
        self.assertEqual(pending[0][1], 1)
    
    def test_get_empty_candidates(self):
        """Test retrieving empty folder candidates"""
        # Add folders with file counts
        folders = [
            ("C:\\Test\\Empty1", 2, 0),
            ("C:\\Test\\NotEmpty", 2, 5),
            ("C:\\Test\\Empty2", 3, 0),
            ("C:\\Test\\Shallow", 1, 0)
        ]
        
        for path, depth, file_count in folders:
            self.db.add_folder(path, depth)
            self.db.update_folder_stats(path, file_count)
        self.db.commit()
        
        candidates = self.db.get_empty_candidates(min_depth=2)
        
        # Should only return empty folders at depth >= 2, ordered deep to shallow
        self.assertEqual(len(candidates), 2)
        self.assertIn("C:\\Test\\Empty1", candidates)
        self.assertIn("C:\\Test\\Empty2", candidates)
        self.assertNotIn("C:\\Test\\Shallow", candidates)
    
    def test_get_errors(self):
        """Test retrieving error list"""
        errors = [
            ("C:\\Test\\Error1", "Access Denied"),
            ("C:\\Test\\Error2", "WinError 1920")
        ]
        
        for path, msg in errors:
            self.db.add_folder(path, 1)
            self.db.log_error(path, msg)
        self.db.commit()
        
        error_list = self.db.get_errors()
        
        self.assertEqual(len(error_list), 2)


if __name__ == '__main__':
    unittest.main()
