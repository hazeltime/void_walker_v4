"""Database migration script - Add new columns for session resume"""
import sqlite3

db_path = "void_walker_history.db"

# Use context manager to ensure connection is closed even if exception occurs
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()

    # Check if columns exist, add if missing
    try:
        cursor.execute("ALTER TABLE sessions ADD COLUMN root_path TEXT")
        print("✓ Added root_path column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("• root_path column already exists")
        else:
            raise

    try:
        cursor.execute("ALTER TABLE sessions ADD COLUMN completed INTEGER DEFAULT 0")
        print("✓ Added completed column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("• completed column already exists")
        else:
            raise

    conn.commit()

print("\n✓ Database migration complete!")
