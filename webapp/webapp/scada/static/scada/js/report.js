//$('#monthly-report-button').click(function () {
//    var user_id = document.getElementById('user-id').getAttribute('data-user-id');
//    var URL = '/scada/pdf-report-1/?user_id=' + user_id;
//    $.ajax({
//        type: 'GET',
//        url: URL,
//        timeout: 60000,  // EC2 containers responds slow, so set 60s
//        error: function (request, error) {
//            alert("An error occurred");
//        },
//        success: function (response) {
//            var newWindow = window.open(URL, '_blank');
//            if (newWindow) {
//                newWindow.focus();  // Ensure the new window is brought to the front
//            } else {
//                alert('Please allow pop-ups for this website');
//            }
//        }
//    });
//});
//
//$('#general-report-button').click(function () {
//    var user_id = document.getElementById('user-id').getAttribute('data-user-id');
//    var URL = '/scada/pdf-report-2/?user_id=' + user_id;
//    $.ajax({
//        type: 'GET',
//        url: URL,
//        timeout: 60000,  // EC2 containers responds slow, so set 60s
//        error: function (request, error) {
//            alert("An error occurred");
//        },
//        success: function (response) {
//            var newWindow = window.open(URL, '_blank');
//            if (newWindow) {
//                newWindow.focus();  // Ensure the new window is brought to the front
//            } else {
//                alert('Please allow pop-ups for this website');
//            }
//        }
//    });
//});

document.getElementById('generate_report_button').addEventListener('click', function() {
    const user_id = document.getElementById('user-id').getAttribute('data-user-id');
    const reportSelect = document.getElementById('reportSelect');
    const selectedOption = reportSelect.options[reportSelect.selectedIndex];

    if (selectedOption.value === "") {
        show_error_animation("#err-generate-report", "Please select a report.");
    }
    else {
        const reportUrl = selectedOption.getAttribute('data-url');
        if (reportUrl) {
            const URL = reportUrl + "?user_id=" + user_id;
            $.ajax({
                type: 'GET',
                url: URL,
                timeout: 60000,  // 60s
                error: function (request, error) {
                    alert("An error occurred");
                },
                success: function (response) {
                    var newWindow = window.open(URL, '_blank');
                    if (newWindow) {
                        newWindow.focus();  // Ensure the new window is brought to the front
                    } else {
                        show_error_animation("#err-generate-report", "Please enable pop-ups in the browser for this website.");
                    }
                }
            });
        }
        else {
            show_error_animation("#err-generate-report", "The selected report is not available now.");
        }
    }
});

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

document.addEventListener("DOMContentLoaded", function () {
    var reportSelect = document.getElementById("reportSelect");
    var pbr_section = document.getElementById("pbr");
    var generateReportButton = document.getElementById("generate_report_button");

    // Ensure the form is hidden when the page loads
    pbr_section.style.display = "none";
    generateReportButton.style.display = "block";

    // Listen for changes in the report select dropdown
    reportSelect.addEventListener("change", function () {
        var selectedOption = reportSelect.options[reportSelect.selectedIndex].value;

        // If "Production Balance Report" is selected, show the form
        if (selectedOption === "Production Balance Report") {
            pbr_section.style.display = "block";
            generateReportButton.style.display = "none";
        } else {
            // Hide the form if any other option is selected
            pbr_section.style.display = "none";
            generateReportButton.style.display = "block";
        }
    });
});

/*
generate pbr report
**********************************************************************/
$('#pbr-button').click(function () {
        var error = false;
//        var pbr_battery_code = $('input#pbr_battery_code').val();
        const reportSelect = document.getElementById('pbr_battery_code');
        const selectedOption = reportSelect.options[reportSelect.selectedIndex];

        if (selectedOption.value === "" || selectedOption.value === " " || selectedOption.value === undefined) {
            show_error_animation("#err-pbr_battery_code", "Please select a facility id.");
            error = true; // change the error state to true
        }

        var pbr_start_date = $('input#pbr_start_date').val().trim();
        var pbr_end_date = $('input#pbr_end_date').val().trim();
        var today = new Date();

        if (pbr_start_date == "" || pbr_start_date == " ") {
            $('#err-pbr_start_date').show(500);
            $('#err-pbr_start_date').delay(2000);
            $('#err-pbr_start_date').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        if (pbr_end_date == "" || pbr_end_date == " ") {
            $('#err-pbr_end_date').show(500);
            $('#err-pbr_end_date').delay(2000);
            $('#err-pbr_end_date').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        if (new Date(pbr_start_date) > today) {
            show_error_animation("#err-pbr_start_date", "Start date must be <= today.");
            error = true;
        }

        if (new Date(pbr_end_date) > today) {
            show_error_animation("#err-pbr_end_date", "End date must be <= today.");
            error = true;
        }

        if (pbr_start_date > pbr_end_date) {
            show_error_animation("#err-pbr", "Start date must be <= end date.");
            error = true;
        }

        if (error === false) {
            const user_id = document.getElementById('user-id').getAttribute('data-user-id');
            const reportSelect = document.getElementById('reportSelect');
            const selectedOption = reportSelect.options[reportSelect.selectedIndex];

            var formDataArray = $('#pbr-form').serializeArray(); // Get form data as an array
            var formDataJson = {}; // Create an empty JSON object
            // Loop through the form data array and add each field to the JSON object
            $.each(formDataArray, function (i, field) {
                formDataJson[field.name] = field.value; // Add key-value pair to the JSON object
            });

//            var dataString = $('#pbr-form').serialize(); // Collect data from form
            const reportUrl = selectedOption.getAttribute('data-url');
            if (reportUrl) {
//                const URL = reportUrl + "?user_id=" + user_id + "&" + dataString;
                const URL = reportUrl + "?user_id=" + user_id + "&pbr_battery_code=" + formDataJson["pbr_battery_code"] + "&pbr_start_date=" + formDataJson["pbr_start_date"] + "&pbr_end_date=" + formDataJson["pbr_end_date"] + "&unit=" + formDataJson["unit"];
                // Hide the "Generate" text and show the spinner
                $('#generate-button-text').text('Generating...');

                // Disable the button to prevent multiple clicks
                $('#pbr-button').prop('disabled', true);

                $.ajax({
                    type: 'GET',
                    url: URL,
                    timeout: 60000,  // 60s
                    error: function (request, error) {
                        $('#generate-button-text').text('Generate');
                        $('#pbr-button').prop('disabled', false);

                        alert("An error occurred");
                    },
                    success: function (response) {
                        $('#generate-button-text').text('Generate');
                        $('#pbr-button').prop('disabled', false);

                        if (response.facility_id_available == false) {
                            alert(response.error);
//                            show_error_animation("#err-pbr", response.error);
                            return;
                        }

                        var newWindow = window.open(URL, '_blank');
                        if (newWindow) {
                            newWindow.focus();  // Ensure the new window is brought to the front
                        } else {
                            show_error_animation("#err-generate-report", "Please enable pop-ups in the browser for this website.");
                        }
                    }
                });
            }
            else {
                show_error_animation("#err-generate-report", "The selected report is not available now.");
            }

        };

        return false;
});

function openMyFacilities(userId) {
    const message = '"My Facilities" window may take about 15s to load, please do NOT close the window while loading. Click "OK" to pop up the window and load.';

    // Use the confirm dialog
    const userConfirmed = confirm(message);

    if (userConfirmed) {
        const url = "/scada/update-facilities/" + userId + "/";
        window.open(url, '_blank', 'width=600,height=850');
    }
}

// This function will be called when the popup is closed
function onPopupClosed() {
    alert('Click "OK" to refresh the page and get updated facilities in dropdown.');
    location.reload(); // Refresh the page after the alert is closed
}

//function ReloadFacilitiesDropdown(userId) {
//    const URL = "/scada/reload-facilities/?user_id=" + userId; // Adjust URL to your endpoint
//
//    fetch(URL)
//        .then(response => response.json())
//        .then(data => {
//            const batteryCodeSelect = document.querySelector('select[name="pbr_battery_code"]');
//            batteryCodeSelect.innerHTML = ''; // Clear existing options
//
//            // Create the default option
//            const defaultOption = document.createElement('option');
//            defaultOption.value = '';
//            defaultOption.textContent = 'Select a facility ID';
//            batteryCodeSelect.appendChild(defaultOption);
//
//            // Populate the dropdown with the new options
//            data.facilities.forEach(facility => {
//                const option = document.createElement('option');
//                option.value = facility.id; // Adjust based on your data structure
//                option.textContent = facility.id; // Adjust based on your data structure
//                batteryCodeSelect.appendChild(option);
//            });
//        })
//        .catch(error => {
//            show_error_animation("#err-pbr", "Error loading battery code dropdown: " + error);
//        });
//}

//$(document).ready(function() {
//    var URL = '/scada/search-facility-ids/';
//    $('#pbr_battery_code').select2({
//        placeholder: 'Select a facility ID',
//        ajax: {
//            url: URL,
//            dataType: 'json',
//            delay: 250,
//            data: function(params) {
//                return {
//                    term: params.term
//                };
//            },
//            processResults: function(data) {
//                return {
//                    results: $.map(data, function(item) {
//                        return {
//                            id: item.id,
//                            text: item.label
//                        };
//                    })
//                };
//            },
//            cache: true
//        },
//        minimumInputLength: 4,
//    });
//});

//$(document).ready(function() {
//    var URL = '/scada/search-facility-ids/';
//    $("#pbr_battery_code").select2({
//        ajax: {
//            url: URL,
//            dataType: 'json',
//            delay: 250,
//            data: function (params) {
//                return {
//                    term: params.term,  // Search term entered by the user
//                    page: params.page || 1,  // Pagination page
//                    size: 20  // Size per page
//                };
//            },
//            processResults: function (data, params) {
//                params.page = params.page || 1;
//
//                return {
//                    results: data.results.map(function (facility) {
//                    return {
//                            id: facility.id,       // The ID for the facility
//                            text: facility.label   // The label for the dropdown
//                        };
//                    }),
//                    pagination: {
//                        more: data.pagination.has_next  // If there are more pages
//                    }
//                };
//            },
//            cache: true
//        },
//        placeholder: "Input at least 4 characters.",
//        minimumInputLength: 4,
//    });
//});

//$(document).ready(function() {
//    var URL = '/scada/search-facility-ids/';
//    var allResults = [];
//    var currentPage = 0;
//    var pageSize = 20;
//
//    // Load initial results
//    function loadResults(term) {
//        $.ajax({
//            url: URL,
//            dataType: 'json',
//            data: { term: term },
//            success: function(data) {
//                allResults = data.results;
//                displayResults();
//            }
//        });
//    }
//
//    function displayResults() {
//        var start = currentPage * pageSize;
//        var end = start + pageSize;
//        var paginatedResults = allResults.slice(start, end);
//
//        $("#pbr_battery_code").empty();
//        paginatedResults.forEach(function(item) {
//            $("#pbr_battery_code").append(new Option(item.label, item.id));
//        });
//
//        // Update pagination buttons
//        $("#paginationInfo").text(`Showing ${start + 1} to ${Math.min(end, allResults.length)} of ${allResults.length}`);
//        $("#prevButton").prop("disabled", currentPage === 0);
//        $("#nextButton").prop("disabled", end >= allResults.length);
//    }
//
//    $("#pbr_battery_code").select2({
//        placeholder: "Input at least 4 characters.",
//        minimumInputLength: 4,
//        ajax: {
//            url: URL,
//            dataType: 'json',
//            delay: 250,
//            data: function (params) {
//                return {
//                    term: params.term,  // Search term entered by the user
//                };
//            },
//            processResults: function (data) {
//                return {
//                    results: data.results,
//                };
//            },
//            cache: true
//        }
//    }).on("select2:select", function(e) {
//        // Handle selection
//    });
//
//    // Previous Button Click
//    $("#prevButton").click(function() {
//        if (currentPage > 0) {
//            currentPage--;
//            displayResults();
//        }
//    });
//
//    // Next Button Click
//    $("#nextButton").click(function() {
//        if ((currentPage + 1) * pageSize < allResults.length) {
//            currentPage++;
//            displayResults();
//        }
//    });
//
//    // Initial load
//    loadResults('');
//
//    // Search handling
//    $("#pbr_battery_code").on("select2:search", function(e) {
//        currentPage = 0; // Reset to first page on new search
//        loadResults(e.target.value); // Load results based on search term
//    });
//});