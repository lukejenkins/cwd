@echo off
REM Cell War Driver (cwd) Windows Launcher
REM This script launches the Cell War Driver program on Windows
setlocal EnableDelayedExpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd "%SCRIPT_DIR%"

REM Check if Python is installed
python --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in the PATH.
    echo Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "%SCRIPT_DIR%\venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
    
    echo Installing requirements...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Failed to install requirements.
        pause
        exit /b 1
    )
) else (
    call venv\Scripts\activate.bat
)

REM Set default COM port if not specified
set COM_PORT=COM3
if "%1"=="--port" set COM_PORT=%2

REM Pass all arguments to the main script
echo Launching Cell War Driver...
python main.py %*

REM If no arguments are passed, show help
if "%*"=="" (
    echo.
    echo No arguments provided. Showing help:
    echo.
    python main.py --help
)

echo.
echo Cell War Driver execution completed.
pause
endlocal
