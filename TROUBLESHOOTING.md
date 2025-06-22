# Troubleshooting Guide

## Import Errors

If you encounter import errors when running the Cell War Driver, here are the most common solutions:

### 1. Virtual Environment Setup

The Cell War Driver uses a Python virtual environment to manage dependencies. On systems with externally managed Python (like Kali Linux), this is required.

**Automatic Setup (Recommended):**

```bash
./cwd.sh --help
```

The wrapper script (`cwd.sh`) will automatically:

- Create a virtual environment if it doesn't exist
- Install all required dependencies
- Activate the environment and run the program

**Manual Setup:**

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the program
python -B main.py --help
```

### 2. Common Import Issues

#### Missing Dependencies

**Error:** `ModuleNotFoundError: No module named 'dotenv'`
**Solution:** Install dependencies with `pip install -r requirements.txt`

#### GPSD Library Missing

**Error:** `gpsd library not found. GPSd functionality will be disabled.`
**Solution:** This is normal if you don't need GPS functionality. The program will work without it.

#### Relative Import Errors

**Error:** `ImportError: attempted relative import with no known parent package`
**Solution:** This has been fixed in the current version. Make sure you're using the latest code.

### 3. System-Specific Issues

#### Kali Linux / Debian Systems

- Use the virtual environment approach (automatic via `cwd.sh`)
- Don't use `--break-system-packages` as it can damage your system

#### Permission Issues

```bash
# Make the wrapper script executable
chmod +x cwd.sh
```

#### Serial Port Access

```bash
# Add your user to the dialout group
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

### 4. Testing Your Installation

Run these commands to verify everything is working:

```bash
# Test basic functionality
./cwd.sh --help
./cwd.sh --version
./cwd.sh --list-commands

# Test configuration loading
./cwd.sh --show-env

# Test serial port scanning (if ports available)
./cwd.sh --scan-ports
```

### 5. Getting Help

If you're still experiencing issues:

1. Check that you have Python 3.8+ installed: `python3 --version`
2. Verify your .env file exists and has the correct settings
3. Run with debug logging: `./cwd.sh --log-level DEBUG`
4. Check the logs in the output directory

## Environment Variables

Make sure your `.env` file is properly configured. You can copy `.env.example` to `.env` and modify as needed:

```bash
cp .env.example .env
```

Key settings to verify:

- `PORT`: Your modem's serial port (check with `--scan-ports`)
- `BAUDRATE`: Usually 115200 for most modems
- `LOG_LEVEL`: Set to DEBUG for troubleshooting

## Dependencies

The program requires these Python packages:

- python-dotenv: Environment variable loading
- pyserial: Serial port communication
- pyyaml: YAML configuration files
- pandas: Data processing
- gpsd-py3: GPS functionality (optional)

All dependencies are automatically installed when using the wrapper script.
