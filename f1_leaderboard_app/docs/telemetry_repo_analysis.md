# F1 2024 Telemetry Repository Analysis

This document contains an analysis of the provided F1 2024 telemetry repository located at `/c:/Users/landg/Desktop/f1-24-app/f1-24-telemetry-application`.

## Overview

The telemetry repository is a Python-based solution for receiving, parsing, and displaying telemetry data from the F1 2024 game. It captures UDP data sent by the game and processes it into usable information about tracks, lap times, car status, and other race-related data.

## Key Components

### Core Files and Classes

1. **parser2024.py**:
   - Contains the `Listener` class for UDP packet reception and various packet structures
   - Defines data structures for all telemetry packet types
   - Includes packet parsers for the F1 2024 game format

2. **packet_management.py**:
   - Handles processing of different packet types received from the game
   - Updates player and session data with received telemetry
   - Contains functions like `update_lap_data()` which is crucial for our lap time tracking

3. **Player.py**:
   - Defines a `Player` class that stores all data related to a driver/car
   - Maintains important data like position, lap times, sector times, and best lap information

4. **Session.py**:
   - Defines a `Session` class that stores session-related information
   - Maintains track data, weather data, and best lap times for the session

5. **dictionnaries.py**:
   - Contains mappings for tracks, teams, tires, weather, and other game data
   - Includes the `track_dictionary` which maps track IDs to track names and visual properties

### Telemetry Data Reception

The repository uses a `Listener` class (in parser2024.py) for UDP data reception:

```python
class Listener:
    def __init__(self, port=20777, adress="127.0.0.1", redirect=0, redirect_port=20777):
        self.port = port
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.socket.setblocking(0)
        self.address = adress
        self.redirect = redirect
        self.redirect_port = redirect_port
        
    def get(self, packet=None):
        # Receives UDP packets and returns header and packet data
        # ...
```

### Key Data Structures for Lap Times

The most relevant packet types for our lap time tracking purposes:

1. **PacketLapData**:
   - Contains lap times, sector times, and car positions
   - Holds both current and last lap information
   - Includes validity flags for laps

2. **PacketSessionData**:
   - Contains information about the current session (practice, qualifying, race)
   - Includes track information and weather data

## Relevant Track Data

The repository includes track data files in the `tracks/` directory, with racing line information for each official F1 track. These files follow naming patterns like `[track_name]_2020_racingline.txt`.

The `track_dictionary` in `dictionnaries.py` maps track IDs to their names and visual properties:

```python
track_dictionary = {
    0: ("melbourne", 3.5, 300, 300),
    1: ("paul_ricard", 2.5, 500, 300),
    # ... more tracks ...
    31: ("Las Vegas", 4, 400, 300),
    32: ("Losail", 2.5, 400, 300)
}
```

## Example Usage for Lap Time Extraction

Based on the repository's structure, here's how we can extract lap time data:

1. Initialize a listener to receive UDP data from the game:
```python
from parser2024 import Listener
listener = Listener(port=20777)  # Default port used by F1 2024
```

2. Set up data structures to store player and session information:
```python
from Player import Player
from Session import Session
players = [Player() for _ in range(22)]  # F1 has up to 22 cars
session = Session()
```

3. Continuously receive and process packets:
```python
while True:
    header_and_packet = listener.get()
    if header_and_packet:
        header, packet = header_and_packet
        
        # Process lap data packets to extract lap times
        if header.m_packet_id == 2:  # Lap data packet
            for i in range(len(packet.m_lap_data)):
                lap_data = packet.m_lap_data[i]
                player = players[i]
                
                # Update player lap times
                player.lastLapTime = lap_data.m_last_lap_time_in_ms / 1000  # Convert to seconds
                player.currentLapTime = lap_data.m_current_lap_time_in_ms / 1000
                
                # Track best lap times
                if player.bestLapTime > player.lastLapTime != 0 or player.bestLapTime == 0:
                    player.bestLapTime = player.lastLapTime
```

## Integration Challenges

1. **Data Consistency**: The telemetry data comes in separate packets, so we need to ensure consistency when combining data from different packet types.

2. **Player/Rig Identification**: The repository is designed for viewing telemetry data, not for assigning specific players to rigs. We'll need to extend the system to:
   - Identify which telemetry data comes from which simulator rig
   - Associate the correct player name with each rig's telemetry data

3. **UDP Packet Loss**: UDP doesn't guarantee packet delivery, so our system must be resilient to packet loss.

4. **Multiple Listeners**: We'll need to run separate listener instances for each simulator rig, each configured with a unique identifier.

5. **Track Identification**: The game uses numeric IDs for tracks, so we'll need to map these IDs to human-readable track names using the `track_dictionary`.

## Conclusion

The F1 2024 telemetry repository provides a solid foundation for capturing and parsing telemetry data from the game. We can leverage its `Listener` class and packet structures to extract lap times, track information, and other relevant data for our leaderboard application.

For our application, we'll need to:
1. Set up a listener for each simulator rig
2. Process lap time data from the UDP packets
3. Send this data to our backend API, including the rig identifier
4. Store lap times in our database with associated player names
5. Present this data in a leaderboard UI

The repository's code for handling UDP packets and parsing telemetry data will be instrumental in building our telemetry listener component. 