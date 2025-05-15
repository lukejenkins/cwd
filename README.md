# cwd - Cell War Driver

## Overview

### Purpose

The purpose of this project is to create a python program that:

- [ ] Opens a serial port to interact with a cellular modem - Initially we're going to use the Quectel EG25-G module
- [ ] Runs some commands to set up the modem for our purposes
- [ ] Runs some commands once to gather data from the modem that shouldn't change
  - [ ] Make of the modem
  - [ ] Model of the modem
  - [ ] Firmware version
  - [ ] Serial number
  - [ ] SIM info
  - [ ] Firmware subversion/carrier profile details
  - [ ] Cell technology configuration (e.g. LTE vs. 5GNR preference)
  - [ ] Band capabilities and configuration
- [ ] There will be a main loop where we run a list of commands in a loop until the program is terminated
  - [ ] Different commands will run on a different cadence
  - [ ] The primary commands that run the most often will be to gather
    - [ ] Gather Location information from a data source such as the cell modem or gpsd
    - [ ] Information about the cell that the modem is connected to as well as all signal stats
    - [ ] Any other cells that the modem can provide us information about and any signal information available
  - [ ] Commands that run less often will gather stats that won't change as often
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
## Setup the Cellular Modem:
######
# Enable automatic time zone update via NITZ and update LOCAL time to RTC
AT+CTZU=3
# Clear the FPLMN list
AT+QFPLMNCFG="Delete","all" 

######
## Setup the GNSS:
######
# Power off the GNSS functionality so we can configure it:
AT+QGPSEND
# GNSS - Set the output port to "USB NMEA", one of the TTYs presented to the host OS
AT+QGPSCFG="outport","usbnmea"

# GNSS - Enable use of the AT+QGPSGNMEA command to output NMEA sentences to the AT port
AT+QGPSCFG="nmeasrc",1

# GNSS - Turn on all GPS NMEA Sentences
AT+QGPSCFG="gpsnmeatype",31

# GNSS - Turn on all GLONASS NMEA Sentences
AT+QGPSCFG="glonassnmeatype",7

# GNSS - Turn on all Galileo NMEA Sentences 
AT+QGPSCFG="galileonmeatype",1

# GNSS - Turn on all Beidou NMEA Sentences
AT+QGPSCFG="beidounmeatype",3

# GNSS - Turn on Extended GGSV
AT+QGPSCFG="gsvextnmeatype",1

# GNSS - Turn on all supported GNSS constellations
AT+QGPSCFG="gnssconfig",1

# GNSS - Enable the GNSS functionality to run automatically on module restart
AT+QGPSCFG="autogps",1

# GNSS - Configure GNSS to operate in standalone mode only. No AGPS.
AT+QGPSCFG="agpsposmode",0

# GNSS - Set NMEA Output Frequency to 10Hz
AT+QGPSCFG="fixfreq",10

# GNSS - (possibly) turn on 1PPS output to somewhere
AT+QGPSCFG="1pps",1

# GNSS - Turn on raw GNSS output, all constellations, to the NMEA port
# Source: https://github.com/commaai/openpilot/pull/29745/files
AT+QGPSCFG="gnssrawdata",31,0

# Power on the GNSS functionality:
AT+QGPS=1


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
# Query SIM ICCID:
AT+QCCID
# Query SIM IMSI:
AT+CIMI
# Get the full list of MBNs and versions:
AT+QMBNCFG="List"
# GNSS - Power - Check
AT+QGPS?
# GNSS - Check all of the things we set above
AT+QGPSCFG="outport"
AT+QGPSCFG="nmeasrc"
AT+QGPSCFG="gpsnmeatype"
AT+QGPSCFG="glonassnmeatype"
AT+QGPSCFG="galileonmeatype"
AT+QGPSCFG="beidounmeatype"
AT+QGPSCFG="gsvextnmeatype"
AT+QGPSCFG="gnssconfig"
AT+QGPSCFG="autogps"
AT+QGPSCFG="agpsposmode"
AT+QGPSCFG="fixfreq"
AT+QGPSCFG="1pps"
AT+QGPSCFG="gnssrawdata"
# Read Automatic Time Zone Update configuration
AT+CTZU?
# Read configured LTE bands
AT+QCFG="band"

# Check network scan mode (RAT limitations)
AT+QCFG="NWSCANMODE"

# Check what bands are set to be scanned 
AT+QOPSCFG="scancontrol" 

# Check if there are any LTE network locking settings
AT+QNWLOCK="common/lte"

# Check if there are any 4g network locking settings
AT+QNWLOCK="common/4g"

#Check FPMLN List
AT+QFPLMNCFG="list"

# Enumerate what will be returned by the "AT+CIND?" command 
AT+CIND=?

```

### Loop Commands

These commands are run continously in a loop. They are used to gather information about the modem and the network it is connected to.

```plaintext

# Read the current setting of <fun>.
AT+CFUN? 

# Read the real-time clock
AT+CCLK?

# Obtain the Latest Time Synchronized Through Network
AT+QLTS

# Get the current location
AT+QGPSLOC

# Get the current GNSS Quality of signal
AT+QGPSCFG="estimation_error"

# Get one set of each of the following GNSS NMEA sentances. Possibly trim this down a bit.
AT+QGPSGNMEA="GGA"
AT+QGPSGNMEA="RMC"
AT+QGPSGNMEA="GSV"
AT+QGPSGNMEA="GSA"
AT+QGPSGNMEA="VTG"
AT+QGPSGNMEA="GNS"

# Read the receieved signal quality indicators
# +CSQ: <rssi>,<ber>
AT+CSQ 

# Report Signal Quality
# <sysmode> <value1> <value2> <value3> <value4>
# "NOSERVICE" - - - -
# "GSM" <gsm_rssi> - - -
# "TDSCDMA" <tdscdma_rssi> <tdscdma_rscp> <tdscdma_ecio> -
# "WCDMA" <wcdma_rssi> <wcdma_rscp> <wcdma_ecio> -
# "LTE" <lte_rssi> <lte_rsrp> <lte_sinr> <lte_rsrq>
AT+QCSQ

# Query Network Information
# +QNWINFO: <access technology>,<oper>,<band>,<Channel ID>
AT+QNWINFO

# Display the Name of Registered Network
# +QSPN: <FNN>,<SNN>,<SPN>,<alphabet>,<RPLMN>
# <FNN> String type. Full network name.
# <SNN> String type. Short network name.
# <SPN> String type. Service provider name.
# <alphabet> Integer type. Alphabet of full network name and short network name.
# 0 GSM 7-bit default alphabet
# 1 UCS2
# <RPLMN> String type. Registered PLMN.
AT+QSPN

# Query rsssnr of LTE network
AT+QNETINFO=2,1

# Query timingadvance of LTE network
AT+QNETINFO=2,2

# Query DRX of LTE network
AT+QNETINFO=2,4

#Read the current service state (associated with a cell network)
AT+CGATT?

# Query the current network operator
AT+COPS?

# Query the current network registration status
AT+CREG?

# Query the information of serving cells
AT+QENG="servingcell"

# Query the information of neighbour cells
AT+QENG="neighbourcell"


#  Command of Control Instructions
# +CIND: ("battchg",(0-5)),("signal",(0-5)),("service",(0-1)),("call",(0-1)),("roam",(0-1)),("smsfull",(0-1)),("GPRS coverage",(0-1)),("callsetup",(0-3))
AT+CIND?

# Read the real-time clock a second time
AT+CCLK?
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

## Tech Stack

- Python 3.x
- [pyserial](https://pypi.org/project/pyserial/)
  - The pyserial library provides a simple interface for reading and writing data to the serial port.
- [python-dotenv](https://pypi.org/project/python-dotenv/)
  - The dotenv library is used to load environment variables from a .env file into the Python environment.
