import os
import sys
import subprocess
import json
from utils.validators import normalize_path

class Menu:
    def __init__(self):
        self.config_file = "last_run_config.json"
        self.defaults = self.load_config()

    def run_wizard(self):
        """Entry point for interactive wizard"""
        self.main_loop()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except: pass
        return {"path": os.getcwd(), "mode": "t", "disk": "a"}

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        self.clear()
        print("\033[96m" + "="*60)
        print(" VOID WALKER v4.1 - ENTERPRISE CONSOLE")
        print("="*60 + "\033[0m")

    def get_input(self, prompt, key, valid_options=None):
        """Dynamic input with colored defaults loaded from JSON."""
        default_val = self.defaults.get(key, "")
        
        # Colorize default value (Yellow)
        prompt_str = f"{prompt} [\033[93m{default_val}\033[0m]: "
        
        choice = input(prompt_str).strip()

        if choice == "":
            return default_val
        
        if choice.lower() in ['q', 'quit', 'exit']:
            print("\n[!] Exiting...")
            sys.exit(0)

        if valid_options:
            if choice.lower() in valid_options:
                return choice.lower()
            print(f"    \033[91m[!] Invalid. Options: {', '.join(valid_options)}\033[0m")
            return self.get_input(prompt, key, valid_options)
            
        return choice

    def main_loop(self):
        while True:
            self.print_header()
            
            # 1. Path
            while True:
                raw = self.get_input("1. Target Path", "path")
                clean = normalize_path(raw)
                if os.path.isdir(clean):
                    target_path = clean
                    # Update local default for this session
                    self.defaults["path"] = clean 
                    break
                else:
                    print(f"    \033[91m[!] Directory not found: {raw}\033[0m")

            # 2. Mode
            print("\n2. Operation Mode")
            print("   [D] Delete Mode : ACTUALLY REMOVES FILES")
            print("   [T] Dry Run     : Simulation only")
            mode = self.get_input("   Choice", "mode", ['d', 't'])
            self.defaults["mode"] = mode

            # 3. Disk
            print("\n3. Hardware Strategy")
            print("   [A] Auto (Safe) [S] SSD (Fast) [H] HDD (Sequential)")
            disk = self.get_input("   Choice", "disk", ['a', 's', 'h'])
            self.defaults["disk"] = disk

            # 4. Action
            print("\n4. Confirm")
            print("   [R] Run Analysis")
            print("   [S] Save Defaults & Run")
            action = input("   Choice [R]: ").strip().lower()

            if action == 's':
                self.save_config()

            # LAUNCH
            self.launch_engine(target_path, mode, disk)
            
            # POST-RUN LOOP
            print("\n" + "-"*60)
            cont = input("Press [Enter] to return to Menu or 'q' to Quit: ")
            if cont.lower() == 'q':
                sys.exit(0)

    def launch_engine(self, path, mode, disk):
        cmd = [sys.executable, "main.py", path]
        if mode == 'd': cmd.append("--delete")
        
        cmd.append("--disk")
        if disk == 's': cmd.append("ssd")
        elif disk == 'h': cmd.append("hdd")
        else: cmd.append("auto")

        print(f"\n\033[92m[+] Starting Engine...\033[0m")
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            pass

    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.defaults, f, indent=4)
            print("    [i] Defaults saved.")
        except Exception as e:
            print(f"    [!] Save failed: {e}")

if __name__ == "__main__":
    Menu().main_loop()
