"""
F1 Leaderboard Application Configuration
"""

import os

# List of official F1 2024 tracks
F1_2024_TRACKS = [
    "Bahrain International Circuit",      # Bahrain (Sakhir)
    "Jeddah Corniche Circuit",            # Saudi Arabia
    "Albert Park Circuit",                # Australia (Melbourne)
    "Suzuka International Racing Course", # Japan
    "Shanghai International Circuit",     # China
    "Miami International Autodrome",      # Miami
    "Autodromo Enzo e Dino Ferrari",      # Imola
    "Circuit de Monaco",                  # Monaco
    "Circuit Gilles Villeneuve",          # Canada (Montreal)
    "Circuit de Barcelona-Catalunya",     # Spain
    "Red Bull Ring",                      # Austria
    "Silverstone Circuit",                # Great Britain
    "Hungaroring",                        # Hungary
    "Circuit de Spa-Francorchamps",       # Belgium
    "Circuit Zandvoort",                  # Netherlands
    "Autodromo Nazionale Monza",          # Italy
    "Baku City Circuit",                  # Azerbaijan
    "Marina Bay Street Circuit",          # Singapore
    "Circuit of the Americas",            # USA (Texas)
    "Autódromo Hermanos Rodríguez",       # Mexico
    "Autódromo José Carlos Pace",         # Brazil (Interlagos)
    "Las Vegas Street Circuit",           # Las Vegas
    "Losail International Circuit",       # Qatar
    "Yas Marina Circuit"                  # Abu Dhabi
]

# Simplified display names for tracks (Country/City)
F1_TRACK_DISPLAY_NAMES = {
    "Bahrain International Circuit": "Bahrain",
    "Jeddah Corniche Circuit": "Saudi Arabia",
    "Albert Park Circuit": "Australia",
    "Suzuka International Racing Course": "Japan",
    "Shanghai International Circuit": "China",
    "Miami International Autodrome": "Miami",
    "Autodromo Enzo e Dino Ferrari": "Imola",
    "Circuit de Monaco": "Monaco",
    "Circuit Gilles Villeneuve": "Canada",
    "Circuit de Barcelona-Catalunya": "Spain",
    "Red Bull Ring": "Austria",
    "Silverstone Circuit": "Great Britain",
    "Hungaroring": "Hungary",
    "Circuit de Spa-Francorchamps": "Belgium",
    "Circuit Zandvoort": "Netherlands",
    "Autodromo Nazionale Monza": "Italy",
    "Baku City Circuit": "Azerbaijan",
    "Marina Bay Street Circuit": "Singapore",
    "Circuit of the Americas": "USA",
    "Autódromo Hermanos Rodríguez": "Mexico",
    "Autódromo José Carlos Pace": "Brazil",
    "Las Vegas Street Circuit": "Las Vegas",
    "Losail International Circuit": "Qatar",
    "Yas Marina Circuit": "Abu Dhabi"
}

# Map of track names to IDs based on the telemetry repository
TRACK_ID_MAPPING = {
    "Bahrain International Circuit": 3,        # sakhir in track_dictionary
    "Jeddah Corniche Circuit": 29,             # jeddah
    "Albert Park Circuit": 0,                  # melbourne
    "Suzuka International Racing Course": 13,  # suzuka
    "Shanghai International Circuit": 2,       # shanghai
    "Miami International Autodrome": 30,       # Miami
    "Autodromo Enzo e Dino Ferrari": 27,       # imola
    "Circuit de Monaco": 5,                    # monaco
    "Circuit Gilles Villeneuve": 6,            # montreal
    "Circuit de Barcelona-Catalunya": 4,       # catalunya
    "Red Bull Ring": 17,                       # austria
    "Silverstone Circuit": 7,                  # silverstone
    "Hungaroring": 9,                          # hungaroring
    "Circuit de Spa-Francorchamps": 10,        # spa
    "Circuit Zandvoort": 26,                   # zandvoort
    "Autodromo Nazionale Monza": 11,           # monza
    "Baku City Circuit": 20,                   # baku
    "Marina Bay Street Circuit": 12,           # singapore
    "Circuit of the Americas": 15,             # texas
    "Autódromo Hermanos Rodríguez": 19,        # mexico
    "Autódromo José Carlos Pace": 16,          # brazil
    "Las Vegas Street Circuit": 31,            # Las Vegas
    "Losail International Circuit": 32,        # Losail
    "Yas Marina Circuit": 14                   # abu_dhabi
}

# Path to the telemetry repository - check multiple possible locations
TELEMETRY_REPO_PATH = "C:/Users/landg/Desktop/f1-24-app/f1-24-telemetry-application"

DATABASE_URL = "backend/database/f1_leaderboard.db"
API_PORT = 8000
AUTO_CYCLE_INTERVAL_SECONDS = 30
NUMBER_OF_RIGS = 4 # Updated to 4
DEFAULT_RIG_NAMES = {
    "RIG1": "Simulator 1",
    "RIG2": "Simulator 2",
    "RIG3": "Simulator 3",
    "RIG4": "Simulator 4" # Added RIG4
}
DEFAULT_UDP_PORT = 20777

# --- Network Configuration Profiles ---
SHOP_NETWORK_CONFIG = {
    "name": "Shop/Home Network",
    "api_server_ip": "192.168.0.224", # Your operator PC's SHOP IP
    "rig_ips": {
        'RIG1': '192.168.0.210', 'RIG2': '192.168.0.211',
        'RIG3': '192.168.0.212', 'RIG4': '192.168.0.213',
    },
    "gateway": "192.168.0.1", "subnet_mask": "255.255.255.0",
    "network_range": "192.168.0.x"
}

MOBILE_NETWORK_CONFIG = {
    "name": "Mobile/Event Network",
    "api_server_ip": "192.168.1.100", # Your operator PC's MOBILE IP
    "rig_ips": {
        'RIG1': '192.168.1.103', 'RIG2': '192.168.1.104', # Your RIG1 actual MOBILE IP
        'RIG3': '192.168.1.105', 'RIG4': '192.168.1.106',
    },
    "gateway": "192.168.1.1", "subnet_mask": "255.255.255.0",
    "network_range": "192.168.1.x"
}

# --- Active Network Configuration ---
# Determined at runtime by environment variable in main.py (and startup scripts)
ACTIVE_NETWORK_PROFILE = os.environ.get('NETWORK_PROFILE', 'SHOP').upper()

if ACTIVE_NETWORK_PROFILE == "MOBILE":
    CURRENT_NETWORK_CONFIG = MOBILE_NETWORK_CONFIG
    print(f"INFO: Using MOBILE network profile from app_config.py. Operator IP: {MOBILE_NETWORK_CONFIG['api_server_ip']}")
else: # Default to SHOP
    CURRENT_NETWORK_CONFIG = SHOP_NETWORK_CONFIG
    if ACTIVE_NETWORK_PROFILE != "SHOP": 
        print(f"Warning: Invalid NETWORK_PROFILE env var '{ACTIVE_NETWORK_PROFILE}'. Defaulting to SHOP. Operator IP: {SHOP_NETWORK_CONFIG['api_server_ip']}")
    else:
        print(f"INFO: Using SHOP network profile from app_config.py. Operator IP: {SHOP_NETWORK_CONFIG['api_server_ip']}")
    ACTIVE_NETWORK_PROFILE = "SHOP"


# Export these directly - they will reflect the chosen profile from above
API_HOST = CURRENT_NETWORK_CONFIG["api_server_ip"]
RIG_IP_MAPPING = CURRENT_NETWORK_CONFIG["rig_ips"]
# Keep NETWORK_CONFIG for any other part of the system that might need the full current config
NETWORK_CONFIG = CURRENT_NETWORK_CONFIG 

# For convenience, also export SHOP_NETWORK and MOBILE_NETWORK if needed by other modules (e.g. admin UI)
SHOP_NETWORK = SHOP_NETWORK_CONFIG
MOBILE_NETWORK = MOBILE_NETWORK_CONFIG

# Function to print current effective settings (for debugging or info)
def print_active_network_config():
    # This function is for debugging and can be called from main.py if needed
    print(f"--- app_config.py: Active Network Profile Report ---")
    print(f"  Effective Profile: {ACTIVE_NETWORK_PROFILE}")
    print(f"  API Host (Server IP for Uvicorn): {API_HOST}")
    print(f"  Rig IPs Used for Commands: {RIG_IP_MAPPING}")
    print(f"  Full Current Config Object: {NETWORK_CONFIG}")
    print(f"----------------------------------------------------")

# The set_network_profile function is removed as profile is set by ENV var at import time. 