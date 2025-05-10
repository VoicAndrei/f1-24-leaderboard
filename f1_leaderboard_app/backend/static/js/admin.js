/**
 * F1 Leaderboard Admin JavaScript
 * 
 * This script handles the admin panel functionality:
 * - Fetching and displaying current rig-player assignments
 * - Handling form submission to assign a player to a rig
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
    
    // Add event listener for form submission
    const form = document.getElementById('assign-player-form');
    form.addEventListener('submit', assignPlayer);
}); 