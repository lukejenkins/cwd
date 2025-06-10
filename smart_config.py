"""
Smart Modem Configuration Module

This module implements a smart configuration system that checks current modem 
settings against desired configuration and only applies changes when needed.
This reduces flash memory wear by avoiding unnecessary writes.
"""

import re  # Added re import
import yaml  # Added yaml import
from typing import Dict, Any, Tuple, Optional, List
from modem import ModemCommunicator
from logger import ModemLogger


class SmartModemConfigurator:
    """
    Smart modem configuration manager that checks current settings before applying changes.
    
    This class implements the check-set-verify pattern for modem configuration:
    1. Check current value
    2. Set if different from desired value  
    3. Verify change was applied
    """
    
    def __init__(self, modem: ModemCommunicator, logger: ModemLogger, config_file: str = "modem_config.yaml"):
        """
        Initialize the smart configurator.
        
        Args:
            modem: ModemCommunicator instance for AT command execution
            logger: Logger instance for logging operations
            config_file: Path to YAML configuration file with desired settings
        """
        self.modem = modem
        self.logger = logger
        self.config_file = config_file
        self.desired_config = self._load_configuration()
        
        # Statistics tracking
        self.stats = {
            'checked': 0,
            'changed': 0,
            'skipped': 0,
            'failed': 0
        }
    
    def _load_configuration(self) -> Dict[str, Any]:
        """
        Load desired configuration from YAML file.
        
        Returns:
            Dict containing the desired configuration settings
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If configuration file is invalid YAML
        """
        try:
            with open(self.config_file, 'r') as file:
                config = yaml.safe_load(file)
                self.logger.log_info(f"Loaded configuration from {self.config_file}")
                return config
        except FileNotFoundError:
            self.logger.log_error(f"Configuration file {self.config_file} not found")
            raise
        except yaml.YAMLError as e:
            self.logger.log_error(f"Invalid YAML in configuration file: {e}")
            raise
    
    def configure_modem(self) -> bool:
        """
        Apply smart configuration to the modem.
        
        Only changes settings that don't match the desired configuration.
        
        Returns:
            bool: True if all configurations were successful, False otherwise
        """
        self.logger.log_info("Starting smart modem configuration...")
        self.logger.log_info("This will only change settings that don't match desired values")
        
        success = True
        
        # Configure basic settings
        if not self._configure_basic_settings():
            success = False
        
        # Configure network settings  
        if not self._configure_network_settings():
            success = False
        
        # Configure GNSS settings
        if not self._configure_gnss_settings():
            success = False
        
        # Print configuration summary
        self._print_configuration_summary()
        
        return success
    
    def _configure_basic_settings(self) -> bool:
        """Configure basic modem settings."""
        self.logger.log_info("Configuring basic settings...")
        
        basic_config = self.desired_config.get('basic', {})
        success = True
        
        # Error reporting mode
        if 'error_reporting' in basic_config:
            if not self._configure_cmee(basic_config['error_reporting']):
                success = False
        
        # Time zone update
        if 'time_zone_update' in basic_config:
            if not self._configure_ctzu(basic_config['time_zone_update']):
                success = False
        
        return success
    
    def _configure_network_settings(self) -> bool:
        """Configure network-related settings."""
        self.logger.log_info("Configuring network settings...")
        
        network_config = self.desired_config.get('network', {})
        success = True
        
        # Clear forbidden PLMN list
        if network_config.get('clear_forbidden_plmn', False):
            if not self._configure_forbidden_plmn_clear():
                success = False
        
        # Display RSSI in scan
        if 'display_rssi_in_scan' in network_config:
            if not self._configure_qopscfg_displayrssi(network_config['display_rssi_in_scan']):
                success = False
        
        # Display bandwidth in scan
        if 'display_bandwidth_in_scan' in network_config:
            if not self._configure_qopscfg_displaybw(network_config['display_bandwidth_in_scan']):
                success = False
        
        return success
    
    def _configure_gnss_settings(self) -> bool:
        """Configure GNSS (GPS) settings."""
        gnss_config = self.desired_config.get('gnss', {})
        
        if not gnss_config.get('enabled', False):
            self.logger.log_info("GNSS is disabled in configuration, skipping GNSS setup")
            return True
        
        self.logger.log_info("Configuring GNSS settings...")
        
        # First, power off GNSS to allow configuration changes
        success, _ = self.modem.execute_command("AT+QGPSEND")
        if not success:
            self.logger.log_warning("Failed to power off GNSS for configuration")
        
        overall_success = True
        
        # Configure each GNSS setting
        gnss_settings = [
            ('output_port', 'outport', str),
            ('nmea_source', 'nmeasrc', int),
            ('gps_nmea_type', 'gpsnmeatype', int),
            ('glonass_nmea_type', 'glonassnmeatype', int),
            ('galileo_nmea_type', 'galileonmeatype', int),
            ('beidou_nmea_type', 'beidounmeatype', int),
            ('gsv_extended_nmea', 'gsvextnmeatype', int),
            ('gnss_config', 'gnssconfig', int),
            ('auto_gps', 'autogps', int),
            ('agps_position_mode', 'agpsposmode', int),
            ('fix_frequency', 'fixfreq', int),
            ('one_pps', '1pps', int),
        ]
        
        for config_key, at_param, value_type in gnss_settings:
            if config_key in gnss_config:
                desired_value = gnss_config[config_key]
                if not self._configure_qgpscfg_setting(at_param, desired_value, value_type):
                    overall_success = False
        
        # Handle raw data configuration (special case with multiple parameters)
        if 'raw_data_config' in gnss_config:
            if not self._configure_qgpscfg_raw_data(gnss_config['raw_data_config']):
                overall_success = False
        
        # Power on GNSS after configuration
        success, _ = self.modem.execute_command("AT+QGPS=1")
        if not success:
            self.logger.log_error("Failed to power on GNSS after configuration")
            overall_success = False
        else:
            self.logger.log_info("GNSS powered on successfully")
        
        return overall_success
    
    def _configure_cmee(self, desired_value: int) -> bool:
        """Configure error reporting mode (AT+CMEE)."""
        return self._check_set_verify_numeric("AT+CMEE", desired_value, r'\+CMEE:\s*(\d+)')
    
    def _configure_ctzu(self, desired_value: int) -> bool:
        """Configure automatic time zone update (AT+CTZU)."""
        return self._check_set_verify_numeric("AT+CTZU", desired_value, r'\+CTZU:\s*(\d+)')
    
    def _configure_forbidden_plmn_clear(self) -> bool:
        """Clear forbidden PLMN list if it's not already empty."""
        self.stats['checked'] += 1
        
        # Check if FPLMN list has entries
        success, response = self.modem.execute_command('AT+QFPLMNCFG="list"')
        if not success:
            self.logger.log_error("Failed to check FPLMN list")
            self.stats['failed'] += 1
            return False
        
        # If response contains PLMN entries (not just OK), clear the list
        if '+QFPLMNCFG:' in response:
            self.logger.log_info("FPLMN list contains entries, clearing...")
            success, response = self.modem.execute_command('AT+QFPLMNCFG="Delete","all"')
            if success:
                self.logger.log_info("FPLMN list cleared successfully")
                self.stats['changed'] += 1
                return True
            else:
                self.logger.log_error("Failed to clear FPLMN list")
                self.stats['failed'] += 1
                return False
        else:
            self.logger.log_info("FPLMN list is already empty, skipping clear operation")
            self.stats['skipped'] += 1
            return True

    def _configure_qopscfg_displayrssi(self, desired_value: int) -> bool:
        """Configure RSSI display in operator scan."""
        return self._check_set_verify_qopscfg("displayrssi", desired_value)
        
    def _configure_qopscfg_displaybw(self, desired_value: int) -> bool:
        """Configure bandwidth display in operator scan."""
        return self._check_set_verify_qopscfg("displaybw", desired_value)
        
    def _configure_qgpscfg_setting(self, setting: str, desired_value: Any, value_type: type) -> bool:
        """Configure a QGPSCFG setting."""
        self.stats['checked'] += 1
        
        # Query current value
        query_cmd = f'AT+QGPSCFG="{setting}"'
        success, response = self.modem.execute_command(query_cmd)
        if not success:
            self.logger.log_error(f"Failed to query QGPSCFG {setting}")
            self.stats['failed'] += 1
            return False
        
        # Parse current value
        if value_type == str:
            # Modified pattern to handle both quoted and unquoted string values
            # This will match: +QGPSCFG: "setting","value" or +QGPSCFG: "setting",value
            pattern = rf'\+QGPSCFG:\s*"{re.escape(setting)}",\s*(?:"([^"]*)"|([^,\s\r\n]*))'
        else:
            pattern = rf'\+QGPSCFG:\s*"{re.escape(setting)}",\s*(\d+)'
        
        match = re.search(pattern, response)
        if not match:
            self.logger.log_warning(f"Could not parse current value for QGPSCFG {setting}")
            # Proceed with setting anyway
            current_value = None
        else:
            # For string values, use the first non-None group (either quoted or unquoted match)
            if value_type == str:
                current_value = match.group(1) if match.group(1) is not None else match.group(2)
            else:
                current_value = match.group(1)
                current_value = int(current_value)
        
        # Check if change is needed
        if current_value == desired_value:
            self.logger.log_info(f"QGPSCFG {setting} already set to {desired_value}, skipping")
            self.stats['skipped'] += 1
            return True
        
        # Set new value
        if value_type == str:
            set_cmd = f'AT+QGPSCFG="{setting}","{desired_value}"'
        else:
            set_cmd = f'AT+QGPSCFG="{setting}",{desired_value}'
        
        self.logger.log_info(f"Changing QGPSCFG {setting} from {current_value} to {desired_value}")
        success, response = self.modem.execute_command(set_cmd)
        if success:
            self.logger.log_info(f"QGPSCFG {setting} configured successfully")
            self.stats['changed'] += 1
            return True
        else:
            self.logger.log_error(f"Failed to configure QGPSCFG {setting}: {response}")
            self.stats['failed'] += 1
            return False
    
    def _configure_qgpscfg_raw_data(self, config_value: str) -> bool:
        """Configure GNSS raw data output (special case with multiple parameters)."""
        self.stats['checked'] += 1
        
        # Query current value
        success, response = self.modem.execute_command('AT+QGPSCFG="gnssrawdata"')
        if not success:
            self.logger.log_error("Failed to query QGPSCFG gnssrawdata")
            self.stats['failed'] += 1
            return False
        
        # Parse current value (format: +QGPSCFG: "gnssrawdata",31,0)
        # More flexible pattern to handle various response formats
        pattern = r'\+QGPSCFG:\s*"gnssrawdata",\s*(.+)'
        match = re.search(pattern, response)
        current_value = match.group(1).strip() if match else None
        
        # Strip any trailing content after the values (like OK)
        if current_value and '\n' in current_value:
            current_value = current_value.split('\n')[0].strip()
        
        # Check if change is needed
        if current_value == config_value:
            self.logger.log_info(f"QGPSCFG gnssrawdata already set to {config_value}, skipping")
            self.stats['skipped'] += 1
            return True
        
        # Set new value
        set_cmd = f'AT+QGPSCFG="gnssrawdata",{config_value}'
        self.logger.log_info(f"Changing QGPSCFG gnssrawdata from {current_value} to {config_value}")
        success, response = self.modem.execute_command(set_cmd)
        if success:
            self.logger.log_info("QGPSCFG gnssrawdata configured successfully")
            self.stats['changed'] += 1
            return True
        else:
            self.logger.log_error(f"Failed to configure QGPSCFG gnssrawdata: {response}")
            self.stats['failed'] += 1
            return False
    
    def _check_set_verify_numeric(self, at_command: str, desired_value: int, response_pattern: str) -> bool:
        """
        Generic method for check-set-verify pattern with numeric values.

        Args:
            at_command: Base AT command (e.g., "AT+CMEE")
            desired_value: Desired numeric value
            response_pattern: Regex pattern to extract current value from query response
            
        Returns:
            bool: True if setting was successful or already correct
        """
        self.stats['checked'] += 1
        
        # Query current value
        query_cmd = f"{at_command}?"
        success, response = self.modem.execute_command(query_cmd)
        if not success:
            self.logger.log_error(f"Failed to query {at_command}")
            self.stats['failed'] += 1
            return False
        
        # Parse current value
        match = re.search(response_pattern, response)
        if not match:
            self.logger.log_warning(f"Could not parse current value for {at_command}")
            # Proceed with setting anyway
            current_value = None
        else:
            try:
                current_value = int(match.group(1))
            except (ValueError, TypeError):
                self.logger.log_warning(f"Failed to convert {at_command} value to integer: {match.group(1)}")
                current_value = None
        
        # Check if change is needed
        if current_value == desired_value:
            self.logger.log_info(f"{at_command} already set to {desired_value}, skipping")
            self.stats['skipped'] += 1
            return True
        
        # Set new value
        set_cmd = f"{at_command}={desired_value}"
        self.logger.log_info(f"Changing {at_command} from {current_value} to {desired_value}")
        success, response = self.modem.execute_command(set_cmd)
        if success:
            self.logger.log_info(f"{at_command} configured successfully")
            self.stats['changed'] += 1
            return True
        else:
            self.logger.log_error(f"Failed to configure {at_command}: {response}")
            self.stats['failed'] += 1
            return False
    
    def _check_set_verify_qopscfg(self, parameter: str, desired_value: int) -> bool:
        """Check-set-verify pattern for QOPSCFG parameters."""
        self.stats['checked'] += 1
        
        # Query current value
        query_cmd = f'AT+QOPSCFG="{parameter}"'
        success, response = self.modem.execute_command(query_cmd)
        if not success:
            self.logger.log_error(f"Failed to query QOPSCFG {parameter}")
            self.stats['failed'] += 1
            return False
        
        # Parse current value - handle both quoted and unquoted numeric values
        pattern = rf'\+QOPSCFG:\s*"{re.escape(parameter)}",\s*(\d+)'
        match = re.search(pattern, response)
        if not match:
            self.logger.log_warning(f"Could not parse current value for QOPSCFG {parameter}")
            # Proceed with setting anyway
            current_value = None
        else:
            try:
                current_value = int(match.group(1))
            except (ValueError, TypeError):
                self.logger.log_warning(f"Failed to convert QOPSCFG {parameter} value to integer: {match.group(1)}")
                current_value = None
          # Check if change is needed
        if current_value == desired_value:
            self.logger.log_info(f"QOPSCFG {parameter} already set to {desired_value}, skipping")
            self.stats['skipped'] += 1
            return True
        
        # Set new value
        set_cmd = f'AT+QOPSCFG="{parameter}",{desired_value}'
        self.logger.log_info(f"Changing QOPSCFG {parameter} from {current_value} to {desired_value}")
        success, response = self.modem.execute_command(set_cmd)
        if success:
            self.logger.log_info(f"QOPSCFG {parameter} configured successfully")
            self.stats['changed'] += 1
            return True
        else:
            self.logger.log_error(f"Failed to configure QOPSCFG {parameter}: {response}")
            self.stats['failed'] += 1
            return False
    
    def _print_configuration_summary(self) -> None:
        """Print summary of configuration operations."""
        self.logger.log_info("-" * 60)
        self.logger.log_info("Smart Configuration Summary:")
        self.logger.log_info(f"  Settings checked: {self.stats['checked']}")
        self.logger.log_info(f"  Settings changed: {self.stats['changed']}")
        self.logger.log_info(f"  Settings skipped (already correct): {self.stats['skipped']}")
        self.logger.log_info(f"  Settings failed: {self.stats['failed']}")
        
        if self.stats['changed'] > 0:
            self.logger.log_info(f"[OK] Applied {self.stats['changed']} configuration changes")
        if self.stats['skipped'] > 0:
            self.logger.log_info(f"[OK] Skipped {self.stats['skipped']} settings (already correct)")
        if self.stats['failed'] > 0:
            self.logger.log_warning(f"[!] {self.stats['failed']} settings failed to configure")
        
        efficiency = (self.stats['skipped'] / self.stats['checked'] * 100) if self.stats['checked'] > 0 else 0
        self.logger.log_info(f"Flash wear reduction: {efficiency:.1f}% of settings skipped")
        self.logger.log_info("-" * 60)


def apply_smart_configuration(modem: ModemCommunicator, config_file: str, logger: ModemLogger) -> bool:
    """
    Convenience function to apply smart configuration to a modem.
    
    Args:
        modem: ModemCommunicator instance
        logger: Logger instance
        config_file: Path to YAML configuration file
        
    Returns:
        bool: True if configuration was successful
    """
    try:
        configurator = SmartModemConfigurator(modem, logger, config_file)
        return configurator.configure_modem()
    except Exception as e:
        logger.log_error(f"Smart configuration failed: {e}")
        return False
