# Windows Usage Guide for Cell War Driver

This document provides instructions for setting up and running the Cell War Driver (cwd) program on Windows systems.

## Installation

### Prerequisites

1. **Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **COM Port for your modem**
   - Most USB modems will appear as a COM port (e.g., COM3, COM4)
   - You may need to install drivers for your specific modem

### Setup Options

There are three ways to set up and run the Cell War Driver on Windows:

#### Option 1: Using the GUI Launcher (Recommended for beginners)

1. Double-click on `cwd_gui.bat` in the project directory
2. The GUI will launch, allowing you to:
   - Select your COM port
   - Configure all settings
   - Run the program with a click of a button
   - View output in real-time

#### Option 2: Using the Command Line (Batch file)

1. Open Command Prompt
2. Navigate to the project directory
3. Run the program using the batch file:

   ```powershell
   cwd.bat --port COM3 [other options]
   ```

4. If run without arguments, it will display help information

#### Option 3: Using PowerShell

1. Open PowerShell
2. Navigate to the project directory
3. Run the program using the PowerShell script:

   ```powershell
   .\cwd.ps1 --port COM3 [other options]
   ```

4. If run without arguments, it will display help information

## Common Command Line Options

The following options work with all methods above:

```powershell
--port PORT           Serial port for the modem (e.g., COM3)
--baudrate BAUDRATE   Baud rate for serial communication (default: 115200)
--timeout TIMEOUT     Timeout for serial communication in seconds (default: 1.0)
--scan-ports          Scan for available serial ports and exit
--log-dir DIR         Directory for log files (default: output)
--csv-dir DIR         Directory for CSV output (default: output)
```

## Troubleshooting

### COM Port Not Found

1. Open Device Manager (press Win+X and select Device Manager)
2. Look under "Ports (COM & LPT)" for your modem
3. If not found, you may need to install drivers for your modem
4. Use the `--scan-ports` option to see available ports:

   ```powershell
   cwd.bat --scan-ports
   ```

### Permission Issues

If you encounter permission errors:

1. Try running Command Prompt or PowerShell as Administrator
2. Check if another program is using the COM port

### Virtual Environment Issues

If the virtual environment fails to create:

1. Make sure you have Python 3.8+ installed correctly
2. Run the following commands manually:

   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Output Files

All data is saved in the `output` directory by default:

- CSV files with cell data
- Log files with detailed operation logs

You can change the output directory using the `--log-dir` and `--csv-dir` options.
