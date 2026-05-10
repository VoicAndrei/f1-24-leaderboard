/**
 * F1 Leaderboard JavaScript
 *
 * Fetches leaderboard data and rig timer status, updates the UI on a refresh
 * interval. The rig status panel shows which simulators are busy and how much
 * time remains so waiting players know how long they have to queue.
 */

const REFRESH_MS = 5000;
const RIG_TICK_MS = 1000;

// Local copy of the latest server-reported timer state so we can tick
// remaining seconds down between full refreshes without flooding the API.
let rigStatesLocal = [];
let rigsLastFetchedAt = 0;

function formatLapTime(timeMs) {
    if (!timeMs) return "00:00.000";

    const totalSeconds = timeMs / 1000;
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = Math.floor(totalSeconds % 60);
    const milliseconds = Math.floor((totalSeconds - Math.floor(totalSeconds)) * 1000);

    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
}

function formatRemaining(seconds) {
    const safe = Math.max(0, Math.floor(seconds));
    const mm = Math.floor(safe / 60);
    const ss = safe % 60;
    return `${mm}:${ss.toString().padStart(2, '0')}`;
}

function rigDisplayLabel(rigId) {
    // "RIG3" -> "RIG 3"
    const match = /^RIG(\d+)$/i.exec(rigId);
    return match ? `RIG ${match[1]}` : rigId;
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

async function refreshRigStatus() {
    try {
        const response = await fetch('/api/admin/timer/status');
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();
        rigStatesLocal = Array.isArray(data) ? data : [];
        rigsLastFetchedAt = Date.now();
        renderRigStatus();
    } catch (error) {
        console.error('Error fetching rig timer status:', error);
        const list = document.getElementById('rig-status-list');
        if (list) {
            list.innerHTML = '<li class="rig-status-empty">Status indisponibil</li>';
        }
    }
}

function renderRigStatus() {
    const list = document.getElementById('rig-status-list');
    if (!list) return;

    const elapsedSec = Math.floor((Date.now() - rigsLastFetchedAt) / 1000);
    const active = rigStatesLocal
        .filter(r => r && r.timer_active)
        .map(r => ({
            rig_identifier: r.rig_identifier,
            remaining_time: Math.max(0, (r.remaining_time || 0) - elapsedSec)
        }));

    list.innerHTML = '';

    if (active.length === 0) {
        const li = document.createElement('li');
        li.className = 'rig-free';
        li.textContent = 'Toate simulatoarele sunt libere — urcă acum!';
        list.appendChild(li);
        return;
    }

    active
        .sort((a, b) => a.rig_identifier.localeCompare(b.rig_identifier))
        .forEach(rig => {
            const li = document.createElement('li');
            li.className = 'rig-active';
            li.textContent = `${rigDisplayLabel(rig.rig_identifier)}: ${formatRemaining(rig.remaining_time)} rămase`;
            list.appendChild(li);
        });
}

document.addEventListener('DOMContentLoaded', () => {
    updateLeaderboard();
    refreshRigStatus();

    setInterval(updateLeaderboard, REFRESH_MS);
    setInterval(refreshRigStatus, REFRESH_MS);
    setInterval(renderRigStatus, RIG_TICK_MS);
});
