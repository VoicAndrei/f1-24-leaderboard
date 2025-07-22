/**
 * F1 Leaderboard Database Management JavaScript
 * 
 * This script handles the database management functionality:
 * - Fetching and displaying database statistics
 * - Displaying all lap time entries with filtering
 * - Editing and deleting lap time entries
 * - Search and filter capabilities
 */

// Global variables
let allLapTimes = [];
let filteredLapTimes = [];
let editingEntry = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Fetch initial data
    fetchDatabaseStats();
    fetchLapTimes();
    
    // Populate track dropdowns
    populateTrackDropdowns();
    
    // Set up event listeners
    setupEventListeners();
    
    // Set up periodic refresh (every 30 seconds)
    setInterval(() => {
        fetchDatabaseStats();
        fetchLapTimes();
    }, 30000);
});

// Set up event listeners
function setupEventListeners() {
    // Search and filter inputs
    document.getElementById('search-player').addEventListener('input', applyFilters);
    document.getElementById('filter-track').addEventListener('change', applyFilters);
    document.getElementById('filter-rig').addEventListener('change', applyFilters);
    document.getElementById('clear-filters').addEventListener('click', clearFilters);
    
    // Edit form buttons
    document.getElementById('save-edit').addEventListener('click', saveEdit);
    document.getElementById('cancel-edit').addEventListener('click', cancelEdit);
}

// Fetch database statistics
async function fetchDatabaseStats() {
    try {
        const response = await fetch('/api/database/stats');
        const stats = await response.json();
        
        if (response.ok) {
            displayStats(stats);
        } else {
            console.error('Error fetching database stats:', stats.detail);
        }
    } catch (error) {
        console.error('Error fetching database stats:', error);
    }
}

// Display database statistics
function displayStats(stats) {
    document.getElementById('total-lap-times').textContent = stats.total_lap_times || 0;
    document.getElementById('unique-players').textContent = stats.unique_players || 0;
    document.getElementById('total-rigs').textContent = stats.total_rigs || 0;
    document.getElementById('tracks-with-times').textContent = stats.tracks_with_times || 0;
    
    // Display fastest lap if available
    if (stats.fastest_lap) {
        document.getElementById('fastest-lap-time').textContent = stats.fastest_lap.time_formatted;
        document.getElementById('fastest-lap-details').textContent = 
            `${stats.fastest_lap.player} on ${stats.fastest_lap.track}`;
        document.getElementById('fastest-lap-section').style.display = 'block';
    } else {
        document.getElementById('fastest-lap-section').style.display = 'none';
    }
}

// Fetch all lap times
async function fetchLapTimes() {
    try {
        const response = await fetch('/api/database/lap_times');
        const lapTimes = await response.json();
        
        if (response.ok) {
            allLapTimes = lapTimes;
            filteredLapTimes = [...lapTimes];
            displayLapTimes(filteredLapTimes);
            populateFilterOptions();
        } else {
            console.error('Error fetching lap times:', lapTimes.detail);
            showMessage('Error loading lap times: ' + (lapTimes.detail || 'Unknown error'), false);
        }
    } catch (error) {
        console.error('Error fetching lap times:', error);
        showMessage('Error loading lap times: ' + error.message, false);
    }
}

// Display lap times table
function displayLapTimes(lapTimes) {
    const container = document.getElementById('lap-times-container');
    
    if (lapTimes.length === 0) {
        container.innerHTML = '<div class="loading">No lap times found.</div>';
        return;
    }
    
    let tableHTML = `
        <table class="lap-times-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Player</th>
                    <th>Track</th>
                    <th>Lap Time</th>
                    <th>Rig</th>
                    <th>Date</th>
                    <th>Contact</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    lapTimes.forEach(entry => {
        const date = new Date(entry.timestamp);
        const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        const contactInfo = getContactInfo(entry);
        
        tableHTML += `
            <tr id="row-${entry.id}">
                <td>${entry.id}</td>
                <td><strong>${entry.player_name}</strong></td>
                <td>${entry.track_name}</td>
                <td><span style="font-family: monospace; font-weight: bold; color: #f39c12;">${entry.lap_time_formatted}</span></td>
                <td>${entry.rig_identifier}</td>
                <td>${formattedDate}</td>
                <td class="contact-info">${contactInfo}</td>
                <td>
                    <button class="edit-btn" onclick="startEdit(${entry.id})">Edit</button>
                    <button class="delete-btn" onclick="confirmDelete(${entry.id})">Delete</button>
                </td>
            </tr>
        `;
    });
    
    tableHTML += `
            </tbody>
        </table>
    `;
    
    container.innerHTML = tableHTML;
}

// Get contact info display
function getContactInfo(entry) {
    const parts = [];
    if (entry.phone_number) parts.push(`📞 ${entry.phone_number}`);
    if (entry.email) parts.push(`📧 ${entry.email}`);
    return parts.length > 0 ? parts.join('<br>') : '-';
}

// Populate track dropdowns
function populateTrackDropdowns() {
    const filterTrackSelect = document.getElementById('filter-track');
    const editTrackSelect = document.getElementById('edit-track');
    
    // Clear existing options (except default)
    filterTrackSelect.innerHTML = '<option value="">All tracks</option>';
    editTrackSelect.innerHTML = '<option value="">Select track...</option>';
    
    // Add track options
    F1_TRACKS_LIST.forEach(track => {
        const filterOption = document.createElement('option');
        filterOption.value = track;
        filterOption.textContent = track;
        filterTrackSelect.appendChild(filterOption);
        
        const editOption = document.createElement('option');
        editOption.value = track;
        editOption.textContent = track;
        editTrackSelect.appendChild(editOption);
    });
}

// Populate filter options based on available data
function populateFilterOptions() {
    const filterRigSelect = document.getElementById('filter-rig');
    
    // Get unique rig identifiers
    const uniqueRigs = [...new Set(allLapTimes.map(entry => entry.rig_identifier))];
    
    // Clear existing options (except default)
    filterRigSelect.innerHTML = '<option value="">All rigs</option>';
    
    // Add rig options
    uniqueRigs.sort().forEach(rig => {
        const option = document.createElement('option');
        option.value = rig;
        option.textContent = rig;
        filterRigSelect.appendChild(option);
    });
}

// Apply search and filter
function applyFilters() {
    const searchTerm = document.getElementById('search-player').value.toLowerCase();
    const trackFilter = document.getElementById('filter-track').value;
    const rigFilter = document.getElementById('filter-rig').value;
    
    filteredLapTimes = allLapTimes.filter(entry => {
        const matchesSearch = entry.player_name.toLowerCase().includes(searchTerm);
        const matchesTrack = !trackFilter || entry.track_name === trackFilter;
        const matchesRig = !rigFilter || entry.rig_identifier === rigFilter;
        
        return matchesSearch && matchesTrack && matchesRig;
    });
    
    displayLapTimes(filteredLapTimes);
}

// Clear all filters
function clearFilters() {
    document.getElementById('search-player').value = '';
    document.getElementById('filter-track').value = '';
    document.getElementById('filter-rig').value = '';
    
    filteredLapTimes = [...allLapTimes];
    displayLapTimes(filteredLapTimes);
}

// Start editing an entry
function startEdit(entryId) {
    const entry = allLapTimes.find(e => e.id === entryId);
    if (!entry) return;
    
    editingEntry = entry;
    
    // Populate edit form
    document.getElementById('edit-id').value = entry.id;
    document.getElementById('edit-player').value = entry.player_name;
    document.getElementById('edit-time').value = entry.lap_time_formatted;
    document.getElementById('edit-track').value = entry.track_name;
    
    // Show edit form
    document.getElementById('edit-form').style.display = 'block';
    document.getElementById('edit-player').focus();
    
    // Scroll to form
    document.getElementById('edit-form').scrollIntoView({ behavior: 'smooth' });
}

// Save edit
async function saveEdit() {
    const id = document.getElementById('edit-id').value;
    const playerName = document.getElementById('edit-player').value.trim();
    const lapTime = document.getElementById('edit-time').value.trim();
    const trackName = document.getElementById('edit-track').value;
    
    // Validation
    if (!playerName) {
        showMessage('Please enter a player name.', false);
        return;
    }
    
    if (!lapTime) {
        showMessage('Please enter a lap time.', false);
        return;
    }
    
    if (!trackName) {
        showMessage('Please select a track.', false);
        return;
    }
    
    // Validate lap time format (MM:SS.mmm)
    if (!isValidLapTimeFormat(lapTime)) {
        showMessage('Please enter lap time in format MM:SS.mmm (e.g., 01:23.456)', false);
        return;
    }
    
    try {
        const response = await fetch(`/api/database/lap_times/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: parseInt(id),
                player_name: playerName,
                lap_time: lapTime,
                track_name: trackName
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(result.message || 'Lap time updated successfully!', true);
            cancelEdit();
            fetchLapTimes(); // Refresh data
        } else {
            showMessage('Error: ' + (result.detail || 'Failed to update lap time'), false);
        }
    } catch (error) {
        console.error('Error saving edit:', error);
        showMessage('Error: ' + error.message, false);
    }
}

// Cancel edit
function cancelEdit() {
    document.getElementById('edit-form').style.display = 'none';
    editingEntry = null;
    
    // Clear form
    document.getElementById('edit-id').value = '';
    document.getElementById('edit-player').value = '';
    document.getElementById('edit-time').value = '';
    document.getElementById('edit-track').value = '';
}

// Confirm delete
function confirmDelete(entryId) {
    const entry = allLapTimes.find(e => e.id === entryId);
    if (!entry) return;
    
    if (confirm(`Are you sure you want to delete this lap time entry?\n\nPlayer: ${entry.player_name}\nTrack: ${entry.track_name}\nTime: ${entry.lap_time_formatted}\n\nThis action cannot be undone.`)) {
        deleteLapTime(entryId);
    }
}

// Delete lap time entry
async function deleteLapTime(entryId) {
    try {
        const response = await fetch(`/api/database/lap_times/${entryId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(result.message || 'Lap time deleted successfully!', true);
            fetchLapTimes(); // Refresh data
            fetchDatabaseStats(); // Update stats
        } else {
            showMessage('Error: ' + (result.detail || 'Failed to delete lap time'), false);
        }
    } catch (error) {
        console.error('Error deleting entry:', error);
        showMessage('Error: ' + error.message, false);
    }
}

// Validate lap time format
function isValidLapTimeFormat(timeString) {
    // Match MM:SS.mmm format
    const regex = /^\d{1,2}:\d{2}\.\d{3}$/;
    return regex.test(timeString);
}

// Show message
function showMessage(message, isSuccess) {
    const messageDiv = document.getElementById('db-message');
    messageDiv.textContent = message;
    messageDiv.className = isSuccess ? 'success' : 'error';
    messageDiv.style.display = 'block';
    
    // Hide message after 5 seconds
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}