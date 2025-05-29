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

# Path to the telemetry repository - check multiple possible locations
import os

# Common locations where the F1 telemetry repository might be installed
_POSSIBLE_TELEMETRY_PATHS = [
    "C:/f1-24-telemetry-application",         # Auto-downloaded location
    "C:/Users/landg/Desktop/f1-24-app/f1-24-telemetry-application",
    "C:/F1Telemetry/f1-24-telemetry-application", 
    "D:/f1-24-telemetry-application",
    os.path.join(os.path.expanduser("~"), "Desktop", "f1-24-telemetry-application"),
    os.path.join(os.path.expanduser("~"), "Documents", "f1-24-telemetry-application"),
    os.path.join(os.path.dirname(__file__), "..", "f1-24-telemetry-application"),  # Relative to installer
]

# Find the first existing telemetry repository path
TELEMETRY_REPO_PATH = None
for path in _POSSIBLE_TELEMETRY_PATHS:
    if os.path.exists(path):
        TELEMETRY_REPO_PATH = path
        break

# If not found, use the default (original) path - the rig_listener will handle the error
if TELEMETRY_REPO_PATH is None:
    TELEMETRY_REPO_PATH = "C:/f1-24-telemetry-application"

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