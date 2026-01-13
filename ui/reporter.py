import json
import os

class Reporter:
    def __init__(self, config, db):
        self.config = config
        self.db = db
        
    def show_summary(self):
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
                print("-" * 60)
                for path, msg in errors:
                    print(f" {path} -> {msg}")
                print("-" * 60)
        
        # Note: We do NOT hold the user here anymore using input().
        # The Menu Loop in menu.py handles the pause.
    
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
                    options.append("[N]ext")
                if current_page > 0:
                    options.append("[P]revious")
                options.append("[Q]uit")
                
                prompt = f" {' | '.join(options)}: "
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
