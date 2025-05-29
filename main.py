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
  
See README.md for complete documentation and usage examples.
"""
import os
import sys
import time
import signal
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from config import load_config
from logger import ModemLogger
from modem import ModemCommunicator
from parser import ModemResponseParser
from smart_config import apply_smart_configuration

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

    return parser


def test_modem_connection(config: Dict[str, Any]) -> int:
    """
    Test the modem connection and display basic information.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Set up temporary logging to stdout only
    logger = ModemLogger(config["LOG_DIR"], config["LOG_LEVEL"])
    logger.log_info(f"Testing modem connection on {config['PORT']} at {config['BAUDRATE']} baud...")
    
    # Create a modem communicator
    modem = ModemCommunicator(config, logger)
    
    try:
        # Connect to the modem
        if not modem.connect():
            logger.log_error(f"Failed to connect to modem on {config['PORT']}")
            return 1
        
        logger.log_info(f"Successfully connected to modem on {config['PORT']}")
        
        # Verify the modem is a Quectel EG25
        is_quectel_eg25 = verify_quectel_eg25_modem(modem, logger)
        if not is_quectel_eg25:
            logger.log_error("Modem verification failed. This program is designed for Quectel EG25 modems.")
            logger.log_warning("Test continuing but some commands may not work properly.")
        
        # Basic test commands with friendly descriptions
        test_commands = [
            ("AT", "Basic connectivity test"),
            ("AT+CGMI", "Manufacturer information"),
            ("AT+CGMM", "Model information"),
            ("AT+CGMR", "Firmware version"),
            ("AT+CGSN", "IMEI/Serial number"),
            ("AT+CIMI", "SIM IMSI"),
            ("AT+CSQ", "Signal quality"),
            ("AT+CREG?", "Network registration status"),
            ("AT+COPS?", "Current operator"),
            ("AT+QNWINFO", "Network information"),
        ]
        
        success_count = 0
        modem_info = {}
        
        for cmd, description in test_commands:
            logger.log_info(f"Testing: {description} ({cmd})")
            success, response = modem.execute_command(cmd)
            
            if success:
                success_count += 1
                clean_response = response.replace(cmd, "").replace("OK", "").strip()
                
                # Process specific responses for better output
                if "CGMI:" in response:
                    manufacturer = clean_response.split("+CGMI:")[1].strip() if "+CGMI:" in clean_response else clean_response
                    modem_info["manufacturer"] = manufacturer
                    logger.log_info(f"Manufacturer: {manufacturer}")
                
                elif "CGMM:" in response:
                    model = clean_response.split("+CGMM:")[1].strip() if "+CGMM:" in clean_response else clean_response
                    modem_info["model"] = model
                    logger.log_info(f"Model: {model}")
                
                elif "CGMR:" in response:
                    firmware = clean_response.split("+CGMR:")[1].strip() if "+CGMR:" in clean_response else clean_response
                    modem_info["firmware"] = firmware
                    logger.log_info(f"Firmware: {firmware}")
                
                elif "CGSN:" in response:
                    imei = clean_response.split("+CGSN:")[1].strip() if "+CGSN:" in clean_response else clean_response
                    modem_info["imei"] = imei
                    logger.log_info(f"IMEI: {imei}")
                
                elif "CIMI:" in response:
                    imsi = clean_response.split("+CIMI:")[1].strip() if "+CIMI:" in clean_response else clean_response
                    modem_info["imsi"] = imsi
                    logger.log_info(f"SIM IMSI: {imsi}")
                
                elif "CSQ:" in response:
                    csq_parts = clean_response.split("+CSQ:")[1].strip().split(",") if "+CSQ:" in clean_response else []
                    if len(csq_parts) >= 2:
                        rssi = int(csq_parts[0])
                        rssi_dbm = -113 + (2 * rssi) if rssi < 99 else "Unknown"
                        logger.log_info(f"Signal strength: {rssi_dbm} dBm (CSQ: {rssi})")
                
                elif "COPS:" in response:
                    cops_parts = clean_response.split("+COPS:")[1].strip().split(",") if "+COPS:" in clean_response else []
                    if len(cops_parts) >= 3:
                        operator = cops_parts[2].strip('"')
                        modem_info["operator"] = operator
                        logger.log_info(f"Operator: {operator}")
                
                elif "QNWINFO:" in response:
                    nw_parts = clean_response.split("+QNWINFO:")[1].strip().split(",") if "+QNWINFO:" in clean_response else []
                    if len(nw_parts) >= 4:
                        tech = nw_parts[0].strip('"')
                        band = nw_parts[3].strip('"')
                        logger.log_info(f"Network type: {tech}")
                        logger.log_info(f"Band: {band}")
                
                elif "CREG:" in response:
                    reg_parts = clean_response.split("+CREG:")[1].strip().split(",") if "+CREG:" in clean_response else []
                    if len(reg_parts) >= 2:
                        status_code = int(reg_parts[1].strip())
                        status_text = {
                            0: "Not registered, not searching",
                            1: "Registered, home network",
                            2: "Not registered, searching",
                            3: "Registration denied",
                            4: "Unknown",
                            5: "Registered, roaming"
                        }.get(status_code, f"Unknown ({status_code})")
                        logger.log_info(f"Registration status: {status_text}")
                
                else:
                    if clean_response:
                        logger.log_info(f"Response: {clean_response}")
                    else:
                        logger.log_info("Command executed successfully")
            else:
                logger.log_error(f"Command failed: {response}")
        
        # Show summary
        logger.log_info("-" * 50)
        if modem_info.get("manufacturer") and modem_info.get("model"):
            logger.log_info(f"Modem: {modem_info.get('manufacturer')} {modem_info.get('model')}")
        if modem_info.get("firmware"):
            logger.log_info(f"Firmware: {modem_info.get('firmware')}")
        
        if success_count == len(test_commands):
            logger.log_info("All test commands executed successfully")
            logger.log_info("Modem connection test PASSED")
            return 0
        else:
            logger.log_warning(f"{success_count}/{len(test_commands)} test commands succeeded")
            logger.log_warning("Modem connection test PARTIAL SUCCESS")
            return 0
            
    except Exception as e:
        logger.log_error(f"Error during modem test: {str(e)}")
        return 1
        
    finally:
        # Clean up
        modem.disconnect()
        logger.close()


def scan_serial_ports() -> int:
    """
    Scan for available serial ports and display them.
    
    Returns:
        int: Exit code (0 for success)
    """
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        if not ports:
            print("No serial ports found.")
            return 0
        
        print(f"Found {len(ports)} serial ports:")
        print("-" * 60)
        print(f"{'Port':<15} {'Description':<25} {'Hardware ID':<20}")
        print("-" * 60)
        
        for port in ports:
            print(f"{port.device:<15} {port.description:<25} {port.hwid:<20}")
        
        print("\nTo use a specific port:")
        print("  ./cwd --port <PORT_NAME>")
        print("Example:")
        print("  ./cwd --port /dev/ttyUSB2")
        
        return 0
    except ImportError:
        print("Error: pyserial package is required for port scanning.")
        print("Install it with: pip install pyserial")
        return 1
    except Exception as e:
        print(f"Error scanning ports: {str(e)}")
        return 1


def export_config_to_file(config: Dict[str, Any], filename: str) -> int:
    """
    Export the current configuration to a .env file.
    
    Args:
        config: The configuration dictionary
        filename: Name of the file to export to
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        # Ensure the filename ends with .env
        if not filename.endswith('.env'):
            filename += '.env'
        
        # Create the file
        with open(filename, 'w') as f:
            f.write("# Cell War Driver Configuration File\n")
            f.write("# Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            
            # Serial connection settings
            f.write("# Serial connection settings\n")
            f.write(f"PORT={config['PORT']}\n")
            f.write(f"BAUDRATE={config['BAUDRATE']}\n")
            f.write(f"TIMEOUT={config['TIMEOUT']}\n\n")
            
            # Logging settings
            f.write("# Logging settings\n")
            f.write(f"LOG_DIR={config['LOG_DIR']}\n")
            f.write(f"LOG_LEVEL={config['LOG_LEVEL']}\n\n")
            
            # Command execution settings
            f.write("# Command execution settings\n")
            f.write(f"COMMAND_DELAY={config['COMMAND_DELAY']}\n")
            f.write(f"RETRY_COUNT={config['RETRY_COUNT']}\n\n")
            
            # Output settings
            f.write("# Output settings\n")
            f.write(f"CSV_DIR={config['CSV_DIR']}\n")
            f.write(f"CSV_FILENAME={config['CSV_FILENAME']}\n")
            f.write(f"JSON_DIR={config['JSON_DIR']}\n")
            f.write(f"JSON_FILENAME={config['JSON_FILENAME']}\n\n")
            
            # Database settings
            f.write("# Database settings\n")
            f.write(f"USE_DATABASE={'true' if config['USE_DATABASE'] else 'false'}\n")
            f.write(f"DB_TYPE={config['DB_TYPE']}\n")
            f.write(f"DB_PATH={config['DB_PATH']}\n\n")
            
            # Command cadence settings
            f.write("# Command cadence settings (in seconds)\n")
            f.write(f"FAST_COMMAND_INTERVAL={config['FAST_COMMAND_INTERVAL']}\n")
            f.write(f"MEDIUM_COMMAND_INTERVAL={config['MEDIUM_COMMAND_INTERVAL']}\n")
            f.write(f"SLOW_COMMAND_INTERVAL={config['SLOW_COMMAND_INTERVAL']}\n")
        
        print(f"Configuration exported to: {filename}")
        return 0
    
    except Exception as e:
        print(f"Error exporting configuration: {str(e)}")
        return 1


def show_environment_variables() -> int:
    """
    Show all environment variables and their values.
    
    Returns:
        int: Exit code (0 for success)
    """
    print("Cell War Driver Environment Variables")
    print("=" * 50)
    
    # Get all environment variables
    env_vars = os.environ
    
    # Filter for relevant variables
    cwd_vars = {k: v for k, v in env_vars.items() if k in [
        "PORT", "BAUDRATE", "TIMEOUT", 
        "LOG_DIR", "LOG_LEVEL", 
        "COMMAND_DELAY", "RETRY_COUNT",
        "CSV_DIR", "CSV_FILENAME", "JSON_DIR", "JSON_FILENAME",
        "USE_DATABASE", "DB_TYPE", "DB_PATH",
        "FAST_COMMAND_INTERVAL", "MEDIUM_COMMAND_INTERVAL", "SLOW_COMMAND_INTERVAL"
    ]}
    
    if not cwd_vars:
        print("No Cell War Driver environment variables found.")
        print("You can set environment variables or use a .env file.")
        return 0
    
    # Print them in categories
    categories = {
        "Serial Connection": ["PORT", "BAUDRATE", "TIMEOUT"],
        "Logging": ["LOG_DIR", "LOG_LEVEL"],
        "Command Execution": ["COMMAND_DELAY", "RETRY_COUNT"],
        "Output": ["CSV_DIR", "CSV_FILENAME", "JSON_DIR", "JSON_FILENAME"],
        "Database": ["USE_DATABASE", "DB_TYPE", "DB_PATH"],
        "Command Intervals": ["FAST_COMMAND_INTERVAL", "MEDIUM_COMMAND_INTERVAL", "SLOW_COMMAND_INTERVAL"]
    }
    
    for category, vars in categories.items():
        found = False
        for var in vars:
            if var in cwd_vars:
                if not found:
                    print(f"\n{category} Settings:")
                    print("-" * 30)
                    found = True
                print(f"{var:<25} = {cwd_vars[var]}")
    
    return 0


def list_supported_modems() -> int:
    """
    List all supported modem types and their capabilities.
    
    Returns:
        int: Exit code (0 for success)
    """
    print("Cell War Driver - Supported Modem Types")
    print("=======================================")
    
    supported_modems = [
        {
            "manufacturer": "Quectel",
            "models": ["EG25-G", "EM12-G", "RM500Q", "RM520N"],
            "technologies": ["LTE", "LTE-A", "5G NSA", "5G SA"],
            "command_set": "Quectel",
            "supported_features": [
                "Basic cell information", 
                "Signal quality", 
                "Cell tower information",
                "Neighboring cells",
                "GPS/GNSS support"
            ]
        },
        {
            "manufacturer": "Sierra Wireless",
            "models": ["EM7455", "EM7565", "EM7690"],
            "technologies": ["LTE", "LTE-A"],
            "command_set": "Sierra Wireless",
            "supported_features": [
                "Basic cell information", 
                "Signal quality", 
                "Cell tower information"
            ]
        },
        {
            "manufacturer": "Telit",
            "models": ["LM960", "FN980"],
            "technologies": ["LTE", "LTE-A", "5G NSA", "5G SA"],
            "command_set": "Telit",
            "supported_features": [
                "Basic cell information", 
                "Signal quality", 
                "Full cell scan"
            ]
        }
    ]
    
    for modem in supported_modems:
        print(f"\n{modem['manufacturer']}:")
        print(f"  Models: {', '.join(modem['models'])}")
        print(f"  Technologies: {', '.join(modem['technologies'])}")
        print(f"  Command Set: {modem['command_set']}")
        print("  Supported Features:")
        for feature in modem['supported_features']:
            print(f"    - {feature}")
    
    print("\nNote: Support for some modem types is experimental.")
    print("To use the program with a specific modem type (future feature):")
    print("  ./cwd --modem-type <manufacturer>:<model>")
    
    return 0


def monitor_signal_strength(config: Dict[str, Any]) -> int:
    """
    Monitor signal strength in real-time with a simple display.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Set up temporary logging to stdout only
    logger = ModemLogger(config["LOG_DIR"], config["LOG_LEVEL"])
    logger.log_info(f"Starting signal monitor on {config['PORT']} at {config['BAUDRATE']} baud...")
    
    # Create a modem communicator
    modem = ModemCommunicator(config, logger)
    
    try:
        # Connect to the modem
        if not modem.connect():
            logger.log_error(f"Failed to connect to modem on {config['PORT']}")
            return 1
        
        logger.log_info("Connected to modem. Monitoring signal strength (Ctrl+C to exit)...")
        
        # Verify the modem is a Quectel EG25
        is_quectel_eg25 = verify_quectel_eg25_modem(modem, logger)
        if not is_quectel_eg25:
            logger.log_warning("Modem verification failed. Signal monitoring may not work properly.")
        
        print("\nSignal Monitor - Cell War Driver")
        print("===============================")
        print("Time             | Signal (dBm) | Quality | Technology | Operator")
        print("-" * 75)
        
        # Main monitoring loop
        while True:
            # Get signal quality
            success, response = modem.execute_command("AT+CSQ")
            signal_dbm = "Unknown"
            signal_quality = "Unknown"
            
            if success and "+CSQ:" in response:
                parts = response.split("+CSQ:")[1].strip().split(",")
                if len(parts) >= 2:
                    rssi = int(parts[0].strip())
                    signal_quality = parts[1].strip()
                    if rssi < 99:  # 99 means unknown
                        signal_dbm = f"{-113 + (2 * rssi)}"
            
            # Get technology and operator
            success, tech_response = modem.execute_command("AT+QNWINFO")
            tech = "Unknown"
            operator = "Unknown"
            
            if success and "+QNWINFO:" in tech_response:
                parts = tech_response.split("+QNWINFO:")[1].strip().split(",")
                if len(parts) >= 3:
                    tech = parts[0].strip('"')
                    operator = parts[2].strip('"')
            
            # Print the current status
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"{timestamp} | {signal_dbm:^11} | {signal_quality:^7} | {tech:^10} | {operator}")
            
            # Wait before checking again
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\nSignal monitoring stopped.")
        return 0
        
    except Exception as e:
        logger.log_error(f"Error during signal monitoring: {str(e)}")
        return 1
        
    finally:
        # Clean up
        modem.disconnect()
        logger.close()


def setup_modem_only(config: Dict[str, Any]) -> int:
    """
    Run only the modem setup commands and exit.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Set up temporary logging to stdout only
    logger = ModemLogger(config["LOG_DIR"], config["LOG_LEVEL"])
    logger.log_info(f"Running modem setup on {config['PORT']} at {config['BAUDRATE']} baud...")
    
    # Create a modem communicator
    modem = ModemCommunicator(config, logger)
    
    try:
        # Connect to the modem
        if not modem.connect():
            logger.log_error(f"Failed to connect to modem on {config['PORT']}")
            return 1
        
        logger.log_info("Connected to modem. Running setup commands...")
        
        # Verify the modem is a Quectel EG25
        is_quectel_eg25 = verify_quectel_eg25_modem(modem, logger)
        if not is_quectel_eg25:
            logger.log_error("Modem verification failed. Setup commands are specific to Quectel EG25 modems.")
            logger.log_error("Cannot proceed with setup. Please check your hardware.")
            modem.disconnect()
            logger.close()
            return 1
        
        # Get the setup commands
        commands = setup_modem_commands()
        
        # Initialize the modem first
        if not modem.initialize_modem():
            logger.log_error("Failed to initialize modem.")
            return 1
        
        # Run only the setup commands
        success_count = 0
        total_count = len(commands["setup"])
        
        for cmd in commands["setup"]:
            logger.log_info(f"Executing: {cmd}")
            success, response = modem.execute_command(cmd)
            
            if success:
                success_count += 1
                logger.log_info("Command succeeded")
            else:
                logger.log_warning(f"Command failed: {response}")
        
        # Show summary
        logger.log_info("-" * 50)
        logger.log_info(f"Setup completed: {success_count}/{total_count} commands succeeded")
        
        if success_count == total_count:
            logger.log_info("Modem setup SUCCESSFUL")
            return 0
        elif success_count > 0:
            logger.log_warning("Modem setup PARTIALLY SUCCESSFUL")
            return 0
        else:
            logger.log_error("Modem setup FAILED")
            return 1
            
    except Exception as e:
        logger.log_error(f"Error during modem setup: {str(e)}")
        return 1
        
    finally:
        # Clean up
        modem.disconnect()
        logger.close()


def smart_config_only(config: Dict[str, Any], config_file: str) -> int:
    """
    Run only the smart configuration system and exit.
    
    This function applies the smart configuration system which intelligently
    compares current modem settings with desired values from a YAML configuration
    file and only changes settings that differ from the desired state.
    
    Args:
        config: Configuration dictionary containing connection settings
        config_file: Path to the YAML configuration file
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Set up logging
    logger = ModemLogger(config["LOG_DIR"], config["LOG_LEVEL"])
    logger.log_info(f"Running smart configuration on {config['PORT']} at {config['BAUDRATE']} baud...")
    logger.log_info(f"Using configuration file: {config_file}")
    
    # Create a modem communicator
    modem = ModemCommunicator(config, logger)
    
    try:
        # Connect to the modem
        if not modem.connect():
            logger.log_error(f"Failed to connect to modem on {config['PORT']}")
            return 1
        
        logger.log_info("Connected to modem. Running smart configuration...")
        
        # Verify the modem is a Quectel EG25
        is_quectel_eg25 = verify_quectel_eg25_modem(modem, logger)
        if not is_quectel_eg25:
            logger.log_error("Modem verification failed. Smart configuration is designed for Quectel EG25 modems.")
            logger.log_error("Cannot proceed with smart configuration. Please check your hardware.")
            modem.disconnect()
            logger.close()
            return 1
        
        # Run the smart configuration system
        logger.log_info("Applying smart configuration...")
        success = apply_smart_configuration(modem, config_file, logger)
        
        # Show summary
        logger.log_info("-" * 50)
        if success:
            logger.log_info("Smart configuration SUCCESSFUL")
            logger.log_info("All modem settings have been verified and updated as needed.")
            return 0
        else:
            logger.log_error("Smart configuration FAILED")
            logger.log_error("Some settings could not be applied. Check the logs for details.")
            return 1
            
    except FileNotFoundError:
        logger.log_error(f"Configuration file not found: {config_file}")
        logger.log_error("Please create a YAML configuration file or specify a different path with --config-file")
        return 1
        
    except Exception as e:
        logger.log_error(f"Error during smart configuration: {str(e)}")
        return 1
        
    finally:
        # Clean up
        modem.disconnect()
        logger.close()


def show_detailed_modem_info(config: Dict[str, Any]) -> int:
    """
    Show detailed information about the connected modem.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Set up temporary logging to stdout only
    logger = ModemLogger(config["LOG_DIR"], config["LOG_LEVEL"])
    logger.log_info(f"Getting modem information from {config['PORT']} at {config['BAUDRATE']} baud...")
    
    # Create a modem communicator
    modem = ModemCommunicator(config, logger)
    
    try:
        # Connect to the modem
        if not modem.connect():
            logger.log_error(f"Failed to connect to modem on {config['PORT']}")
            return 1
        
        logger.log_info("Connected to modem. Getting detailed information...")
        
        # Verify the modem is a Quectel EG25
        is_quectel_eg25 = verify_quectel_eg25_modem(modem, logger)
        if not is_quectel_eg25:
            logger.log_warning("Modem verification failed. Some commands may not work properly.")
        
        # Commands to retrieve detailed information
        info_commands = [
            ("AT+CGMI", "Manufacturer"),
            ("AT+CGMM", "Model"),
            ("AT+CGMR", "Firmware Version"),
            ("AT+CGSN", "IMEI/Serial Number"),
            ("AT+QCCID", "SIM ICCID"),
            ("AT+CIMI", "SIM IMSI"),
            ('AT+QMBNCFG="List"', "Carrier Profile"),
            ('AT+QCFG="band"', "Band Configuration"),
            ('AT+QGPSCFG="gnssconfig"', "GNSS Configuration"),
            ("AT+QNWINFO", "Network Information"),
            ("AT+CSQ", "Signal Quality"),
            ("AT+COPS?", "Operator"),
            ('AT+QENG="servingcell"', "Serving Cell Info"),
            ('AT+QENG="neighbourcell"', "Neighbor Cells")
        ]
        
        modem_data = {}
        print("\nDetailed Modem Information")
        print("=========================")
        
        for cmd, description in info_commands:
            print(f"\n{description}:")
            print("-" * (len(description) + 1))
            
            success, response = modem.execute_command(cmd)
            
            if success:
                # Clean up the response
                clean_response = response.replace(cmd, "").replace("OK", "").strip()
                
                # Format the output based on the command
                if "QMBNCFG" in cmd:
                    # Special formatting for MBN list
                    mbn_lines = clean_response.split("\n")
                    formatted_lines = []
                    for line in mbn_lines:
                        if "+QMBNCFG:" in line:
                            formatted_lines.append("  " + line.replace("+QMBNCFG:", "").strip())
                    if formatted_lines:
                        print("\n".join(formatted_lines))
                    else:
                        print("  No carrier profiles found")
                
                elif "QENG=" in cmd:
                    # Special formatting for QENG responses
                    eng_lines = clean_response.split("\n")
                    for line in eng_lines:
                        if "+QENG:" in line:
                            print("  " + line.replace("+QENG:", "").strip())
                
                elif "QCFG=" in cmd or "QGPSCFG=" in cmd:
                    # Special formatting for configuration responses
                    if "+" in clean_response:
                        parts = clean_response.split("+")[1].split(":")
                        if len(parts) > 1:
                            print("  " + parts[1].strip())
                        else:
                            print("  " + clean_response)
                    else:
                        print("  " + clean_response)
                
                else:
                    # Default formatting for simpler responses
                    if "+" in clean_response:
                        parts = clean_response.split("+")
                        for part in parts:
                            if ":" in part:
                                print("  " + part.split(":", 1)[1].strip())
                            elif part.strip():
                                print("  " + part.strip())
                    else:
                        print("  " + clean_response)
            else:
                print(f"  Error: Command failed")
        
        return 0
            
    except Exception as e:
        logger.log_error(f"Error getting modem information: {str(e)}")
        return 1
        
    finally:
        # Clean up
        modem.disconnect()
        logger.close()


def verify_quectel_eg25_modem(modem: ModemCommunicator, logger: ModemLogger) -> bool:
    """
    Verify that the connected modem is a Quectel EG25.
    
    Args:
        modem: The modem communicator instance
        logger: The logger instance
    
    Returns:
        bool: True if the modem is a Quectel EG25, False otherwise
    """
    logger.log_info("Verifying modem type...")
    
    # Check manufacturer
    success, manufacturer_response = modem.execute_command("AT+CGMI")
    if not success:
        logger.log_error("Failed to get modem manufacturer.")
        return False
    
    # Clean up the response
    manufacturer = manufacturer_response.replace("AT+CGMI", "").replace("OK", "").strip()
    if "+CGMI:" in manufacturer_response:
        manufacturer = manufacturer.split("+CGMI:")[1].strip()
    
    if "QUECTEL" not in manufacturer.upper():
        logger.log_error(f"Unsupported modem manufacturer: {manufacturer}. This program requires a Quectel modem.")
        return False
    
    # Check model
    success, model_response = modem.execute_command("AT+CGMM")
    if not success:
        logger.log_error("Failed to get modem model.")
        return False
    
    # Clean up the response
    model = model_response.replace("AT+CGMM", "").replace("OK", "").strip()
    if "+CGMM:" in model_response:
        model = model.split("+CGMM:")[1].strip()
    
    if not (model.upper().startswith("EG25") or "EG25" in model.upper()):
        logger.log_error(f"Unsupported modem model: {model}. This program requires an EG25 modem.")
        logger.log_info("Supported models: EG25-G, EG25-E, EG25-AUT, etc.")
        return False
    
    logger.log_info(f"Verified modem: Quectel {model}")
    return True


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
    
    # Apply remaining command-line argument overrides to config
    if args.csv_dir:
        config["CSV_DIR"] = args.csv_dir
    if args.csv_filename:
        config["CSV_FILENAME"] = args.csv_filename
    if args.json_dir:
        config["JSON_DIR"] = args.json_dir
    if args.json_filename:
        config["JSON_FILENAME"] = args.json_filename
    config["USE_DATABASE"] = args.use_database
    if args.db_type:
        config["DB_TYPE"] = args.db_type
    if args.db_path:
        config["DB_PATH"] = args.db_path
    if args.fast_interval:
        config["FAST_COMMAND_INTERVAL"] = args.fast_interval
    if args.medium_interval:
        config["MEDIUM_COMMAND_INTERVAL"] = args.medium_interval
    if args.slow_interval:
        config["SLOW_COMMAND_INTERVAL"] = args.slow_interval
    
    # If --test-connection is specified, test the modem connection and exit
    if args.test_connection:
        return test_modem_connection(config)
    
    # If --export-config is specified, export the configuration to a file and exit
    if args.export_config:
        return export_config_to_file(config, args.export_config)
    
    # Initialize logger
    logger = ModemLogger(config["LOG_DIR"], config["LOG_LEVEL"])
    logger.log_info("Cell War Driver starting...")
    
    # Log the active configuration
    logger.log_info("Active configuration:")
    logger.log_info(f"  - Port: {config['PORT']}")
    logger.log_info(f"  - Baud rate: {config['BAUDRATE']}")
    logger.log_info(f"  - Command delay: {config['COMMAND_DELAY']}s")
    logger.log_info(f"  - Fast loop interval: {config['FAST_COMMAND_INTERVAL']}s")
    logger.log_info(f"  - Medium loop interval: {config['MEDIUM_COMMAND_INTERVAL']}s")
    logger.log_info(f"  - Slow loop interval: {config['SLOW_COMMAND_INTERVAL']}s")
    
    # Initialize modem communicator
    modem = ModemCommunicator(config, logger)
    
    # Initialize parser with JSON support
    parser = ModemResponseParser(
        config["CSV_DIR"], 
        config["CSV_FILENAME"],
        config["JSON_DIR"],
        config["JSON_FILENAME"],
        logger
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
        
        # Verify that the modem is a Quectel EG25
        if not verify_quectel_eg25_modem(modem, logger):
            logger.log_error("Modem verification failed. This program requires a Quectel EG25 modem.")
            logger.log_error("Please check your hardware and connection settings.")
            modem.disconnect()
            logger.close()
            return 1
        
        # Set up the modem using either traditional setup or smart configuration
        if args.smart_config:
            logger.log_info("Using smart configuration system...")
            if not apply_smart_configuration(modem, args.config_file, logger):
                logger.log_error("Failed to apply smart configuration. Continuing with limited functionality.")
        else:
            logger.log_info("Using traditional modem setup...")
            if not modem_setup(modem, logger):
                logger.log_error("Failed to set up modem. Continuing with limited functionality.")
        
        # Collect static modem information
        if not collect_modem_info(modem, parser, logger):
            logger.log_error("Failed to collect modem information. Continuing with limited functionality.")
        
        # Verify that the modem is a Quectel EG25
        if not verify_quectel_eg25_modem(modem, logger):
            logger.log_error("Modem verification failed. This program requires a Quectel EG25 modem.")
            return 1
        
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