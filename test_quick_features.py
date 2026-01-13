"""Quick test of new features."""
import sys
import os
import argparse
from config.settings import Config
from utils.logger import setup_logger
from core.engine import Engine

# Create minimal args with all required attributes
class Args:
    def __init__(self):
        self.path = os.path.join(os.getcwd(), "test_scan_temp")
        self.workers = 2
        self.delete = False
        self.resume = False
        self.disk = 'auto'
        self.strategy = 'auto'
        self.min_depth = 1
        self.max_depth = 100
        self.exclude_path = []
        self.exclude_name = []
        self.include_name = []

args = Args()

# Configure for test
config = Config(args)

logger = setup_logger(config.session_id)
engine = Engine(config, logger)

print("\n" + "="*70)
print("  TESTING NEW FEATURES")
print("="*70)
print(f"  Target: {config.root_path}")
print(f"  Workers: {config.workers}")
print(f"  Mode: {'DELETE' if config.delete_mode else 'DRY RUN'}")
print("="*70 + "\n")

# Run full scan with cleanup (this should show final summary)
engine.start()

print("\n" + "="*70)
print("  TEST COMPLETE")
print("="*70)
