"""
Logging utilities for Tech Adoption Reality Checker
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """
    Set up logger with console and file handlers

    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler (if log file specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

    return logger

def get_default_logger(module_name: str):
    """
    Get default logger for a module with standard log file

    Args:
        module_name: Name of the module requesting logger

    Returns:
        Logger instance
    """
    log_dir = Path(__file__).parent.parent.parent / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    # Daily log file
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = log_dir / f'{today}_system.log'

    return setup_logger(module_name, str(log_file))
