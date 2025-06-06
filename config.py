"""
Configuration module for the Cell War Driver program.

This module handles loading environment variables from a .env file
and providing configuration values to the rest of the application.
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    """
    Load configuration from .env file and return as a dictionary.
    
    Returns:
        Dict[str, Any]: Dictionary containing configuration values.
        
    Raises:
        FileNotFoundError: If .env file doesn't exist and is required.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Define configuration with default values
    config = {
        # Serial connection settings
        "PORT": os.getenv("PORT", "/dev/ttyUSB0"),
        "BAUDRATE": int(os.getenv("BAUDRATE", "115200")),
        "TIMEOUT": float(os.getenv("TIMEOUT", "1.0")),
        
        # Logging settings
        "LOG_DIR": os.getenv("LOG_DIR", "output"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        
        # Command execution settings
        "COMMAND_DELAY": float(os.getenv("COMMAND_DELAY", "0.5")),
        "RETRY_COUNT": int(os.getenv("RETRY_COUNT", "3")),
        
        # Output settings
        "CSV_DIR": os.getenv("CSV_DIR", "output"),
        "CSV_FILENAME": os.getenv("CSV_FILENAME", "cell_data.csv"),
        "JSON_DIR": os.getenv("JSON_DIR", "output"),
        "JSON_FILENAME": os.getenv("JSON_FILENAME", "modem_info.json"),
        
        # Database settings (for potential future use)
        "USE_DATABASE": os.getenv("USE_DATABASE", "false").lower() == "true",
        "DB_TYPE": os.getenv("DB_TYPE", "sqlite"),
        "DB_PATH": os.getenv("DB_PATH", os.path.join(os.getenv("LOG_DIR", "output"), "cell_data.sqlite")),
        
        # GPSd settings
        "GPSD_SERVER": os.getenv("GPSD_SERVER", "localhost"),
        "GPSD_PORT": int(os.getenv("GPSD_PORT", "2947")),
        
        # Command cadence settings - how often to run different command sets (in seconds)
        "FAST_COMMAND_INTERVAL": float(os.getenv("FAST_COMMAND_INTERVAL", "5.0")),
        "MEDIUM_COMMAND_INTERVAL": float(os.getenv("MEDIUM_COMMAND_INTERVAL", "30.0")),
        "SLOW_COMMAND_INTERVAL": float(os.getenv("SLOW_COMMAND_INTERVAL", "300.0")),
    }
    
    return config