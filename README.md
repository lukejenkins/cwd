# cwd - Cell War Driver

## Overview

### Purpose

The purpose of this project is to create a python program that:

- [ ] Opens a serial port to interact with a cellular modem - Initially we're going to use the Telit LM960
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

## Commands

### Run Once Commands

These commands are run once when the program starts up. They are used to gather information about the modem and set it up for our purposes.

```plaintext
# Set the error reporting to verbose, resulting in more descriptive error messages:
AT+CMEE=2

######
## Setup the modem:
######
# Power on the GPS functionality:
AT$GPSP=1
# GPS - Turn on NMEA stream and all sentences
AT$GPSNMUN=2,1,1,1,1,1,1
AT$GPSNMUNEX=1,1,1
# GPS - Set GPS location service mode to autonomous
AT$GPSSLSR=2,3,,,,,1,255
# GPS - Set GPS position mode to autonomous only
AT$AGPSEN=0
# GPS - Configure constellations - GPS + GLONASS + Beidou + Galileo
AT$GNSSCONF=6,0
# GPS - Save Parameters
AT$GPSSAV

######
## Query all of the things we want to record once:
######
# Query module manufacturer:
AT+CGMI
# Query module model:
AT+CGMM
# Query module revision: 
AT+CGMR
# Query module serial number:
AT+CGSN
# Query module IMEI:
AT+CGSN=1
# Query SIM ICCID:
AT+CICCID
# Query SIM IMSI:
AT+CIMI
# Get all firmware information:
AT#FIRMWARE
# Get the full list of MBNs and versions:
AT#GETFWEXT
# Get the current MBN version:
AT#GETFWVER
# Get the active carrier
AT#GETFW?
# GPS - Power - Check
AT$GPSP?
# GPS - Check NMEA stream status
AT$GPSNMUN?
# GPS - Check NMEA extended data configuration
AT$GPSNMUNEX?
# GPS - Check GPS location service mode
AT$GPSSLSR?
# GPS - Check GPS position mode
AT$AGPSEN?
# GPS - Check GNSS constellation configuration
AT$GNSSCONF?
# GPS - Check antenna port configuration
AT$GPSANTPORT?

# Read configured LTE bands
AT#BND?

# Get the Preferred Operator List from the SIM
AT+CPOL? 
# Get the list of preferred PLMNs in the SIM
AT+CPLS?
AT+CPLS=?
```

### Loop Commands

These commands are run continously in a loop. They are used to gather information about the modem and the network it is connected to.

```plaintext

# Read the current setting of <fun>.
AT+CFUN? 
# Read the real-time clock:
AT+CCLK?
# Get Acquired Position
AT$GPSACP?
# Get the current location:
AT$GETLOCATION
# Get the current GPS Quality of signal:
AT$GPSQOS? 
# Read the receieved signal quality indicators:
AT+CSQ 
# Read the current extended signal quality indicators:
AT+CESQ
#Read the current service state (associated with a cell network)
AT+CGATT?
#Reads current network status,
AT#RFSTS
# Query the current network operator:
AT+COPS?
# Query the current network registration status:
AT+CREG?
```

## Schemas

### Run Once Schema

```json
#Schema goes here
```

### Loop Schema

```json
#Schema goes here
```
