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
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from config import load_config
from logger import ModemLogger
from modem import ModemCommunicator
from parser import ModemResponseParser


def setup_modem_commands() -> Dict[str, List[str]]:
    """
    Set up all modem commands organized by purpose.
    
    Returns:
        Dict[str, List[str]]: Dictionary of command lists by category
    """
    commands = {
        # Setup commands to configure the modem
        "setup": [
            "AT+CMEE=2",                         # Set the error reporting to verbose
            "AT+CTZU=3",                         # Enable automatic time zone update via NITZ and update LOCAL time to RTC
            'AT+QFPLMNCFG="Delete","all"',       # Clear the FPLMN list
            "AT+QGPSEND",                        # Power off the GNSS functionality so we can configure it
            'AT+QGPSCFG="outport","usbnmea"',    # GNSS - Set the output port to "USB NMEA", one of the TTYs presented to the host OS
            'AT+QGPSCFG="nmeasrc",1',            # GNSS - Enable use of the AT+QGPSGNMEA command to output NMEA sentences to the AT port
            'AT+QGPSCFG="gpsnmeatype",31',       # GNSS - Turn on all GPS NMEA Sentences
            'AT+QGPSCFG="glonassnmeatype",7',    # GNSS - Turn on all GLONASS NMEA Sentences
            'AT+QGPSCFG="galileonmeatype",1',    # GNSS - Turn on all Galileo NMEA Sentences 
            'AT+QGPSCFG="beidounmeatype",3',     # GNSS - Turn on all Beidou NMEA Sentences
            'AT+QGPSCFG="gsvextnmeatype",1',     # GNSS - Turn on Extended GGSV
            'AT+QGPSCFG="gnssconfig",1',         # GNSS - Turn on all supported GNSS constellations
            'AT+QGPSCFG="autogps",1',            # GNSS - Enable the GNSS functionality to run automatically on module restart
            'AT+QGPSCFG="agpsposmode",0',        # GNSS - Configure GNSS to operate in standalone mode only. No AGPS.
            'AT+QGPSCFG="fixfreq",10',           # GNSS - Set NMEA Output Frequency to 10Hz
            'AT+QGPSCFG="1pps",1',               # GNSS - (possibly) turn on 1PPS output to somewhere
            'AT+QGPSCFG="gnssrawdata",31,0',     # GNSS - Turn on raw GNSS output, all constellations, to the NMEA port
            "AT+QGPS=1",                         # Power on the GNSS functionality.
        ],
        
        # One-time query commands for static modem information
        "modem_info": [
            "AT+CGMI",     					# Query module manufacturer
            "AT+CGMM",        				# Query module model
            "AT+CGMR",        				# Query module revision
            "AT+CGSN",        				# Query module serial number
            # "AT+CICCID",      				# Query SIM ICCID #FIXME
            "AT+CIMI",        				# Query SIM IMSI
            'AT+QMBNCFG="List"',    	    # Get the full list of MBNs and versions:
        ],
        
        # One-time query commands for GPS configuration
        "gnss_info": [
            "AT+QGPS?",						# GNSS - Power - Check
            'AT+QGPSCFG="outport"',			# GNSS - Check all of the things we set above
            'AT+QGPSCFG="nmeasrc"',			# GNSS - Check all of the things we set above
            'AT+QGPSCFG="gpsnmeatype"',		# GNSS - Check all of the things we set above
            'AT+QGPSCFG="glonassnmeatype"',	# GNSS - Check all of the things we set above
            'AT+QGPSCFG="galileonmeatype"',	# GNSS - Check all of the things we set above
            'AT+QGPSCFG="beidounmeatype"',	# GNSS - Check all of the things we set above
            'AT+QGPSCFG="gsvextnmeatype"',	# GNSS - Check all of the things we set above
            'AT+QGPSCFG="gnssconfig"',		# GNSS - Check all of the things we set above
            'AT+QGPSCFG="autogps"',			# GNSS - Check all of the things we set above
            'AT+QGPSCFG="agpsposmode"',		# GNSS - Check all of the things we set above
            'AT+QGPSCFG="fixfreq"',			# GNSS - Check all of the things we set above
            'AT+QGPSCFG="1pps"',			# GNSS - Check all of the things we set above
            'AT+QGPSCFG="gnssrawdata"',		# GNSS - Check all of the things we set above
        ],
        
        # One-time query commands for network configuration
        "network_config": [
            "AT+CTZU?",						# Read Automatic Time Zone Update configuration
            'AT+QCFG="band"',				# Read configured LTE bands
            'AT+QCFG="NWSCANMODE"',			# Check network scan mode (RAT limitations)
            'AT+QOPSCFG="scancontrol"',		# Check what bands are set to be scanned 
            'AT+QNWLOCK="common/lte"',		# Check if there are any LTE network locking settings
            'AT+QNWLOCK="common/4g"',		# Check if there are any 4g network locking settings
            'AT+QFPLMNCFG="list"',			# Check FPMLN List
            "AT+CIND=?",					# Enumerate what will be returned by the "AT+CIND?" command 
        ],
        
        # Loop commands that run frequently
        "fast_loop": [
            "AT+CSQ",                # Signal quality
            "AT+CREG?",              # GSM network registration
            "AT+CGREG?",             # UMTS network registration
            "AT+CEREG?",             # LTE network registration
            "AT+QCSQ",               # LTE signal quality
            "AT+QNETINFO=2,1",       # Query rsssnr of LTE network
            "AT+QNWINFO",            # LTE network information
            "AT+QSPN",               # Service provider name
            "AT+CIND?",              # Command of Control Instructions
            'AT+QENG="servingcell"', # Query the information of serving cell
        ],
        
        # Loop commands that run at medium frequency
        "medium_loop": [
            "AT+CFUN?",       # How much <fun> are we having?
            "AT+CGATT?",          # Read the current service state
            "AT+COPS?",           # Query the current network operator
            "AT+QNETINFO=2,4",    # Query DRX of LTE network
            'AT+QENG="neighbourcell"', # Query the information of neighbour cells
        ],
        
        # Loop commands that run less frequently
        "slow_loop": [
            "AT+QNETINFO=2,2",                # Query timingadvance of LTE network
            "AT+CCLK?",                       # Read the real-time clock
            "AT+QLTS",                        # Obtain the Latest Time Synchronized Through Network
            'AT+QGPSGNMEA="GGA"',             # Get one GGA NMEA sentance
            'AT+QGPSGNMEA="RMC"',             # Get one RMC NMEA sentance
            'AT+QGPSGNMEA="GSV"',             # Get one GSV NMEA sentance
            'AT+QGPSGNMEA="GSA"',             # Get one GSA NMEA sentance
            'AT+QGPSGNMEA="VTG"',             # Get one VTG NMEA sentance
            'AT+QGPSGNMEA="GNS"',             # Get one GNS NMEA sentance
            'AT+QGPSCFG="estimation_error"',  # Get the current GNSS Quality of signal
        ]
    }
    
    return commands


def modem_setup(modem: ModemCommunicator, logger: ModemLogger) -> bool:
    """
    Perform initial modem setup with commands from the README.
    
    Args:
        modem: The modem communicator instance
        logger: The logger instance
    
    Returns:
        bool: True if setup was successful, False otherwise
    """
    logger.log_info("Setting up modem...")
    
    commands = setup_modem_commands()
    
    # Run basic initialization first
    if not modem.initialize_modem():
        logger.log_error("Failed to initialize modem.")
        return False
    
    # Run setup commands to configure the modem
    for cmd in commands["setup"]:
        success, response = modem.execute_command(cmd)
        if not success:
            logger.log_error(f"Failed to execute setup command: {cmd}")
            # Continue with other commands even if one fails
    
    logger.log_info("Modem setup completed.")
    return True


def collect_modem_info(modem: ModemCommunicator, parser: ModemResponseParser, logger: ModemLogger) -> bool:
    """
    Collect static modem information.
    
    Args:
        modem: The modem communicator instance
        parser: The parser instance
        logger: The logger instance
    
    Returns:
        bool: True if information collection was successful, False otherwise
    """
    logger.log_info("Collecting modem information...")
    
    commands = setup_modem_commands()
    success_count = 0
    command_count = 0
    
    # Run modem info queries
    for cmd in commands["modem_info"]:
        command_count += 1
        success, response = modem.execute_command(cmd)
        if success:
            parser.parse_modem_info(cmd, response)
            success_count += 1
        else:
            logger.log_warning(f"Failed to execute modem info command: {cmd}")
    
    # Run GPS configuration queries
    for cmd in commands["gnss_info"]:
        command_count += 1
        success, response = modem.execute_command(cmd)
        if success:
            parser.parse_modem_info(cmd, response)
            success_count += 1
        else:
            logger.log_warning(f"Failed to execute GPS config command: {cmd}")
    
    # Run network configuration queries
    for cmd in commands["network_config"]:
        command_count += 1
        success, response = modem.execute_command(cmd)
        if success:
            parser.parse_modem_info(cmd, response)
            success_count += 1
        else:
            logger.log_warning(f"Failed to execute network config command: {cmd}")
    
    success_rate = (success_count / command_count * 100) if command_count > 0 else 0
    logger.log_info(f"Modem information collection completed. Success rate: {success_rate:.1f}%")
    
    return success_count > 0


def run_command_set(modem: ModemCommunicator, parser: ModemResponseParser, 
                   command_set: List[str], logger: ModemLogger) -> Tuple[int, int]:
    """
    Run a set of commands and parse the responses.
    
    Args:
        modem: The modem communicator instance
        parser: The parser instance
        command_set: List of commands to execute
        logger: The logger instance
    
    Returns:
        Tuple[int, int]: (success_count, command_count)
    """
    success_count = 0
    command_count = 0
    
    for cmd in command_set:
        command_count += 1
        success, response = modem.execute_command(cmd)
        if success:
            parser.parse_cell_info(cmd, response)
            success_count += 1
        else:
            logger.log_warning(f"Failed to execute command: {cmd}")
    
    return success_count, command_count


def main():
    """Main function to run the Cell War Driver program."""
    # Load configuration
    config = load_config()
    
    # Initialize logger
    logger = ModemLogger(config["LOG_DIR"], config["LOG_LEVEL"])
    logger.log_info("Cell War Driver starting...")
    
    # Initialize modem communicator
    modem = ModemCommunicator(config, logger)
    
    # Initialize parser with JSON support
    parser = ModemResponseParser(
        config["CSV_DIR"], 
        config["CSV_FILENAME"],
        config["JSON_DIR"],
        config["JSON_FILENAME"]
    )
    
    # Set up signal handling for graceful exit
    def signal_handler(sig, frame):
        logger.log_info("Signal received, shutting down...")
        modem.disconnect()
        logger.close()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get all command sets
    commands = setup_modem_commands()
    
    # Variables for timing the command loops
    fast_last_run = 0
    medium_last_run = 0
    slow_last_run = 0
    
    try:
        # Connect to the modem
        if not modem.connect():
            logger.log_error("Failed to connect to modem. Exiting.")
            return 1
        
        # Set up the modem
        if not modem_setup(modem, logger):
            logger.log_error("Failed to set up modem. Continuing with limited functionality.")
        
        # Collect static modem information
        if not collect_modem_info(modem, parser, logger):
            logger.log_error("Failed to collect modem information. Continuing with limited functionality.")
        
        # Main loop for gathering cell information
        logger.log_info("Starting main monitoring loop...")
        
        while True:
            current_time = time.time()
            
            # Run fast loop commands
            if current_time - fast_last_run >= config["FAST_COMMAND_INTERVAL"]:
                logger.log_info("Running fast loop commands...")
                success, total = run_command_set(modem, parser, commands["fast_loop"], logger)
                logger.log_info(f"Fast loop completed. Success: {success}/{total}")
                fast_last_run = current_time
            
            # Run medium loop commands
            if current_time - medium_last_run >= config["MEDIUM_COMMAND_INTERVAL"]:
                logger.log_info("Running medium loop commands...")
                success, total = run_command_set(modem, parser, commands["medium_loop"], logger)
                logger.log_info(f"Medium loop completed. Success: {success}/{total}")
                medium_last_run = current_time
            
            # Run slow loop commands
            if current_time - slow_last_run >= config["SLOW_COMMAND_INTERVAL"]:
                logger.log_info("Running slow loop commands...")
                success, total = run_command_set(modem, parser, commands["slow_loop"], logger)
                logger.log_info(f"Slow loop completed. Success: {success}/{total}")
                slow_last_run = current_time
            
            # Sleep a short time to prevent CPU hogging
            time.sleep(1.0)
    
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