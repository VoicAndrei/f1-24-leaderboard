/**
 * F1 Leaderboard JavaScript
 * 
 * This script fetches leaderboard data from the API and updates the HTML table.
 * It also handles auto-refresh to keep the data up-to-date.
 */

// Format lap time from milliseconds to MM:SS.mmm
function formatLapTime(timeMs) {
    if (!timeMs) return "00:00.000";
    
    const totalSeconds = timeMs / 1000;
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = Math.floor(totalSeconds % 60);
    const milliseconds = Math.floor((totalSeconds - Math.floor(totalSeconds)) * 1000);
    
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
}

// Fetch leaderboard data from the API
async function fetchLeaderboardData(trackName) {
    try {
        // Update track name in UI
        const trackNameElement = document.getElementById('track-name');
        trackNameElement.textContent = trackName;
        
        // Encode the track name for URL
        const encodedTrackName = encodeURIComponent(trackName);
        
        // Fetch data from the API
        const response = await fetch(`/api/leaderboard/${encodedTrackName}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const leaderboardData = await response.json();
        
        // Get the table body element
        const leaderboardBody = document.getElementById('leaderboard-body');
        
        // Clear existing rows
        leaderboardBody.innerHTML = '';
        
        // Check if there's no data
        if (leaderboardData.length === 0) {
            const noDataRow = document.createElement('tr');
            noDataRow.className = 'no-data';
            noDataRow.innerHTML = `
                <td colspan="3">No lap times recorded for this track yet.</td>
            `;
            leaderboardBody.appendChild(noDataRow);
            return;
        }
        
        // Add rows for each lap time
        leaderboardData.forEach((lapData, index) => {
            const row = document.createElement('tr');
            
            // Highlight the first place
            if (index === 0) {
                row.className = 'first-place';
            }
            
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${lapData.player_name}</td>
                <td>${formatLapTime(lapData.lap_time_ms)}</td>
            `;
            
            leaderboardBody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Error fetching leaderboard data:', error);
        
        // Display error message in the table
        const leaderboardBody = document.getElementById('leaderboard-body');
        leaderboardBody.innerHTML = `
            <tr class="error">
                <td colspan="3">Error loading leaderboard. Please try again later.</td>
            </tr>
        `;
    }
}

// Initialize the leaderboard when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Make sure INITIAL_TRACK is defined in the HTML (passed from the server)
    if (typeof INITIAL_TRACK === 'undefined') {
        console.error('Error: INITIAL_TRACK is not defined');
        
        // Fallback to a hardcoded track name if needed
        const fallbackTrack = "Bahrain International Circuit";
        fetchLeaderboardData(fallbackTrack);
    } else {
        // Remove quotes if they're in the string (from tojson filter)
        const trackName = INITIAL_TRACK.replace(/^"|"$/g, '');
        fetchLeaderboardData(trackName);
    }
    
    // Auto-refresh the leaderboard every 8 seconds
    setInterval(() => {
        // Use the current track name from the UI
        const currentTrack = document.getElementById('track-name').textContent;
        fetchLeaderboardData(currentTrack);
    }, 8000);
}); 