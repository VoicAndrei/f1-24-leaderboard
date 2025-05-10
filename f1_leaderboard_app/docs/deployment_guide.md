# F1 Leaderboard Application - Deployment Guide

This guide provides instructions for deploying the F1 Leaderboard application, with a focus on setting up the telemetry listeners on multiple simulator PCs.

## System Architecture Overview

The F1 Leaderboard application consists of the following components:

1. **Central Backend Server** (runs on the reception laptop)
   - FastAPI-based web server
   - SQLite database
   - Leaderboard display UI
   - Admin control panel UI

2. **Telemetry Listeners** (run on each simulator PC)
   - Python script that captures telemetry data from F1 2024
   - Sends lap times to the central backend

3. **Leaderboard Display** (any browser connected to the reception laptop)
   - Displays the top lap times for each track
   - Auto-cycles between tracks or shows a manually selected track

## Hardware Requirements

- **Reception Laptop**: Windows PC running the central backend server
- **Simulator PCs** (3): Windows PCs running F1 2024 with telemetry enabled
- **Local Network**: All PCs must be on the same local network

## Software Prerequisites

### Reception Laptop

1. Python 3.8+ with pip
2. Required Python packages (see `requirements.txt`)
3. Git (optional, for cloning repository)

### Simulator PCs

1. Python 3.8+ with pip
2. F1 2024 game installed
3. Required Python packages:
   - `requests`
   - F1 telemetry parsing library (from the telemetry repository)

## Installation

### Central Backend Server (Reception Laptop)

1. Clone or download the repository to the reception laptop
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Start the backend server:
   ```
   cd f1_leaderboard_app
   python backend/main.py
   ```
4. Note the IP address of the reception laptop on the local network (use `ipconfig` in command prompt)

### Telemetry Listeners (Simulator PCs)

Each simulator PC needs to run a telemetry listener that captures F1 2024 telemetry data and sends it to the central backend.

#### Prerequisites Setup

1. Install Python 3.8+ if not already installed
2. Install required packages:
   ```
   pip install requests
   ```
3. Copy the F1 telemetry repository to each simulator PC:
   - Create a directory: `C:/Users/[username]/Desktop/f1-24-app/f1-24-telemetry-application`
   - Copy the contents of the telemetry repository into this directory

#### Listener Setup

1. Copy the following files from the main repository to each simulator PC:
   - `f1_leaderboard_app/listeners/rig_listener.py`
   - `f1_leaderboard_app/config/app_config.py`

2. Create a directory structure on each simulator PC:
   ```
   C:/Users/[username]/Desktop/f1-24-app/f1_leaderboard_app/
   ├── config/
   │   └── app_config.py
   └── listeners/
       └── rig_listener.py
   ```

3. Edit the `app_config.py` file on each simulator PC:
   - Update `TELEMETRY_REPO_PATH` to point to the telemetry repository on that PC
   - Update `API_HOST` to the IP address of the reception laptop

## F1 2024 Game Configuration

On each simulator PC, configure F1 2024 to broadcast telemetry data:

1. Launch F1 2024
2. Navigate to Game Options > Settings > Telemetry Settings
3. Set the following options:
   - UDP Telemetry: **On**
   - UDP Broadcast Mode: **Off**
   - UDP IP Address: **127.0.0.1** (localhost)
   - UDP Port: **20777** (default)
   - UDP Send Rate: **60 Hz** (or higher if available)
   - UDP Format: **2024** (latest format)

## Running the Telemetry Listeners

On each simulator PC, run the telemetry listener with a unique rig identifier.

### Simulator PC 1

```
cd C:/Users/[username]/Desktop/f1-24-app/f1_leaderboard_app
python listeners/rig_listener.py --rig-id RIG1 --api-host [reception_laptop_ip] --api-port 8000
```

### Simulator PC 2

```
cd C:/Users/[username]/Desktop/f1-24-app/f1_leaderboard_app
python listeners/rig_listener.py --rig-id RIG2 --api-host [reception_laptop_ip] --api-port 8000
```

### Simulator PC 3

```
cd C:/Users/[username]/Desktop/f1-24-app/f1_leaderboard_app
python listeners/rig_listener.py --rig-id RIG3 --api-host [reception_laptop_ip] --api-port 8000
```

Replace `[reception_laptop_ip]` with the actual IP address of the reception laptop.

## Monitoring and Troubleshooting

### Checking Listener Logs

The telemetry listener logs to both the console and a log file in the format `rig_listener_YYYYMMDD_HHMMSS.log`. Check these logs to verify that:

1. The listener is capturing telemetry data
2. Track names are being correctly resolved
3. Lap times are being submitted to the API

Example of a successful lap time submission in logs:
```
2024-07-01 14:30:15 - INFO - New Lap Completed - Player Car (Index: 0)
  Track: Circuit de Monaco
  Lap Time: 01:15.234
  Position: 1
  Current Lap: 5

2024-07-01 14:30:15 - INFO - Submitting lap time to API: Circuit de Monaco - 01:15.234
2024-07-01 14:30:15 - INFO - Lap time submitted successfully: Lap time added for Player 1 on Circuit de Monaco
```

### Common Issues and Solutions

1. **Listener can't connect to the API**
   - Check that the reception laptop IP address is correct
   - Ensure the backend server is running
   - Verify that both PCs are on the same network
   - Check for firewalls blocking connections

2. **No telemetry data being received**
   - Verify F1 2024 telemetry settings
   - Make sure the game is running and you're in a race session
   - Check that the UDP port matches (default: 20777)

3. **Incorrect track names**
   - Track mapping issues will be logged with warnings
   - Check that `TRACK_ID_MAPPING` in `app_config.py` is correct

## Using the Admin Panel

Once the system is running, you can use the admin panel to:

1. Assign players to rigs
2. Control which track is displayed on the leaderboard
3. Toggle automatic track cycling

To access the admin panel, navigate to `http://[reception_laptop_ip]:8000/admin` in a web browser.

## Deployment Checklist

- [ ] Backend server running on reception laptop
- [ ] Each simulator PC has Python and required packages
- [ ] Telemetry repository copied to each simulator PC
- [ ] Listener files copied to each simulator PC
- [ ] F1 2024 telemetry settings configured on each simulator PC
- [ ] Telemetry listeners running with correct rig IDs
- [ ] Player names assigned to rigs in admin panel
- [ ] Leaderboard correctly showing lap times from all rigs 