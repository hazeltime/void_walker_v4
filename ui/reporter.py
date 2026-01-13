import json
import os

class Reporter:
    def __init__(self, config, db):
        self.config = config
        self.db = db
        
    def show_summary(self) -> None:
        """Display session summary report with error statistics."""
        print("\n" + "="*60)
        print(" SESSION REPORT")
        print("="*60)
        
        errors = self.db.get_errors()
        err_count = len(errors)
        
        print(f" Session:  {self.config.session_id}")
        print(f" Logs:     logs/{self.config.session_id}.log")
        print(f" Errors:   {err_count}")
        print("-" * 60)

        if err_count > 0:
            print(f" \033[93m[!] {err_count} folders could not be scanned (Access Denied/System).\033[0m")
            q = input(" View error list? (y/N): ").lower()
            if q == 'y':
                self._scroll_error_list(errors)
        
        # Note: We do NOT hold the user here anymore using input().
        # The Menu Loop in menu.py handles the pause.
    
    def show_final_summary(self) -> None:
        """Display comprehensive final summary with statistics and top root folders."""
        print("\n" + "="*70)
        print(" " + "FINAL SESSION SUMMARY".center(68))
        print("="*70)
        
        # Get statistics from database
        stats = self.db.get_statistics()
        total_scanned = stats.get('total_scanned', 0)
        total_empty = stats.get('total_empty', 0)
        total_errors = stats.get('total_errors', 0)
        
        print(f" Session ID:       {self.config.session_id}")
        print(f" Root Path:        {self.config.root_path}")
        print(f" Log File:         logs/{self.config.session_id}.log")
        print("-" * 70)
        print(f" Total Scanned:    {total_scanned:,} folders")
        # Safe percentage calculation (avoid division by zero)
        empty_pct = (total_empty * 100 / total_scanned) if total_scanned > 0 else 0.0
        print(f" Empty Found:      {total_empty:,} folders ({empty_pct:.1f}%)")
        print(f" Errors:           {total_errors:,} folders")
        print("-" * 70)
        
        # Show top 3 root folders with most empty subfolders
        print(" Top 3 Root Folders with Most Empty Subfolders:")
        top_roots = self.db.get_top_root_folders(limit=3)
        
        if top_roots:
            for idx, (root_folder, count) in enumerate(top_roots, 1):
                # Shorten path if too long
                display_root = root_folder
                if len(display_root) > 50:
                    display_root = "..." + display_root[-47:]
                print(f"   {idx}. {display_root}")
                # Safe percentage calculation
                pct = (count * 100 / total_empty) if total_empty > 0 else 0.0
                print(f"      Empty subfolders: {count:,} ({pct:.1f}% of total)")
        else:
            print("   (No empty folders found)")
        
        print("="*70)
        print()
    
    def _scroll_error_list(self, errors, page_size=20):
        """Display errors in a scrollable paginated list with Page Up/Down support."""
        total = len(errors)
        total_pages = (total + page_size - 1) // page_size
        current_page = 0
        
        while True:
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, total)
            
            # Display current page
            print("\n" + "="*70)
            print(f" ERROR LIST - Page {current_page + 1}/{total_pages} (Showing {start_idx + 1}-{end_idx} of {total})")
            print("="*70)
            
            for i in range(start_idx, end_idx):
                path, msg = errors[i]
                # Shorten path if too long
                display_path = path
                if len(display_path) > 50:
                    display_path = "..." + display_path[-47:]
                print(f" {i+1:4}. {display_path}")
                print(f"       Error: {msg}")
            
            print("-"*70)
            
            # Navigation prompt
            if total_pages > 1:
                options = []
                if current_page < total_pages - 1:
                    options.append("[N]ext / PgDn")
                if current_page > 0:
                    options.append("[P]revious / PgUp")
                options.append("[Q]uit / ESC")
                
                prompt = f" {' | '.join(options)}: "
                
                # Try to use keyboard input for page keys (Windows)
                try:
                    import msvcrt
                    print(prompt, end='', flush=True)
                    
                    while True:
                        if msvcrt.kbhit():
                            key = msvcrt.getch()
                            
                            # Handle special keys
                            if key == b'\xe0' or key == b'\x00':
                                key = msvcrt.getch()
                                if key == b'I':  # Page Up
                                    if current_page > 0:
                                        print("\n[Page Up]")
                                        current_page -= 1
                                        break
                                elif key == b'Q':  # Page Down
                                    if current_page < total_pages - 1:
                                        print("\n[Page Down]")
                                        current_page += 1
                                        break
                            elif key == b'\x1b':  # ESC
                                print("\n")
                                return
                            elif key in (b'q', b'Q'):
                                print("\n")
                                return
                            elif key in (b'n', b'N') and current_page < total_pages - 1:
                                print("n\n")
                                current_page += 1
                                break
                            elif key in (b'p', b'P') and current_page > 0:
                                print("p\n")
                                current_page -= 1
                                break
                            elif key in (b'\r', b'\n'):  # Enter
                                print("\n")
                                return
                except ImportError:
                    # Fallback to standard input for non-Windows
                    choice = input(prompt).lower().strip()
                    
                    if choice == 'n' and current_page < total_pages - 1:
                        current_page += 1
                    elif choice == 'p' and current_page > 0:
                        current_page -= 1
                    elif choice == 'q' or choice == '':
                        return
                    else:
                        print("\033[93m[!] Invalid choice. Try again.\033[0m")
            else:
                # Single page
                input("\n Press Enter to continue...")
                return
    
    def scroll_empty_folders(self, empty_folder_paths=None, page_size=20):
        """
        Display empty folders in a scrollable paginated list.
        
        Args:
            empty_folder_paths: List of folder paths. If None, fetches from DB.
            page_size: Number of folders to show per page.
        
        Returns:
            int: Total number of folders displayed
        """
        if empty_folder_paths is None:
            empty_folder_paths = self.db.get_empty_candidates(self.config.min_depth)
        
        if not empty_folder_paths:
            print("\n\033[93m[!] No empty folders found.\033[0m")
            return 0
        
        # Get detailed info for each folder from database
        empty_folders = []
        for path in empty_folder_paths:
            # Query depth and file_count from database
            self.db.cursor.execute(
                "SELECT depth, file_count FROM folders WHERE path=? AND session_id=?",
                (path, self.db.session_id)
            )
            result = self.db.cursor.fetchone()
            if result:
                depth, file_count = result
                empty_folders.append((path, depth, file_count))
            else:
                # Fallback if not in DB
                empty_folders.append((path, 0, 0))
        
        total = len(empty_folders)
        print(f"\n{'='*70}")
        print(f" EMPTY FOLDERS FOUND: {total}")
        print(f"{'='*70}\n")
        
        # Paginate
        current_page = 0
        total_pages = (total + page_size - 1) // page_size
        
        while True:
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, total)
            
            # Display current page
            print(f"\n Page {current_page + 1}/{total_pages} (Showing {start_idx + 1}-{end_idx} of {total})")
            print("-"*70)
            
            for i in range(start_idx, end_idx):
                path, depth, file_count = empty_folders[i]
                # Shorten path if too long
                display_path = path
                if len(display_path) > 60:
                    display_path = "..." + display_path[-57:]
                
                indent = "  " * min(depth, 3)  # Max 3 levels of indent for display
                depth_marker = f"[D{depth}]" if depth < 100 else "[D99+]"
                print(f" {i+1:4}. {indent}{depth_marker} {display_path}")
            
            print("-"*70)
            
            # Navigation prompt
            if total_pages > 1:
                options = []
                if current_page < total_pages - 1:
                    options.append("[N]ext / PgDn")
                if current_page > 0:
                    options.append("[P]revious / PgUp")
                options.append("[Q]uit / ESC")
                
                prompt = f" {' | '.join(options)}: "
                
                # Try to use keyboard input for arrow/page keys (Windows)
                try:
                    import msvcrt
                    print(prompt, end='', flush=True)
                    
                    while True:
                        if msvcrt.kbhit():
                            key = msvcrt.getch()
                            
                            # Handle special keys (arrow keys, page up/down, etc)
                            if key == b'\xe0' or key == b'\x00':  # Special key prefix
                                key = msvcrt.getch()
                                if key == b'I':  # Page Up
                                    if current_page > 0:
                                        print("\n[Page Up]")
                                        current_page -= 1
                                        break
                                elif key == b'Q':  # Page Down
                                    if current_page < total_pages - 1:
                                        print("\n[Page Down]")
                                        current_page += 1
                                        break
                            elif key == b'\x1b':  # ESC
                                print("\n[ESC - Quit]")
                                return total
                            elif key in (b'q', b'Q'):
                                print("\n")
                                return total
                            elif key in (b'n', b'N') and current_page < total_pages - 1:
                                print("n\n")
                                current_page += 1
                                break
                            elif key in (b'p', b'P') and current_page > 0:
                                print("p\n")
                                current_page -= 1
                                break
                            elif key in (b'\r', b'\n'):  # Enter
                                print("\n")
                                return total
                except ImportError:
                    # Fallback to standard input for non-Windows
                    choice = input(prompt).lower().strip()
                    
                    if choice == 'n' and current_page < total_pages - 1:
                        current_page += 1
                    elif choice == 'p' and current_page > 0:
                        current_page -= 1
                    elif choice == 'q' or choice == '':
                        break
                    else:
                        # Invalid input, stay on current page
                        print("\033[93m[!] Invalid choice. Try again.\033[0m")
            else:
                # Single page, just prompt to continue
                input("\n Press Enter to continue...")
                break
        
        print(f"\n\033[92m[OK] Review complete\033[0m\n")
        return total
