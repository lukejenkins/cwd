# Smart Configuration System

## Overview

The smart configuration system in Cell War Driver (cwd) intelligently manages modem settings by comparing current values with desired configurations specified in a YAML file. It only applies changes when necessary, reducing flash memory wear on the modem and extending its lifespan.

## How It Works

The system follows a "check-set-verify" pattern for each configuration setting:

1. **Check**: Query the current value of a setting from the modem
2. **Compare**: Compare the current value with the desired value in the configuration file
3. **Set**: If values differ, send a command to change the setting
4. **Verify**: Confirm the change was applied correctly

This approach ensures that modem flash memory is only written to when absolutely necessary.

## Configuration File Structure

The configuration file (`modem_config.yaml` by default) uses YAML format and is organized into logical sections:

```yaml
# Basic configuration settings
basic:
  error_reporting: 2              # AT+CMEE=2 (verbose error messages)
  time_zone_update: 3             # AT+CTZU=3 (enable automatic time zone update)

# Network configuration
network:
  clear_forbidden_plmn: true      # AT+QFPLMNCFG="Delete","all"
  display_rssi_in_scan: 1         # AT+QOPSCFG="displayrssi",1
  display_bandwidth_in_scan: 1    # AT+QOPSCFG="displaybw",1

# GNSS (GPS) configuration
gnss:
  enabled: true                   # Whether GNSS should be enabled
  output_port: "usbnmea"          # AT+QGPSCFG="outport","usbnmea"
  nmea_source: 1                  # AT+QGPSCFG="nmeasrc",1
  gps_nmea_type: 31               # AT+QGPSCFG="gpsnmeatype",31 (all GPS sentences)
  glonass_nmea_type: 7            # AT+QGPSCFG="glonassnmeatype",7 (all GLONASS sentences)
  galileo_nmea_type: 1            # AT+QGPSCFG="galileonmeatype",1 (all Galileo sentences)
  beidou_nmea_type: 3             # AT+QGPSCFG="beidounmeatype",3 (all Beidou sentences)
  gsv_extended_nmea: 1            # AT+QGPSCFG="gsvextnmeatype",1 (extended GGSV)
  gnss_config: 1                  # AT+QGPSCFG="gnssconfig",1 (all supported constellations)
  auto_gps: 1                     # AT+QGPSCFG="autogps",1 (auto-start on restart)
  agps_position_mode: 0           # AT+QGPSCFG="agpsposmode",0 (standalone mode)
  fix_frequency: 10               # AT+QGPSCFG="fixfreq",10 (10Hz NMEA output)
  one_pps: 1                      # AT+QGPSCFG="1pps",1 (1PPS output)
  raw_data_config: "31,0"         # AT+QGPSCFG="gnssrawdata",31,0 (raw output for all constellations)
```

## Supported Configuration Options

### Basic Settings

| Configuration Key | Description | AT Command | Possible Values |
|------------------|-------------|------------|-----------------|
| `error_reporting` | Error message verbosity | AT+CMEE | 0 (disabled), 1 (numeric), 2 (verbose) |
| `time_zone_update` | Automatic time zone update | AT+CTZU | 0 (disabled), 1 (enabled), 3 (enabled with RTC update) |

### Network Settings

| Configuration Key | Description | AT Command | Possible Values |
|------------------|-------------|------------|-----------------|
| `clear_forbidden_plmn` | Clear forbidden PLMN list | AT+QFPLMNCFG="Delete","all" | true, false |
| `display_rssi_in_scan` | Show RSSI in network scan | AT+QOPSCFG="displayrssi" | 0 (disabled), 1 (enabled) |
| `display_bandwidth_in_scan` | Show bandwidth in network scan | AT+QOPSCFG="displaybw" | 0 (disabled), 1 (enabled) |

### GNSS (GPS) Settings

| Configuration Key | Description | AT Command | Possible Values |
|------------------|-------------|------------|-----------------|
| `enabled` | Whether GPS is enabled | Controls overall GPS configuration | true, false |
| `output_port` | GPS output port | AT+QGPSCFG="outport" | "usbnmea", "uart1", "none", etc. |
| `nmea_source` | Enable NMEA output on AT port | AT+QGPSCFG="nmeasrc" | 0 (disabled), 1 (enabled) |
| `gps_nmea_type` | GPS NMEA sentence types | AT+QGPSCFG="gpsnmeatype" | Bitmask (31 = all) |
| `glonass_nmea_type` | GLONASS NMEA sentence types | AT+QGPSCFG="glonassnmeatype" | Bitmask (7 = all) |
| `galileo_nmea_type` | Galileo NMEA sentence types | AT+QGPSCFG="galileonmeatype" | Bitmask (1 = all) |
| `beidou_nmea_type` | BeiDou NMEA sentence types | AT+QGPSCFG="beidounmeatype" | Bitmask (3 = all) |
| `gsv_extended_nmea` | Extended GSV sentences | AT+QGPSCFG="gsvextnmeatype" | 0 (disabled), 1 (enabled) |
| `gnss_config` | GNSS constellation config | AT+QGPSCFG="gnssconfig" | Bitmask (1 = all) |
| `auto_gps` | Auto-start GPS on module restart | AT+QGPSCFG="autogps" | 0 (disabled), 1 (enabled) |
| `agps_position_mode` | Assisted GPS mode | AT+QGPSCFG="agpsposmode" | 0 (standalone), 1 (MS-based), 2 (MS-assisted) |
| `fix_frequency` | NMEA output frequency | AT+QGPSCFG="fixfreq" | 1-10 Hz |
| `one_pps` | 1PPS output | AT+QGPSCFG="1pps" | 0 (disabled), 1 (enabled) |
| `raw_data_config` | Raw GNSS data output | AT+QGPSCFG="gnssrawdata" | Format: "constellation,port" |

## Usage Examples

### Basic Usage

```bash
# Use default configuration file (modem_config.yaml)
./cwd --smart-config

# Specify a custom configuration file
./cwd --smart-config --config-file my_custom_config.yaml

# Run only the smart configuration and exit
./cwd --smart-config --setup-only
```

### Creating a Custom Configuration

Start by copying the default configuration:

```bash
cp modem_config.yaml my_custom_config.yaml
```

Edit the file to match your requirements, then use it:

```bash
./cwd --smart-config --config-file my_custom_config.yaml
```

## Implementation Details

The smart configuration system is implemented in `smart_config.py`. Key components include:

- `SmartModemConfigurator`: Main class that handles the configuration process
- `apply_smart_configuration`: Convenience function for applying smart configuration

The system tracks statistics about configuration operations:
- Number of settings checked
- Number of settings changed
- Number of settings skipped (already correct)
- Number of settings that failed to configure

These statistics are displayed at the end of the configuration process to show the effectiveness of the system in reducing flash wear.

## Best Practices

1. **Start with the default configuration** and make incremental changes
2. **Document changes** with comments in the YAML file
3. **Test changes** using the `--setup-only` flag before using in production
4. **Create different configuration files** for different use cases or environments
