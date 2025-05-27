/**
 * F1 Leaderboard Admin JavaScript
 * 
 * This script handles the admin panel functionality:
 * - Fetching and displaying current rig-player assignments
 * - Handling form submission to assign a player to a rig
 * - Leaderboard display control (track selection and auto-cycle toggle)
 * - Timer control for each rig
 */

// Global timer status cache
let currentTimerStatuses = {};

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
                    <td colspan="3">No rigs found. Please check the database setup.</td>
                </tr>
            `;
            return;
        }
        
        // Add each rig to the table
        rigs.forEach(rig => {
            const row = document.createElement('tr');
            
            // Get timer status for this rig
            const timerStatus = currentTimerStatuses[rig.rig_identifier] || {
                timer_active: false,
                remaining_time: 0,
                duration_minutes: 0
            };
            
            // Create timer control HTML
            const timerControlHtml = createTimerControlHtml(rig.rig_identifier, timerStatus);
            
            row.innerHTML = `
                <td>${rig.rig_identifier}</td>
                <td>${rig.current_player_name}</td>
                <td>${timerControlHtml}</td>
            `;
            tableBody.appendChild(row);
            
            // Add rig to dropdown
            const option = document.createElement('option');
            option.value = rig.rig_identifier;
            option.textContent = rig.rig_identifier;
            rigSelect.appendChild(option);
        });
        
        // Add event listeners for timer buttons
        addTimerEventListeners();
        
    } catch (error) {
        console.error('Error fetching rig assignments:', error);
        
        // Display error message
        const tableBody = document.getElementById('rigs-table-body');
        tableBody.innerHTML = `
            <tr>
                <td colspan="3" class="error">Error loading rig assignments. Please try again later.</td>
            </tr>
        `;
        
        // Display error message
        showMessage(`Error: ${error.message}`, false);
    }
}

// Create timer control HTML for a rig
function createTimerControlHtml(rigId, timerStatus) {
    if (timerStatus.timer_active) {
        const remainingTime = formatTimerDisplay(timerStatus.remaining_time);
        return `
            <div class="timer-controls">
                <span class="timer-status timer-active">Active: ${remainingTime}</span>
                <button class="timer-button" onclick="stopTimer('${rigId}')">Stop</button>
            </div>
        `;
    } else {
        return `
            <div class="timer-controls">
                <input type="number" class="timer-input" id="timer-input-${rigId}" 
                       placeholder="10" min="0.1" step="0.1" value="10">
                <span style="font-size: 0.9rem;">min</span>
                <button class="timer-button" onclick="startTimer('${rigId}')">Start</button>
                <span class="timer-status timer-inactive">Inactive</span>
            </div>
        `;
    }
}

// Format timer display (seconds to MM:SS)
function formatTimerDisplay(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Add event listeners for timer buttons
function addTimerEventListeners() {
    // Event listeners are added via onclick attributes in createTimerControlHtml
    // This function is here for future expansion if needed
}

// Start timer for a specific rig
async function startTimer(rigId) {
    try {
        // Get duration from input
        const durationInput = document.getElementById(`timer-input-${rigId}`);
        if (!durationInput) {
            showTimerMessage(`Error: Could not find duration input for ${rigId}`, false);
            return;
        }
        
        const durationMinutes = parseFloat(durationInput.value);
        if (!durationMinutes || durationMinutes <= 0) {
            showTimerMessage(`Please enter a valid duration for ${rigId}`, false);
            return;
        }
        
        // Send start request
        const response = await fetch('/api/admin/timer/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                rig_identifier: rigId,
                duration_minutes: durationMinutes
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Failed to start timer');
        }
        
        showTimerMessage(result.message, true);
        
        // Refresh timer status
        fetchTimerStatus();
        
    } catch (error) {
        console.error('Error starting timer:', error);
        showTimerMessage(`Error starting timer for ${rigId}: ${error.message}`, false);
    }
}

// Stop timer for a specific rig
async function stopTimer(rigId) {
    try {
        const response = await fetch(`/api/admin/timer/stop/${rigId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Failed to stop timer');
        }
        
        showTimerMessage(result.message, true);
        
        // Refresh timer status
        fetchTimerStatus();
        
    } catch (error) {
        console.error('Error stopping timer:', error);
        showTimerMessage(`Error stopping timer for ${rigId}: ${error.message}`, false);
    }
}

// Fetch timer status for all rigs
async function fetchTimerStatus() {
    try {
        const response = await fetch('/api/admin/timer/status');
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const timerStatuses = await response.json();
        
        // Update global status cache
        currentTimerStatuses = {};
        timerStatuses.forEach(status => {
            currentTimerStatuses[status.rig_identifier] = status;
        });
        
        // Refresh the rig assignments table to show updated timer status
        fetchRigAssignments();
        
    } catch (error) {
        console.error('Error fetching timer status:', error);
    }
}

// Show message in the timer control message div
function showTimerMessage(message, isSuccess) {
    const messageDiv = document.getElementById('timer-control-message');
    
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
    
    // Fetch initial timer status
    fetchTimerStatus();
    
    // Add event listener for form submission
    const form = document.getElementById('assign-player-form');
    form.addEventListener('submit', assignPlayer);
    
    // Add event listeners for track control
    document.getElementById('set-track-button').addEventListener('click', setDisplayTrack);
    document.getElementById('toggle-autocycle-button').addEventListener('click', toggleAutoCycle);
    
    // Auto-refresh display status every 5 seconds
    setInterval(fetchDisplayStatus, 5000);
    
    // Auto-refresh timer status every 2 seconds (more frequent for timer countdown)
    setInterval(fetchTimerStatus, 2000);
}); 