import os
import time
import platform
import subprocess
from datetime import datetime

class Config:
    def __init__(self, args):
        self.args = args
        
        # CRITICAL: Resume mode should NOT accept a path argument
        if args.resume and args.path:
            raise ValueError("Cannot specify path with --resume flag. Path is loaded from resume state.")
        
        # Handle resume mode - load from database
        if args.resume:
            from data.database import Database
            last_session = Database.get_last_incomplete_session("void_walker_history.db")
            
            if not last_session:
                raise ValueError("No incomplete session found to resume")
            
            print(f"\033[93m[*] Resuming session: {last_session['session_id']}\033[0m")
            print(f"    Path: {last_session['root_path']}")
            print(f"    Started: {last_session['timestamp']}\n")
            
            # Use the previous session ID and load its config
            self.session_id = last_session['session_id']
            self.root_path = last_session['root_path']
            
            # Validate resumed path exists and is accessible
            if not self.root_path:
                raise ValueError("Resume path is empty or None")
            
            if not os.path.exists(self.root_path):
                raise ValueError(f"Resume path no longer exists: {self.root_path}\n"
                               f"  (Drive may be unmounted or path was deleted)")
            
            if not os.path.isdir(self.root_path):
                raise ValueError(f"Resume path is not a directory: {self.root_path}")
            
            try:
                # Test read permissions by attempting to list directory
                os.listdir(self.root_path)
            except PermissionError:
                raise ValueError(f"No permission to access resume path: {self.root_path}")
            except OSError as e:
                raise ValueError(f"Cannot access resume path: {self.root_path}\n  Error: {e}")
            
            # Load saved config values
            saved = last_session['config']
            self.delete_mode = saved.get('delete_mode', args.delete)
            self.min_depth = saved.get('min_depth', args.min_depth)
            self.max_depth = saved.get('max_depth', args.max_depth)
            self.exclude_paths = saved.get('exclude_paths', args.exclude_path)
            self.exclude_names = saved.get('exclude_names', args.exclude_name + [".git", "$RECYCLE.BIN", "System Volume Information"])
            self.include_names = saved.get('include_names', args.include_name)
            self.disk_type = saved.get('disk_type', 'auto')
            self.strategy = saved.get('strategy', 'BFS')
            self.workers = saved.get('workers', 16)
            
            # Don't create new session, we're resuming
            self.timestamp = last_session['timestamp']
            self.db_path = "void_walker_history.db"
            self.resume_mode = True
            return
        
        # Normal mode - create new session
        # Normalize path: handle drive letters, relative paths, etc.
        if args.path:
            path = args.path.strip()
            # Handle drive letter without trailing slash (F: -> F:\\)
            if len(path) == 2 and path[1] == ':':
                path = path + '\\\\'
            self.root_path = os.path.abspath(path)
        else:
            self.root_path = None
        
        self.delete_mode = args.delete
        self.resume_mode = args.resume
        
        # Filters
        self.min_depth = args.min_depth
        self.max_depth = args.max_depth
        self.exclude_paths = args.exclude_path
        self.exclude_names = args.exclude_name + [".git", "$RECYCLE.BIN", "System Volume Information"]
        self.include_names = args.include_name

        # Session
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"session_{self.timestamp}"
        self.db_path = "void_walker_history.db"

        # Hardware Strategy
        self.disk_type = self._detect_disk(args.disk)
        
        # Scan Strategy - explicit or auto-derived
        if hasattr(args, 'strategy') and args.strategy and args.strategy != "auto":
            self.strategy = args.strategy.upper()
        else:
            self.strategy = "BFS" if self.disk_type == "ssd" else "DFS"
        
        # Concurrency Tuning
        if args.workers > 0:
            self.workers = args.workers
        else:
            # SSD = High threads, HDD = Low threads
            self.workers = 16 if self.disk_type == "ssd" else 4

    def _detect_disk(self, user_choice):
        """Enhanced disk detection using Windows PowerShell or platform heuristics"""
        if user_choice != "auto":
            return user_choice
        
        if not self.root_path or not os.path.exists(self.root_path):
            return "hdd"  # Safe default
        
        # Extract drive letter (Windows specific)
        if os.name == 'nt' and len(self.root_path) >= 2 and self.root_path[1] == ':':
            drive_letter = self.root_path[0]
            
            try:
                # Use PowerShell to query disk type
                ps_cmd = f"Get-PhysicalDisk | Where-Object {{$_.DeviceID -eq (Get-Partition -DriveLetter {drive_letter}).DiskNumber}} | Select-Object -ExpandProperty MediaType"
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_cmd],
                    capture_output=True,
                    text=True,
                    timeout=2  # Reduced timeout for faster tests
                )
                
                if result.returncode == 0:
                    media_type = result.stdout.strip().lower()
                    if "ssd" in media_type or "nvme" in media_type:
                        return "ssd"
                    elif "hdd" in media_type:
                        return "hdd"
            except subprocess.TimeoutExpired:
                print("\033[90m[i] Disk detection timeout, defaulting to HDD\033[0m")
            except (FileNotFoundError, OSError) as e:
                print(f"\033[90m[i] PowerShell unavailable: {e}, defaulting to HDD\033[0m")
            
            # Heuristic: C: drive often SSD in modern systems
            if drive_letter.lower() == 'c':
                return "ssd"
        
        # Safe default for auto-detect failure
        return "hdd"

    def save_to_db(self, db):
        """Save current configuration to database for resume functionality"""
        config_dict = {
            'delete_mode': self.delete_mode,
            'min_depth': self.min_depth,
            'max_depth': self.max_depth,
            'exclude_paths': self.exclude_paths,
            'exclude_names': self.exclude_names,
            'include_names': self.include_names,
            'disk_type': self.disk_type,
            'strategy': self.strategy,
            'workers': self.workers
        }
        db.save_config(config_dict, self.root_path) 
