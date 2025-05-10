/**
 * F1 Leaderboard JavaScript
 * 
 * This script fetches leaderboard data from the API and updates the HTML table.
 * It handles dynamic track changes and auto-cycling.
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

// Update the display with current leaderboard data
async function updateDisplay() {
    try {
        // Fetch data from the current leaderboard endpoint
        const response = await fetch('/api/display/current_leaderboard_data');
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update track name in UI
        const trackNameElement = document.getElementById('track-name');
        trackNameElement.textContent = data.track_name;
        
        // Update cycle status indicator if present
        const cycleStatusIndicator = document.getElementById('cycle-status-indicator');
        if (cycleStatusIndicator) {
            cycleStatusIndicator.textContent = data.auto_cycle_enabled ? 'Auto-Cycling' : 'Manual Selection';
            cycleStatusIndicator.className = data.auto_cycle_enabled ? 'cycling' : 'manual';
        }
        
        // Get the table body element
        const leaderboardBody = document.getElementById('leaderboard-body');
        
        // Clear existing rows
        leaderboardBody.innerHTML = '';
        
        // Get the leaderboard data
        const leaderboardData = data.leaderboard;
        
        // Check if there's no data
        if (!leaderboardData || leaderboardData.length === 0) {
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
    // Initial update
    updateDisplay();
    
    // Auto-refresh the leaderboard every 5 seconds
    setInterval(updateDisplay, 5000);
}); 