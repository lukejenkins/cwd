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
  - [ ] Possibly a database of some sort

### Longer term goals

- [ ] Add support for gathering location information from gpsd
- [ ] Switch from clobering modem config each time it is run, move to a configuration file (YAML?) and have the program check config and only make a change if needed. This will reduce wear on the flash memory of the modem.
- [ ] Support for multiple cell modem command sets
  - [ ] Telit LM960
  - [ ] Quectel RM5xxN Series
  - [ ] Quectel RM5xxQ Series
  - [ ] Sierra Wireless EM74xx/MC74xx Series
- [ ] Use multiple cell modems to gather more data at once. Perhaps one per major cell provider in an area.
- [ ] Gather data using "full scan" style commands that some cell modems support
  - [ ] Certain Telit Modems - AT#CSURVC
  - [ ] Certain Quectel Modems - AT+QSCAN=X,Y
- [ ] Log extra location information from additional location data sources such as cell modems, gpsd, raw gnss data
- [ ] Automatically identify cell modem type and set up for scanning
- [ ] Support for formatting data to submit to wigle.net
- [ ] Generate coverage maps

## Commands

Previously there was a list of modem commands here. Rather than maintaining the list in two places, I'm going to referr the reader to the main.py file where the commands are listed and documented.

## Schemas

### X Schema

```json
#Schema goes here
```

### Y Schema

```json
#Schema goes here
```

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

You can export settings to a `.env` file using the `--export-config` option:

```bash
./cwd --export-config my_config.env
```

Then edit the file as needed and place it in the same directory as the program.
