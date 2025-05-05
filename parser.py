"""
Parser module for the Cell War Driver program.

This module handles parsing of AT command responses into structured data.
"""
import os
import csv
from datetime import datetime
from typing import Dict, List, Optional, Any


class ModemResponseParser:
    """Parses and stores modem response data."""
    
    def __init__(self, csv_dir: str, csv_filename: str):
        """
        Initialize the parser.
        
        Args:
            csv_dir: Directory for CSV output
            csv_filename: Base filename for CSV output
        """
        self.csv_dir = csv_dir
        self.csv_filename = csv_filename
        
        # Create output directory if it doesn't exist
        os.makedirs(csv_dir, exist_ok=True)
        
        # Store parsed data
        self.modem_info = {}
        self.current_cell_data = {}
        self.cell_history = []
        
        # Set up CSV files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.cell_csv_path = os.path.join(csv_dir, f"{timestamp}_{csv_filename}")
        self.modem_info_path = os.path.join(csv_dir, f"{timestamp}_modem_info.csv")
        
        # Column headers for cell data CSV
        self.cell_data_fields = [
            "timestamp", "latitude", "longitude", 
            "mcc", "mnc", "lac", "cell_id", "technology",
            "rssi", "rsrp", "rsrq", "sinr", "band", "bandwidth", "frequency"
        ]
        
        # Initialize cell data CSV
        with open(self.cell_csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.cell_data_fields)
            writer.writeheader()
    
    def parse_modem_info(self, command: str, response: str) -> Dict[str, Any]:
        """
        Parse modem information from command response.
        
        Args:
            command: The AT command that was sent
            response: The response from the modem
            
        Returns:
            Dict[str, Any]: Parsed modem information
        """
        result = {}
        
        # Remove command echo if present
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        if lines and lines[0] == command.strip():
            lines = lines[1:]
        
        # Parse based on command
        if command.startswith("AT+CGMI"):  # Manufacturer
            if len(lines) > 0 and "ERROR" not in lines[0]:
                result["manufacturer"] = lines[0]
        
        elif command.startswith("AT+CGMM"):  # Model
            if len(lines) > 0 and "ERROR" not in lines[0]:
                result["model"] = lines[0]
        
        elif command.startswith("AT+CGMR"):  # Firmware version
            if len(lines) > 0 and "ERROR" not in lines[0]:
                result["firmware"] = lines[0]
        
        elif command.startswith("AT+CGSN"):  # Serial number
            if len(lines) > 0 and "ERROR" not in lines[0]:
                result["serial_number"] = lines[0]
        
        # Store the parsed info
        self.modem_info.update(result)
        
        # Write to modem info CSV if we have new data
        if result:
            self._write_modem_info()
        
        return result
    
    def parse_cell_info(self, command: str, response: str) -> Dict[str, Any]:
        """
        Parse cell information from command response.
        
        Args:
            command: The AT command that was sent
            response: The response from the modem
            
        Returns:
            Dict[str, Any]: Parsed cell information
        """
        result = {}
        current_time = datetime.now()
        
        # Add timestamp
        result["timestamp"] = current_time.isoformat()
        
        # Parse based on command
        if command.startswith("AT+CREG?") or command.startswith("AT+CGREG?") or command.startswith("AT+CEREG?"):
            # Network registration status
            self._parse_network_registration(command, response, result)
        
        elif command.startswith("AT+CSQ"):
            # Signal quality
            self._parse_signal_quality(response, result)
        
        # Update current cell data
        self.current_cell_data.update(result)
        
        # If we have enough data, save a record
        if self._has_minimum_cell_data():
            self._save_cell_record()
        
        return result
    
    def _parse_network_registration(self, command: str, response: str, result: Dict[str, Any]) -> None:
        """
        Parse network registration information.
        
        Args:
            command: The AT command that was sent
            response: The response from the modem
            result: Dictionary to update with parsed values
        """
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        # Different commands for different technologies
        if command.startswith("AT+CREG?"):  # GSM
            result["technology"] = "GSM"
        elif command.startswith("AT+CGREG?"):  # GPRS/EDGE/UMTS
            result["technology"] = "UMTS"
        elif command.startswith("AT+CEREG?"):  # LTE/5G
            result["technology"] = "LTE"
        
        # Parse location information
        for line in lines:
            if "+CREG:" in line or "+CGREG:" in line or "+CEREG:" in line:
                parts = line.split(",")
                if len(parts) >= 3:
                    # Registration status in parts[1]
                    if len(parts) >= 5:  # If we have location info
                        try:
                            # Location Area Code
                            lac = parts[2].strip().strip('"')
                            result["lac"] = int(lac, 16) if lac.startswith("0x") else int(lac)
                            
                            # Cell ID
                            cell_id = parts[3].strip().strip('"')
                            result["cell_id"] = int(cell_id, 16) if cell_id.startswith("0x") else int(cell_id)
                        except (ValueError, IndexError):
                            pass
    
    def _parse_signal_quality(self, response: str, result: Dict[str, Any]) -> None:
        """
        Parse signal quality information.
        
        Args:
            response: The response from the modem
            result: Dictionary to update with parsed values
        """
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        for line in lines:
            if "+CSQ:" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    values = parts[1].strip().split(",")
                    if len(values) >= 2:
                        try:
                            rssi_val = int(values[0])
                            # Convert to dBm (-113 to -51 dBm)
                            if rssi_val < 99:  # 99 means unknown
                                result["rssi"] = -113 + (2 * rssi_val)
                        except (ValueError, IndexError):
                            pass
    
    def _has_minimum_cell_data(self) -> bool:
        """
        Check if we have minimum required cell data to record an entry.
        
        Returns:
            bool: True if we have minimum data, False otherwise
        """
        # At minimum, we should have timestamp and some identifier for the cell
        return ("timestamp" in self.current_cell_data and 
                ("cell_id" in self.current_cell_data or "rssi" in self.current_cell_data))
    
    def _save_cell_record(self) -> None:
        """Save the current cell data as a record and append to CSV."""
        # Make a copy of the current data
        record = self.current_cell_data.copy()
        
        # Add to history
        self.cell_history.append(record)
        
        # Write to CSV
        with open(self.cell_csv_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.cell_data_fields)
            # Fill in missing fields with empty strings
            row = {field: record.get(field, "") for field in self.cell_data_fields}
            writer.writerow(row)
    
    def _write_modem_info(self) -> None:
        """Write modem information to CSV file."""
        # Only write if we have some modem info
        if not self.modem_info:
            return
        
        # Get the fields from our current modem info
        fields = list(self.modem_info.keys())
        
        # Create or append to the CSV
        file_exists = os.path.isfile(self.modem_info_path)
        
        with open(self.modem_info_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(self.modem_info)