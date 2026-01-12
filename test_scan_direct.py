"""Direct scan test without dashboard to verify scanning works"""
import os
import time

def scan_directory(root, max_depth=2):
    """Simple recursive scan"""
    folders_found = []
    
    def _scan(path, depth):
        if depth > max_depth:
            return
        
        print(f"[{depth}] Scanning: {path}", flush=True)
        
        try:
            items = list(os.scandir(path))
            has_files = any(e.is_file() for e in items if not e.is_symlink())
            subdirs = [e for e in items if e.is_dir() and not e.is_symlink()]
            
            if not has_files and not subdirs:
                folders_found.append(path)
                print(f"  [EMPTY] {path}", flush=True)
            
            for entry in subdirs:
                try:
                    _scan(entry.path, depth + 1)
                except PermissionError:
                    print(f"  [SKIP] Permission denied: {entry.path}", flush=True)
        
        except PermissionError:
            print(f"  [SKIP] Permission denied: {path}", flush=True)
        except Exception as e:
            print(f"  [ERROR] {path}: {e}", flush=True)
    
    start = time.time()
    _scan(root, 0)
    elapsed = time.time() - start
    
    print(f"\n=== RESULTS ===")
    print(f"Empty folders found: {len(folders_found)}")
    print(f"Time: {elapsed:.2f}s")
    
    return folders_found

if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "F:\\"
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    print(f"Testing scan of {root} (max depth: {max_depth})")
    scan_directory(root, max_depth)
