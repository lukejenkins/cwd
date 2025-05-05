"""
Modem module for the Cell War Driver program.

This module handles communication with the cellular modem via serial port.
"""
import time
import serial
from typing import Dict, List, Tuple, Optional, Any

from logger import ModemLogger


class ModemCommunicator:
    """Handles communication with the cellular modem."""
    
    def __init__(self, config: Dict[str, Any], logger: ModemLogger):
        """
        Initialize the modem communicator.
        
        Args:
            config: Configuration dictionary
            logger: Logger for modem communication
        """
        self.port = config["PORT"]
        self.baudrate = config["BAUDRATE"]
        self.timeout = config["TIMEOUT"]
        self.command_delay = config["COMMAND_DELAY"]
        self.retry_count = config["RETRY_COUNT"]
        self.logger = logger
        self.serial = None
        self.connected = False
    
    def connect(self) -> bool:
        """
        Connect to the modem.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            # Clear any pending data
            if self.serial.in_waiting:
                self.serial.reset_input_buffer()
            
            self.connected = True
            self.logger.log_info(f"Connected to modem on {self.port} at {self.baudrate} baud")
            return True
            
        except serial.SerialException as e:
            self.logger.log_error(f"Failed to connect to modem: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the modem."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.logger.log_info("Disconnected from modem")
        self.connected = False
    
    def send_command(self, command: str, wait_time: float = None) -> str:
        """
        Send a command to the modem and return the response.
        
        Args:
            command: AT command to send
            wait_time: Custom time to wait for response (overrides command_delay)
            
        Returns:
            str: Response from the modem
            
        Raises:
            RuntimeError: If not connected to modem
        """
        if not self.connected or not self.serial or not self.serial.is_open:
            self.logger.log_error("Not connected to modem")
            raise RuntimeError("Not connected to modem")
        
        # Add \r if not already present
        if not command.endswith('\r'):
            command += '\r'
        
        self.logger.log_command(command.strip())
        
        # Send the command
        self.serial.write(command.encode('utf-8'))
        
        # Wait for response
        if wait_time is None:
            wait_time = self.command_delay
        time.sleep(wait_time)
        
        # Read response
        response = ""
        while self.serial.in_waiting:
            chunk = self.serial.read(self.serial.in_waiting).decode('utf-8', errors='replace')
            response += chunk
            # Small delay to allow for more data to arrive
            time.sleep(0.1)
        
        self.logger.log_response(response.strip())
        return response
    
    def execute_command(self, command: str, retries: int = None) -> Tuple[bool, str]:
        """
        Execute a command with retry logic and response checking.
        
        Args:
            command: AT command to execute
            retries: Number of retries (defaults to self.retry_count)
            
        Returns:
            Tuple[bool, str]: Success status and response
        """
        if retries is None:
            retries = self.retry_count
        
        attempt = 0
        while attempt <= retries:
            try:
                response = self.send_command(command)
                
                # Check for common error responses
                if "ERROR" in response:
                    self.logger.log_warning(f"Command '{command.strip()}' returned error: {response}")
                    attempt += 1
                    if attempt <= retries:
                        time.sleep(self.command_delay)
                        continue
                    return False, response
                
                # Success
                return True, response
                
            except Exception as e:
                self.logger.log_error(f"Error executing command '{command.strip()}': {str(e)}")
                attempt += 1
                if attempt <= retries:
                    time.sleep(self.command_delay)
                    continue
                return False, str(e)
        
        return False, "Max retries exceeded"
    
    def initialize_modem(self) -> bool:
        """
        Initialize the modem with basic setup commands.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        commands = [
            "AT",  # Basic AT command to test communication
            "ATE0",  # Turn off echo
            "AT+CMEE=2",  # Enable verbose error messages
        ]
        
        for cmd in commands:
            success, response = self.execute_command(cmd)
            if not success:
                self.logger.log_error(f"Failed to initialize modem with command: {cmd}")
                return False
        
        self.logger.log_info("Modem initialized successfully")
        return True