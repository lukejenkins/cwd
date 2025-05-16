"""
Logger module for the Cell War Driver program.

This module handles logging of AT commands, modem responses, and program events.
"""
import os
import logging
from datetime import datetime
from typing import Optional, TextIO


class ModemLogger:
    """Logger for modem communication and program events."""
    
    def __init__(self, log_dir: str, log_level: str = "INFO"):
        """
        Initialize the logger.
        
        Args:
            log_dir: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Create a timestamp for the log file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"{timestamp}_cwd.log")
        
        # Configure logging
        log_level_num = getattr(logging, log_level.upper())
        logging.basicConfig(
            level=log_level_num,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("cwd")
        
        # Create raw communication log file
        self.raw_log_file = os.path.join(log_dir, f"{timestamp}_cwd_raw.log")
        self.raw_log = open(self.raw_log_file, 'w')
        
        self.logger.info(f"Logging initialized. Main log: {log_file}")
        self.logger.info(f"Raw log: {self.raw_log_file}")
    
    def log_command(self, command: str) -> None:
        """
        Log an AT command sent to the modem.
        
        Args:
            command: The AT command string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.logger.debug(f"Command: {command}")
        self.raw_log.write(f"{timestamp} >>> {command}\n")
        self.raw_log.flush()
    
    def log_response(self, response: str) -> None:
        """
        Log a response received from the modem.
        
        Args:
            response: The response string from the modem
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.logger.debug(f"Response: {response}")
        self.raw_log.write(f"{timestamp} <<< {response}\n")
        self.raw_log.flush()
    
    def log_info(self, message: str) -> None:
        """
        Log an informational message.
        
        Args:
            message: The message to log
        """
        self.logger.info(message)
    
    def log_error(self, message: str) -> None:
        """
        Log an error message.
        
        Args:
            message: The error message to log
        """
        self.logger.error(message)
    
    def log_warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: The warning message to log
        """
        self.logger.warning(message)
    
    def close(self) -> None:
        """Close the raw log file."""
        if self.raw_log and not self.raw_log.closed:
            self.raw_log.close()