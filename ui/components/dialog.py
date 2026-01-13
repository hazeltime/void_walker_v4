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


class CheckboxList:
    """Interactive checkbox list for multi-selection"""
    
    def __init__(self, title, items, selected_indices=None, description=None):
        """
        Args:
            title: Header text for the checkbox list
            items: List of tuples (display_name, value) or list of strings
            selected_indices: List of initially selected item indices
            description: Optional description text
        """
        self.title = title
        self.description = description
        
        # Normalize items to (display_name, value) tuples
        if items and isinstance(items[0], str):
            self.items = [(item, item) for item in items]
        else:
            self.items = items
        
        self.selected = set(selected_indices or [])
    
    def show(self):
        """
        Display checkbox list and return selected values.
        
        Returns:
            List of selected values
        """
        print(f"\n{Color.CYAN}╔{'═' * 68}╗{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET} {Color.YELLOW}{self.title:^66}{Color.RESET} {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}╠{'═' * 68}╣{Color.RESET}")
        
        if self.description:
            print(f"{Color.CYAN}║{Color.RESET} {Color.GRAY}{self.description:66}{Color.RESET} {Color.CYAN}║{Color.RESET}")
            print(f"{Color.CYAN}╠{'═' * 68}╣{Color.RESET}")
        
        # Display items with checkboxes
        for idx, (display, value) in enumerate(self.items):
            checkbox = "☑" if idx in self.selected else "☐"
            color = Color.GREEN if idx in self.selected else Color.GRAY
            print(f"{Color.CYAN}║{Color.RESET} {color}[{idx+1}] {checkbox} {display:55}{Color.RESET} {Color.CYAN}║{Color.RESET}")
        
        print(f"{Color.CYAN}╠{'═' * 68}╣{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET} {Color.YELLOW}{'Options:':^66}{Color.RESET} {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}   [A] Select All    [N] Select None    [#,#] Toggle items    {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}   [Enter] Confirm   [Q] Cancel                              {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}╚{'═' * 68}╝{Color.RESET}")
        
        choice = input(f"\n{Color.CYAN}Your selection:{Color.RESET} ").strip().lower()
        
        if choice == 'q':
            return None  # Cancelled
        elif choice == 'a':
            self.selected = set(range(len(self.items)))
            return self.show()  # Redisplay with all selected
        elif choice == 'n':
            self.selected = set()
            return self.show()  # Redisplay with none selected
        elif choice == '':
            # Confirm selection
            return [self.items[idx][1] for idx in sorted(self.selected)]
        else:
            # Toggle specific items
            try:
                toggles = [int(x.strip()) - 1 for x in choice.split(',')]
                for idx in toggles:
                    if 0 <= idx < len(self.items):
                        if idx in self.selected:
                            self.selected.remove(idx)
                        else:
                            self.selected.add(idx)
                return self.show()  # Redisplay with updated selection
            except ValueError:
                Dialog.show_error("Invalid input. Enter numbers separated by commas.", pause=False)
                return self.show()


class WizardStep:
    """Wizard step with breadcrumb navigation"""
    
    @staticmethod
    def show_breadcrumb(current_step, total_steps, step_name):
        """
        Display wizard progress breadcrumb.
        
        Args:
            current_step: Current step number (1-based)
            total_steps: Total number of steps
            step_name: Name of current step
        """
        # Progress bar
        progress = int((current_step / total_steps) * 50)
        bar = "█" * progress + "░" * (50 - progress)
        percent = int((current_step / total_steps) * 100)
        
        print(f"\n{Color.CYAN}╔{'═' * 68}╗{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET} {Color.YELLOW}Configuration Wizard{Color.RESET} - Step {current_step} of {total_steps} ({percent}%){'':30} {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET} {Color.GREEN}{bar}{Color.RESET}{'':18} {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET} {Color.CYAN}{step_name:^66}{Color.RESET} {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}╚{'═' * 68}╝{Color.RESET}\n")
    
    @staticmethod
    def show_shortcuts(show_previous=True, show_skip=False):
        """
        Display keyboard shortcuts legend.
        
        Args:
            show_previous: Show "P" for previous step
            show_skip: Show "K" for skip step
        """
        shortcuts = []
        
        if show_previous:
            shortcuts.append(f"{Color.CYAN}[P]{Color.RESET} Previous")
        
        shortcuts.append(f"{Color.CYAN}[S]{Color.RESET} Save")
        shortcuts.append(f"{Color.CYAN}[V]{Color.RESET} View Config")
        shortcuts.append(f"{Color.CYAN}[H]{Color.RESET} Help")
        
        if show_skip:
            shortcuts.append(f"{Color.CYAN}[K]{Color.RESET} Skip")
        
        shortcuts.append(f"{Color.RED}[Q]{Color.RESET} Quit")
        
        print(f"\n{Color.GRAY}└─ {' │ '.join(shortcuts)}{Color.RESET}\n")


class InputValidator:
    """Real-time input validation with visual feedback"""
    
    @staticmethod
    def validate_path(path):
        """
        Validate directory path with visual feedback.
        
        Returns:
            (is_valid, normalized_path, message)
        """
        import os
        from utils.validators import normalize_path
        
        if not path or path.strip() == '':
            return False, None, f"{Color.RED}✗{Color.RESET} Path cannot be empty"
        
        try:
            normalized = normalize_path(path)
            if os.path.isdir(normalized):
                return True, normalized, f"{Color.GREEN}✓{Color.RESET} Valid directory"
            else:
                return False, None, f"{Color.RED}✗{Color.RESET} Directory does not exist"
        except Exception as e:
            return False, None, f"{Color.RED}✗{Color.RESET} Invalid path: {str(e)}"
    
    @staticmethod
    def validate_number(value, min_val=None, max_val=None, allow_zero=True):
        """
        Validate numeric input with range checking.
        
        Returns:
            (is_valid, number, message)
        """
        try:
            num = int(value)
            
            if not allow_zero and num == 0:
                return False, None, f"{Color.RED}✗{Color.RESET} Value must be greater than 0"
            
            if min_val is not None and num < min_val:
                return False, None, f"{Color.YELLOW}⚠{Color.RESET} Value below minimum ({min_val})"
            
            if max_val is not None and num > max_val:
                return False, None, f"{Color.YELLOW}⚠{Color.RESET} Value above maximum ({max_val})"
            
            return True, num, f"{Color.GREEN}✓{Color.RESET} Valid number"
        except ValueError:
            return False, None, f"{Color.RED}✗{Color.RESET} Must be a number"
    
    @staticmethod
    def show_validation(is_valid, message):
        """Display validation result with color coding"""
        print(f"  {message}")
