-- F1 Leaderboard Application Database Schema

-- Tracks table - stores information about all F1 tracks
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Rigs table - stores information about simulator rigs
CREATE TABLE IF NOT EXISTS rigs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rig_identifier TEXT UNIQUE NOT NULL,
    current_player_name TEXT DEFAULT "N/A"
);

-- Lap times table - stores lap times for each track and rig
CREATE TABLE IF NOT EXISTS lap_times (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rig_id INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    player_name_on_lap TEXT NOT NULL,
    lap_time_ms INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rig_id) REFERENCES rigs (id),
    FOREIGN KEY (track_id) REFERENCES tracks (id)
);

-- Create indices for faster querying
CREATE INDEX IF NOT EXISTS idx_lap_times_track_id ON lap_times (track_id);
CREATE INDEX IF NOT EXISTS idx_lap_times_rig_id ON lap_times (rig_id);
CREATE INDEX IF NOT EXISTS idx_lap_times_lap_time_ms ON lap_times (lap_time_ms); 