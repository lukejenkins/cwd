"""
Parser module for the Cell War Driver program.

This module handles parsing of AT command responses into structured data.
"""
import os
import csv
import json
from datetime import datetime
from typing import Dict, List, Optional, Any


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

def _parse_quectel_signal_quality(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse Quectel-specific signal quality information from AT+QCSQ response.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    for line in lines:
        if "+QCSQ:" in line:
            parts = line.split(":", 1)
            if len(parts) < 2:
                continue
                
            values = parts[1].strip().split(",")
            if not values:
                continue
                
            try:
                if len(values) >= 1:
                    sysmode = values[0].strip('"')
                    result["qcsq_sysmode"] = sysmode
                
                # Parse values based on system mode
                if sysmode == "GSM":
                    if len(values) >= 2:
                        rssi = values[1].strip()
                        if rssi and rssi != "":
                            result["rssi"] = int(rssi)
                
                elif sysmode == "WCDMA":
                    if len(values) >= 2:
                        rssi = values[1].strip()
                        if rssi and rssi != "":
                            result["rssi"] = int(rssi)
                    if len(values) >= 3:
                        rscp = values[2].strip()
                        if rscp and rscp != "":
                            result["rscp"] = int(rscp)
                    if len(values) >= 4:
                        ecno = values[3].strip()
                        if ecno and ecno != "":
                            result["ecno"] = int(ecno)
                
                elif sysmode == "LTE" or sysmode == "CAT-M" or sysmode == "NB-IoT":
                    if len(values) >= 2:
                        rssi = values[1].strip()
                        if rssi and rssi != "":
                            result["rssi"] = int(rssi)
                    if len(values) >= 3:
                        rsrp = values[2].strip()
                        if rsrp and rsrp != "":
                            result["rsrp"] = int(rsrp)
                    if len(values) >= 4:
                        rsrq = values[3].strip()
                        if rsrq and rsrq != "":
                            result["rsrq"] = int(rsrq)
                    if len(values) >= 5:
                        sinr = values[4].strip()
                        if sinr and sinr != "":
                            result["sinr"] = int(sinr)
                
                elif sysmode == "5G":
                    if len(values) >= 2:
                        rsrp = values[1].strip()
                        if rsrp and rsrp != "":
                            result["rsrp"] = int(rsrp)
                    if len(values) >= 3:
                        sinr = values[2].strip()
                        if sinr and sinr != "":
                            result["sinr"] = int(sinr)
                    if len(values) >= 4:
                        rsrq = values[3].strip()
                        if rsrq and rsrq != "":
                            result["rsrq"] = int(rsrq)
            except (ValueError, IndexError):
                pass


def _parse_quectel_network_info(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse Quectel network information from AT+QNWINFO response.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    for line in lines:
        if "+QNWINFO:" in line:
            parts = line.split(":", 1)
            if len(parts) < 2:
                continue
                
            values = parts[1].strip().split(",")
            if len(values) < 4:
                continue
                
            try:
                # Access technology
                act = values[0].strip('"')
                if act:
                    result["network_type"] = act
                
                # Operator name
                if len(values) >= 2:
                    operator = values[1].strip('"')
                    if operator:
                        result["network_operator"] = operator
                
                # Band
                if len(values) >= 3:
                    band = values[2].strip('"')
                    if band:
                        result["band"] = band
                
                # Channel
                if len(values) >= 4:
                    channel = values[3].strip()
                    if channel and channel.isdigit():
                        result["channel"] = int(channel)
            except (ValueError, IndexError):
                pass


def _parse_quectel_serving_cell(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse Quectel serving cell information from AT+QENG="servingcell" response.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    for line in lines:
        if "+QENG:" in line and "servingcell" in line.lower():
            parts = line.split(":", 1)
            if len(parts) < 2:
                continue
                
            values = parts[1].strip().split(",")
            if len(values) < 3:  # At minimum we need the RAT type
                continue
                
            try:
                # Parse values based on system mode
                if len(values) >= 1 and values[0].strip() == "servingcell":
                    rat_type = values[1].strip('"')
                    result["rat_type"] = rat_type
                    
                    if rat_type == "GSM":
                        # GSM parsing
                        if len(values) >= 4:  # MCC
                            result["mcc"] = values[3].strip('"')
                        if len(values) >= 5:  # MNC
                            result["mnc"] = values[4].strip('"')
                        if len(values) >= 7:  # LAC
                            lac = values[6].strip()
                            if lac.isdigit():
                                result["lac"] = int(lac)
                        if len(values) >= 8:  # Cell ID
                            cell_id = values[7].strip()
                            if cell_id.isdigit():
                                result["cell_id"] = int(cell_id)
                        if len(values) >= 9:  # BSIC
                            bsic = values[8].strip()
                            if bsic.isdigit():
                                result["bsic"] = int(bsic)
                        if len(values) >= 10:  # ARFCN
                            arfcn = values[9].strip()
                            if arfcn.isdigit():
                                result["arfcn"] = int(arfcn)
                        if len(values) >= 11:  # RxLev
                            rxlev = values[10].strip()
                            if rxlev.isdigit():
                                result["rxlev"] = int(rxlev)
                    
                    elif rat_type == "WCDMA":
                        # WCDMA parsing
                        if len(values) >= 4:  # MCC
                            result["mcc"] = values[3].strip('"')
                        if len(values) >= 5:  # MNC
                            result["mnc"] = values[4].strip('"')
                        if len(values) >= 7:  # LAC
                            lac = values[6].strip()
                            if lac.isdigit():
                                result["lac"] = int(lac)
                        if len(values) >= 8:  # Cell ID
                            cell_id = values[7].strip()
                            if cell_id.isdigit():
                                result["cell_id"] = int(cell_id)
                        if len(values) >= 9:  # UARFCN
                            uarfcn = values[8].strip()
                            if uarfcn.isdigit():
                                result["uarfcn"] = int(uarfcn)
                        if len(values) >= 10:  # PSC
                            psc = values[9].strip()
                            if psc.isdigit():
                                result["psc"] = int(psc)
                        if len(values) >= 11:  # RSCP
                            rscp = values[10].strip()
                            if rscp.isdigit():
                                result["rscp"] = int(rscp)
                        if len(values) >= 12:  # ECNO
                            ecno = values[11].strip()
                            if ecno.isdigit():
                                result["ecno"] = int(ecno)
                    
                    elif rat_type in ["LTE", "CAT-M", "NB-IoT"]:
                        # LTE parsing
                        if len(values) >= 4:  # MCC
                            result["mcc"] = values[3].strip('"')
                        if len(values) >= 5:  # MNC
                            result["mnc"] = values[4].strip('"')
                        if len(values) >= 7:  # TAC
                            tac = values[6].strip()
                            if tac.isdigit():
                                result["tac"] = int(tac)
                        if len(values) >= 8:  # Cell ID
                            cell_id = values[7].strip()
                            if cell_id.isdigit():
                                result["cell_id"] = int(cell_id)
                        if len(values) >= 9:  # PCID
                            pcid = values[8].strip()
                            if pcid.isdigit():
                                result["pcid"] = int(pcid)
                        if len(values) >= 10:  # EARFCN
                            earfcn = values[9].strip()
                            if earfcn.isdigit():
                                result["earfcn"] = int(earfcn)
                        if len(values) >= 11:  # Band
                            band = values[10].strip()
                            result["band_num"] = band
                        if len(values) >= 12:  # Bandwidth (MHz)
                            bw = values[11].strip()
                            if bw.isdigit():
                                result["bandwidth"] = int(bw)
                        if len(values) >= 13:  # RSRP
                            rsrp = values[12].strip()
                            if rsrp.lstrip("-").isdigit():
                                result["rsrp"] = int(rsrp)
                        if len(values) >= 14:  # RSRQ
                            rsrq = values[13].strip()
                            if rsrq.lstrip("-").isdigit():
                                result["rsrq"] = int(rsrq)
                        if len(values) >= 15:  # RSSI
                            rssi = values[14].strip()
                            if rssi.lstrip("-").isdigit():
                                result["rssi"] = int(rssi)
                        if len(values) >= 16:  # SINR
                            sinr = values[15].strip()
                            if sinr.lstrip("-").isdigit():
                                result["sinr"] = int(sinr)
            except (ValueError, IndexError):
                pass


def _parse_quectel_neighbor_cells(lines: List[str], result: Dict[str, Any]) -> None:
    """
    Parse Quectel neighbor cell information from AT+QENG="neighbourcell" response.
    
    Args:
        lines: Response lines from the modem
        result: Dictionary to update with parsed values
    """
    neighbor_cells = []
    current_rat = None
    
    for line in lines:
        if "+QENG:" in line:
            parts = line.split(":", 1)
            if len(parts) < 2:
                continue
                
            values = parts[1].strip().split(",")
            if len(values) < 2:
                continue
                
            try:
                if values[0].strip() == "neighbourcell":
                    current_rat = values[1].strip('"')
                elif values[0].strip() == "intra":
                    # Intra-frequency cell
                    cell = {"type": "intra", "rat": current_rat}
                    
                    if current_rat == "GSM":
                        if len(values) >= 2:  # ARFCN
                            arfcn = values[1].strip()
                            if arfcn.isdigit():
                                cell["arfcn"] = int(arfcn)
                        if len(values) >= 3:  # BSIC
                            bsic = values[2].strip()
                            if bsic.isdigit():
                                cell["bsic"] = int(bsic)
                        if len(values) >= 4:  # RxLev
                            rxlev = values[3].strip()
                            if rxlev.isdigit():
                                cell["rxlev"] = int(rxlev)
                    
                    elif current_rat == "WCDMA":
                        if len(values) >= 2:  # UARFCN
                            uarfcn = values[1].strip()
                            if uarfcn.isdigit():
                                cell["uarfcn"] = int(uarfcn)
                        if len(values) >= 3:  # PSC
                            psc = values[2].strip()
                            if psc.isdigit():
                                cell["psc"] = int(psc)
                        if len(values) >= 4:  # RSCP
                            rscp = values[3].strip()
                            if rscp.isdigit():
                                cell["rscp"] = int(rscp)
                        if len(values) >= 5:  # ECNO
                            ecno = values[4].strip()
                            if ecno.isdigit():
                                cell["ecno"] = int(ecno)
                    
                    elif current_rat in ["LTE", "CAT-M", "NB-IoT"]:
                        if len(values) >= 2:  # EARFCN
                            earfcn = values[1].strip()
                            if earfcn.isdigit():
                                cell["earfcn"] = int(earfcn)
                        if len(values) >= 3:  # PCID
                            pcid = values[2].strip()
                            if pcid.isdigit():
                                cell["pcid"] = int(pcid)
                        if len(values) >= 4:  # RSRP
                            rsrp = values[3].strip()
                            if rsrp.lstrip("-").isdigit():
                                cell["rsrp"] = int(rsrp)
                        if len(values) >= 5:  # RSRQ
                            rsrq = values[4].strip()
                            if rsrq.lstrip("-").isdigit():
                                cell["rsrq"] = int(rsrq)
                        if len(values) >= 6:  # RSSI
                            rssi = values[5].strip()
                            if rssi.lstrip("-").isdigit():
                                cell["rssi"] = int(rssi)
                        if len(values) >= 7:  # SINR
                            sinr = values[6].strip()
                            if sinr.lstrip("-").isdigit():
                                cell["sinr"] = int(sinr)
                    
                    neighbor_cells.append(cell)
                
                elif values[0].strip() == "inter":
                    # Inter-frequency cell
                    cell = {"type": "inter", "rat": current_rat}
                    
                    # Parse based on RAT - similar to intra but with potential differences
                    # Add parsing logic similar to intra for different RATs
                    
                    neighbor_cells.append(cell)
            except (ValueError, IndexError):
                pass
    
    if neighbor_cells:
        result["neighbor_cells"] = neighbor_cells


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
    
    elif command.startswith("AT+COPS?"):
        # Current operator
        _parse_current_operator(lines, result)
    
    elif command.startswith("AT+CFUN?"):
        # Functionality status
        _parse_functionality_status(lines, result)
    
    elif command.startswith("AT+CCLK?"):
        # Real-time clock
        _parse_real_time_clock(lines, result)
    
    # Quectel-specific commands
    elif command.startswith("AT+QCSQ"):
        # Quectel extended signal quality
        _parse_quectel_signal_quality(lines, result)
    
    elif command.startswith("AT+QNWINFO"):
        # Quectel network information
        _parse_quectel_network_info(lines, result)
    
    elif command.startswith('AT+QENG="servingcell"'):
        # Quectel serving cell information
        _parse_quectel_serving_cell(lines, result)
    
    elif command.startswith('AT+QENG="neighbourcell"'):
        # Quectel neighbor cell information
        _parse_quectel_neighbor_cells(lines, result)
    
    elif command.startswith("AT+QSPN"):
        # Quectel service provider name
        for line in lines:
            if "+QSPN:" in line:
                parts = line.split(":", 1)
                if len(parts) >= 2:
                    values = parts[1].strip().split(",")
                    if len(values) >= 1:
                        result["operator_full"] = values[0].strip('"')
                    if len(values) >= 2:
                        result["operator_short"] = values[1].strip('"')
                    if len(values) >= 4:
                        result["spn_mcc"] = values[2].strip('"')
                        result["spn_mnc"] = values[3].strip('"')
    
    elif command.startswith("AT+QNETINFO"):
        # Quectel network information (timing advance, DRX, etc.)
        for line in lines:
            if "+QNETINFO:" in line:
                parts = line.split(":", 1)
                if len(parts) >= 2:
                    values = parts[1].strip().split(",")
                    if len(values) >= 3:
                        if values[0] == "2" and values[1] == "1":  # RSSSNR
                            if len(values) >= 3 and values[2].strip():
                                result["rsssnr"] = values[2].strip()
                        elif values[0] == "2" and values[1] == "2":  # Timing Advance
                            if len(values) >= 3 and values[2].strip():
                                result["timing_advance"] = values[2].strip()
                        elif values[0] == "2" and values[1] == "4":  # DRX
                            if len(values) >= 3 and values[2].strip():
                                result["drx"] = values[2].strip()
    
    return result


class ModemResponseParser:
    """Handles parsing of modem responses and saves data to various formats."""
    
    def __init__(self, csv_dir: str, csv_filename: str, json_dir: str = None, json_filename: str = None, logger = None):
        """
        Initialize the parser.
        
        Args:
            csv_dir: Directory for CSV output
            csv_filename: Base filename for CSV output
            json_dir: Directory for JSON output, defaults to csv_dir if None
            json_filename: Base filename for JSON output, defaults to "modem_info.json" if None
            logger: Logger instance for logging messages
        """
        self.csv_dir = csv_dir
        self.csv_filename = csv_filename
        self.json_dir = json_dir if json_dir else csv_dir
        self.json_filename = json_filename if json_filename else "modem_info.json"
        self.logger = logger
        
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
            
        # Log file creation if logger is available
        if self.logger:
            self.logger.log_info(f"Cell data CSV: {self.cell_csv_path}")
            self.logger.log_info(f"Modem info JSON: {self.json_path}")
    
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
        
        # Write to JSON file if we have new data
        if result:
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
    
    def _write_modem_info_json(self) -> None:
        """Write modem information to JSON file."""
        # Only write if we have some modem info
        if not self.modem_info:
            return
        
        # Create a structured output
        output_data = {
            "host_timestamp": datetime.now().isoformat()
        }
        
        # Add basic modem information fields
        for key in ["cgmi", "cgmm", "cgmr", "cgsn", "cimi"]:
            if key in self.modem_info:
                output_data[key] = self.modem_info[key]
        
        # Write to file
        with open(self.json_path, 'w') as f:
            json.dump(output_data, f, indent=2)
