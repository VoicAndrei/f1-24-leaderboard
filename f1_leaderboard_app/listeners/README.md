# F1 Leaderboard Telemetry Listeners

This directory contains the telemetry listener scripts for the F1 Leaderboard application.

## Basic Listener (Proof of Concept)

The `basic_listener.py` script demonstrates how to receive and process telemetry data from the F1 2024 game. This is a standalone proof-of-concept that prints lap time information to the console.

### Prerequisites

1. F1 2024 game with UDP telemetry enabled
2. Python 3.8+ installed
3. The F1 telemetry repository at the path specified in the `app_config.py` file

### Configuring F1 2024 Game for Telemetry

1. Start F1 2024
2. Go to **Settings** > **Telemetry Settings**
3. Set **UDP Telemetry** to **On**
4. Set **UDP Broadcast Mode** to **On** (if the game and listener are on the same computer)
   - If not, set **UDP IP Address** to the IP address of the computer running the listener
5. Set **UDP Port** to **20777** (default)
6. Recommended: Set **UDP Send Rate** to **60Hz** for more accurate telemetry data
7. Optional: Set **UDP Format** to **2024** (should be the default for F1 2024)

### Running the Basic Listener

From the root of the `f1_leaderboard_app` directory:

```bash
python listeners/basic_listener.py
```

### Testing

1. Start the listener script
2. Launch the F1 2024 game
3. Enter any game mode (Time Trial is recommended for testing)
4. Complete laps to see the lap times appear in the console output
5. Press Ctrl+C to stop the listener

### Expected Output

When a lap is completed, the listener will display information in the console:

```
2025-05-10 22:45:32,123 - INFO - New Lap Completed - Player Car (Index: 0)
  Track: Bahrain International Circuit
  Lap Time: 01:32.456
  Position: 1
  Current Lap: 2

2025-05-10 22:45:32,124 - INFO - New Personal Best: 01:32.456
```

## Advanced Listeners

Future implementations will extend this basic listener to:

1. Associate telemetry data with specific simulator rigs
2. Send lap time data to the backend API
3. Implement connection status monitoring and reconnection logic 