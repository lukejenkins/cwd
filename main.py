# Test comment to refresh analysis
# filepath: c:\Users\ljenkins\Documents\GitHub\cwd\main.py
"""
Cell War Driver (cwd) - Main Program

This program connects to a cellular modem via serial port,
sends AT commands to gather cell network information,
and logs the results for analysis.

Command-Line Usage:
  ./cwd [options]
  
Basic Options:
  --help                Show this help message and exit
  --version             Show the program version and exit
  
Serial Connection Settings:
  --port PORT           Serial port for the modem (default: /dev/ttyUSB0)
  --baudrate BAUDRATE   Baud rate for serial communication (default: 115200)
  --timeout TIMEOUT     Timeout for serial communication in seconds (default: 1.0)
  --scan-ports          Scan for available serial ports and exit
  
Logging Settings:
  --log-dir DIR         Directory for log files (default: output)
  --log-level LEVEL     Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  
Command Execution Settings:
  --command-delay DELAY Delay between commands in seconds (default: 0.5)
  --retry-count COUNT   Number of retries for failed commands (default: 3)
  
Output Settings:
  --csv-dir DIR         Directory for CSV output (default: output)
  --csv-filename NAME   Base filename for cell data CSV (default: cell_data.csv)
  --json-dir DIR        Directory for JSON output (default: output)
  --json-filename NAME  Base filename for modem info JSON (default: modem_info.json)
  
Database Settings:
  --use-database        Enable database storage
  --db-type TYPE        Database type (sqlite only for now) (default: sqlite)
  --db-path PATH        Path to the database file (default: output/cell_data.sqlite)
  
Command Interval Settings:
  --fast-interval SECS  Fast command loop interval in seconds (default: 5.0)
  --medium-interval SECS Medium command loop interval in seconds (default: 30.0)
  --slow-interval SECS  Slow command loop interval in seconds (default: 300.0)
  
Utility Options:
  --list-commands       Display all AT commands used by the program and exit
  --test-connection     Test the modem connection and exit
  --export-config FILE  Export current configuration to a .env file and exit
  --show-env            Show all environment variables and their values
  --list-modems         List all supported modem types and exit
  --modem-info          Show detailed information about the connected modem and exit
  --setup-only          Run only the modem setup commands and exit
  --smart-config        Use smart configuration system (only changes settings that differ from desired values)
  --config-file FILE    Path to YAML configuration file for smart configuration (default: modem_config.yaml)
  --signal-monitor      Monitor signal strength in real-time (simplified mode)
  --oneshot             Run smart config, then each command cycle once, then exit
  
See README.md for complete documentation and usage examples.
"""
import os
import sys
import time
import signal
import json
import argparse
import traceback # Added traceback import
from datetime import datetime
from typing import Any, Dict, Optional, List, Tuple # Added List and Tuple

# Attempt to import gpsd, but make it optional so the program can run without it
try:
    import gpsd as gpsd_client # Use an alias to avoid potential global/local scope issues
except ImportError:
    gpsd_client = None # type: ignore 
    print("gpsd library not found. GPSd functionality will be disabled.")

from config import load_config
from logger import ModemLogger # Assuming ModemLogger is in logger.py
from modem import ModemCommunicator # ModemCommunicator is in modem.py
from parser import ModemResponseParser  # Changed to relative import
from smart_config import apply_smart_configuration  # Changed to relative import

# Version information
__version__ = "1.0.0"
__author__ = "Luke Jenkins"
__license__ = "MIT"


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
            'AT+QOPSCFG="displayrssi",1',        # Enable RSSI display in AT+QOPS scan
            'AT+QOPSCFG="displaybw",1',          # Enable bandwidth display in AT+QOPS scan
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
            "AT+CPIN?",      				# Query SIM PIN status
            "AT+QINISTAT",      			# Query SIM status
            "AT+QCCID",      				# Query SIM ICCID
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
            'AT+QCFG="NWSCANMODEEX"',		# Check network scan mode (extended)
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
            #"AT+QOPS",                        # List the available network information of operators for all neighbor cells #SuperSlow
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
                   command_set: List[str], logger: ModemLogger, command_set_name: str) -> Tuple[int, int]:
    """
    Run a specific set of AT commands and parse their responses.

    Args:
        modem: ModemCommunicator instance.
        parser: ModemResponseParser instance.
        command_set: List of AT commands to execute.
        logger: ModemLogger instance.
        command_set_name: Name of the command set for logging.

    Returns:
        Tuple[int, int]: Number of successful commands, total commands executed.
    """
    success_count = 0
    total_commands = len(command_set)

    if not command_set:
        logger.log_info(f"Command set '{command_set_name}' is empty, skipping.")
        return 0, 0

    logger.log_info(f"--- Running command set: {command_set_name} ---")
    for cmd in command_set:
        logger.log_info(f"Executing: {cmd}")
        success, response = modem.execute_command(cmd)
        if success:
            logger.log_info(f"Successful response for {cmd}: {response.strip()}") 
            parser.parse_modem_info(cmd, response)
            success_count += 1
        else:
            logger.log_warning(f"Command failed: {cmd} - Response: {response}")

    logger.log_info(f"--- Finished command set: {command_set_name} ({success_count}/{total_commands} successful) ---")
    return success_count, total_commands


def oneshot_mode(config: Dict[str, Any], config_file: str) -> int:
    """
    Run smart configuration, then each command cycle once, then exit.

    Args:
        config: Configuration dictionary.
        config_file: Path to the smart configuration YAML file.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    logger = ModemLogger(
        log_dir=config.get("LOG_DIR", "output"),
        log_level=config.get("LOG_LEVEL", "INFO")
    )
    logger.log_info("Starting Cell War Driver in oneshot mode...")

    modem = ModemCommunicator(
        config=config,
        logger=logger
    )

    parser = ModemResponseParser(
        logger=logger,
        csv_dir=config.get("CSV_DIR", "output"),
        csv_filename=config.get("CSV_FILENAME", "cell_data.csv"),
        json_dir=config.get("JSON_DIR", "output"),
        json_filename=config.get("JSON_FILENAME", "modem_info.json")
    )

    try:
        if not modem.connect():
            logger.log_error("Failed to connect to modem. Exiting oneshot mode.")
            return 1
        logger.log_info("Connected to modem.")

        if not modem.initialize_modem():
            logger.log_warning("Modem initialization failed. Continuing, but some commands might behave unexpectedly.")

        logger.log_info("Applying smart configuration...")
        smart_config_success = apply_smart_configuration(modem, config_file, logger)
        if smart_config_success:
            logger.log_info("Smart configuration applied successfully.")
        else:
            logger.log_warning("Smart configuration failed or had issues. Continuing with command cycles.")

        all_commands = setup_modem_commands()

        command_sets_to_run = [
            "setup", "modem_info", "gnss_info", "network_config",
            "fast_loop", "medium_loop", "slow_loop"
        ]
        total_successful_commands = 0
        total_executed_commands = 0

        for set_name in command_sets_to_run:
            command_set = all_commands.get(set_name, [])
            if command_set:
                s_count, t_count = run_command_set(modem, parser, command_set, logger, set_name)
                total_successful_commands += s_count
                total_executed_commands += t_count
            else:
                logger.log_info(f"Command set '{set_name}' not found or is empty, skipping.")

        logger.log_info(f"All command cycles executed. Total successful: {total_successful_commands}/{total_executed_commands}")
        logger.log_info("Oneshot mode completed successfully.")
        return 0

    except Exception as e:
        logger.log_error(f"An error occurred during oneshot mode: {str(e)}")
        import traceback
        logger.log_error(traceback.format_exc())
        return 1
    finally:
        if modem and modem.connected:
            modem.disconnect()
        if logger:
            logger.close()


def scan_serial_ports() -> int:
    """
    Scan for available serial ports and display them.
    
    Returns:
        int: Exit code (0 for success)
    """
    print("Scanning for available serial ports...")
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        if ports:
            print("Available serial ports:")
            for port in ports:
                print(f"  {port.device} - {port.description}")
        else:
            print("No serial ports found.")
    except ImportError:
        print("Error: pyserial not installed. Install with: pip install pyserial")
        return 1
    return 0


def show_environment_variables() -> int:
    """
    Show all environment variables and their values.
    
    Returns:
        int: Exit code (0 for success)
    """
    print("Environment Variables:")
    print("=====================")
    config = load_config()
    for key, value in config.items():
        print(f"{key}: {value}")
    return 0


def list_supported_modems() -> int:
    """
    List all supported modem types.
    
    Returns:
        int: Exit code (0 for success)
    """
    print("Supported Modem Types:")
    print("====================")
    print("  - Quectel EG25-G")
    print("  - Other AT command compatible modems (limited support)")
    return 0


def show_detailed_modem_info(config: Dict[str, Any]) -> int:
    """
    Show detailed information about the connected modem.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    logger = ModemLogger(
        log_dir=config.get("LOG_DIR", "output"),
        log_level=config.get("LOG_LEVEL", "INFO")
    )
    
    modem = ModemCommunicator(config=config, logger=logger)
    
    try:
        if not modem.connect():
            logger.log_error("Failed to connect to modem")
            return 1
            
        if not modem.initialize_modem():
            logger.log_error("Failed to initialize modem")
            return 1
            
        parser = ModemResponseParser(
            csv_dir=config.get("CSV_DIR", "output"),
            csv_filename=config.get("CSV_FILENAME", "cell_data.csv"),
            json_dir=config.get("JSON_DIR", "output"),
            json_filename=config.get("JSON_FILENAME", "modem_info.json"),
            logger=logger
        )
        
        # Collect modem information
        collect_modem_info(modem, parser, logger)
        
        logger.log_info("Modem information collection completed")
        return 0
        
    except Exception as e:
        logger.log_error(f"Error collecting modem info: {str(e)}")
        return 1
    finally:
        if modem and modem.connected:
            modem.disconnect()
        if logger:
            logger.close()


def setup_modem_only(config: Dict[str, Any]) -> int:
    """
    Run only the modem setup commands.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    logger = ModemLogger(
        log_dir=config.get("LOG_DIR", "output"),
        log_level=config.get("LOG_LEVEL", "INFO")
    )
    
    modem = ModemCommunicator(config=config, logger=logger)
    
    try:
        if not modem.connect():
            logger.log_error("Failed to connect to modem")
            return 1
            
        # Run modem setup
        success = modem_setup(modem, logger)
        
        if success:
            logger.log_info("Modem setup completed successfully")
            return 0
        else:
            logger.log_error("Modem setup failed")
            return 1
            
    except Exception as e:
        logger.log_error(f"Error during modem setup: {str(e)}")
        return 1
    finally:
        if modem and modem.connected:
            modem.disconnect()
        if logger:
            logger.close()


def smart_config_only(config: Dict[str, Any], config_file: str) -> int:
    """
    Run only the smart configuration system.
    
    Args:
        config: Configuration dictionary
        config_file: Path to the YAML configuration file
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    logger = ModemLogger(
        log_dir=config.get("LOG_DIR", "output"),
        log_level=config.get("LOG_LEVEL", "INFO")
    )
    
    modem = ModemCommunicator(config=config, logger=logger)
    
    try:
        if not modem.connect():
            logger.log_error("Failed to connect to modem")
            return 1
            
        if not modem.initialize_modem():
            logger.log_warning("Modem initialization failed, continuing anyway")
            
        # Apply smart configuration
        success = apply_smart_configuration(modem, config_file, logger)
        
        if success:
            logger.log_info("Smart configuration completed successfully")
            return 0
        else:
            logger.log_error("Smart configuration failed")
            return 1
            
    except Exception as e:
        logger.log_error(f"Error during smart configuration: {str(e)}")
        return 1
    finally:
        if modem and modem.connected:
            modem.disconnect()
        if logger:
            logger.close()


def monitor_signal_strength(config: Dict[str, Any]) -> int:
    """
    Monitor signal strength in real-time.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    logger = ModemLogger(
        log_dir=config.get("LOG_DIR", "output"),
        log_level=config.get("LOG_LEVEL", "INFO")
    )
    
    modem = ModemCommunicator(config=config, logger=logger)
    
    try:
        if not modem.connect():
            logger.log_error("Failed to connect to modem")
            return 1
            
        if not modem.initialize_modem():
            logger.log_error("Failed to initialize modem")
            return 1
            
        logger.log_info("Starting signal strength monitoring... Press Ctrl+C to stop")
        
        # Signal monitoring loop
        while True:
            success, response = modem.execute_command("AT+CSQ")
            if success:
                logger.log_info(f"Signal quality: {response.strip()}")
            else:
                logger.log_warning("Failed to get signal quality")
                
            time.sleep(2)  # Monitor every 2 seconds
            
    except KeyboardInterrupt:
        logger.log_info("Signal monitoring stopped by user")
        return 0
    except Exception as e:
        logger.log_error(f"Error during signal monitoring: {str(e)}")
        return 1
    finally:
        if modem and modem.connected:
            modem.disconnect()
        if logger:
            logger.close()


def get_gpsd_fix(config: Dict[str, Any], logger: ModemLogger) -> Optional[Dict[str, Any]]:
    """
    Connects to GPSd, fetches the current GPS fix, and returns structured data.

    Args:
        config: Application configuration dictionary.
        logger: Application logger instance.

    Returns:
        A dictionary containing GPS fix data if successful, None otherwise.
    """
    if gpsd_client is None:
        logger.log_warning("GPSd library not available. Skipping GPSd fix.")
        return None
    try:
        gpsd_server = config.get("GPSD_SERVER", "localhost")
        gpsd_port = config.get("GPSD_PORT", 2947)
        
        logger.log_debug(f"Attempting to connect to GPSd at {gpsd_server}:{gpsd_port}")
        gpsd_client.connect(host=gpsd_server, port=gpsd_port)
        logger.log_debug("Successfully connected to GPSd.")
        
        packet = gpsd_client.get_current()
        # gpsd_client.close() # gpsd-py3 handles connection implicitly; explicit close not typically needed here.

        # packet.mode: 0=no mode, 1=no fix, 2=2D fix, 3=3D fix
        # getattr is used for safety as GpsResponse attributes are dynamic.
        current_mode = getattr(packet, 'mode', 0)

        if current_mode >= 2:  # We have a 2D or 3D fix
            logger.log_debug(f"GPSd mode {current_mode} fix detected. Extracting data.")

            # Helper function to safely extract values, calling methods if needed
            def safe_getattr(obj, attr_name, default=None):
                """Safely get attribute value, calling it if it's a method."""
                try:
                    value = getattr(obj, attr_name, default)
                    # If it's a callable (method), call it to get the actual value
                    if callable(value):
                        return value()
                    return value
                except Exception:
                    return default

            # Prioritize altMSL for altitude, fallback to 'alt'
            # altMSL: Altitude (Mean Sea Level) in meters.
            # alt: Altitude (Height Above Ellipsoid or MSL if MSL not separately reported) in meters.
            altitude_val = safe_getattr(packet, 'altMSL', None)
            if altitude_val is None:
                altitude_val = safe_getattr(packet, 'alt', None)
            
            # Extract GNSS time and ensure it's JSON serializable
            gnss_time_val = safe_getattr(packet, 'time', None)
            # Convert to string immediately to avoid isoformat attribute error
            if gnss_time_val is not None:
                # Just convert to string directly - simplest and most reliable approach
                gnss_time_val = str(gnss_time_val)
                # Add Z if it looks like an ISO format but doesn't already end with Z
                if 'T' in gnss_time_val and not gnss_time_val.endswith('Z'):
                    gnss_time_val += "Z"

            fix_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "latitude": safe_getattr(packet, 'lat', None),
                "longitude": safe_getattr(packet, 'lon', None),
                "altitude": altitude_val,
                "speed": safe_getattr(packet, 'speed', None),      # Speed over ground in meters/second
                "course": safe_getattr(packet, 'track', None),     # Course over ground, degrees from true north
                "gnss_time": gnss_time_val,   # ISO8601 timestamp from GNSS device
                "lock_status": current_mode,                  # 0=no mode, 1=no fix, 2=2D, 3=3D
                # TPV status: 0=NO_FIX, 1=FIX, 2=DGPS_FIX. This is a basic quality indicator.
                "signal_quality": safe_getattr(packet, 'status', None), 
                "satellites_used": safe_getattr(packet, 'sats', None) # Number of satellites used in solution
            }

            # A 2D/3D fix must have latitude and longitude to be considered valid.
            if fix_data["latitude"] is not None and fix_data["longitude"] is not None:
                logger.log_info(
                    f"GPSd Fix: Lat={fix_data['latitude']:.6f}, Lon={fix_data['longitude']:.6f}, "
                    f"Alt={fix_data['altitude']}, Speed={fix_data['speed']}, Course={fix_data['course']}"
                )
                return fix_data
            else:
                logger.log_warning(
                    f"GPSd: Mode {current_mode} fix, but latitude/longitude data is missing from packet."
                )
                return None
            
        elif current_mode == 1:
            logger.log_info("GPSd: No fix yet (mode 1). Waiting for satellite lock.")
            return None
        else:  # mode == 0 or other unexpected mode
            logger.log_info(f"GPSd: No GPS data or inactive (mode {current_mode}).")
            return None

    except ConnectionRefusedError:
        logger.log_error(f"GPSd connection refused. Ensure GPSd is running at {config.get('GPSD_SERVER', 'localhost')}:{config.get('GPSD_PORT', 2947)}.")
        return None
    except gpsd_client.NoFixError:
        logger.log_warning("GPSd: No fix could be obtained from GPSd (NoFixError).")
        return None
    except AttributeError as e:
        # This might catch issues if GpsResponse is missing 'mode' or other fundamental attributes
        logger.log_error(f"GPSd: Error accessing packet attribute: {e}. The GPSd packet might be malformed or incomplete.")
        return None
    except Exception as e:
        logger.log_error(f"An unexpected error occurred while fetching GPSd data: {e}")
        return None

def run_main_loop(config: Dict[str, Any], args) -> int:
    """
    Run the main Cell War Driver loop.
    
    Args:
        config: Configuration dictionary
        args: Parsed command line arguments
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    logger = ModemLogger(
        log_dir=config.get("LOG_DIR", "output"),
        log_level=config.get("LOG_LEVEL", "INFO")
    )
    
    modem = ModemCommunicator(config=config, logger=logger)
    
    parser = ModemResponseParser(
        csv_dir=config.get("CSV_DIR", "output"),
        csv_filename=config.get("CSV_FILENAME", "cell_data.csv"),
        json_dir=config.get("JSON_DIR", "output"),
        json_filename=config.get("JSON_FILENAME", "modem_info.json"),
        logger=logger
    )
    
    try:
        if not modem.connect():
            logger.log_error("Failed to connect to modem")
            return 1
            
        if args.smart_config:
            if not modem.initialize_modem():
                logger.log_warning("Modem initialization failed, continuing anyway.")
            
            logger.log_info("Applying smart configuration...")
            if not apply_smart_configuration(modem, args.config_file, logger):
                logger.log_warning("Smart configuration failed. Continuing with main loop.")
        else:
            if not modem_setup(modem, logger):
                logger.log_error("Failed to setup modem")
                return 1
            
        # Collect static modem information
        collect_modem_info(modem, parser, logger)
        
        commands = setup_modem_commands()
        
        logger.log_info("Starting main monitoring loop... Press Ctrl+C to stop")
        
        # Main loop timers
        last_fast_loop_time = 0
        last_medium_loop_time = 0
        last_slow_loop_time = 0
        
        while True:
            current_time = time.time()
            
            # Attempt to get GPSd fix at the start of each loop iteration
            gpsd_fix = get_gpsd_fix(config, logger)
            if gpsd_fix:
                parser.save_gpsd_data(gpsd_fix)

            # Fast loop
            if current_time - last_fast_loop_time >= config.get("FAST_INTERVAL", 5.0):
                run_command_set(modem, parser, commands["fast_loop"], logger, "fast_loop")
                last_fast_loop_time = current_time

            # Medium loop
            if current_time - last_medium_loop_time >= config.get("MEDIUM_INTERVAL", 30.0):
                run_command_set(modem, parser, commands["medium_loop"], logger, "medium_loop")
                last_medium_loop_time = current_time

            # Slow loop
            if current_time - last_slow_loop_time >= config.get("SLOW_INTERVAL", 300.0):
                run_command_set(modem, parser, commands["slow_loop"], logger, "slow_loop")
                last_slow_loop_time = current_time
            
            # Minimum sleep time to prevent high CPU usage
            time.sleep(0.1)

    except KeyboardInterrupt:
        logger.log_info("Cell War Driver stopped by user.")
        return 0
    except Exception as e:
        logger.log_error(f"Error in main loop: {str(e)}")
        logger.log_error(traceback.format_exc())
        return 1
    finally:
        if modem and modem.connected:
            modem.disconnect()
        if logger:
            logger.close()


class CustomFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    """Custom formatter that combines RawDescriptionHelpFormatter and ArgumentDefaultsHelpFormatter."""
    pass


def setup_argument_parser() -> argparse.ArgumentParser:
    """
    Set up command-line argument parser with all available options.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="""
Cell War Driver (cwd) - A tool for gathering cellular network information

This program connects to a cellular modem via serial port, sends AT commands to
gather cell network information, and logs the results for analysis. It supports various
modem types and cellular technologies including LTE, 5G, and other protocols.
""",
        formatter_class=CustomFormatter,
        epilog="""
Examples:
  # Basic usage with default settings
  ./cwd
  
  # Specify a different serial port and increase logging level
  ./cwd --port /dev/ttyUSB2 --log-level DEBUG
  
  # Change the timing of command intervals
  ./cwd --fast-interval 10 --medium-interval 60 --slow-interval 600
  
  # Customize output locations
  ./cwd --csv-dir /path/to/data --json-dir /path/to/data
  
  # Run utility commands
  ./cwd --list-commands
  ./cwd --test-connection
  ./cwd --scan-ports
  ./cwd --export-config my_config.env
  ./cwd --show-env
"""
    )
    
    # Version information
    parser.add_argument('--version', action='version', 
                        version=f'Cell War Driver v{__version__} - by {__author__}')
    
    # Serial connection settings
    serial_group = parser.add_argument_group("Serial Connection Settings")
    serial_group.add_argument("--port", type=str, default="/dev/ttyUSB0",
                       help="Serial port for the modem")
    serial_group.add_argument("--baudrate", type=int, default=115200,
                       help="Baud rate for serial communication")
    serial_group.add_argument("--timeout", type=float, default=1.0,
                       help="Timeout for serial communication in seconds")
    serial_group.add_argument("--scan-ports", action="store_true", default=False,
                       help="Scan for available serial ports")
    
    # Logging settings
    logging_group = parser.add_argument_group("Logging Settings")
    logging_group.add_argument("--log-dir", type=str, default="output",
                       help="Directory for log files")
    logging_group.add_argument("--log-level", type=str, default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                       help="Logging level")
    
    # Command execution settings
    cmd_group = parser.add_argument_group("Command Execution Settings")
    cmd_group.add_argument("--command-delay", type=float, default=0.5,
                       help="Delay between commands in seconds")
    cmd_group.add_argument("--retry-count", type=int, default=3,
                       help="Number of retries for failed commands")
    
    # Output settings
    output_group = parser.add_argument_group("Output Settings")
    output_group.add_argument("--csv-dir", type=str, default="output",
                       help="Directory for CSV output")
    output_group.add_argument("--csv-filename", type=str, default="cell_data.csv",
                       help="Base filename for cell data CSV")
    output_group.add_argument("--json-dir", type=str, default="output",
                       help="Directory for JSON output")
    output_group.add_argument("--json-filename", type=str, default="modem_info.json",
                       help="Base filename for modem info JSON")
    
    # Database settings
    db_group = parser.add_argument_group("Database Settings")
    db_group.add_argument("--use-database", action="store_true", default=False,
                       help="Enable database storage")
    db_group.add_argument("--db-type", type=str, default="sqlite",
                       help="Database type (sqlite only for now)")
    db_group.add_argument("--db-path", type=str, default="output/cell_data.sqlite",
                       help="Path to the database file")
    
    # GPSd settings
    gpsd_group = parser.add_argument_group("GPSd Settings")
    gpsd_group.add_argument("--gpsd-server", type=str,
                            help="GPSd server address (default: localhost from .env or code default)")
    gpsd_group.add_argument("--gpsd-port", type=int,
                            help="GPSd server port (default: 2947 from .env or code default)")
                            
    # Command cadence settings
    interval_group = parser.add_argument_group("Command Interval Settings")
    interval_group.add_argument("--fast-interval", type=float, default=5.0,
                       help="Fast command loop interval in seconds")
    interval_group.add_argument("--medium-interval", type=float, default=30.0,
                       help="Medium command loop interval in seconds")
    interval_group.add_argument("--slow-interval", type=float, default=300.0,
                       help="Slow command loop interval in seconds")
    
    # Utility options
    util_group = parser.add_argument_group("Utility Options")
    util_group.add_argument("--list-commands", action="store_true", default=False,
                      help="Display all AT commands used by the program and exit")
    util_group.add_argument("--test-connection", action="store_true", default=False,
                      help="Test the modem connection and exit")
    util_group.add_argument("--export-config", type=str, metavar="FILENAME",
                      help="Export current configuration to a .env file and exit")
    util_group.add_argument("--show-env", action="store_true", default=False,
                      help="Show all environment variables and their values")
    util_group.add_argument("--list-modems", action="store_true", default=False,
                      help="List all supported modem types and exit")
    util_group.add_argument("--modem-info", action="store_true", default=False,
                      help="Show detailed information about the connected modem and exit")
    util_group.add_argument("--setup-only", action="store_true", default=False,
                      help="Run only the modem setup commands and exit")
    util_group.add_argument("--smart-config", action="store_true", default=False,
                      help="Use smart configuration system (only changes settings that differ from desired values)")
    util_group.add_argument("--config-file", type=str, default="modem_config.yaml",
                      help="Path to YAML configuration file for smart configuration")
    util_group.add_argument("--signal-monitor", action="store_true", default=False,
                      help="Monitor signal strength in real-time (simplified mode)")
    util_group.add_argument("--oneshot", action="store_true", default=False,
                      help="Run smart config, then each command cycle once, then exit")

    return parser


def main():
    """Main function to run the Cell War Driver program."""
    # Parse command-line arguments
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Load configuration from .env file first
    config = load_config()
    
    # Apply command-line argument overrides to config early
    # so they are available for utility functions
    if args.port:
        config["PORT"] = args.port
    if args.baudrate:
        config["BAUDRATE"] = args.baudrate
    if args.timeout:
        config["TIMEOUT"] = args.timeout
    if args.log_dir:
        config["LOG_DIR"] = args.log_dir
    if args.log_level:
        config["LOG_LEVEL"] = args.log_level
    if args.command_delay:
        config["COMMAND_DELAY"] = args.command_delay
    if args.retry_count:
        config["RETRY_COUNT"] = args.retry_count
    if args.gpsd_server:
        config["GPSD_SERVER"] = args.gpsd_server
    if args.gpsd_port:
        config["GPSD_PORT"] = args.gpsd_port
    
    # If --list-commands is specified, display all command sets and exit
    if args.list_commands:
        print("Cell War Driver - AT Commands")
        print("============================")
        commands = setup_modem_commands()
        for category, cmd_list in commands.items():
            print(f"\n{category.replace('_', ' ').title()} Commands:")
            print("-" * (len(category) + 10))
            for cmd in cmd_list:
                print(f"  {cmd}")
        return 0
    
    # If --scan-ports is specified, scan for available serial ports and exit
    if args.scan_ports:
        return scan_serial_ports()
    
    # If --show-env is specified, show all environment variables and exit
    if args.show_env:
        return show_environment_variables()
        
    # If --list-modems is specified, list all supported modem types and exit
    if args.list_modems:
        return list_supported_modems()
        
    # If --modem-info is specified, show detailed modem information and exit
    if args.modem_info:
        return show_detailed_modem_info(config)
        
    # If --setup-only is specified, run only the modem setup commands and exit
    if args.setup_only:
        return setup_modem_only(config)
        
    # If --smart-config is specified, run only the smart configuration system and exit
    if args.smart_config:
        return smart_config_only(config, args.config_file)
        
    # If --signal-monitor is specified, monitor signal strength in real-time and exit
    if args.signal_monitor:
        return monitor_signal_strength(config)
    
    # If --oneshot is specified, run smart config, then each command cycle once, then exit
    if args.oneshot:
        return oneshot_mode(config, args.config_file)

    # Default behavior: Run the main Cell War Driver loop
    return run_main_loop(config, args)


if __name__ == "__main__":
    sys.exit(main())