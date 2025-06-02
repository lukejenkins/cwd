# cwd - Cell War Driver

## Overview

### Purpose

The purpose of this project is to create a python program that:

- [X] Opens a serial port to interact with a cellular modem - Initially we're going to use the Quectel EG25-G module
- [X] Runs some commands to set up the modem for our purposes
- [X] Runs some commands once to gather data from the modem that shouldn't change
  - [X] Make of the modem
  - [X] Model of the modem
  - [X] Firmware version
  - [X] Serial number
  - [X] SIM info
  - [X] Firmware subversion/carrier profile details
  - [X] Cell technology configuration (e.g. LTE vs. 5GNR preference)
  - [X] Band capabilities and configuration
- [X] There will be a main loop where we run a list of commands in a loop until the program is terminated
  - [X] Different commands will run on a different cadence
  - [X] The primary commands that run the most often will be to gather
    - [X] Gather Location information from the cell modem
    - [X] Information about the cell that the modem is connected to as well as all signal stats
    - [X] Any other cells that the modem can provide us information about and any signal information available
  - [X] Commands that run less often will gather stats that won't change as often
    - [X] Stats such as the temperature of the cell modem
    - [X] If we're connected to a data service through the cell modem and details about that
- [X] We will record all output to
  - [X] A text based log file
  - [X] Some sort of parsed data file
- [X] Switch from clobering modem config each time it is run, move to a YAML configuration file and have the program check config and only make a change if needed. This will reduce wear on the flash memory of the modem.

### To-Do / Longer term goals

- [ ] Add support for gathering location information from gpsd
  - [ ] Log extra location information from additional location data sources
    - [ ] Any GPS functions in any cell modems
    - [ ] raw gnss data
  - [ ] RTK support?
- [P] Automatically detect and parae cell modem
  - [X] Make
  - [X] Model
  - [ ] Code Version
  - [ ] Serial Port(s)
  - [ ] Supported RAT/Band pairs
- [ ] Move command lists to config file(s)
- [ ] Abstract the desired outcome from the actual command & parsing. This seems like a necessary step for the ability to handle multiple makes/models/versions of cell modems
- [ ] Support for multiple cell modem types
  - [ ] Telit LM960
  - [ ] Quectel RM5xxN Series
  - [ ] Quectel RM5xxQ Series
  - [ ] Sierra Wireless EM74xx/MC74xx Series
- [ ] Check cell modem firmware versions
  - [ ] warn on versions that dont match tested versions
  - [ ] use different versions of a command / parser per modem code version
- [ ] Automatically configure and start scanning on any allow-listed cell modem make/model/versions/serials
- [ ] Use multiple cell modems to gather more data at once. Perhaps one per major cell provider in an area.
- [ ] Gather data using "full scan" style commands that some cell modems support
  - [ ] Certain Telit Modems - AT#CSURVC
  - [ ] Certain Quectel Modems - AT+QSCAN=X,Y
- [ ] Support for formatting data to submit to wigle.net
- [ ] Generate coverage maps
- [ ] Improve error handling and response
  - [ ] Better handle unexpected inputs
  - [ ] Gracefully Handle modem disconnects/reconnects
    - [ ] until modem reconnects are implemented, gracefully exit if the modem disconnects.
- [ ] Add automated tests (unit tests, integration tests) for better code quality
  - [ ] Gather some sample data that can be public to test against
- [ ] Implement a database

## Commands

Previously there was a list of modem commands here. Rather than maintaining the list in two places, I'm going to referr the reader to the main.py file where the commands are listed and documented.

## Tech Stack

- Python 3.x
- [pyserial](https://pypi.org/project/pyserial/)
  - The pyserial library provides a simple interface for reading and writing data to the serial port.
- [python-dotenv](https://pypi.org/project/python-dotenv/)
  - The dotenv library is used to load environment variables from a .env file into the Python environment.

## Usage

### Command-Line Interface

Cell War Driver provides a comprehensive command-line interface with various options for customizing its behavior. You can run the program using the `./cwd` command followed by options:

```bash
./cwd [options]
```

#### Basic Examples

```bash
# Run with default settings
./cwd

# Specify a different port
./cwd --port /dev/ttyUSB2

# Test connection to modem
./cwd --test-connection

# Scan for available serial ports
./cwd --scan-ports

# Show more detailed logs
./cwd --log-level DEBUG

# Export configuration to .env file
./cwd --export-config my_config.env

# Monitor signal strength in real-time
./cwd --signal-monitor
```

#### Complete Command-Line Reference

##### Basic Options

- `--help` - Show the help message and exit
- `--version` - Show the program version and exit

##### Serial Connection Settings

- `--port PORT` - Serial port for the modem (default: /dev/ttyUSB0)
- `--baudrate BAUDRATE` - Baud rate for serial communication (default: 115200)
- `--timeout TIMEOUT` - Timeout for serial communication in seconds (default: 1.0)
- `--scan-ports` - Scan for available serial ports and exit

##### Logging Settings

- `--log-dir DIR` - Directory for log files (default: output)
- `--log-level LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

##### Command Execution Settings

- `--command-delay DELAY` - Delay between commands in seconds (default: 0.5)
- `--retry-count COUNT` - Number of retries for failed commands (default: 3)

##### Output Settings

- `--csv-dir DIR` - Directory for CSV output (default: output)
- `--csv-filename NAME` - Base filename for cell data CSV (default: cell_data.csv)
- `--json-dir DIR` - Directory for JSON output (default: output)
- `--json-filename NAME` - Base filename for modem info JSON (default: modem_info.json)

##### Database Settings

- `--use-database` - Enable database storage
- `--db-type TYPE` - Database type (sqlite only for now) (default: sqlite)
- `--db-path PATH` - Path to the database file (default: output/cell_data.sqlite)

##### Command Interval Settings

- `--fast-interval SECS` - Fast command loop interval in seconds (default: 5.0)
- `--medium-interval SECS` - Medium command loop interval in seconds (default: 30.0)
- `--slow-interval SECS` - Slow command loop interval in seconds (default: 300.0)

##### Utility Options

- `--list-commands` - Display all AT commands used by the program and exit
- `--test-connection` - Test the modem connection and exit
- `--export-config FILE` - Export current configuration to a .env file and exit
- `--show-env` - Show all environment variables and their values
- `--list-modems` - List all supported modem types and exit
- `--modem-info` - Show detailed information about the connected modem and exit
- `--setup-only` - Run only the modem setup commands and exit
- `--smart-config` - Use smart configuration system (only changes settings that differ from desired values)
- `--config-file FILE` - Path to YAML configuration file for smart configuration (default: modem_config.yaml)
- `--signal-monitor` - Monitor signal strength in real-time (simplified mode)

### Using Environment Variables

All configuration options can also be set using environment variables or a `.env` file in the program directory. The following environment variables are supported:

- `PORT` - Serial port for the modem
- `BAUDRATE` - Baud rate for serial communication
- `TIMEOUT` - Timeout for serial communication in seconds
- `LOG_DIR` - Directory for log files
- `LOG_LEVEL` - Logging level
- `COMMAND_DELAY` - Delay between commands in seconds
- `RETRY_COUNT` - Number of retries for failed commands
- `CSV_DIR` - Directory for CSV output
- `CSV_FILENAME` - Base filename for cell data CSV
- `JSON_DIR` - Directory for JSON output
- `JSON_FILENAME` - Base filename for modem info JSON
- `USE_DATABASE` - Enable database storage (true/false)
- `DB_TYPE` - Database type
- `DB_PATH` - Path to the database file
- `FAST_COMMAND_INTERVAL` - Fast command loop interval in seconds
- `MEDIUM_COMMAND_INTERVAL` - Medium command loop interval in seconds
- `SLOW_COMMAND_INTERVAL` - Slow command loop interval in seconds
- `SMART_CONFIG` - Use smart configuration system (true/false)
- `CONFIG_FILE` - Path to YAML configuration file for smart configuration

You can export settings to a `.env` file using the `--export-config` option:

```bash
./cwd --export-config my_config.env
```

Then edit the file as needed and place it in the same directory as the program.

### Smart Configuration System

Cell War Driver includes a smart configuration system that intelligently checks current modem settings against desired values in a YAML configuration file. This system only applies changes when needed, which reduces flash memory wear on the modem and extends its lifespan.

#### Using Smart Configuration

To use the smart configuration system:

```bash
# Run with smart configuration (uses default modem_config.yaml)
./cwd --smart-config

# Use a custom configuration file
./cwd --smart-config --config-file my_modem_config.yaml

# Run only the smart configuration and exit
./cwd --smart-config --setup-only
```

#### Configuration File Format

The configuration file uses YAML format and is organized into sections for different types of settings:

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
  # ... other GNSS settings ...
```

#### How It Works

1. The system first reads the current modem settings using query commands
2. It compares each setting with the desired value from the configuration file
3. Only if a setting differs from the desired value, it sends a command to change it
4. It verifies the change was applied correctly

This approach minimizes writes to the modem's flash memory, which has a limited number of write cycles.

#### Example: Customizing the Configuration File

You can customize the modem_config.yaml file to match your specific requirements. Here's an example that changes GPS settings:

```bash
# Create a copy of the default configuration
cp modem_config.yaml my_custom_config.yaml

# Edit the file with your preferred text editor
vim my_custom_config.yaml
```

Example customization (changing GPS fix frequency to 1Hz instead of 10Hz):

```yaml
# GNSS (GPS) configuration
gnss:
  enabled: true
  # ... other settings ...
  fix_frequency: 1                # Changed from 10Hz to 1Hz to save power
  # ... other settings ...
```

Then run with your custom configuration:

```bash
./cwd --smart-config --config-file my_custom_config.yaml
```

#### Benefits of Smart Configuration

- **Reduced Flash Wear**: Only applies changes when needed, extending modem lifespan
- **Consistency**: Ensures modem settings are always in the desired state
- **Transparency**: Logs which settings were changed and which were already correct
- **Configurability**: Easy to adjust settings via YAML file without changing code

For detailed documentation on the smart configuration system, see [documentation/smart_configuration.md](documentation/smart_configuration.md).

## Windows Support

Cell War Driver now supports Windows with several convenient ways to run the program:

1. **GUI Launcher**: A graphical interface for easy configuration and execution
2. **Command Line**: Batch file for running from Command Prompt
3. **PowerShell**: Native PowerShell script support

For detailed Windows setup and usage instructions, see [documentation/windows_usage.md](documentation/windows_usage.md).

### Quick Start for Windows

1. Double-click `cwd_gui.bat` for the graphical interface
2. Or run `cwd.bat --port COM3` from Command Prompt
3. Or run `.\cwd.ps1 --port COM3` from PowerShell

The Windows version supports all the same features as the Linux version.
