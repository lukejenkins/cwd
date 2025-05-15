"""
Parser module for the Cell War Driver program.

This module handles parsing of AT command responses into structured data.
"""
import os
import csv
import json
from datetime import datetime
from typing import Dict, List, Optional, Any


def parse_modem_info(command: str, response: str) -> Dict[str, Any]:
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
    
    # Remove OK response if present
    if lines and lines[-1] == "OK":
        lines = lines[:-1]
    
    # Parse based on command
    if command.startswith("AT+CGMI"):  # Manufacturer
        if len(lines) > 0 and "ERROR" not in lines[0]:
            result["cgmi"] = lines[0]
    
    elif command.startswith("AT+CGMM"):  # Model
        if len(lines) > 0 and "ERROR" not in lines[0]:
            result["cgmm"] = lines[0]
    
    elif command.startswith("AT+CGMR"):  # Firmware version
        if len(lines) > 0 and "ERROR" not in lines[0]:
            result["cgmr"] = lines[0]
    
    elif command.startswith("AT+CGSN"):  # Serial number
        if len(lines) > 0 and "ERROR" not in lines[0]:
            result["cgsn"] = lines[0]
    
    elif command.startswith("AT+CIMI"):  # IMSI
        if len(lines) > 0 and "ERROR" not in lines[0]:
            result["cimi"] = lines[0]
    
    elif command.startswith("AT+CICCID"):  # SIM ICCID
        if len(lines) > 0 and "ERROR" not in lines[0]:
            if "+ICCID:" in lines[0]:
                result["iccid"] = lines[0].split("+ICCID:")[1].strip()
            else:
                result["iccid"] = lines[0]
    
    elif command.startswith("AT+COPS?"):  # Current operator
        for line in lines:
            if "+COPS:" in line:
                parts = line.split(",")
                if len(parts) >= 3:
                    result["operator_mode"] = parts[0].split(":")[1].strip()
                    result["operator_format"] = parts[1].strip()
                    result["operator_name"] = parts[2].strip().strip('"')
                    if len(parts) >= 4:
                        result["act"] = parts[3].strip()
    
    elif command.startswith("AT#GETFWEXT"):  # MBN list
        # Initialize the getfwext data
        if not "getfwext_host_firmware" in result:
            result["getfwext_host_firmware"] = ""
            result["getfwex_table"] = []
        
        # First line often contains host firmware version
        if lines and "HOST FIRMWARE" in lines[0]:
            host_fw_line = lines[0].strip()
            if ":" in host_fw_line:
                result["getfwext_host_firmware"] = host_fw_line.split(":", 1)[1].strip()
            
            # Remove processed line
            lines = lines[1:]
        
        # Skip "MODEM FIRMWARE" line and column headers if present
        skip_lines = 0
        for i, line in enumerate(lines):
            if "MODEM FIRMWARE" in line or "INDEX" in line:
                skip_lines = i + 1
                break
        
        if skip_lines > 0:
            lines = lines[skip_lines:]
        
        # Process remaining lines as carrier entries
        for line in lines:
            if not line.strip() or "ERROR" in line:
                continue
            
            # Split line into fields
            fields = line.split()
            if len(fields) < 7:
                continue
            
            # Extract values from fields
            entry = {
                "getfwext_slot": int(fields[0]) if fields[0].isdigit() else None,
                "getfwext_status": fields[1] if len(fields) > 1 and not fields[1].isdigit() else None,
                "getfwext_carrier": fields[-5] if len(fields) > 5 else "",
                "getfwext_version.": fields[-4] if len(fields) > 4 else "",
                "getfwext_tmcfg.": int(fields[-3]) if len(fields) > 3 and fields[-3].isdigit() else None,
                "getfwext_cnv": fields[-2] if len(fields) > 2 else "",
                "getfwext_loc": int(fields[-1]) if len(fields) > 1 and fields[-1].isdigit() else None
            }
            
            # Handle status field correctly
            if entry["getfwext_status"] == "Activated" or entry["getfwext_status"] == "Active":
                pass  # Keep as is
            else:
                # If first field after index isn't status, shift everything
                carrier_idx = 1 if entry["getfwext_status"] else 0
                entry["getfwext_status"] = None
                entry["getfwext_carrier"] = fields[carrier_idx] if len(fields) > carrier_idx else ""
                
            result["getfwex_table"].append(entry)
    
    elif command.startswith("AT#GETFWVER"):  # Current MBN version
        for line in lines:
            if ":" in line and "ERROR" not in line:
                result["getfwver"] = line.strip()
    
    elif command.startswith("AT#GETFW?"):  # Active carrier
        for line in lines:
            if "#GETFW:" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    result["active_carrier"] = parts[1].strip()
    
    elif command.startswith("AT$GPSP?"):  # GPS power
        for line in lines:
            if "$GPSP:" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    result["gps_power"] = "On" if parts[1].strip() == "1" else "Off"
    
    elif command.startswith("AT$GPSNMUN?"):  # NMEA stream status
        for line in lines:
            if "$GPSNMUN:" in line:
                result["nmea_stream_config"] = line.split(":", 1)[1].strip()
    
    elif command.startswith("AT$GPSNMUNEX?"):  # NMEA extended config
        for line in lines:
            if "$GPSNMUNEX:" in line:
                result["nmea_extended_config"] = line.split(":", 1)[1].strip()
    
    elif command.startswith("AT$AGPSEN?"):  # GPS position mode
        for line in lines:
            if "$AGPSEN:" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    mode = parts[1].strip()
                    if mode == "0":
                        result["gps_position_mode"] = "Autonomous"
                    elif mode == "1":
                        result["gps_position_mode"] = "MSA"
                    elif mode == "2":
                        result["gps_position_mode"] = "MSB"
                    else:
                        result["gps_position_mode"] = f"Unknown ({mode})"
    
    elif command.startswith("AT$GNSSCONF?"):  # GNSS constellation
        for line in lines:
            if "$GNSSCONF:" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    gnss_config = parts[1].strip()
                    constellations = []
                    config_value = int(gnss_config.split(",")[0])
                    
                    if config_value & 1:  # Bit 0 - GPS
                        constellations.append("GPS")
                    if config_value & 2:  # Bit 1 - GLONASS
                        constellations.append("GLONASS")
                    if config_value & 4:  # Bit 2 - Beidou
                        constellations.append("Beidou")
                    if config_value & 8:  # Bit 3 - Galileo
                        constellations.append("Galileo")
                        
                    result["gnss_constellations"] = ", ".join(constellations)
                    result["gnss_config_raw"] = gnss_config
    
    elif command.startswith("AT$GPSANTPORT?"):  # GPS antenna port
        for line in lines:
            if "$GPSANTPORT:" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    port = parts[1].strip()
                    if port == "0":
                        result["gps_antenna_port"] = "Internal"
                    elif port == "1":
                        result["gps_antenna_port"] = "External"
                    else:
                        result["gps_antenna_port"] = f"Unknown ({port})"
    
    elif command.startswith("AT#BND?"):  # LTE bands
        for line in lines:
            if "#BND:" in line:
                result["band_config"] = line.split(":", 1)[1].strip()
                
                # More detailed parsing could be added here if needed
                # to decode the band configuration values
    
    elif command.startswith("AT+CPOL?"):  # Preferred operator list
        result["preferred_operators"] = []
        for line in lines:
            if "+CPOL:" in line:
                result["preferred_operators"].append(line.split(":", 1)[1].strip())
    
    elif command.startswith("AT+CPLS?"):  # Preferred PLMN list
        for line in lines:
            if "+CPLS:" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    value = parts[1].strip()
                    if value == "0":
                        result["plmn_selector"] = "User controlled PLMN selector with access technology"
                    elif value == "1":
                        result["plmn_selector"] = "Operator controlled PLMN selector with access technology"
                    elif value == "2":
                        result["plmn_selector"] = "HPLMN selector with access technology"
                    else:
                        result["plmn_selector"] = f"Unknown ({value})"
    
    return result


def parse_cell_info(command: str, response: str) -> Dict[str, Any]:
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
    
    # Remove command echo if present
    lines = [line.strip() for line in response.split('\n') if line.strip()]
    if lines and lines[0] == command.strip():
        lines = lines[1:]
    
    # Remove OK response if present
    if lines and lines[-1] == "OK":
        lines = lines[:-1]
    
    # Parse based on command
    if command.startswith("AT+CREG?") or command.startswith("AT+CGREG?") or command.startswith("AT+CEREG?"):
        # Network registration status
        _parse_network_registration(command, lines, result)
    
    elif command.startswith("AT+CSQ"):
        # Signal quality
        _parse_signal_quality(lines, result)
    
    elif command.startswith("AT+CESQ"):
        # Extended signal quality
        _parse_extended_signal_quality(lines, result)
    
    elif command.startswith("AT+CGATT?"):
        # GPRS attachment status
        _parse_gprs_attachment(lines, result)
    
    elif command.startswith("AT#RFSTS"):
        # Network status information
        _parse_network_status(lines, result)
    
    elif command.startswith("AT+COPS?"):
        # Current operator
        _parse_current_operator(lines, result)
    
    elif command.startswith("AT+CFUN?"):
        # Functionality status
        _parse_functionality_status(lines, result)
    
    elif command.startswith("AT+CCLK?"):
        # Real-time clock
        _parse_real_time_clock(lines, result)
    
    elif command.startswith("AT$GPSACP?"):
        # GPS Acquired Position
        _parse_gps_acquired_position(lines, result)
    
    elif command.startswith("AT$GETLOCATION"):
        # Location information
        _parse_location_info(lines, result)
    
    elif command.startswith("AT$GPSQOS?"):
        # GPS Quality of Service
        _parse_gps_qos(lines, result)
    
    return result


def _parse_network_registration(command: str, lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse network registration information.
    
    Args:
        command: The AT command that was sent
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    # Different commands for different technologies
    if command.startswith("AT+CREG?"):  # GSM
        result["technology"] = "GSM"
        reg_prefix = "+CREG:"
    elif command.startswith("AT+CGREG?"):  # GPRS/EDGE/UMTS
        result["technology"] = "UMTS"
        reg_prefix = "+CGREG:"
    elif command.startswith("AT+CEREG?"):  # LTE/5G
        result["technology"] = "LTE"
        reg_prefix = "+CEREG:"
    else:
        return
    
    # Parse registration information
    for line in lines:
        if reg_prefix in line:
            parts = line.split(",")
            
            # Extract registration status
            if len(parts) >= 2:
                status_part = parts[1].strip()
                status_code = int(status_part)
                
                if status_code == 0:
                    result["registration_status"] = "Not registered, not searching"
                elif status_code == 1:
                    result["registration_status"] = "Registered, home network"
                elif status_code == 2:
                    result["registration_status"] = "Not registered, searching"
                elif status_code == 3:
                    result["registration_status"] = "Registration denied"
                elif status_code == 4:
                    result["registration_status"] = "Unknown"
                elif status_code == 5:
                    result["registration_status"] = "Registered, roaming"
                else:
                    result["registration_status"] = f"Unknown status ({status_code})"
            
            # Extract location information if available
            if len(parts) >= 4:  # If we have location info
                try:
                    # Location Area Code
                    lac = parts[2].strip().strip('"')
                    result["lac"] = int(lac, 16) if lac.startswith("0x") else int(lac)
                    
                    # Cell ID
                    cell_id = parts[3].strip().strip('"')
                    result["cell_id"] = int(cell_id, 16) if cell_id.startswith("0x") else int(cell_id)
                    
                    # Access technology if available
                    if len(parts) >= 5:
                        act = int(parts[4].strip())
                        if act == 0:
                            result["access_technology"] = "GSM"
                        elif act == 1:
                            result["access_technology"] = "GSM Compact"
                        elif act == 2:
                            result["access_technology"] = "UTRAN"
                        elif act == 3:
                            result["access_technology"] = "GSM w/EGPRS"
                        elif act == 4:
                            result["access_technology"] = "UTRAN w/HSDPA"
                        elif act == 5:
                            result["access_technology"] = "UTRAN w/HSUPA"
                        elif act == 6:
                            result["access_technology"] = "UTRAN w/HSDPA and HSUPA"
                        elif act == 7:
                            result["access_technology"] = "E-UTRAN"
                        elif act == 8:
                            result["access_technology"] = "EC-GSM-IoT"
                        elif act == 9:
                            result["access_technology"] = "E-UTRAN (NB-S1 mode)"
                        elif act == 10:
                            result["access_technology"] = "E-UTRA connected to a 5GCN"
                        elif act == 11:
                            result["access_technology"] = "NR connected to a 5GCN"
                        elif act == 12:
                            result["access_technology"] = "NG-RAN"
                        elif act == 13:
                            result["access_technology"] = "E-UTRA-NR dual connectivity"
                        else:
                            result["access_technology"] = f"Unknown ({act})"
                except (ValueError, IndexError) as e:
                    pass


def _parse_signal_quality(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse signal quality information.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
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
                            result["rssi_raw"] = rssi_val
                        else:
                            result["rssi"] = "unknown"
                            result["rssi_raw"] = 99
                        
                        # Parse bit error rate
                        ber_val = int(values[1])
                        if ber_val < 7:  # 7 means unknown
                            result["ber"] = ber_val
                        else:
                            result["ber"] = "unknown"
                    except (ValueError, IndexError):
                        pass


def _parse_extended_signal_quality(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse extended signal quality information.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    for line in lines:
        if "+CESQ:" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                values = parts[1].strip().split(",")
                if len(values) >= 6:
                    try:
                        # RXLEV - GSM
                        rxlev = int(values[0])
                        if rxlev < 99:
                            result["rxlev"] = -111 + rxlev
                            result["rxlev_raw"] = rxlev
                        
                        # BER - GSM
                        ber = int(values[1])
                        if ber < 99:
                            result["ber_extended"] = ber
                        
                        # RSCP - WCDMA
                        rscp = int(values[2])
                        if rscp < 127:
                            result["rscp"] = -121 + rscp
                            result["rscp_raw"] = rscp
                        
                        # ECNO - WCDMA
                        ecno = int(values[3])
                        if ecno < 99:
                            result["ecno"] = -24.5 + (0.5 * ecno)
                            result["ecno_raw"] = ecno
                        
                        # RSRQ - LTE
                        rsrq = int(values[4])
                        if rsrq < 99:
                            result["rsrq"] = -20 + (rsrq * 0.5)
                            result["rsrq_raw"] = rsrq
                        
                        # RSRP - LTE
                        rsrp = int(values[5])
                        if rsrp < 99:
                            result["rsrp"] = -141 + rsrp
                            result["rsrp_raw"] = rsrp
                    except (ValueError, IndexError):
                        pass


def _parse_gprs_attachment(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse GPRS attachment status.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    for line in lines:
        if "+CGATT:" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                try:
                    status = int(parts[1].strip())
                    result["gprs_attached"] = status == 1
                    result["gprs_status"] = "Attached" if status == 1 else "Detached"
                except (ValueError, IndexError):
                    pass


def _parse_network_status(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse detailed network status information.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    if not lines:
        return
    
    # The RFSTS response is complex and varies by modem
    # This is a basic implementation that extracts key fields
    for line in lines:
        if "#RFSTS:" in line:
            parts = line.split(":", 1)
            if len(parts) < 2:
                continue
                
            values = parts[1].strip().split(",")
            if len(values) < 10:
                continue
                
            try:
                # Extract common fields - may need adjustment based on modem
                if len(values) >= 1:
                    result["rat"] = values[0].strip()
                if len(values) >= 2:
                    result["plmn"] = values[1].strip().strip('"')
                if len(values) >= 3:
                    result["band"] = values[2].strip()
                if len(values) >= 4:
                    result["channel"] = values[3].strip()
                if len(values) >= 5 and values[4].strip():
                    result["network_rfsts_rssi"] = values[4].strip()
                if len(values) >= 6 and values[5].strip():
                    result["rsrp"] = values[5].strip()
                if len(values) >= 7 and values[6].strip():
                    result["rsrq"] = values[6].strip()
                if len(values) >= 8 and values[7].strip():
                    result["tac"] = values[7].strip()
                if len(values) >= 9 and values[8].strip():
                    result["cell_id_rfsts"] = values[8].strip()
                if len(values) >= 10 and values[9].strip():
                    result["pci"] = values[9].strip()
                if len(values) >= 11 and values[10].strip():
                    result["sinr"] = values[10].strip()
            except (ValueError, IndexError):
                pass


def _parse_current_operator(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse current operator information.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    for line in lines:
        if "+COPS:" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                values = parts[1].strip().split(",")
                if len(values) >= 3:
                    try:
                        # Mode
                        mode = int(values[0])
                        if mode == 0:
                            result["operator_selection_mode"] = "Automatic"
                        elif mode == 1:
                            result["operator_selection_mode"] = "Manual"
                        elif mode == 2:
                            result["operator_selection_mode"] = "Manual deregister"
                        elif mode == 3:
                            result["operator_selection_mode"] = "Set only format"
                        elif mode == 4:
                            result["operator_selection_mode"] = "Manual/Automatic"
                        else:
                            result["operator_selection_mode"] = f"Unknown ({mode})"
                        
                        # Format
                        format_type = int(values[1])
                        if format_type == 0:
                            result["operator_format"] = "Long alphanumeric"
                        elif format_type == 1:
                            result["operator_format"] = "Short alphanumeric"
                        elif format_type == 2:
                            result["operator_format"] = "Numeric"
                        else:
                            result["operator_format"] = f"Unknown ({format_type})"
                        
                        # Operator name/code
                        result["operator"] = values[2].strip('"')
                        
                        # Access technology
                        if len(values) >= 4:
                            act = int(values[3])
                            if act == 0:
                                result["act"] = "GSM"
                            elif act == 1:
                                result["act"] = "GSM Compact"
                            elif act == 2:
                                result["act"] = "UTRAN"
                            elif act == 3:
                                result["act"] = "GSM w/EGPRS"
                            elif act == 4:
                                result["act"] = "UTRAN w/HSDPA"
                            elif act == 5:
                                result["act"] = "UTRAN w/HSUPA"
                            elif act == 6:
                                result["act"] = "UTRAN w/HSDPA and HSUPA"
                            elif act == 7:
                                result["act"] = "E-UTRAN"
                            elif act == 8:
                                result["act"] = "EC-GSM-IoT"
                            elif act == 9:
                                result["act"] = "E-UTRAN (NB-S1 mode)"
                            elif act == 10:
                                result["act"] = "E-UTRA connected to a 5GCN"
                            elif act == 11:
                                result["act"] = "NR connected to a 5GCN"
                            elif act == 12:
                                result["act"] = "NG-RAN"
                            elif act == 13:
                                result["act"] = "E-UTRA-NR dual connectivity"
                            else:
                                result["act"] = f"Unknown ({act})"
                    except (ValueError, IndexError):
                        pass


def _parse_functionality_status(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse phone functionality status.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    for line in lines:
        if "+CFUN:" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                try:
                    fun = int(parts[1].strip())
                    if fun == 0:
                        result["functionality"] = "Minimum"
                    elif fun == 1:
                        result["functionality"] = "Full"
                    elif fun == 2:
                        result["functionality"] = "Disabled"
                    elif fun == 3:
                        result["functionality"] = "Disabled phone Tx and Rx"
                    elif fun == 4:
                        result["functionality"] = "Disabled phone Tx and Rx, standalone GPS"
                    elif fun == 5:
                        result["functionality"] = "Factory Test"
                    elif fun == 6:
                        result["functionality"] = "Offline"
                    elif fun == 7:
                        result["functionality"] = "Offline factory test"
                    else:
                        result["functionality"] = f"Unknown ({fun})"
                except (ValueError, IndexError):
                    pass


def _parse_real_time_clock(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse real-time clock information.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    for line in lines:
        if "+CCLK:" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                time_str = parts[1].strip().strip('"')
                try:
                    # Format is typically "YY/MM/DD,HH:MM:SS±TZ"
                    result["modem_time"] = time_str
                    
                    # Could parse into datetime object if needed
                    # However, the format can vary by modem
                except (ValueError, IndexError):
                    pass


def _parse_gps_acquired_position(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse GPS acquired position information.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    for line in lines:
        if "$GPSACP:" in line:
            parts = line.split(":", 1)
            if len(parts) < 2:
                continue
                
            values = parts[1].strip().split(",")
            if len(values) < 10:
                continue
                
            try:
                # Extract GPS information
                result["gps_utc_time"] = values[0].strip()
                
                # Latitude and Longitude
                lat = values[1].strip()
                if lat:
                    result["latitude"] = float(lat)
                    
                lon = values[2].strip()
                if lon:
                    result["longitude"] = float(lon)
                    
                # HDOP
                hdop = values[3].strip()
                if hdop:
                    result["hdop"] = float(hdop)
                    
                # Altitude
                altitude = values[4].strip()
                if altitude:
                    result["altitude"] = float(altitude)
                    
                # Fix
                fix = values[5].strip()
                if fix:
                    result["fix"] = int(fix)
                    
                # Course over ground
                cog = values[6].strip()
                if cog:
                    result["cog"] = float(cog)
                    
                # Speed over ground (km/h)
                spkm = values[7].strip()
                if spkm:
                    result["speed_kmh"] = float(spkm)
                    
                # Speed over ground (knots)
                spkn = values[8].strip()
                if spkn:
                    result["speed_knots"] = float(spkn)
                    
                # Date
                date = values[9].strip()
                if date:
                    result["gps_date"] = date
                    
                # Number of satellites
                if len(values) >= 11:
                    nsat = values[10].strip()
                    if nsat:
                        result["satellites"] = int(nsat)
            except (ValueError, IndexError):
                pass


def _parse_location_info(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse location information.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    # The $GETLOCATION response format can vary by modem
    # This is a simplified implementation
    if not lines:
        return
    
    # Some modems return a simple lat/long pair
    for line in lines:
        if "," in line and not line.startswith("+") and not line.startswith("$"):
            try:
                lat_str, lon_str = line.split(",", 1)
                lat = float(lat_str.strip())
                lon = float(lon_str.strip())
                result["getlocation_latitude"] = lat
                result["getlocation_longitude"] = lon
                return
            except (ValueError, IndexError):
                pass
        
        # Some modems have a prefixed response
        if "$GETLOCATION:" in line:
            try:
                parts = line.split(":", 1)
                if len(parts) >= 2:
                    values = parts[1].strip().split(",")
                    if len(values) >= 2:
                        result["getlocation_latitude"] = float(values[0])
                        result["getlocation_longitude"] = float(values[1])
                        
                        if len(values) >= 3:
                            result["getlocation_accuracy"] = values[2]
            except (ValueError, IndexError):
                pass


def _parse_gps_qos(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse GPS Quality of Service information.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    for line in lines:
        if "$GPSQOS:" in line:
            parts = line.split(":", 1)
            if len(parts) < 2:
                continue
                
            values = parts[1].strip().split(",")
            if len(values) < 3:
                continue
                
            try:
                # Extract QoS values
                if values[0].strip():
                    result["gps_qos_horiz_accuracy"] = values[0].strip()
                if values[1].strip():
                    result["gps_qos_vert_accuracy"] = values[1].strip()
                if values[2].strip():
                    result["gps_qos_response_time"] = values[2].strip()
            except (ValueError, IndexError):
                pass


class ModemResponseParser:
    """Handles parsing of modem responses and saves data to various formats."""
    
    def __init__(self, csv_dir: str, csv_filename: str, json_dir: str = None, json_filename: str = None):
        """
        Initialize the parser.
        
        Args:
            csv_dir: Directory for CSV output
            csv_filename: Base filename for CSV output
            json_dir: Directory for JSON output, defaults to csv_dir if None
            json_filename: Base filename for JSON output, defaults to 'modem_info.json' if None
        """
        self.csv_dir = csv_dir
        self.csv_filename = csv_filename
        self.json_dir = json_dir if json_dir else csv_dir
        self.json_filename = json_filename if json_filename else "modem_info.json"
        
        # Create output directories if they don't exist
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)
        
        # Store parsed data
        self.modem_info = {}
        self.current_cell_data = {}
        self.cell_history = []
        
        # Set up CSV files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.cell_csv_path = os.path.join(csv_dir, f"{timestamp}_{csv_filename}")
        self.modem_info_path = os.path.join(csv_dir, f"{timestamp}_modem_info.csv")
        self.json_path = os.path.join(self.json_dir, f"{timestamp}_{self.json_filename}")
        
        # Column headers for cell data CSV - adjusted to include all possible fields
        self.cell_data_fields = [
            "timestamp", "latitude", "longitude", 
            "mcc", "mnc", "lac", "cell_id", "technology",
            "rssi", "rsrp", "rsrq", "sinr", "band", "bandwidth", "frequency",
            # Additional fields from enhanced parsing
            "registration_status", "access_technology", "gprs_status",
            "operator", "operator_selection_mode", "act",
            "functionality", "fix", "satellites", "hdop", "altitude",
            "speed_kmh", "cog"
        ]
        
        # Initialize cell data CSV
        with open(self.cell_csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.cell_data_fields)
            writer.writeheader()
        
        # Initialize JSON file with empty object
        with open(self.json_path, 'w') as f:
            json.dump({}, f, indent=2)
    
    def parse_modem_info(self, command: str, response: str) -> Dict[str, Any]:
        """
        Parse modem information from command response and save to files.
        
        Args:
            command: The AT command that was sent
            response: The response from the modem
            
        Returns:
            Dict[str, Any]: Parsed modem information
        """
        # Use the standalone parsing function
        result = parse_modem_info(command, response)
        
        # Store the parsed info
        self.modem_info.update(result)
        
        # Write to files if we have new data
        if result:
            self._write_modem_info()
            self._write_modem_info_json()
        
        return result
    
    def parse_cell_info(self, command: str, response: str) -> Dict[str, Any]:
        """
        Parse cell information from command response and save to files.
        
        Args:
            command: The AT command that was sent
            response: The response from the modem
            
        Returns:
            Dict[str, Any]: Parsed cell information
        """
        # Use the standalone parsing function
        result = parse_cell_info(command, response)
        
        # Update current cell data
        self.current_cell_data.update(result)
        
        # If we have enough data, save a record
        if self._has_minimum_cell_data():
            self._save_cell_record()
        
        return result
    
    def _has_minimum_cell_data(self) -> bool:
        """
        Check if we have minimum required cell data to record an entry.
        
        Returns:
            bool: True if we have minimum data, False otherwise
        """
        # At minimum, we should have timestamp and some identifier for the cell
        return ("timestamp" in self.current_cell_data and 
                any(key in self.current_cell_data for key in 
                    ["cell_id", "rssi", "latitude", "longitude", "lac", "operator"]))
    
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
    
    def _write_modem_info_json(self) -> None:
        """Write modem information to JSON file in the format specified in README.md."""
        # Only write if we have some modem info
        if not self.modem_info:
            return
        
        # Create a structured output matching the README's schema
        output_data = {
            "host_timestamp": datetime.now().isoformat()
        }
        
        # Add basic modem information fields
        for key in ["cgmi", "cgmm", "cgmr", "cgsn", "cimi"]:
            if key in self.modem_info:
                output_data[key] = self.modem_info[key]
        
        # Add firmware information
        if "getfwext_host_firmware" in self.modem_info:
            output_data["getfwext_host_firmware"] = self.modem_info["getfwext_host_firmware"]
        
        # Add the firmware table if available
        if "getfwex_table" in self.modem_info:
            output_data["getfwex_table"] = self.modem_info["getfwex_table"]
        
        # Write to file
        with open(self.json_path, 'w') as f:
            json.dump(output_data, f, indent=2)