import os

def normalize_path(raw_path):
    """
    Cleans inputs like:
    - "E:\"  (Windows Copy Path artifact)
    - 'E:/'  (Unix style)
    - E:     (Drive root)
    """
    if raw_path is None: 
        return ""
    
    # 1. Strip surrounding quotes (User input artifact)
    path = raw_path.strip('"').strip("'").strip()
    
    # Handle empty after stripping
    if not path:
        return ""
    
    # 2. Normalize Slashes ( / -> \ on Windows)
    path = os.path.normpath(path)
    
    # 3. Handle Drive Root special case
    # os.path.normpath("E:") returns "E:", but python requires "E:\" to verify it as a dir sometimes
    if len(path) == 2 and path[1] == ':':
        path = path + "\\"
        
    return path

def validate_target_path(path):
    """Checks if path exists and permissions are sufficient."""
    clean = normalize_path(path)
    
    if not clean:
        return False, "Path cannot be empty."
    
    if not os.path.exists(clean):
        return False, f"Path does not exist: {clean}"
        
    if not os.path.isdir(clean):
        return False, f"Target is not a directory: {clean}"
        
    try:
        # Test read permission
        with os.scandir(clean):
            pass
    except PermissionError:
        return False, f"Permission denied accessing: {clean}"
        
    return True, "OK"
