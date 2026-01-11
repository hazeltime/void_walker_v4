import sys
import os
import argparse
import time
import sqlite3
from datetime import datetime

# Ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Config
from core.engine import Engine
from ui.menu import Menu
from ui.reporter import Reporter
from utils.logger import setup_logger

def show_cache_status(db_path="void_walker_history.db"):
    """Display cached session information"""
    if not os.path.exists(db_path):
        print("[!] No cache database found.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all sessions
        cursor.execute("SELECT id, timestamp FROM sessions ORDER BY timestamp DESC LIMIT 10")
        sessions = cursor.fetchall()
        
        if not sessions:
            print("[!] No previous sessions found.")
            return
        
        print("\n" + "="*70)
        print(" CACHED SESSIONS")
        print("="*70)
        
        for session_id, timestamp in sessions:
            # Get session stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status='SCANNED' THEN 1 ELSE 0 END) as scanned,
                    SUM(CASE WHEN status='PENDING' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status='ERROR' THEN 1 ELSE 0 END) as errors,
                    SUM(CASE WHEN status='DELETED' THEN 1 ELSE 0 END) as deleted,
                    SUM(CASE WHEN status='WOULD_DELETE' THEN 1 ELSE 0 END) as would_delete
                FROM folders WHERE session_id=?
            """, (session_id,))
            
            stats = cursor.fetchone()
            total, scanned, pending, errors, deleted, would_delete = stats
            
            # Get root path
            cursor.execute("SELECT path FROM folders WHERE session_id=? ORDER BY depth ASC LIMIT 1", (session_id,))
            root = cursor.fetchone()
            root_path = root[0] if root else "Unknown"
            
            completion = (scanned / total * 100) if total > 0 else 0
            
            print(f"\n Session: {session_id}")
            print(f" Time:    {timestamp}")
            print(f" Root:    {root_path}")
            print(f" Status:  {scanned}/{total} scanned ({completion:.1f}% complete)")
            if pending > 0:
                print(f" ⚠ {pending} folders pending (can resume with --resume)")
            if deleted > 0:
                print(f" ✓ {deleted} folders deleted")
            if would_delete > 0:
                print(f" ✓ {would_delete} empty folders identified (dry run)")
            if errors > 0:
                print(f" ✗ {errors} errors")
            print("-"*70)
        
        conn.close()
        print("\n")
        
    except Exception as e:
        print(f"[!] Error reading cache: {e}")

def main():
    # 1. Parse Arguments
    parser = argparse.ArgumentParser(description="Void Walker v4: Enterprise Folder Cleaner", formatter_class=argparse.RawTextHelpFormatter)
    
    # Mode Selection
    parser.add_argument("path", nargs='?', help="Target Root Directory")
    parser.add_argument("--delete", action="store_true", help="Enable DELETION mode (Default is Dry Run)")
    parser.add_argument("--resume", action="store_true", help="Resume a previous interrupted session")
    parser.add_argument("--show-cache", action="store_true", help="Display cached session status and exit")
    
    # Hardware Config
    parser.add_argument("--disk", choices=["ssd", "hdd", "auto"], default="auto", help="Optimize strategy for disk type.\nSSD = BFS/High Concurrency\nHDD = DFS/Low Concurrency")
    parser.add_argument("--workers", type=int, default=0, help="Manual thread count override")
    
    # Filters & Depth
    parser.add_argument("--min-depth", type=int, default=0, help="Minimum depth to start deleting")
    parser.add_argument("--max-depth", type=int, default=100, help="Maximum depth to traverse")
    parser.add_argument("--exclude-path", nargs='*', default=[], help="Glob patterns for full paths to exclude (e.g. *System32*)")
    parser.add_argument("--exclude-name", nargs='*', default=[], help="Glob patterns for folder names to exclude (e.g. .git node_modules)")
    parser.add_argument("--include-name", nargs='*', default=[], help="Strictly include ONLY these folder names")
    
    args = parser.parse_args()

    # Show cache if requested
    if args.show_cache:
        show_cache_status()
        return

    # 2. Interactive Menu (if no path)
    if not args.path:
        Menu().run_wizard()
        return

    # 3. Initialization
    try:
        config = Config(args)
        logger = setup_logger(config.session_id)
        
        logger.info(f"Initializing Void Walker v4 [Session: {config.session_id}]")
        logger.info(f"Target: {config.root_path} | Mode: {'DELETE' if config.delete_mode else 'DRY RUN'}")
        logger.info(f"Strategy: {config.strategy} | Workers: {config.workers}")

        # 4. Execution
        engine = Engine(config, logger)
        engine.start()

        # 5. Reporting
        Reporter(config, engine.db).show_summary()

    except KeyboardInterrupt:
        print("\n[!] User Force Exit")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
