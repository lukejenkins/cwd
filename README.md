# cwd - Cell War Driver

## Overview

### Purpose

The purpose of this project is to create a python program that:

- [ ] Opens a serial port to interact with a cellular modem
- [ ] Runs some commands to set up the modem for our purposes
- [ ] Runs some commands once to gather data from the modem that shouldn't change
  - [ ] Make of the modem
  - [ ] Model of the modem
  - [ ] Firmware version
  - [ ] Serial number
  - [ ] SIM info
  - [ ] Firmware subersion/carrier profile details
  - [ ] Cell technology configuration (e.g. LTE vs. 5GNR preference)
  - [ ] Band capabilities and configuration
- [ ] There will be a main loop where we run a list of commands in a loop until the program is terminated
  - [ ] Different commands will run on a different cadence
  - [ ] The primary commands that run the most often will be to gather
    - [ ] Gather Location information from a data source such as the cell modem or gpsd
    - [ ] Information about the cell that the modem is connected to as well as all signal stats
    - [ ] Any other cells that the modem can provide us information about and any signal information available
  - [ ] Commands that run less often will gather stats that won't chage as often
    - [ ] Stats such as the temperature of the cell modem
    - [ ] If we're connected to a data service through the cell modem and details about that
- [ ] We will record all output to
  - [ ] A text based log file
  - [ ] Some sort of parsed data file
  - [ ] Possibly a database of some sort

### Longer term goals

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
