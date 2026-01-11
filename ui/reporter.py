import json

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
