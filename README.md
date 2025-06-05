# F1 24 Leaderboard

The project contains everything needed to run a local leaderboard system for F1 2024. It exposes a FastAPI backend with a simple UI, telemetry listeners for each simulator rig, optional timer utilities and scripts for managing different network profiles.

## Repository layout

```
/README.md                   – this file
/f1_leaderboard_app/         – main application
  backend/                   – FastAPI server and templates
  config/                    – application configuration
  listeners/                 – UDP telemetry listeners
  scripts/                   – helper scripts (database, network, tests)
  rig_installer/             – installer resources for rig PCs
/timer_app/                  – standalone timer client (optional)
/f1-24-telemetry-application – telemetry parsing repository (submodule)
```

## Installation

1. Clone the repository and initialise submodules:
   ```bash
   git clone <repo-url>
   cd f1-24-leaderboard
   git submodule update --init --recursive
   ```
2. Install Python dependencies for the backend:
   ```bash
   pip install -r f1_leaderboard_app/requirements.txt
   ```
   The telemetry repository provides additional modules used by the listeners. Ensure it is available on each machine running a listener.

## Database setup

Initialise the SQLite database before starting the server:
```bash
python f1_leaderboard_app/scripts/init_db.py
```
This creates `backend/database/f1_leaderboard.db` and populates the tracks and default rigs.

## Running the backend server

Launch the FastAPI server from the project root:
```bash
python f1_leaderboard_app/backend/main.py
```
Batch files `Start_server_shop.bat` and `Start_server_mobile.bat` are provided for Windows. They set the active network profile and start the server accordingly.

- Leaderboard: `http://<server_ip>:8000`
- Admin panel: `http://<server_ip>:8000/admin`

## Starting telemetry listeners

Run one listener per simulator PC. Each listener submits lap times to the backend:
```bash
python f1_leaderboard_app/listeners/rig_listener.py --rig-id RIG1 --api-host <server_ip> --api-port 8000
```
Replace `RIG1` with the rig identifier and `<server_ip>` with the IP address of the machine running the backend.

After installing the rig components using `install_complete_rig.bat`, desktop shortcuts
named `Start F1 System [RIG_ID] - SHOP.bat` and `Start F1 System [RIG_ID] - MOBILE.bat`
will be created. These scripts launch both the timer client and telemetry listener for
the selected network profile and are the recommended way to start the rig services.

## Network configuration

The application can operate on two predefined network profiles (SHOP and MOBILE). Use the helper script to view or switch profiles and to generate batch files for configuring rig PCs:
```bash
python f1_leaderboard_app/scripts/network_config_helper.py --show-current
python f1_leaderboard_app/scripts/network_config_helper.py --set-profile MOBILE
python f1_leaderboard_app/scripts/network_config_helper.py --generate-batch RIG1
```
See `docs/NETWORK_SETUP_GUIDE.md` for complete instructions.

## Timer system

The admin panel exposes controls for starting and stopping timers on each rig. The optional `timer_app` directory contains a lightweight timer client that can run on rig PCs if more direct control is required.

## Additional documentation

- `docs/deployment_guide.md` – step‑by‑step deployment instructions
- `docs/NETWORK_SETUP_GUIDE.md` – detailed network configuration guide
- `listeners/README.md` – information on telemetry listeners

With the backend running and each rig listener connected, lap times will be recorded in the database and displayed on the public leaderboard.
