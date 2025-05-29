"""
F1 Leaderboard Application Configuration
"""

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

# Path to the telemetry repository - fixed for Windows
TELEMETRY_REPO_PATH = "C:/Users/landg/Desktop/f1-24-app/f1-24-telemetry-application"

# Database URL
DATABASE_URL = "backend/database/f1_leaderboard.db"

# API server configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# Auto cycle interval for leaderboard display (in seconds)
AUTO_CYCLE_INTERVAL_SECONDS = 30

# Number of racing simulator rigs
NUMBER_OF_RIGS = 3

# Default names for the simulator rigs
DEFAULT_RIG_NAMES = {
    "RIG1": "Simulator 1",
    "RIG2": "Simulator 2",
    "RIG3": "Simulator 3"
}

# Default UDP port for telemetry data
DEFAULT_UDP_PORT = 20777

# Network Configuration Profiles
# Choose which profile to use by setting NETWORK_PROFILE below

# Profile 1: Shop/Home Network (192.168.0.x)
SHOP_NETWORK = {
    "name": "Shop/Home Network",
    "api_server_ip": "192.168.0.224",  # Reception laptop
    "rig_ips": {
        'RIG1': '192.168.0.210',
        'RIG2': '192.168.0.211', 
        'RIG3': '192.168.0.212',
        'RIG4': '192.168.0.213',
    },
    "gateway": "192.168.0.1",
    "subnet_mask": "255.255.255.0",
    "network_range": "192.168.0.x"
}

# Profile 2: Mobile/Event Network (192.168.1.x) 
MOBILE_NETWORK = {
    "name": "Mobile/Event Network", 
    "api_server_ip": "192.168.1.100",  # Reception laptop (actual IP)
    "rig_ips": {
        'RIG1': '192.168.1.103',  # Using actual rig IP as base
        'RIG2': '192.168.1.104',
        'RIG3': '192.168.1.105', 
        'RIG4': '192.168.1.106',
    },
    "gateway": "192.168.1.1",
    "subnet_mask": "255.255.255.0", 
    "network_range": "192.168.1.x"
}

# Default profile (will be overridden by startup scripts)
NETWORK_PROFILE = "SHOP"

# Get the active network configuration  
if NETWORK_PROFILE == "MOBILE":
    NETWORK_CONFIG = MOBILE_NETWORK
else:
    NETWORK_CONFIG = SHOP_NETWORK

# Extract values for backward compatibility
API_SERVER_IP = NETWORK_CONFIG["api_server_ip"]
RIG_IP_MAPPING = NETWORK_CONFIG["rig_ips"]

# Function to override network config at runtime
def set_network_profile(profile):
    """Set network profile programmatically."""
    global NETWORK_PROFILE, NETWORK_CONFIG, API_SERVER_IP, RIG_IP_MAPPING
    
    NETWORK_PROFILE = profile
    if profile == "MOBILE":
        NETWORK_CONFIG = MOBILE_NETWORK
    else:
        NETWORK_CONFIG = SHOP_NETWORK
    
    API_SERVER_IP = NETWORK_CONFIG["api_server_ip"]
    RIG_IP_MAPPING = NETWORK_CONFIG["rig_ips"] 