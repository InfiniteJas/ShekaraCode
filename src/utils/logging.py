# src/utils/logging.py
import logging
from typing import Optional
import sys

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    if level:
        logger.setLevel(level.upper())
    
    return logger