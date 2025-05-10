/**
 * F1 Leaderboard Admin JavaScript
 * 
 * This script handles the admin panel functionality:
 * - Fetching and displaying current rig-player assignments
 * - Handling form submission to assign a player to a rig
 * - Leaderboard display control (track selection and auto-cycle toggle)
 */

// Fetch and display rig assignments
async function fetchRigAssignments() {
    try {
        // Get table body element
        const tableBody = document.getElementById('rigs-table-body');
        
        // Get dropdown for rigs
        const rigSelect = document.getElementById('rig-select');
        
        // Clear existing content
        tableBody.innerHTML = '';
        
        // Clear existing options except the disabled/selected placeholder
        const placeholder = rigSelect.querySelector('option[disabled]');
        rigSelect.innerHTML = '';
        rigSelect.appendChild(placeholder);
        
        // Fetch data from API
        const response = await fetch('/api/admin/rigs');
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const rigs = await response.json();
        
        // Check if there are any rigs
        if (rigs.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="2">No rigs found. Please check the database setup.</td>
                </tr>
            `;
            return;
        }
        
        // Add each rig to the table
        rigs.forEach(rig => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${rig.rig_identifier}</td>
                <td>${rig.current_player_name}</td>
            `;
            tableBody.appendChild(row);
            
            // Add rig to dropdown
            const option = document.createElement('option');
            option.value = rig.rig_identifier;
            option.textContent = rig.rig_identifier;
            rigSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching rig assignments:', error);
        
        // Display error message
        const tableBody = document.getElementById('rigs-table-body');
        tableBody.innerHTML = `
            <tr>
                <td colspan="2" class="error">Error loading rig assignments. Please try again later.</td>
            </tr>
        `;
        
        // Display error message
        showMessage(`Error: ${error.message}`, false);
    }
}

// Handle form submission
async function assignPlayer(event) {
    // Prevent default form submission
    event.preventDefault();
    
    // Get form values
    const rigIdentifier = document.getElementById('rig-select').value;
    const playerName = document.getElementById('player-name-input').value.trim();
    
    // Basic validation
    if (!rigIdentifier) {
        showMessage('Please select a rig.', false);
        return;
    }
    
    if (!playerName) {
        showMessage('Please enter a player name.', false);
        return;
    }
    
    try {
        // Prepare request data
        const data = {
            rig_identifier: rigIdentifier,
            player_name: playerName
        };
        
        // Submit data to API
        const response = await fetch('/api/admin/rigs/assign_player', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        // Parse response
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Failed to assign player to rig.');
        }
        
        // Show success message
        showMessage(result.message || 'Player assigned successfully!', true);
        
        // Refresh rig assignments
        fetchRigAssignments();
        
        // Clear the form
        document.getElementById('player-name-input').value = '';
        document.getElementById('rig-select').selectedIndex = 0;
    } catch (error) {
        console.error('Error assigning player:', error);
        showMessage(`Error: ${error.message}`, false);
    }
}

// Populate track selection dropdown
function populateTrackSelectDropdown() {
    try {
        // Get track select dropdown
        const trackSelect = document.getElementById('manual-track-select');
        
        // Clear existing options except the placeholder
        const placeholder = trackSelect.querySelector('option[disabled]');
        trackSelect.innerHTML = '';
        trackSelect.appendChild(placeholder);
        
        // Make sure F1_TRACKS_LIST is defined
        if (typeof F1_TRACKS_LIST === 'undefined') {
            console.error('F1_TRACKS_LIST is not defined');
            
            // Add a fallback option
            const option = document.createElement('option');
            option.value = "Bahrain International Circuit";
            option.textContent = "Bahrain International Circuit";
            trackSelect.appendChild(option);
            return;
        }
        
        // Add each track to the dropdown
        F1_TRACKS_LIST.forEach(track => {
            const option = document.createElement('option');
            option.value = track;
            option.textContent = track;
            trackSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error populating track dropdown:', error);
    }
}

// Fetch and display current leaderboard status
async function fetchDisplayStatus() {
    try {
        // Get status elements
        const currentTrackElement = document.getElementById('current-display-track');
        const manualSelectionElement = document.getElementById('manual-selection-status');
        const autoCycleElement = document.getElementById('auto-cycle-status');
        const toggleButton = document.getElementById('toggle-autocycle-button');
        
        // Fetch status from API
        const response = await fetch('/api/admin/track/status');
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const status = await response.json();
        
        // Update current track
        currentTrackElement.textContent = status.current_display_track || 'Unknown';
        
        // Update manual selection status
        if (status.manual_selection_active) {
            manualSelectionElement.textContent = status.manual_selection || 'Active';
            manualSelectionElement.className = 'status-enabled';
        } else {
            manualSelectionElement.textContent = 'Inactive';
            manualSelectionElement.className = 'status-disabled';
        }
        
        // Update auto-cycle status
        autoCycleElement.textContent = status.auto_cycle_enabled ? 'Enabled' : 'Disabled';
        autoCycleElement.className = status.auto_cycle_enabled ? 'status-enabled' : 'status-disabled';
        
        // Update toggle button text
        toggleButton.textContent = status.auto_cycle_enabled ? 'Turn Auto-Cycle OFF' : 'Turn Auto-Cycle ON';
        
    } catch (error) {
        console.error('Error fetching display status:', error);
        
        // Show error in status elements
        document.getElementById('current-display-track').textContent = 'Error loading status';
        document.getElementById('manual-selection-status').textContent = 'Error';
        document.getElementById('auto-cycle-status').textContent = 'Error';
    }
}

// Handle manual track selection
async function setDisplayTrack() {
    // Get selected track
    const trackSelect = document.getElementById('manual-track-select');
    const selectedTrack = trackSelect.value;
    
    // Basic validation
    if (!selectedTrack) {
        showTrackControlMessage('Please select a track.', false);
        return;
    }
    
    try {
        // Prepare request data
        const data = {
            track_name: selectedTrack
        };
        
        // Submit data to API
        const response = await fetch('/api/admin/track/select', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        // Parse response
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Failed to set display track.');
        }
        
        // Show success message
        showTrackControlMessage(result.message || `Now displaying ${selectedTrack}`, true);
        
        // Refresh display status
        fetchDisplayStatus();
        
    } catch (error) {
        console.error('Error setting display track:', error);
        showTrackControlMessage(`Error: ${error.message}`, false);
    }
}

// Handle auto-cycle toggle
async function toggleAutoCycle() {
    try {
        // Submit request to API
        const response = await fetch('/api/admin/track/toggle_autocycle', {
            method: 'POST'
        });
        
        // Parse response
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Failed to toggle auto-cycle.');
        }
        
        // Show success message
        const newStatus = result.auto_cycle_enabled ? 'enabled' : 'disabled';
        showTrackControlMessage(`Auto-cycle ${newStatus}`, true);
        
        // Refresh display status
        fetchDisplayStatus();
        
    } catch (error) {
        console.error('Error toggling auto-cycle:', error);
        showTrackControlMessage(`Error: ${error.message}`, false);
    }
}

// Show message in the track control message div
function showTrackControlMessage(message, isSuccess) {
    const messageDiv = document.getElementById('track-control-message');
    
    // Set message text
    messageDiv.textContent = message;
    
    // Remove existing classes
    messageDiv.classList.remove('success', 'error');
    
    // Add appropriate class
    if (isSuccess) {
        messageDiv.classList.add('success');
    } else {
        messageDiv.classList.add('error');
    }
    
    // Hide the message after 5 seconds
    setTimeout(() => {
        messageDiv.classList.remove('success', 'error');
        messageDiv.textContent = '';
    }, 5000);
}

// Show message in the admin message div
function showMessage(message, isSuccess) {
    const messageDiv = document.getElementById('admin-message');
    
    // Set message text
    messageDiv.textContent = message;
    
    // Remove existing classes
    messageDiv.classList.remove('success', 'error');
    
    // Add appropriate class
    if (isSuccess) {
        messageDiv.classList.add('success');
    } else {
        messageDiv.classList.add('error');
    }
    
    // Hide the message after 5 seconds
    setTimeout(() => {
        messageDiv.classList.remove('success', 'error');
        messageDiv.textContent = '';
    }, 5000);
}

// Initialize admin panel
document.addEventListener('DOMContentLoaded', () => {
    // Fetch initial rig assignments
    fetchRigAssignments();
    
    // Populate track select dropdown
    populateTrackSelectDropdown();
    
    // Fetch initial display status
    fetchDisplayStatus();
    
    // Add event listener for form submission
    const form = document.getElementById('assign-player-form');
    form.addEventListener('submit', assignPlayer);
    
    // Add event listeners for track control
    document.getElementById('set-track-button').addEventListener('click', setDisplayTrack);
    document.getElementById('toggle-autocycle-button').addEventListener('click', toggleAutoCycle);
    
    // Auto-refresh display status every 5 seconds
    setInterval(fetchDisplayStatus, 5000);
}); 