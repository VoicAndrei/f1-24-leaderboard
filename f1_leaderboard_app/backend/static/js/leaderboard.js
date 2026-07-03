/**
 * F1 Leaderboard JavaScript
 *
 * Fetches leaderboard data and updates the UI on a refresh interval.
 */

const REFRESH_MS = 5000;

function formatLapTime(timeMs) {
    if (!timeMs) return "00:00.000";

    const totalSeconds = timeMs / 1000;
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = Math.floor(totalSeconds % 60);
    const milliseconds = Math.floor((totalSeconds - Math.floor(totalSeconds)) * 1000);

    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
}

async function updateLeaderboard() {
    try {
        const response = await fetch('/api/display/current_leaderboard_data');
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const data = await response.json();

        const trackNameElement = document.getElementById('track-name');
        trackNameElement.textContent = data.track_name;

        const leaderboardBody = document.getElementById('leaderboard-body');
        leaderboardBody.innerHTML = '';

        const leaderboardData = data.leaderboard;

        if (!leaderboardData || leaderboardData.length === 0) {
            const noDataRow = document.createElement('tr');
            noDataRow.className = 'no-data';
            noDataRow.innerHTML = `<td colspan="3">No lap times recorded for this track yet.</td>`;
            leaderboardBody.appendChild(noDataRow);
            return;
        }

        leaderboardData.forEach((lapData, index) => {
            const row = document.createElement('tr');
            if (index === 0) row.className = 'first-place';
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${lapData.player_name}</td>
                <td>${formatLapTime(lapData.lap_time_ms)}</td>
            `;
            leaderboardBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching leaderboard data:', error);
        const leaderboardBody = document.getElementById('leaderboard-body');
        leaderboardBody.innerHTML = `
            <tr class="error">
                <td colspan="3">Error loading leaderboard. Please try again later.</td>
            </tr>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateLeaderboard();
    setInterval(updateLeaderboard, REFRESH_MS);
});
