# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This project is an F1 2024 leaderboard system designed for simulator rigs. It consists of a FastAPI backend with a web UI, telemetry listeners for each rig, and optional timer utilities for managing racing sessions.

## Architecture

The application has a distributed architecture with the following main components:

- **Backend Server** (`f1_leaderboard_app/backend/main.py`): FastAPI application serving the leaderboard and admin interfaces
- **Database Layer** (`f1_leaderboard_app/backend/database/`): SQLite database with schema and management functions
- **Telemetry Listeners** (`f1_leaderboard_app/listeners/`): UDP listeners capturing F1 2024 telemetry data from each rig
- **Timer System** (`timer_app/`): Optional timer clients for rig PCs with overlay displays
- **Configuration Management** (`f1_leaderboard_app/config/app_config.py`): Centralized configuration with network profile support
- **F1 Telemetry Repository** (`f1-24-telemetry-application/`): Git submodule containing telemetry parsing utilities

## Key Development Commands

### Environment Setup
```bash
# Initialize git submodules (required for telemetry parsing)
git submodule update --init --recursive

# Install Python dependencies
pip install -r f1_leaderboard_app/requirements.txt

# Initialize database
python f1_leaderboard_app/scripts/init_db.py
```

### Running the Application
```bash
# Start the backend server
python f1_leaderboard_app/backend/main.py

# Start a telemetry listener for a specific rig
python f1_leaderboard_app/listeners/rig_listener.py --rig-id RIG1 --api-host <server_ip> --api-port 8000

# Run tests
python -m pytest f1_leaderboard_app/
```

### Network Configuration
```bash
# View current network profile
python f1_leaderboard_app/scripts/network_config_helper.py --show-current

# Switch network profile
python f1_leaderboard_app/scripts/network_config_helper.py --set-profile MOBILE

# Generate batch files for rig configuration
python f1_leaderboard_app/scripts/network_config_helper.py --generate-batch RIG1
```

### Database Management
```bash
# Clear all lap times (keeps tracks and rigs)
python f1_leaderboard_app/scripts/clear_database.py

# Test API endpoints
python f1_leaderboard_app/scripts/test_api.py
```

## Network Profile System

The application supports two network profiles configured in `config/app_config.py`:

- **SHOP**: Home/office network (192.168.0.x)
- **MOBILE**: Event/mobile network (192.168.1.x)

The active profile is determined by the `NETWORK_PROFILE` environment variable and affects:
- API server bind address
- Rig IP mappings for timer commands
- Batch file generation for rig setup

## Important File Locations

- **Main Configuration**: `f1_leaderboard_app/config/app_config.py`
- **Database Schema**: `f1_leaderboard_app/backend/database/schema.sql`
- **Static Assets**: `f1_leaderboard_app/backend/static/`
- **HTML Templates**: `f1_leaderboard_app/backend/templates/`
- **Startup Scripts**: `Start_server_shop.bat`, `Start_server_mobile.bat`

## Development Notes

- The telemetry repository is a git submodule and must be initialized
- Each rig runs a separate telemetry listener process
- The database uses SQLite for simplicity but supports concurrent access
- Track names must match official F1 2024 circuit names (see `F1_2024_TRACKS` in config)
- Network profile switching requires restarting the backend server
- Timer functionality communicates with rig clients via HTTP on port 5001

## Testing

The project includes test scripts for various components:
- `test_api.py`: Tests backend API endpoints
- `test_rig_listener.py`: Tests telemetry listener functionality
- `test_leaderboard_control.py`: Tests leaderboard control features

## Deployment

For production deployment, see `docs/deployment_guide.md` and `docs/NETWORK_SETUP_GUIDE.md` for detailed instructions on network configuration and multi-rig setup.