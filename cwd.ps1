# Cell War Driver (cwd) Windows PowerShell Launcher
# This script launches the Cell War Driver program on Windows

# Get the directory where this script is located
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Using $pythonVersion"
} catch {
    Write-Host "Python is not installed or not in the PATH."
    Write-Host "Please install Python 3.8 or higher."
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path -Path "$scriptDir\venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment."
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "Installing requirements..."
    & $scriptDir\venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install requirements."
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    & $scriptDir\venv\Scripts\Activate.ps1
}

# Set default COM port if not specified
$comPort = "COM3"
$portSpecified = $false
for ($i = 0; $i -lt $args.Count; $i++) {
    if ($args[$i] -eq "--port" -and $i+1 -lt $args.Count) {
        $comPort = $args[$i+1]
        $portSpecified = $true
        break
    }
}

# Pass all arguments to the main script, ensuring port is specified
Write-Host "Launching Cell War Driver with port: $comPort"
if ($portSpecified) {
    python main.py $args
} else {
    python main.py --port $comPort $args
}

# If no arguments are passed, show help
if ($args.Count -eq 0) {
    Write-Host ""
    Write-Host "No arguments provided. Showing help:"
    Write-Host ""
    python main.py --help
}

Write-Host ""
Write-Host "Cell War Driver execution completed."
Read-Host "Press Enter to exit"
