import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = "ai_social_bot") -> logging.Logger:
    """Setup logger con file rotation e console output"""
    
    # Crea directory logs
    Path("logs").mkdir(exist_ok=True)
    
    # Logger principale
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler (con rotation)
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        f"logs/bot_{datetime.now().strftime('%Y%m')}.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
