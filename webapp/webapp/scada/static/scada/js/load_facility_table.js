document.addEventListener('DOMContentLoaded', function() {
    const facilityBody = document.getElementById('facility-body');

    var user_id = document.getElementById('user-id').getAttribute('data-user-id');
    var URL = "/scada/get-facilities/?user_id=" + user_id

    // Show the loading message
    const loadingMessage = document.getElementById('loading-message');
    loadingMessage.style.display = 'block';

    // Fetch the facilities when the page loads
    fetch(URL)
        .then(response => response.json())
        .then(data => {
            const facilities = data.facilities;

            facilities.forEach(facility => {
                const row = document.createElement('tr');

                const cellId = document.createElement('td');
                cellId.className = 'align-left';
                cellId.textContent = facility.id; // Facility ID
                row.appendChild(cellId);

                const cellAction = document.createElement('td');
                cellAction.className = 'align-right';

                const actionButton = document.createElement('button');
                actionButton.className = 'action-button'; // Add class for styling
                actionButton.textContent = facility.action;

                actionButton.onclick = function() {
                    // Handle Add/Remove action
                    actionButton.disabled = true; // Disable the button after first click
                    actionButton.textContent = "Processing...";

                    const action = facility.action;
                    const apiUrl = action === 'Add' ? '/scada/add-facilities/' : '/scada/remove-facilities/';
                    fetch(apiUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCsrfToken() // Assuming you use Django's CSRF protection
                        },
                        body: JSON.stringify({
                            facility_id: facility.id,
                            user_id: user_id
                        })
                    })
                    .then(response => response.json())
                    .then(result => {
                        if (result.success) {
                            // Toggle the action text between 'Add' and 'Remove'
                            actionButton.disabled = false;
                            facility.action = action === 'Add' ? 'Remove' : 'Add';
                            actionButton.textContent = facility.action;
                        } else {
                            actionButton.disabled = true;
                            actionButton.textContent = facility.action;
                            show_error_animation("#err-update-facilities", 'Failed to update facility: ' + result.error);
                        }
                    })
                    .catch(error => {
                        show_error_animation("#err-update-facilities", 'Error in facility update: ' + error);
                    });
                };
                cellAction.appendChild(actionButton);
                row.appendChild(cellAction);

                facilityBody.appendChild(row);
            });

            // Hide the loading message once loaded
            loadingMessage.style.display = 'none';
        })
        .catch(error => {
            show_error_animation("#err-update-facilities", 'Error fetching facilities:' + error);
        });
});

// Function to get the CSRF token
function getCsrfToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];
    return cookieValue;
}

function show_error_animation(element, error_message) {
    $(element).html(error_message);
    $(element).show(500);
    $(element).delay(2000);
    $(element).animate({
        height: 'toggle'
    }, 500, function () {
        // Animation complete.
    });
}