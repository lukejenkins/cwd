"""
Logger module for the Cell War Driver program.

This module handles logging of AT commands, modem responses, and program events.
"""
import os
import logging
from datetime import datetime
from typing import Optional, TextIO, Dict, Any
import json


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
        self.log_dir = log_dir
        self.log_level = log_level_num
    
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

    def _log(self, level: str, message: str) -> None:
        """Internal method to log messages at a specific level."""
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if level == "DEBUG":
            self.logger.debug(message)
        elif level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "CRITICAL":
            self.logger.critical(message)
        self.raw_log.write(f"{timestamp_str} {level}: {message}\n")
        self.raw_log.flush()

    def log_debug(self, message: str) -> None:
        """Logs a debug message."""
        if self.log_level <= logging.DEBUG:
            self._log("DEBUG", message)

    def log_gpsd_data(self, gpsd_data: Dict[str, Any]) -> None:
        """Logs GPSd data to a separate file and to the main log."""
        if not self.log_dir:
            return

        timestamp_prefix = datetime.now().strftime("%Y%m%d_%H%M%S")
        gpsd_log_filename = os.path.join(self.log_dir, f"{timestamp_prefix}_gpsd_data.json")

        try:
            # Create a JSON-safe copy of the data
            json_safe_data = {}
            for key, value in gpsd_data.items():
                try:
                    # Test if the value is JSON serializable
                    json.dumps(value)
                    json_safe_data[key] = value
                except (TypeError, ValueError):
                    # If not serializable, convert to string representation
                    json_safe_data[key] = str(value) if value is not None else None
            
            with open(gpsd_log_filename, "a") as f:
                json.dump(json_safe_data, f)
                f.write("\n") # Add a newline for separation if logging multiple entries
            self.log_info(f"GPSd data logged to {gpsd_log_filename}")
            # Also log a summary to the main log
            summary = f"GPSd data: time={json_safe_data.get('gnss_time')}, lat={json_safe_data.get('latitude')}, lon={json_safe_data.get('longitude')}, alt={json_safe_data.get('altitude')}, fix={json_safe_data.get('lock_status')}"
            self._log("INFO", summary)
        except Exception as e:
            self.log_error(f"Failed to log GPSd data: {e}")

    def close(self) -> None:
        """Close the raw log file."""
        if self.raw_log and not self.raw_log.closed:
            self.raw_log.close()