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
            "max_depth": 100,
            "exclude_paths": [],
            "exclude_names": [],
            "include_names": [],
            "resume": False
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    saved = json.load(f)
                    defaults.update(saved)
            except: 
                pass
        
        return defaults

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        self.clear()
        print("\033[96m" + "="*60)
        print(" VOID WALKER v4.1 - ENTERPRISE CONSOLE")
        print("="*60 + "\033[0m")

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

    def get_input(self, prompt, key, valid_options=None):
        """Dynamic input with colored defaults loaded from JSON."""
        default_val = self.defaults.get(key, "")
        
        # Format default for display
        if isinstance(default_val, list):
            display_default = ", ".join(default_val) if default_val else "none"
        else:
            display_default = str(default_val)
        
        # Colorize default value (Yellow)
        prompt_str = f"{prompt} [\033[93m{display_default}\033[0m]: "
        
        choice = input(prompt_str).strip()

        if choice == "":
            return default_val
        
        if choice.lower() in ['q', 'quit', 'exit']:
            print("\n[!] Exiting...")
            sys.exit(0)
        
        if choice.lower() == 'h' or choice.lower() == 'help':
            self.print_help()
            return self.get_input(prompt, key, valid_options)

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
            print("\n[!] Exiting...")
            sys.exit(0)
        
        if choice.lower() == 'none' or choice.lower() == 'n':
            return []
        
        # Split by comma and clean
        items = [item.strip() for item in choice.split(',') if item.strip()]
        return items

    def main_loop(self):
        while True:
            self.print_header()
            
            # === SPECIAL ACTIONS ===
            print("\033[92mSPECIAL ACTIONS:\033[0m")
            print("  [C] View Cache Status   [L] Load Saved Config")
            print("  [R] Resume Last Session [H] Help\n")
            
            special = input("Choose action or press Enter to configure: ").strip().lower()
            
            if special == 'c':
                self.show_cache()
                continue
            elif special == 'l':
                self.load_and_apply_config()
                continue
            elif special == 'r':
                self.resume_session()
                continue
            elif special == 'h':
                self.print_help()
                continue
            elif special in ['q', 'quit', 'exit']:
                sys.exit(0)
            
            # === CONFIGURATION ===
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
            print("   [D] Delete Mode : ACTUALLY REMOVES FILES")
            print("   [T] Dry Run     : Simulation only (safe)")
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
            except:
                workers = 0
            self.defaults["workers"] = workers

            # 6. Depth Limits
            print("\n\033[93m6. DEPTH LIMITS\033[0m")
            print("   Min Depth: Only delete folders at this depth or deeper")
            print("   Max Depth: Stop scanning beyond this depth")
            print("   Example: min=2 protects C:\\Program Files\\<folder>")
            
            min_depth_input = self.get_input("   Min Depth", "min_depth")
            try:
                min_depth = int(min_depth_input)
                if min_depth < 0: min_depth = 0
            except:
                min_depth = 0
            self.defaults["min_depth"] = min_depth
            
            max_depth_input = self.get_input("   Max Depth", "max_depth")
            try:
                max_depth = int(max_depth_input)
                if max_depth < 1: max_depth = 100
            except:
                max_depth = 100
            self.defaults["max_depth"] = max_depth

            # 7. Filters
            print("\n\033[93m7. FILTERS (comma-separated patterns)\033[0m")
            print("   Examples: *.tmp*, node_modules, .git")
            
            exclude_paths = self.get_list_input("   Exclude Paths", "exclude_paths")
            self.defaults["exclude_paths"] = exclude_paths
            
            exclude_names = self.get_list_input("   Exclude Names", "exclude_names")
            self.defaults["exclude_names"] = exclude_names
            
            include_names = self.get_list_input("   Include Names (leave empty for all)", "include_names")
            self.defaults["include_names"] = include_names

            # 8. Confirm Action
            print("\n\033[93m8. CONFIRM\033[0m")
            print("   [R] Run Analysis Now")
            print("   [S] Save Config & Run")
            print("   [Q] Quit")
            action = input("   Choice [R]: ").strip().lower()

            if action == 's':
                self.save_config()
                print("   \033[92m[✓] Configuration saved to void_walker_config.json\033[0m")
                time.sleep(1)

            if action == 'q':
                sys.exit(0)

            # LAUNCH
            self.launch_engine(target_path, mode, disk, strategy, workers, min_depth, max_depth, 
                             exclude_paths, exclude_names, include_names)
            
            # POST-RUN LOOP
            print("\n" + "-"*60)
            cont = input("Press [Enter] to return to Menu or 'q' to Quit: ")
            if cont.lower() == 'q':
                sys.exit(0)

    def launch_engine(self, path, mode, disk, strategy, workers, min_depth, max_depth, 
                     exclude_paths, exclude_names, include_names):
        """Launch engine with all parameters"""
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
        
        # Workers
        if workers > 0:
            cmd.extend(["--workers", str(workers)])
        
        # Depth
        if min_depth > 0:
            cmd.extend(["--min-depth", str(min_depth)])
        if max_depth != 100:
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
            subprocess.run(cmd)
        except KeyboardInterrupt:
            pass

    def save_config(self):
        """Save current configuration"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.defaults, f, indent=4)
        except Exception as e:
            print(f"    [!] Save failed: {e}")

    def load_and_apply_config(self):
        """Load saved config and show confirmation"""
        self.defaults = self.load_config()
        print("\n\033[92m[✓] Configuration loaded from void_walker_config.json\033[0m")
        print("\nCurrent settings:")
        for key, value in self.defaults.items():
            print(f"  {key}: {value}")
        input("\nPress Enter to continue...")

    def show_cache(self):
        """Display cache status"""
        cmd = [sys.executable, "main.py", "--show-cache"]
        try:
            subprocess.run(cmd)
        except:
            pass
        input("\nPress Enter to continue...")

    def resume_session(self):
        """Resume last session"""
        print("\n\033[93m[!] Resuming last interrupted session...\033[0m")
        cmd = [sys.executable, "main.py", self.defaults.get("path", os.getcwd()), "--resume"]
        if self.defaults.get("mode") == 'd':
            cmd.append("--delete")
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    import time
    Menu().main_loop()

