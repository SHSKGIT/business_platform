let isTableLoading = true;

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

                            sort_facilities();
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

            // Set loading flag to false after the table is fully loaded
            isTableLoading = false;

            sort_facilities();
        })
        .catch(error => {
            show_error_animation("#err-update-facilities", 'Error fetching facilities:' + error);
            isTableLoading = false; // Reset the loading flag on error
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

// Add event listener to the filter input
document.getElementById('facility-filter').addEventListener('input', function() {
    const filterInput = document.getElementById('facility-filter');
    const tableRows = document.querySelectorAll('#facility-body tr');
    const filterValue = filterInput.value.toLowerCase();

    tableRows.forEach(function(row) {
        const facilityId = row.cells[0].textContent.toLowerCase(); // Get the Facility ID from the first cell
        if (facilityId.includes(filterValue)) {
            row.style.display = ''; // Show row if it matches
        } else {
            row.style.display = 'none'; // Hide row if it doesn't match
        }
    });

    sort_facilities();
});

function sort_facilities() {
    const tableBody = document.getElementById('facility-body');
    const tableRows = Array.from(tableBody.querySelectorAll('tr'));

    // Separate into "Remove" and "Add" groups
    const removeRows = [];
    const addRows = [];

    tableRows.forEach(function(row) {
        const actionButton = row.cells[1].querySelector('button').textContent;

        if (actionButton === 'Remove') {
            removeRows.push(row);
        } else if (actionButton === 'Add') {
            addRows.push(row);
        }
    });

    // Function to sort rows alphanumerically by facility ID (first cell content)
    const alphanumericSort = (a, b) => {
        const idA = a.cells[0].textContent.toLowerCase();
        const idB = b.cells[0].textContent.toLowerCase();
        return idA.localeCompare(idB);
    };

    // Sort both groups alphanumerically
    removeRows.sort(alphanumericSort);
    addRows.sort(alphanumericSort);

    // Clear the table body
    tableBody.innerHTML = '';

    // Append the sorted "Remove" rows first, followed by "Add" rows
    removeRows.forEach(function(row) {
        tableBody.appendChild(row);
    });
    addRows.forEach(function(row) {
        tableBody.appendChild(row);
    });
}

window.onbeforeunload = function(event) {
    if (window.opener && typeof window.opener.onPopupClosed === 'function') {
        window.opener.onPopupClosed();
    }
}
//window.onbeforeunload = function(event) {
//    // Check if the document is fully loaded
//    if (!isTableLoading) {
//        // Communicate to the parent window that the popup is being closed
//        if (window.opener && typeof window.opener.onPopupClosed === 'function') {
//            window.opener.onPopupClosed();
//        }
//    } else {
//        // This message will be shown in a confirmation dialog by the browser
//        event.preventDefault();
//        const message = "The page is still loading. Please wait patiently.";
//        event.returnValue = message; // This sets the returnValue to show a confirmation dialog
//        return message; // Return the message to prompt the confirmation dialog
//    }
//};

