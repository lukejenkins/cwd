# Cell War Driver Documentation

This directory contains documentation for the Cell War Driver (cwd) project.

## Contents

- [Smart Configuration System](smart_configuration.md) - Detailed documentation on the smart configuration system that intelligently manages modem settings
- [Quectel EC2x and EG2x](quectel_ec2x_and_eg2x/) - Documentation specific to Quectel EC2x and EG2x series modems

## Project Overview

Cell War Driver is a Python-based tool for interacting with cellular modems, collecting network information, and logging cell tower data. The program is designed primarily for use with Quectel EG25-G modems but has plans to support additional modem types.

## Key Features

- Serial communication with cellular modems
- Collection of cell network information including signal strength, cell IDs, etc.
- GPS/GNSS data collection
- CSV and JSON data logging
- Smart configuration system to reduce modem flash wear
- Real-time signal monitoring
- Configurable command intervals

## Getting Started

For basic usage instructions, please see the main [README.md](../README.md) in the project root directory.

## Contributing to Documentation

If you'd like to contribute to this documentation:

1. Create or edit markdown (.md) files in this directory
2. Follow the existing style and formatting
3. Include clear examples and explanations
4. Submit a pull request with your changes

## License

This documentation is provided under the same license as the main project. See the project's LICENSE file for details.