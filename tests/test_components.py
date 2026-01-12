"""Tests for UI components (Banner and Dialog)"""
import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
from ui.components.banner import Banner
from ui.components.dialog import Dialog


class TestBanner(unittest.TestCase):
    """Test Banner component"""
    
    @patch('os.system')
    def test_clear_windows(self, mock_system):
        """Test clear on Windows"""
        with patch('os.name', 'nt'):
            Banner.clear()
            mock_system.assert_called_once_with('cls')
    
    @patch('os.system')
    def test_clear_unix(self, mock_system):
        """Test clear on Unix/Linux"""
        with patch('os.name', 'posix'):
            Banner.clear()
            mock_system.assert_called_once_with('clear')
    
    @patch('builtins.print')
    @patch('ui.components.banner.Banner.clear')
    def test_print_ascii_banner(self, mock_clear, mock_print):
        """Test ASCII banner printing"""
        Banner.print_ascii_banner()
        mock_clear.assert_called_once()
        self.assertGreater(mock_print.call_count, 5)
    
    @patch('builtins.print')
    @patch('ui.components.banner.Banner.clear')
    def test_print_header_default(self, mock_clear, mock_print):
        """Test default header printing"""
        Banner.print_header()
        mock_clear.assert_called_once()
        self.assertGreater(mock_print.call_count, 0)
    
    @patch('builtins.print')
    @patch('ui.components.banner.Banner.clear')
    def test_print_header_custom(self, mock_clear, mock_print):
        """Test custom header printing"""
        Banner.print_header("Custom Title")
        mock_clear.assert_called_once()
        # Check that custom title was used in print calls
        found_custom = False
        for call in mock_print.call_args_list:
            if 'Custom Title' in str(call):
                found_custom = True
                break
        self.assertTrue(found_custom, "Custom title not found in print calls")
    
    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    @patch('ui.components.banner.Banner.print_header')
    def test_print_about(self, mock_header, mock_print, mock_input):
        """Test about screen printing"""
        Banner.print_about()
        mock_header.assert_called_once()
        self.assertGreater(mock_print.call_count, 10)
        mock_input.assert_called_once()


class TestDialog(unittest.TestCase):
    """Test Dialog component"""
    
    @patch('builtins.input', return_value='n')
    @patch('builtins.print')
    def test_confirm_quit_no(self, mock_print, mock_input):
        """Test quit confirmation - user says no"""
        result = Dialog.confirm_quit()
        self.assertFalse(result)
        mock_input.assert_called_once()
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_confirm_quit_yes(self, mock_print, mock_input):
        """Test quit confirmation - user says yes (should exit)"""
        with self.assertRaises(SystemExit):
            Dialog.confirm_quit()
    
    @patch('builtins.input', return_value='yes')
    @patch('builtins.print')
    def test_confirm_quit_yes_word(self, mock_print, mock_input):
        """Test quit confirmation - user types 'yes'"""
        with self.assertRaises(SystemExit):
            Dialog.confirm_quit()
    
    @patch('builtins.input', return_value='y')
    def test_confirm_action_yes(self, mock_input):
        """Test confirm action - user confirms"""
        result = Dialog.confirm_action("Are you sure?")
        self.assertTrue(result)
    
    @patch('builtins.input', return_value='n')
    def test_confirm_action_no(self, mock_input):
        """Test confirm action - user declines"""
        result = Dialog.confirm_action("Are you sure?")
        self.assertFalse(result)
    
    @patch('builtins.input', return_value='')
    def test_confirm_action_default_no(self, mock_input):
        """Test confirm action - default 'n'"""
        result = Dialog.confirm_action("Continue?", default='n')
        self.assertFalse(result)
    
    @patch('builtins.input', return_value='')
    def test_confirm_action_default_yes(self, mock_input):
        """Test confirm action - default 'y'"""
        result = Dialog.confirm_action("Continue?", default='y')
        self.assertTrue(result)
    
    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_show_error(self, mock_print, mock_input):
        """Test error message display"""
        Dialog.show_error("Test error", pause=True)
        mock_print.assert_called()
        mock_input.assert_called_once()
    
    @patch('builtins.print')
    def test_show_error_no_pause(self, mock_print):
        """Test error message without pause"""
        Dialog.show_error("Test error", pause=False)
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_show_success(self, mock_print):
        """Test success message display"""
        Dialog.show_success("Operation successful")
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_show_info(self, mock_print):
        """Test info message display"""
        Dialog.show_info("Information message")
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_show_warning(self, mock_print):
        """Test warning message display"""
        Dialog.show_warning("Warning message")
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_show_box(self, mock_print):
        """Test box display"""
        Dialog.show_box("Title", ["Line 1", "Line 2", "Line 3"])
        self.assertGreater(mock_print.call_count, 5)
    
    @patch('builtins.input', return_value='')
    def test_pause(self, mock_input):
        """Test pause function"""
        Dialog.pause("Custom message")
        mock_input.assert_called_once()


if __name__ == '__main__':
    unittest.main()
