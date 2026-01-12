import os
import sys
import subprocess
import json
import time
from utils.validators import normalize_path

class Menu:
    def __init__(self):
        self.config_file = "void_walker_config.json"
        self.defaults = self.load_config()

    def run_wizard(self):
        """Entry point for interactive wizard"""
        self.main_loop()

    def load_config(self):
        """Load user configuration with comprehensive defaults"""
        defaults = {
            "path": os.getcwd(),
            "mode": "t",
            "disk": "a",
            "strategy": "auto",
            "workers": 0,
            "min_depth": 0,
            "max_depth": 10000,
            "exclude_paths": [],
            "exclude_names": [],
            "include_names": [],
            "resume": False,
            "windows_exclusions": []
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    saved = json.load(f)
                    defaults.update(saved)
            except (json.JSONDecodeError, IOError, KeyError):
                # Ignore corrupted/unreadable config, use defaults
                pass
        
        return defaults

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_banner(self):
        """Display application banner with version and description"""
        self.clear()
        print("\033[96m" + "="*70)
        print(" __     ______  _____ _____   __          __     _      _  ________ _____  ")
        print(" \\ \\   / / __ \\|_   _|  __ \\  \\ \\        / /\\ \\  | |    | |/ /  ____|  __ \\ ")
        print("  \\ \\_/ / |  | | | | | |  | |  \\ \\  /\\  / /  \\ \\_| |    | ' /| |__  | |__) |")
        print("   \\   /| |  | | | | | |  | |   \\ \\/  \\/ / /\\ \\| |    |  < |  __| |  _  / ")
        print("    | | | |__| |_| |_| |__| |    \\  /\\  / ____ \\ |____| . \\| |____| | \\ \\ ")
        print("    |_|  \\____/|_____|_____/      \\/  \\/_/    \\_\\______|_|\\_\\______|_|  \\_\\")
        print("="*70)
        print("  \033[93mVersion 4.1.1\033[0m | Enterprise Empty Folder Detection & Cleanup Tool")
        print("  \033[90mOptimized for SSD/HDD with concurrent scanning & intelligent filtering\033[0m")
        print("="*70 + "\033[0m\n")

    def print_header(self):
        self.clear()
        print("\033[96m" + "="*70)
        print("  VOID WALKER v4.1.1 - ENTERPRISE CONSOLE")
        print("="*70 + "\033[0m")

    def print_help(self):
        """Display comprehensive help"""
        self.clear()
        print("\033[96m" + "="*60)
        print(" HELP - VOID WALKER CONFIGURATION GUIDE")
        print("="*60 + "\033[0m\n")
        
        print("\033[93m1. TARGET PATH\033[0m")
        print("   The root directory to scan. Example: F:\\ or C:\\Users\\MyFolder")
        print("   Press 'q' at any prompt to quit.\n")
        
        print("\033[93m2. OPERATION MODE\033[0m")
        print("   [T] Dry Run    - Safe preview mode, no files deleted")
        print("   [D] Delete     - ACTUALLY DELETES empty folders\n")
        
        print("\033[93m3. HARDWARE STRATEGY\033[0m")
        print("   [A] Auto  - Detects SSD/HDD automatically")
        print("   [S] SSD   - BFS scan, 16 threads (10-12x faster)")
        print("   [H] HDD   - DFS scan, 4 threads (sequential)\n")
        
        print("\033[93m4. SCAN STRATEGY\033[0m")
        print("   [A] Auto - Match hardware (BFS for SSD, DFS for HDD)")
        print("   [B] BFS  - Breadth-first (best for SSD)")
        print("   [D] DFS  - Depth-first (best for HDD)\n")
        
        print("\033[93m5. THREAD WORKERS\033[0m")
        print("   [0] Auto - 16 for SSD, 4 for HDD")
        print("   [1-32] Manual override\n")
        
        print("\033[93m6. DEPTH LIMITS\033[0m")
        print("   Min Depth - Only delete folders at or below this depth")
        print("   Max Depth - Stop scanning beyond this depth")
        print("   Example: min=2 prevents deleting C:\\Program Files\\EmptyFolder\n")
        
        print("\033[93m7. FILTERS\033[0m")
        print("   Exclude Paths - Skip paths matching patterns")
        print("   Exclude Names - Skip folder names matching patterns")
        print("   Include Names - ONLY scan folders matching these patterns")
        print("   Examples: *.tmp*, node_modules, .git\n")
        
        print("\033[93m8. RESUME MODE\033[0m")
        print("   Continues a previous interrupted scan from cache\n")
        
        print("\033[93mKEYBOARD CONTROLS (during scan):\033[0m")
        print("   P - Pause/Resume   S - Save Progress")
        print("   H - Show Help      C - Show Config")
        print("   D - Disk Stats     V - View Stats")
        print("   Q - Quit\n")
        
        input("Press Enter to return to menu...")

    def confirm_quit(self):
        """Confirm before quitting - defaults to YES"""
        print("\n\033[93m[!] Are you sure you want to quit?\033[0m")
        choice = input("    [\033[1m\033[93mY\033[0m] Yes, quit  [N] No, go back (default: Yes): ").strip().lower()
        if choice in ['y', 'yes', '']:  # Empty string defaults to Yes
            print("\n\033[90m[i] Goodbye! Thank you for using Void Walker.\033[0m\n")
            sys.exit(0)
        return False

    def get_input(self, prompt, key, valid_options=None, example=""):
        """Dynamic input with colored defaults, examples, and universal controls."""
        default_val = self.defaults.get(key, "")
        
        # Format default for display
        if isinstance(default_val, list):
            display_default = ", ".join(default_val) if default_val else "None"
        elif isinstance(default_val, bool):
            display_default = "Yes" if default_val else "No"
        else:
            display_default = str(default_val) if default_val else "Not set"
        
        # Show example if provided
        if example:
            print(f"   \033[90m💡 Example: {example}\033[0m")
        
        # Colorize default value (Bright Yellow + Bold)
        prompt_str = f"{prompt} [\033[1;93m{display_default}\033[0m]\n   \033[90m[H]elp | [S]ave | [V]iew Config | [Q]uit\033[0m\n   → "
        
        choice = input(prompt_str).strip()

        if choice == "":
            return default_val
        
        if choice.lower() in ['q', 'quit', 'exit']:
            self.confirm_quit()
            return self.get_input(prompt, key, valid_options, example)
        
        if choice.lower() in ['h', 'help', '?']:
            self.print_help()
            return self.get_input(prompt, key, valid_options, example)
        
        if choice.lower() in ['s', 'save']:
            self.save_config()
            print("   \033[92m[OK] Config saved to void_walker_config.json\033[0m")
            time.sleep(1)
            return self.get_input(prompt, key, valid_options, example)
        
        if choice.lower() in ['v', 'view']:
            self.show_current_config()
            return self.get_input(prompt, key, valid_options, example)

        if valid_options:
            if choice.lower() in valid_options:
                return choice.lower()
            print(f"    \033[91m[!] Invalid. Options: {', '.join(valid_options)}\033[0m")
            return self.get_input(prompt, key, valid_options)
            
        return choice

    def get_list_input(self, prompt, key):
        """Get comma-separated list input"""
        default_val = self.defaults.get(key, [])
        display_default = ", ".join(default_val) if default_val else "none"
        
        prompt_str = f"{prompt} [\033[93m{display_default}\033[0m]: "
        choice = input(prompt_str).strip()
        
        if choice == "":
            return default_val
        
        if choice.lower() in ['q', 'quit', 'exit']:
            self.confirm_quit()
            return self.get_list_input(prompt, key)
        
        if choice.lower() == 'none' or choice.lower() == 'n':
            return []
        
        # Split by comma and clean
        items = [item.strip() for item in choice.split(',') if item.strip()]
        return items

    def main_loop(self):
        while True:
            # Show banner on first screen
            self.print_banner()
            
            print("\033[92m═══ MAIN MENU ═══\033[0m\n")
            print("\033[93mWELCOME!\033[0m This tool scans directories to find and optionally delete")
            print("empty folders. It's optimized for both SSD and HDD with intelligent")
            print("concurrent scanning, depth filtering, and pattern-based exclusions.\n")
            
            print("\033[96m╔═══ QUICK START ═══════════════════════════════════════════════════╗\033[0m")
            print("\033[96m║\033[0m  \033[92m[1]\033[0m New Scan         - Configure and run a new folder scan          \033[96m║\033[0m")
            print("\033[96m║\033[0m  \033[92m[2]\033[0m Load & Run       - Load saved config and execute immediately    \033[96m║\033[0m")
            print("\033[96m║\033[0m  \033[92m[3]\033[0m Resume Session   - Continue a previously interrupted scan       \033[96m║\033[0m")
            print("\033[96m╚═══════════════════════════════════════════════════════════════════╝\033[0m\n")
            
            print("\033[96m╔═══ INFORMATION ═══════════════════════════════════════════════════╗\033[0m")
            print("\033[96m║\033[0m  \033[93m[4]\033[0m View Cache       - Show previous scan sessions and statistics    \033[96m║\033[0m")
            print("\033[96m║\033[0m  \033[93m[5]\033[0m Help             - Comprehensive guide to all options            \033[96m║\033[0m")
            print("\033[96m║\033[0m  \033[93m[6]\033[0m About            - Application info, version, and features       \033[96m║\033[0m")
            print("\033[96m╚═══════════════════════════════════════════════════════════════════╝\033[0m\n")
            
            print("\033[96m╔═══ EXIT ══════════════════════════════════════════════════════════╗\033[0m")
            print("\033[96m║\033[0m  \033[91m[Q]\033[0m Quit             - Exit Void Walker (with confirmation)          \033[96m║\033[0m")
            print("\033[96m╚═══════════════════════════════════════════════════════════════════╝\033[0m\n")
            
            choice = input("\033[96mYour choice:\033[0m ").strip().lower()
            
            if choice == '1':
                self.configure_and_run()
            elif choice == '2':
                self.load_and_run()
            elif choice == '3':
                self.resume_session()
            elif choice == '4':
                self.show_cache()
            elif choice == '5':
                self.print_help()
            elif choice == '6':
                self.show_about()
            elif choice in ['q', 'quit', 'exit']:
                self.confirm_quit()
            else:
                print("\033[91m[!] Invalid choice. Please select 1-6 or Q.\033[0m")
                time.sleep(1.5)

    def show_about(self):
        """Display about information"""
        self.print_header()
        print("\n\033[96m╔═══ ABOUT VOID WALKER ═════════════════════════════════════════════╗\033[0m")
        print("\033[96m║\033[0m                                                                   \033[96m║\033[0m")
        print("\033[96m║\033[0m  \033[93mVersion:\033[0m 4.1.1                                                  \033[96m║\033[0m")
        print("\033[96m║\033[0m  \033[93mRelease Date:\033[0m January 2026                                     \033[96m║\033[0m")
        print("\033[96m║\033[0m  \033[93mRepository:\033[0m github.com/hazeltime/void_walker_v4                \033[96m║\033[0m")
        print("\033[96m║\033[0m                                                                   \033[96m║\033[0m")
        print("\033[96m║\033[0m  \033[92m⚡ KEY FEATURES:\033[0m                                                \033[96m║\033[0m")
        print("\033[96m║\033[0m    • Concurrent multi-threaded scanning (up to 32 workers)       \033[96m║\033[0m")
        print("\033[96m║\033[0m    • Intelligent SSD/HDD detection and optimization              \033[96m║\033[0m")
        print("\033[96m║\033[0m    • BFS (breadth-first) and DFS (depth-first) strategies       \033[96m║\033[0m")
        print("\033[96m║\033[0m    • Advanced filtering: patterns, depth limits, exclusions     \033[96m║\033[0m")
        print("\033[96m║\033[0m    • Resume capability for interrupted scans                     \033[96m║\033[0m")
        print("\033[96m║\033[0m    • Real-time dashboard with live metrics                       \033[96m║\033[0m")
        print("\033[96m║\033[0m    • SQLite persistence with session history                     \033[96m║\033[0m")
        print("\033[96m║\033[0m    • Dry-run mode for safe testing                               \033[96m║\033[0m")
        print("\033[96m║\033[0m                                                                   \033[96m║\033[0m")
        print("\033[96m║\033[0m  \033[92m📊 PERFORMANCE:\033[0m                                                \033[96m║\033[0m")
        print("\033[96m║\033[0m    • SSD: 10-12x faster with 16 threads + BFS                    \033[96m║\033[0m")
        print("\033[96m║\033[0m    • HDD: 3-4x faster with 4 threads + DFS                       \033[96m║\033[0m")
        print("\033[96m║\033[0m    • Average scan rate: 200-500 folders/second (SSD)             \033[96m║\033[0m")
        print("\033[96m║\033[0m                                                                   \033[96m║\033[0m")
        print("\033[96m╚═══════════════════════════════════════════════════════════════════╝\033[0m\n")
        input("Press Enter to return to main menu...")

    def configure_and_run(self):
            self.print_header()
            print("\033[96mCONFIGURATION\033[0m (Type 'h' for help anytime)\n")
            
            # 1. Path
            print("\033[93m1. TARGET PATH\033[0m")
            print("   Example: F:\\ or C:\\Users\\Documents")
            while True:
                raw = self.get_input("   Path", "path")
                clean = normalize_path(raw)
                if os.path.isdir(clean):
                    target_path = clean
                    self.defaults["path"] = clean
                    break
                else:
                    print(f"    \033[91m[!] Directory not found: {raw}\033[0m")

            # 2. Mode
            print("\n\033[93m2. OPERATION MODE\033[0m")
            print("   [D] Delete Mode : ACTUALLY REMOVES EMPTY FOLDERS ONLY")
            print("   [T] Dry Run     : Simulation only (safe, no deletion)")
            mode = self.get_input("   Choice", "mode", ['d', 't'])
            self.defaults["mode"] = mode

            # 3. Hardware
            print("\n\033[93m3. HARDWARE STRATEGY\033[0m")
            print("   [A] Auto (Safe)  - Detects SSD/HDD")
            print("   [S] SSD (Fast)   - 16 threads, BFS")
            print("   [H] HDD (Safe)   - 4 threads, DFS")
            disk = self.get_input("   Choice", "disk", ['a', 's', 'h'])
            self.defaults["disk"] = disk

            # 4. Strategy
            print("\n\033[93m4. SCAN STRATEGY\033[0m")
            print("   [A] Auto - Match hardware")
            print("   [B] BFS  - Breadth-first (parallel)")
            print("   [D] DFS  - Depth-first (sequential)")
            strategy = self.get_input("   Choice", "strategy", ['a', 'b', 'd'])
            self.defaults["strategy"] = strategy

            # 5. Workers
            print("\n\033[93m5. THREAD WORKERS\033[0m")
            print("   [0] Auto (16 for SSD, 4 for HDD)")
            print("   [1-32] Manual thread count")
            workers_input = self.get_input("   Count", "workers")
            try:
                workers = int(workers_input)
                if workers < 0 or workers > 32:
                    print("   \033[91m[!] Using auto (0)\033[0m")
                    workers = 0
            except ValueError:
                workers = 0
            self.defaults["workers"] = workers

            # 6. Depth Limits
            print("\n\033[93m6. DEPTH LIMITS\033[0m")
            print("   Min Depth: Only delete folders at this depth or deeper")
            print("   Max Depth: Stop scanning beyond this depth (default: 10,000)")
            print("   Example: min=2 protects C:\\Program Files\\<folder>")
            
            min_depth_input = self.get_input("   Min Depth", "min_depth")
            try:
                min_depth = int(min_depth_input)
                if min_depth < 0: min_depth = 0
            except ValueError:
                min_depth = 0
            self.defaults["min_depth"] = min_depth
            
            max_depth_input = self.get_input("   Max Depth", "max_depth")
            try:
                max_depth = int(max_depth_input)
                if max_depth < 1: max_depth = 10000
            except ValueError:
                max_depth = 10000
            self.defaults["max_depth"] = max_depth

            # 7. Windows System Folders Quick Exclusions
            exclude_paths = []  # Initialize exclude_paths
            if os.name == 'nt':
                print("\n\033[93m7. WINDOWS SYSTEM FOLDERS (Quick Exclusions)\033[0m")
                print("   Select common folders to automatically exclude:")
                
                windows_defaults = {
                    "Windows": "*:\\Windows*",
                    "Program Files": "*:\\Program Files*",
                    "Program Files (x86)": "*:\\Program Files (x86)*",
                    "ProgramData": "*:\\ProgramData*",
                    "Users": "*:\\Users*",
                    "$RECYCLE.BIN": "*$RECYCLE.BIN*"
                }
                
                print("\n   \033[96m[A]\033[0m All system folders (recommended)")
                print("   \033[96m[C]\033[0m Custom selection")
                print("   \033[96m[N]\033[0m None (skip)")
                
                win_choice = input("   Your choice [\033[1;93mN\033[0m]: ").strip().upper()
                
                if win_choice == 'A':
                    # Add all Windows exclusions
                    for folder_name, pattern in windows_defaults.items():
                        if pattern not in exclude_paths:
                            exclude_paths.append(pattern)
                    print(f"   \033[92m[✓] Added {len(windows_defaults)} Windows system folders to exclusions\033[0m")
                elif win_choice == 'C':
                    print("\n   \033[90mEnter folder numbers to exclude (e.g., 1,3,5):\033[0m")
                    for idx, (name, pattern) in enumerate(windows_defaults.items(), 1):
                        print(f"   \033[96m[{idx}]\033[0m {name:25} ({pattern})")
                    
                    selections = input("   Your selections: ").strip()
                    if selections:
                        try:
                            selected_indices = [int(x.strip()) for x in selections.split(',')]
                            items = list(windows_defaults.items())
                            for idx in selected_indices:
                                if 1 <= idx <= len(items):
                                    pattern = items[idx-1][1]
                                    if pattern not in exclude_paths:
                                        exclude_paths.append(pattern)
                            print(f"   \033[92m[✓] Added {len(selected_indices)} folder(s) to exclusions\033[0m")
                        except (ValueError, IndexError):
                            print("   \033[91m[!] Invalid selection, skipping\033[0m")
                
                time.sleep(1)

            # 8. Additional Filters
            print("\n\033[93m8. ADDITIONAL FILTERS (comma-separated patterns)\033[0m")
            print("   Examples: *.tmp*, node_modules, .git")
            print("   \033[90m(These will be added to any Windows exclusions above)\033[0m")
            
            more_exclude_paths = self.get_list_input("   More Exclude Paths", "exclude_paths")
            exclude_paths.extend(more_exclude_paths)
            self.defaults["exclude_paths"] = exclude_paths
            
            exclude_names = self.get_list_input("   Exclude Names", "exclude_names")
            self.defaults["exclude_names"] = exclude_names
            
            include_names = self.get_list_input("   Include Names (leave empty for all)", "include_names")
            self.defaults["include_names"] = include_names

            # 9. Confirm Action
            print("\n\033[93m9. CONFIRM\033[0m")
            print("   [R] Run Analysis Now")
            print("   [S] Save Config & Run")
            print("   [C] Cancel (return to main menu)")
            print("   [Q] Quit")
            action = input("   Choice [R]: ").strip().lower()

            if action == 's':
                self.save_config()
                print("   \033[92m[✓] Configuration saved to void_walker_config.json\033[0m")
                time.sleep(1)

            if action == 'c':
                return  # Return to main menu
            
            if action == 'q':
                self.confirm_quit()
                return

            # LAUNCH
            self.launch_engine(target_path, mode, disk, strategy, workers, min_depth, max_depth, 
                             exclude_paths, exclude_names, include_names)
            
            # POST-RUN LOOP
            print("\n" + "-"*70)
            cont = input("Press [Enter] to return to Main Menu or 'q' to Quit: ")
            if cont.lower() == 'q':
                self.confirm_quit()

    def load_and_run(self):
        """Load config and offer to run immediately"""
        self.print_header()
        
        if not os.path.exists(self.config_file):
            print("\n\033[91m[!] No saved configuration found.\033[0m")
            print(f"    File not found: {self.config_file}\n")
            input("Press Enter to return to main menu...")
            return
        
        self.defaults = self.load_config()
        
        print("\n\033[96m╔═══ LOADED CONFIGURATION ══════════════════════════════════════════╗\033[0m")
        print("\033[96m║\033[0m \033[92mConfiguration loaded from:\033[0m void_walker_config.json            \033[96m║\033[0m")
        print("\033[96m╚═══════════════════════════════════════════════════════════════════╝\033[0m\n")
        
        print("\033[93mCurrent Settings:\033[0m")
        for key, value in self.defaults.items():
            if isinstance(value, list):
                display_val = ", ".join(value) if value else "none"
            else:
                display_val = str(value)
            print(f"  \033[96m{key:15}\033[0m : {display_val}")
        
        print("\n\033[96m╔═══ OPTIONS ═══════════════════════════════════════════════════════╗\033[0m")
        print("\033[96m║\033[0m  \033[92m[R]\033[0m Run with this configuration                                \033[96m║\033[0m")
        print("\033[96m║\033[0m  \033[93m[E]\033[0m Edit configuration before running                          \033[96m║\033[0m")
        print("\033[96m║\033[0m  \033[90m[M]\033[0m Return to main menu                                        \033[96m║\033[0m")
        print("\033[96m║\033[0m  \033[91m[Q]\033[0m Quit                                                       \033[96m║\033[0m")
        print("\033[96m╚═══════════════════════════════════════════════════════════════════╝\033[0m\n")
        
        choice = input("\033[96mYour choice [R]:\033[0m ").strip().lower()
        
        if choice == '' or choice == 'r':
            # Run immediately with loaded config
            target_path = self.defaults.get("path", os.getcwd())
            mode = self.defaults.get("mode", "t")
            disk = self.defaults.get("disk", "a")
            strategy = self.defaults.get("strategy", "auto")
            workers = self.defaults.get("workers", 0)
            min_depth = self.defaults.get("min_depth", 0)
            max_depth = self.defaults.get("max_depth", 10000)
            exclude_paths = self.defaults.get("exclude_paths", [])
            exclude_names = self.defaults.get("exclude_names", [])
            include_names = self.defaults.get("include_names", [])
            
            self.launch_engine(target_path, mode, disk, strategy, workers, min_depth, max_depth,
                             exclude_paths, exclude_names, include_names)
            
            print("\n" + "-"*70)
            input("Press Enter to return to Main Menu...")
        elif choice == 'e':
            # Go to configuration wizard
            self.configure_and_run()
        elif choice == 'm':
            return  # Return to main menu
        elif choice == 'q':
            self.confirm_quit()

    def save_config(self):
        """Save current configuration"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.defaults, f, indent=4)
        except Exception as e:
            print(f"    [!] Save failed: {e}")
    
    def show_current_config(self):
        """Display current configuration during setup"""
        import shutil
        try:
            cols = shutil.get_terminal_size().columns
        except OSError:
            cols = 80
        
        sep = "="*min(70, cols)
        print(f"\n\033[96m{sep}\033[0m")
        print("\033[93m CURRENT CONFIGURATION\033[0m")
        print(f"\033[96m{sep}\033[0m")
        
        for key, value in self.defaults.items():
            if isinstance(value, list):
                display_val = ", ".join(value) if value else "None"
            elif isinstance(value, bool):
                display_val = "Yes" if value else "No"
            else:
                display_val = str(value)
            print(f"  \033[96m{key:18}\033[0m : {display_val}")
        
        print(f"\033[96m{sep}\033[0m\n")
        input("Press Enter to continue...")

    def load_and_apply_config(self):
        """Deprecated - use load_and_run instead"""
        self.load_and_run()

    def show_cache(self):
        """Display cache status"""
        cmd = [sys.executable, "main.py", "--show-cache"]
        try:
            subprocess.run(cmd)
        except (subprocess.SubprocessError, OSError):
            pass
        input("\nPress Enter to continue...")

    def resume_session(self):
        """Resume last session"""
        self.print_header()
        print("\n\033[93m[!] Resuming last interrupted session...\033[0m")
        print("    This will continue scanning from where it left off.\n")
        
        confirm = input("Continue? [Y/n]: ").strip().lower()
        if confirm and confirm not in ['y', 'yes']:
            return
        
        # CRITICAL: Do NOT pass path with --resume - path comes from database!
        if getattr(sys, 'frozen', False):
            # Running from exe
            cmd = [sys.executable, "--resume"]
        else:
            # Running from Python
            cmd = [sys.executable, "main.py", "--resume"]
        
        if self.defaults.get("mode") == 'd':
            cmd.append("--delete")
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            pass
        
        print("\n" + "-"*70)
        input("Press Enter to return to Main Menu...")

    def launch_engine(self, path, mode, disk, strategy, workers, min_depth, max_depth, 
                     exclude_paths, exclude_names, include_names):
        """Launch engine with all parameters"""
        # Detect if running from compiled exe or Python script
        if getattr(sys, 'frozen', False):
            # Running from PyInstaller exe - sys.executable is the exe itself
            cmd = [sys.executable, path]
        else:
            # Running from Python - need to call main.py
            cmd = [sys.executable, "main.py", path]
        
        # Mode
        if mode == 'd': 
            cmd.append("--delete")
        
        # Hardware
        cmd.append("--disk")
        if disk == 's': 
            cmd.append("ssd")
        elif disk == 'h': 
            cmd.append("hdd")
        else: 
            cmd.append("auto")
        
        # Strategy
        cmd.append("--strategy")
        if strategy == 'b':
            cmd.append("bfs")
        elif strategy == 'd':
            cmd.append("dfs")
        else:
            cmd.append("auto")
        
        # Workers
        if workers > 0:
            cmd.extend(["--workers", str(workers)])
        
        # Depth
        if min_depth > 0:
            cmd.extend(["--min-depth", str(min_depth)])
        if max_depth != 10000:
            cmd.extend(["--max-depth", str(max_depth)])
        
        # Filters
        if exclude_paths:
            cmd.append("--exclude-path")
            cmd.extend(exclude_paths)
        if exclude_names:
            cmd.append("--exclude-name")
            cmd.extend(exclude_names)
        if include_names:
            cmd.append("--include-name")
            cmd.extend(include_names)

        print(f"\n\033[92m[+] Starting Engine...\033[0m\n")
        print(f"\033[90m[i] Interactive Controls Enabled: Press 'H' for help\033[0m\n")
        
        try:
            # Use unbuffered mode for immediate output visibility
            if getattr(sys, 'frozen', False):
                subprocess.run(cmd)
            else:
                # Add -u flag for unbuffered output when running via Python
                cmd.insert(1, '-u')
                subprocess.run(cmd)
        except KeyboardInterrupt:
            pass
        
        # Explicit completion marker
        print("\n" + "="*70)
        print("\033[92m[✓] Engine execution completed\033[0m")
        print("="*70)

if __name__ == "__main__":
    import time
    Menu().main_loop()

