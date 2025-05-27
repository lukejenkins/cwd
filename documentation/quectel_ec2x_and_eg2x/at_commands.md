# Quectel EG25 AT Commands (Sample List)

This document provides a sample list of AT commands supported by the Quectel EG25 modem module. This list is **not exhaustive** and is intended as a starting point. For complete and detailed information, please refer to the official Quectel AT command manuals.

## Basic & General Commands

| Command        | Function                                                                 | Source Hint (Manual)          |
|----------------|--------------------------------------------------------------------------|-------------------------------|
| AT             | Attention command, used to check if the modem is responsive.             | General AT Commands           |
| ATE[0/1]       | Enable/Disable command echo. ATE0 disables echo, ATE1 enables it.        | General AT Commands           |
| ATI            | Display product identification information.                              | General AT Commands           |
| AT+GMI         | Request Manufacturer Identification.                                     | General AT Commands           |
| AT+GMM         | Request Model Identification.                                            | General AT Commands           |
| AT+GMR         | Request Revision Identification (firmware version).                      | General AT Commands           |
| AT+GSN         | Request Product Serial Number Identification (IMEI or MEID).             | General AT Commands           |
| AT+CGSN        | Request Product Serial Number Identification (IMEI).                     | General AT Commands           |
| AT+QGSN        | Get module GSN number.                                                   | General AT Commands           |
| AT+QIMI        | Get IMEI number.                                                         | General AT Commands           |
| AT&F[n]        | Set to factory defined configuration.                                    | General AT Commands           |
| ATZ[n]         | Reset to default configuration profile.                                  | General AT Commands           |
| AT+CFUN=[<fun>[,<rst>]] | Set Phone Functionality. E.g., `AT+CFUN=1` for full functionality. | General AT Commands           |
| AT+CMEE=[<n>]  | Report Mobile Equipment Error. `AT+CMEE=1` or `AT+CMEE=2` for verbose errors. | General AT Commands           |
| AT+CPAS        | Phone Activity Status.                                                   | General AT Commands           |
| AT+QPOWD=[<n>] | Power Off the Module.                                                    | General AT Commands           |
| AT+IPR?        | Query current DTE-DCE baud rate.                                         | General AT Commands           |
| AT+IPR=<rate>  | Set DTE-DCE baud rate.                                                   | General AT Commands           |
| AT+QFORMATUSRDATA | Format user data partition.                                           | General AT Commands / File    |

## Configuration Commands (`AT+QCFG`)

The `AT+QCFG` command is a versatile command used for various module configurations. It has many sub-parameters. Below are a few examples found:

| Command        | Function                                                                 | Source Hint (Manual)          |
|----------------|--------------------------------------------------------------------------|-------------------------------|
| AT+QCFG="agps/string" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="airplanecontrol" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="amrcodec" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="apready" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="ApRstLevel" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="band" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="bip/auth" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="bootup" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="call_control" | Control voice MO (Mobile Originated) and MT (Mobile Terminated) functions. | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="cdmaruim" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="cdmasms/cmtformat" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="cmux/urcport" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="codec/powsave" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="cops_no_mode_change" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="dhcppktfltr" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="disrplmn" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="divctl" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="diversity" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="efratctl" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="ehrpd" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="eps/guti_enable" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="fast_dormancy" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="fast/poweroff" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="Feature_Switch_Flag" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="freezeband" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="ftm/mbim" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="gprsattach" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="gpsweek" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="hsdpacat" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="hsupacat" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="icf" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="ims" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="imsreg/iptype" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="iproute_enable" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="iprulectl" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="lanip" | Modify the range of LAN IP (e.g., for tethering/router mode).            | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual    |
| AT+QCFG="ledmode" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="lpm/dataind" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="lte/bandprior" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="lte/preferfre" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="ltectcc/smsstorage" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="ltesms/format" | Send SMS in 3GPP2 format only and receive SMS in 3GPP2/3GPP.    | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual    |
| AT+QCFG="mms_rec_control" | Control whether to save received MMS.                           | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual    |
| AT+QCFG="ModemRstLevel" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="msc" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="multi_ip_package" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="noauthcheck" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="ntp" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="nwoptmz/acq" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="nwscanmode" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="nwscanmodeex" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="nwscanseq" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="oostimer" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="pcmclk" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="pdp/duplicatechk" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="plmn/addinfbdn" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="plmn/autoblock" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="poaccept" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="ppp/sleep_ri" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="ppp/termframe" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="ppp/v4v6" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="qcautoconnect" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="qmisync" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="qoos" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="rf/sar/gpioctl" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="risignaltype" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="roamservice" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="rrc" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="rrc/control" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="rssi" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="sarcfg" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="secbootstat" | Get whether secure boot is enabled.                               | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual    |
| AT+QCFG="servicedomain" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="sgsn" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="sim/clk_freq" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="sim/onchip" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="sim/recovery" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="siminvalirecovery" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="sleep/datactrl" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="sleepind/level" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="sms_control" | Control SMS sending and reception.                                | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual    |
| AT+QCFG="SMS/ListMsgMap" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="spi/set" | Write a mark in rawdata to control initialization of SPI6/UART6.       | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual    |
| AT+QCFG="stkauto/setupmenutr" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="TCP/SendMode" | Configure TCP sending mode.                                      | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual    |
| AT+QCFG="tcp/windowsize" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="tdscsq" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="thermal/limit_rates" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="thermal/modem" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="thermal/txpwrlmt" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="tone/incoming" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="urc_cause_support" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="urc/cache" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="urc/delay" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="urc/ri/other" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="urc/ri/pin" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="urc/ri/ring" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="urc/ri/smsincoming" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="urcport/sms" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="usage/apfs" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="usage/apmem" | Get device memory usage.                                          | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual    |
| AT+QCFG="usbcfg" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="usbee" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="usbid" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="usbmode" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="usbnet" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="voice_busytone" | Enable/disable busytone playback.                             | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual    |
| AT+QCFG="volte/disable" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="vts/async" |  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual |
| AT+QCFG="wakeupin/level" | Set the wakeup_in pin level.                                  | EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual    |

**Note on `AT+QCFG`:** The `AT+QCFG` command has numerous sub-parameters for configuring various aspects of the module. The examples above are just a small selection. Refer to the "Quectel_EC2x&EG9x&EG2x-G&EM05_Series_QCFG_AT_Commands_Manual" (or similar specific QCFG manual if available) for a comprehensive list.


## SIM Card Commands

| Command        | Function                                                                 | Source Hint (Manual)          |
|----------------|--------------------------------------------------------------------------|-------------------------------|
| AT+CPIN?       | Query SIM card status (e.g., READY, SIM PIN, SIM PUK).                   | General AT Commands           |
| AT+CPIN=<pin>[,<newpin>] | Enter SIM PIN or PUK, or change PIN.                            | General AT Commands           |
| AT+QSIMSTAT?   | Query SIM card insertion status.                                         | General AT Commands           |
| AT+QCCID       | Read ICCID from SIM card.                                                | General AT Commands           |
| AT+QSIMCHK     | Send UIM_AUTHENTICATE_REQ (UIM authentication).                          | General AT Commands / QCFG    |
| AT+QSIMWRFREQ  | Record the frequency of EF files written to SIM card.                    | General AT Commands / QCFG    |
| AT+QSIMVOL     | Configure SIM card supply voltage.                                       | General AT Commands / QCFG    |

## Network Service Commands

| Command        | Function                                                                 | Source Hint (Manual)          |
|----------------|--------------------------------------------------------------------------|-------------------------------|
| AT+COPS?       | Query current operator.                                                  | General AT Commands           |
| AT+COPS=[<mode>[,<format>[,<oper>[,<AcT>]]]] | Set operator (manual/automatic selection). | General AT Commands           |
| AT+CREG?       | Network Registration status.                                             | General AT Commands           |
| AT+CGREG?      | GPRS Network Registration status.                                        | General AT Commands           |
| AT+CEREG?      | EPS (LTE) Network Registration status.                                   | General AT Commands           |
| AT+CSQ         | Signal Quality Report (RSSI, BER).                                       | General AT Commands           |
| AT+QNWINFO     | Query Network Information (Access Technology, Operator, Band).           | General AT Commands           |
| AT+QENG="servingcell" | Query serving cell information.                                   | General AT Commands           |
| AT+QOPS        | Scan band.                                                               | General AT Commands / QCFG    |
| AT+QOPSCFG="scancontrol" | Configure bands to be scanned under 2G/3G/4G.                  | General AT Commands / QCFG    |
| AT+QOPSCFG="displayrssi" | Enable/disable display of RSSI under LTE.                      | General AT Commands / QCFG    |
| AT+QEGPAPN     | Query the actual APN and the configured APN.                             | General AT Commands / QCFG    |

## Packet Domain (Data) Commands

| Command        | Function                                                                 | Source Hint (Manual)          |
|----------------|--------------------------------------------------------------------------|-------------------------------|
| AT+CGDCONT?    | Show PDP Context definitions.                                            | General AT Commands           |
| AT+CGDCONT=[<cid>[,<PDP_type>[,<APN>...]]] | Define PDP Context.                         | General AT Commands           |
| AT+CGACT=[<state>[,<cid>]] | Activate or Deactivate PDP Context.                         | General AT Commands           |
| AT+CGATT=[<state>] | Attach or Detach from GPRS Service.                                  | General AT Commands           |
| AT+QICSGP=[<contextID>[,<context_type>...]] | Configure Parameters of a TCP/IP Context.   | General AT Commands (TCP/IP)  |
| AT+QIACT=[<contextID>] | Activate a PDP Context.                                         | General AT Commands (TCP/IP)  |
| AT+QIDEACT=[<contextID>] | Deactivate a PDP Context.                                     | General AT Commands (TCP/IP)  |
| AT+QICFG="tcp/keepalive" | Configure whether to enable TCP keepalive function.            | General AT Commands / QCFG    |
| AT+QIKALIVE    | Change to the minimum keepalive value.                                   | General AT Commands / QCFG    |
| AT+QSSLRECV    | Read the remaining SSL data.                                             | General AT Commands / QCFG    |
| AT+QSSLCFG="alpn" | Set SSL ALPN (Application-Layer Protocol Negotiation).                | General AT Commands / QCFG    |

## SMS Commands

| Command        | Function                                                                 | Source Hint (Manual)          |
|----------------|--------------------------------------------------------------------------|-------------------------------|
| AT+CMGF=[<mode>] | Set Message Format (0 for PDU mode, 1 for Text mode).                  | General AT Commands           |
| AT+CMGS=<da>[,<toda>] (Text Mode) | Send Message.                                         | General AT Commands           |
| AT+CMGS=<length> (PDU Mode) | Send Message.                                               | General AT Commands           |
| AT+CMGL=[<stat>] | List Messages from preferred storage.                                  | General AT Commands           |
| AT+CMGR=<index>  | Read Message.                                                            | General AT Commands           |
| AT+CMGD=<index>[,<delflag>] | Delete Message.                                             | General AT Commands           |
| AT+CNMI=[<mode>[,<mt>[,<bm>[,<ds>[,<bfr>]]]]] | New Message Indications to TE.            | General AT Commands           |


## Voice Call Commands (Subset)

| Command        | Function                                                                 | Source Hint (Manual)          |
|----------------|--------------------------------------------------------------------------|-------------------------------|
| ATD<number>;   | Dial a voice call.                                                       | General AT Commands           |
| ATH            | Hang up call.                                                            | General AT Commands           |
| ATA            | Answer incoming call.                                                    | General AT Commands           |
| AT+CLCC        | List Current Calls.                                                      | General AT Commands           |


## File System Commands (from File AT Commands Manual)

| Command        | Function                                                                 | Source Hint (Manual)          |
|----------------|--------------------------------------------------------------------------|-------------------------------|
| AT+QFLDS="<storage>" | Get the Space Information of the Storage (e.g., "UFS", "RAM", "SD"). | File AT Commands              |
| AT+QFLST["<filename_pattern>"] | List the File Information in the Storage.                 | File AT Commands              |
| AT+QFDEL="<filename>" | Delete the File(s) in the Storage.                                | File AT Commands              |
| AT+QFUPL="<filename>",<size>[,<timeout>] | Upload a File to the Storage.                  | File AT Commands              |
| AT+QFDWL="<filename>" | Download a File from the Storage.                                 | File AT Commands              |
| AT+QFOPEN=<filename>[,<mode>] | Open/Create a file.                                      | File AT Commands              |
| AT+QFREAD=<handle>,<read_length> | Read data from file.                                  | File AT Commands              |
| AT+QFWRITE=<handle>,<write_length>[,<timeout>[,<eof>]] | Write data to file.             | File AT Commands              |
| AT+QFCLOSE=<handle> | Close file.                                                          | File AT Commands              |
| AT+QFSEEK=<handle>,<offset>,<relation> | Set file pointer position.                       | File AT Commands              |
| AT+QFDEL="*.*" | Delete all files in the current directory of default storage.            | File AT Commands              |
| AT+QFOTADL     | Download FTP file to UFS (often used for FOTA - Firmware Over The Air).  | General AT Commands / QCFG    |

## GNSS (GPS/GLONASS/BeiDou/Galileo/QZSS) Commands (from GNSS Application Note)

| Command        | Function                                                                 | Source Hint (Manual)          |
|----------------|--------------------------------------------------------------------------|-------------------------------|
| AT+QGPS=[<n>]  | Turn ON/OFF GNSS engine. `AT+QGPS=1` to turn on.                         | GNSS Application Note         |
| AT+QGPS?       | Query GNSS power status.                                                 | GNSS Application Note         |
| AT+QGPSLOC=[<mode>[,<timeout>...]] | Get GNSS Location Information.                       | GNSS Application Note         |
| AT+QGPSINFO    | Get specific GNSS information (e.g. fix status, satellites).             | GNSS Application Note         |
| AT+QGPSGNMEA="<type>" | Get NMEA sentence (e.g., "GGA", "RMC", "GSV", "GSA", "VTG").     | GNSS Application Note         |
| AT+QGPSCFG="<cfg_param>"[,<value>] | Configure GNSS parameters. Examples below:           | GNSS Application Note         |
| AT+QGPSCFG="outport",<port> | Configure NMEA sentence output port ("none", "usbnmea", "uartdebug"). | GNSS Application Note         |
| AT+QGPSCFG="nmeasrc",<enable> | Enable/Disable Acquisition of NMEA Sentences (0=disable, 1=enable). | GNSS Application Note         |
| AT+QGPSCFG="gpsnmeatype",<bitmap> | Configure type of GPS NMEA sentences to output.       | GNSS Application Note         |
| AT+QGPSCFG="glonassnmeatype",<bitmap> | Configure type of GLONASS NMEA sentences.         | GNSS Application Note         |
| AT+QGPSCFG="galileonmeatype",<bitmap> | Configure type of Galileo NMEA sentences.         | GNSS Application Note         |
| AT+QGPSCFG="beidounmeatype",<bitmap> | Configure type of BeiDou NMEA sentences.           | GNSS Application Note         |
| AT+QGPSCFG="gnssconfig",<config> | Configure combined GNSS mode (e.g., GPS+GLONASS).       | GNSS Application Note         |
| AT+QGPSCFG="odpcontrol",<enable> | Configure ODP (On-Demand Positioning) control.         | GNSS Application Note         |
| AT+QGPSCFG="dpoenable",<enable> | Enable/Disable DPO (Dynamic Power Optimization).        | GNSS Application Note         |
| AT+QGPSCFG="plane",<plane_type> | Configure GNSS positioning plane (User/Control plane).   | GNSS Application Note         |
| AT+QGPSCFG="autogps",<enable> | Configure Auto GPS (autonomous or MS-based).              | GNSS Application Note         |
| AT+QGPSCFG="suplver",<version> | Configure SUPL version for A-GPS.                         | GNSS Application Note         |
| AT+QGPSCFG="agpsposmode",<mode> | Configure A-GPS positioning mode.                        | GNSS Application Note         |
| AT+QGPSCFG="fixfreq",<freq_in_hz> | Configure positioning fix frequency (e.g., 1 Hz).     | GNSS Application Note         |
| AT+QGPSEND     | Turn OFF GNSS engine.                                                    | GNSS Application Note         |
| AT+QGPSXTRA=[<n>] | Enable/Disable XTRA function.                                         | GNSS Application Note         |
| AT+QGPSXTRADATA? | Query XTRA data information.                                           | GNSS Application Note         |
| AT+QGPSDEL=<type> | Delete GNSS aiding data (e.g., time, location, almanac, ephemeris). | GNSS Application Note         |
| AT+QGPSPAI     | Obtain GNSS positioning assistance information.                          | General AT Commands / QCFG    |
| AT+QLBSCFG="contextid",<id> | Configure QuecLocator context ID.                          | General AT Commands / QCFG    |
| AT+QLBSEX      | Enter cell parameter for positioning (QuecLocator).                      | General AT Commands / QCFG    |


## Unsorted Commands

| Command        | Function                                                                 | Source Hint (Manual)          |
|----------------|--------------------------------------------------------------------------|-------------------------------|
| AT+QNVFR | Read NV items.                                                        | General AT Commands           |
| AT+QNVR | Read NV items with a specific index.                                 | General AT Commands           |
| AT+QNVFW | Write NV items.                                                       | General AT Commands           |
| AT+QNVFD | Delete NV items.                                                     | General AT Commands           |
| AT+QMBNCFG="select" | Show which MBN is currently selected.                          | General AT Commands           |
| at+qnvfr="nv/item_files/Thin_UI/enable_thin_ui_cfg" | Check status of Thin UI. | General AT Commands           |
| at+qnvfw="nv/item_files/Thin_UI/enable_thin_ui_cfg",<value> | Set status of Thin UI. | General AT Commands           |
| at+qping=<ipaddr>[,<count>[,<size>]] | Ping a host.                                                   | General AT Commands           |
| AT+QVOLTEDBG | Dump a ton of info.                                          | General AT Commands           |
| AT+CIMI | Get the International Mobile Subscriber Identity (IMSI).       | General AT Commands           |
| at+QCPUSN? | Get the CPU serial number.                               | General AT Commands           |
| AT+QWIFICFG="bridgemode" | Support Wi-Fi bridge mode (if Wi-Fi is a feature of the specific EG25 variant). | |
| AT+QMTCFG="protocol/check" | Configure MQTT protocol check.                               |     |


---

**Disclaimer:**

* This list is based on publicly available documents and common knowledge for Quectel modules.
* Command availability and behavior can sometimes vary slightly between firmware versions or specific module sub-variants.
* **Always refer to the official Quectel PDF manuals for the EG25 (or your specific module variant) as the definitive reference.**
