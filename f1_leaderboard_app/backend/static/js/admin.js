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
            row.id = `rig-row-${rig.rig_identifier}`; // Optional: ID for the whole row
            
            // Get timer status for this rig (from global cache, might be stale initially but fetchTimerStatus will update)
            const timerStatus = currentTimerStatuses[rig.rig_identifier] || {
                timer_active: false,
                remaining_time: 0,
                duration_minutes: 0
            };
            
            // Create timer control HTML
            const timerControlHtmlContent = createTimerControlHtml(rig.rig_identifier, timerStatus);
            
            // Create player info HTML with contact details
            const playerInfoHtml = `
                <div class="player-info">
                    <div class="player-name">${rig.current_player_name}</div>
                    ${rig.phone_number || rig.email ? `
                        <div class="contact-info">
                            ${rig.phone_number ? `<div>📞 ${rig.phone_number}</div>` : ''}
                            ${rig.email ? `<div>📧 ${rig.email}</div>` : ''}
                        </div>
                    ` : ''}
                </div>
            `;
            
            row.innerHTML = `
                <td>${rig.rig_identifier}</td>
                <td>${playerInfoHtml}</td>
                <td id="timer-cell-${rig.rig_identifier}">${timerControlHtmlContent}</td>
            `;
            tableBody.appendChild(row);
            
            // Add rig to dropdown
            const option = document.createElement('option');
            option.value = rig.rig_identifier;
            option.textContent = rig.rig_identifier;
            rigSelect.appendChild(option);
        });
        
        // Add event listeners for timer buttons (still relevant if controls are recreated)
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
                <button class="timer-button" onclick="resetTimer('${rigId}')" style="background-color: #ffa500;">Reset</button>
                <br style="margin: 4px 0;">
                <button class="timer-button" onclick="showOverlay('${rigId}')" style="background-color: #dc3545;">Show Overlay</button>
                <button class="timer-button" onclick="dismissOverlay('${rigId}')" style="background-color: #ff6b35;">Dismiss Overlay</button>
                <br style="margin: 4px 0;">
                <button class="timer-button" onclick="pressEsc('${rigId}')" style="background-color: #6c757d;">Press ESC</button>
            </div>
        `;
    } else {
        return `
            <div class="timer-controls">
                <input type="number" class="timer-input" id="timer-input-${rigId}" 
                       placeholder="10" min="1" step="1" value="10">
                <span style="font-size: 0.9rem;">min</span>
                <button class="timer-button" onclick="startTimer('${rigId}')">Start</button>
                <span class="timer-status timer-inactive">Inactive</span>
                <br style="margin: 4px 0;">
                <button class="timer-button" onclick="showOverlay('${rigId}')" style="background-color: #dc3545;">Show Overlay</button>
                <button class="timer-button" onclick="dismissOverlay('${rigId}')" style="background-color: #ff6b35;">Dismiss Overlay</button>
                <br style="margin: 4px 0;">
                <button class="timer-button" onclick="pressEsc('${rigId}')" style="background-color: #6c757d;">Press ESC</button>
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
            console.error(`HTTP error fetching timer status: ${response.status}`);
            // Optionally show an error message to the user here
            return;
        }
        
        const timerStatuses = await response.json();
        
        // Update global status cache and selectively update the DOM
        timerStatuses.forEach(status => {
            currentTimerStatuses[status.rig_identifier] = status; // Update cache

            const rigId = status.rig_identifier;
            const timerCell = document.getElementById(`timer-cell-${rigId}`);
            
            if (!timerCell) {
                // This might happen if rigs are added/removed dynamically and fetchRigAssignments hasn't run yet
                // For now, we'll just log it. A more robust solution might re-trigger fetchRigAssignments here.
                console.warn(`Timer cell for ${rigId} not found in DOM during status update.`);
                return; 
            }

            // Generate the HTML that *would* be there based on the new status
            const newHtmlForCell = createTimerControlHtml(rigId, status);

            if (status.timer_active) {
                // New status is ACTIVE.
                // The active display has no user input, so it's safe to update if different.
                if (timerCell.innerHTML !== newHtmlForCell) {
                    timerCell.innerHTML = newHtmlForCell;
                }
            } else {
                // New status is INACTIVE. The cell should show the input field.
                const existingInput = timerCell.querySelector('input.timer-input');
                if (existingInput) {
                    // Input field already exists. Timer was and remains inactive.
                    // DO NOTHING to preserve the input field's current value and focus.
                    // The "Inactive" text is static and doesn't need updating.
                } else {
                    // No input field exists (e.g., timer was active and now inactive, or cell was empty/malformed).
                    // Render the inactive state, which includes the input field.
                    timerCell.innerHTML = newHtmlForCell;
                }
            }
        });
        
    } catch (error) {
        console.error('Error fetching or processing timer status:', error);
        // Optionally show an error to the user
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
    const phoneNumber = document.getElementById('phone-input').value.trim();
    const email = document.getElementById('email-input').value.trim();
    
    // Basic validation
    if (!rigIdentifier) {
        showMessage('Please select a rig.', false);
        return;
    }
    
    if (!playerName) {
        showMessage('Please enter a player name.', false);
        return;
    }
    
    // Email validation if provided
    if (email && !isValidEmail(email)) {
        showMessage('Please enter a valid email address.', false);
        return;
    }
    
    try {
        // Prepare request data
        const data = {
            rig_identifier: rigIdentifier,
            player_name: playerName,
            phone_number: phoneNumber,
            email: email
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
        document.getElementById('phone-input').value = '';
        document.getElementById('email-input').value = '';
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

// Dismiss overlay for a specific rig
async function dismissOverlay(rigId) {
    try {
        const response = await fetch(`/api/admin/overlay/dismiss/${rigId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Failed to dismiss overlay');
        }
        
        showTimerMessage(result.message, true);
        
    } catch (error) {
        console.error('Error dismissing overlay:', error);
        showTimerMessage(`Error dismissing overlay for ${rigId}: ${error.message}`, false);
    }
}

// Show overlay for a specific rig
async function showOverlay(rigId) {
    try {
        const response = await fetch(`/api/admin/overlay/show/${rigId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Failed to show overlay');
        }
        
        showTimerMessage(result.message, true);
        
    } catch (error) {
        console.error('Error showing overlay:', error);
        showTimerMessage(`Error showing overlay for ${rigId}: ${error.message}`, false);
    }
}

// Reset timer for a specific rig
async function resetTimer(rigId) {
    try {
        const response = await fetch(`/api/admin/timer/reset/${rigId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Failed to reset timer');
        }
        
        showTimerMessage(result.message, true);
        
        // Refresh timer status to show updated state
        fetchTimerStatus();
        
    } catch (error) {
        console.error('Error resetting timer:', error);
        showTimerMessage(`Error resetting timer for ${rigId}: ${error.message}`, false);
    }
}

// Press ESC key for a specific rig
async function pressEsc(rigId) {
    try {
        const response = await fetch(`/api/admin/esc/${rigId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Failed to press ESC');
        }
        
        showTimerMessage(result.message, true);
        
    } catch (error) {
        console.error('Error pressing ESC:', error);
        showTimerMessage(`Error pressing ESC for ${rigId}: ${error.message}`, false);
    }
}

// Event listener for DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    // Fetch and display rig assignments initially
    fetchRigAssignments();
    
    // Populate track select dropdown
    populateTrackSelectDropdown();
    
    // Fetch and display leaderboard status initially
    fetchDisplayStatus();
    
    // Set up interval to refresh display status (e.g., every 10 seconds)
    setInterval(fetchDisplayStatus, 10000); // Poll every 10 seconds
    
    // Set up interval to refresh timer status (e.g., every 5 seconds)
    setInterval(fetchTimerStatus, 5000); // Poll every 5 seconds for timer status
    
    // Attach event listener to the form
    const form = document.getElementById('assign-player-form');
    if (form) {
    form.addEventListener('submit', assignPlayer);
    }
    
    // Attach event listener to manual track selection button
    const manualTrackButton = document.getElementById('set-track-button');
    if (manualTrackButton) {
        manualTrackButton.addEventListener('click', setDisplayTrack);
    }
    
    // Attach event listener to auto-cycle toggle button
    const toggleAutoCycleButton = document.getElementById('toggle-autocycle-button');
    if (toggleAutoCycleButton) {
        toggleAutoCycleButton.addEventListener('click', toggleAutoCycle);
    }
    
    // Fetch timer statuses initially
    fetchTimerStatus();
});

// Email validation function
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
} 