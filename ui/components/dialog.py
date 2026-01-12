"""
Dialog component for user confirmations and prompts.
Provides reusable dialog boxes for various interactions.
"""
import sys
from common.constants import Color


class Dialog:
    """Handles user dialogs and confirmations"""
    
    @staticmethod
    def confirm_quit():
        """
        Confirm before quitting application.
        Returns True if user wants to quit, False otherwise.
        """
        print(f"\n{Color.YELLOW}[!] Are you sure you want to quit?{Color.RESET}")
        choice = input(f"    [Y] Yes, quit  [N] No, go back: ").strip().lower()
        if choice in ['y', 'yes']:
            print(f"\n{Color.GRAY}[i] Goodbye! Thank you for using Void Walker.{Color.RESET}\n")
            sys.exit(0)
        return False
    
    @staticmethod
    def confirm_action(message, default='n'):
        """
        Generic confirmation dialog.
        
        Args:
            message: Question to ask user
            default: Default answer ('y' or 'n')
        
        Returns:
            True if user confirms, False otherwise
        """
        default_text = "Y/n" if default == 'y' else "y/N"
        choice = input(f"{message} [{default_text}]: ").strip().lower()
        
        if not choice:
            choice = default
        
        return choice in ['y', 'yes']
    
    @staticmethod
    def show_error(message, pause=True):
        """Display error message"""
        print(f"{Color.RED}[✗] {message}{Color.RESET}")
        if pause:
            input("\nPress Enter to continue...")
    
    @staticmethod
    def show_success(message, pause=False):
        """Display success message"""
        print(f"{Color.GREEN}[✓] {message}{Color.RESET}")
        if pause:
            input("\nPress Enter to continue...")
    
    @staticmethod
    def show_info(message, pause=False):
        """Display info message"""
        print(f"{Color.CYAN}[i] {message}{Color.RESET}")
        if pause:
            input("\nPress Enter to continue...")
    
    @staticmethod
    def show_warning(message, pause=False):
        """Display warning message"""
        print(f"{Color.YELLOW}[!] {message}{Color.RESET}")
        if pause:
            input("\nPress Enter to continue...")
    
    @staticmethod
    def show_box(title, content_lines, width=70):
        """
        Display content in a formatted box.
        
        Args:
            title: Box title
            content_lines: List of content lines
            width: Box width
        """
        print(f"\n{Color.CYAN}╔{'═' * (width-2)}╗{Color.RESET}")
        
        # Title
        if title:
            padding = (width - len(title) - 4) // 2
            print(f"{Color.CYAN}║{Color.RESET}{' ' * padding}{Color.YELLOW}{title}{Color.RESET}{' ' * (width - len(title) - padding - 4)}{Color.CYAN}║{Color.RESET}")
            print(f"{Color.CYAN}╠{'═' * (width-2)}╣{Color.RESET}")
        
        # Content
        for line in content_lines:
            # Remove ANSI codes for length calculation
            clean_line = line
            for code in [Color.RESET, Color.CYAN, Color.YELLOW, Color.GREEN, Color.RED, Color.GRAY]:
                clean_line = clean_line.replace(code, '')
            
            padding = width - len(clean_line) - 4
            print(f"{Color.CYAN}║{Color.RESET} {line}{' ' * padding} {Color.CYAN}║{Color.RESET}")
        
        print(f"{Color.CYAN}╚{'═' * (width-2)}╝{Color.RESET}\n")
    
    @staticmethod
    def pause(message="Press Enter to continue..."):
        """Pause and wait for user input"""
        input(f"\n{message}")
