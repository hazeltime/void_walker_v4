import logging
import os

def setup_logger(session_id):
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    logger = logging.getLogger("VoidWalker")
    logger.setLevel(logging.INFO)
    
    # File Handler
    fh = logging.FileHandler(f"logs/{session_id}.log", encoding='utf-8')
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    
    logger.addHandler(fh)
    return logger
