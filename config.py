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
    }
    
    return config