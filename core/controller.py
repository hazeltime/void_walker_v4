import threading
import time
import sys

class Controller:
    """Listens for user input to Pause/Resume/Save/Config."""
    def __init__(self, engine):
        self.engine = engine
        self.active = False
        self.thread = None
        self.verbose = False

    def start(self):
        self.active = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()

    def stop(self):
        self.active = False

    def _show_help(self):
        print("\n" + "="*60)
        print(" RUNTIME CONTROLS")
        print("="*60)
        print(" [P] Pause/Resume     [S] Save State      [Q] Quit")
        print(" [D] Dashboard Toggle [C] Show Config     [V] Verbose")
        print(" [H] This Help        [ENTER] Continue")
        print("="*60)
        input(" Press ENTER to continue...")

    def _show_config(self):
        cfg = self.engine.config
        print("\n" + "="*60)
        print(" CURRENT CONFIGURATION")
        print("="*60)
        print(f" Root Path:    {cfg.root_path}")
        print(f" Mode:         {'DELETE' if cfg.delete_mode else 'DRY RUN'}")
        print(f" Strategy:     {cfg.strategy}")
        print(f" Disk Type:    {cfg.disk_type.upper()}")
        print(f" Workers:      {cfg.workers}")
        print(f" Min Depth:    {cfg.min_depth}")
        print(f" Max Depth:    {cfg.max_depth}")
        print(f" Excludes:     {', '.join(cfg.exclude_names[:5])}...")
        print("="*60)
        input(" Press ENTER to continue...")

    def _listen(self):
        try:
            import msvcrt
            print("\n[i] Interactive Controls Enabled: Press 'H' for help\n")
            while self.active:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                    
                    if key == 'p':
                        self.engine.paused = not self.engine.paused
                        state = "PAUSED" if self.engine.paused else "RESUMED"
                        self.engine.logger.info(f"{state} by User")
                        print(f"\n[!] {state}")
                    
                    elif key == 'r':
                        if self.engine.paused:
                            self.engine.paused = False
                            self.engine.logger.info("Resumed by User")
                            print("\n[!] RESUMED")
                    
                    elif key == 's':
                        print("\n[!] Saving state...")
                        self.engine.save_state()
                        print("[✓] State saved!")
                    
                    elif key == 'q':
                        print("\n[!] Quit requested...")
                        self.engine.running = False
                    
                    elif key == 'h':
                        was_paused = self.engine.paused
                        self.engine.paused = True
                        self._show_help()
                        self.engine.paused = was_paused
                    
                    elif key == 'c':
                        was_paused = self.engine.paused
                        self.engine.paused = True
                        self._show_config()
                        self.engine.paused = was_paused
                    
                    elif key == 'd':
                        self.engine.dashboard.active = not self.engine.dashboard.active
                        state = "ON" if self.engine.dashboard.active else "OFF"
                        print(f"\n[!] Dashboard {state}")
                    
                    elif key == 'v':
                        self.verbose = not self.verbose
                        state = "ON" if self.verbose else "OFF"
                        print(f"\n[!] Verbose mode {state}")
                
                time.sleep(0.1)
        except ImportError:
            pass  # Not on Windows, skip interactive keys
