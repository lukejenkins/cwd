"""
Cell War Driver (cwd) - Main Program

This program connects to a cellular modem via serial port,
sends AT commands to gather cell network information,
and logs the results for analysis.
"""
import os
import sys
import time
import signal
from typing import Dict, List, Optional, Any

from config import load_config
from logger import ModemLogger
from modem import ModemCommunicator
from parser import ModemResponseParser


def setup_modem_info_commands() -> List[str]:
    """
    Set up commands to gather static modem information.
    
    Returns:
        List[str]: List of AT commands
    """
    return [
        "AT+CGMI",    # Manufacturer
        "AT+CGMM",    # Model
        "AT+CGMR",    # Firmware version
        "AT+CGSN",    # Serial number
        "AT+CIMI",    # IMSI (SIM identifier)
        "AT+COPS=3,0",  # Set operator format to long alphanumeric
        "AT+COPS?",   # Current operator
    ]


def setup_cell_info_commands() -> List[str]:
    """
    Set up commands to gather cell information.
    
    Returns:
        List[str]: List of AT commands
    """
    return [
        "AT+CSQ",     # Signal quality
        "AT+CREG?",   # GSM network registration
        "AT+CGREG?",  # UMTS network registration
        "AT+CEREG?",  # LTE network registration
        # Add more commands based on your specific modem
    ]


def main():
    """Main function to run the Cell War Driver program."""
    # Load configuration
    config = load_config()
    
    # Initialize logger
    logger = ModemLogger(config["LOG_DIR"], config["LOG_LEVEL"])
    logger.log_info("Cell War Driver starting...")
    
    # Initialize modem communicator
    modem = ModemCommunicator(config, logger)
    
    # Initialize parser
    parser = ModemResponseParser(config["CSV_DIR"], config["CSV_FILENAME"])
    
    # Set up signal handling for graceful exit
    def signal_handler(sig, frame):
        logger.log_info("Signal received, shutting down...")
        modem.disconnect()
        logger.close()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Connect to the modem
        if not modem.connect():
            logger.log_error("Failed to connect to modem. Exiting.")
            return 1
        
        # Initialize the modem
        if not modem.initialize_modem():
            logger.log_error("Failed to initialize modem. Exiting.")
            return 1
        
        # Get static modem information
        logger.log_info("Gathering modem information...")
        for command in setup_modem_info_commands():
            success, response = modem.execute_command(command)
            if success:
                parser.parse_modem_info(command, response)
        
        # Main loop for gathering cell information
        logger.log_info("Starting main monitoring loop...")
        while True:
            for command in setup_cell_info_commands():
                success, response = modem.execute_command(command)
                if success:
                    parser.parse_cell_info(command, response)
            
            # Sleep between iterations
            time.sleep(config["COMMAND_DELAY"] * 2)
    
    except Exception as e:
        logger.log_error(f"Unexpected error: {str(e)}")
        return 1
    
    finally:
        # Clean up
        modem.disconnect()
        logger.close()
        logger.log_info("Cell War Driver shut down.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())