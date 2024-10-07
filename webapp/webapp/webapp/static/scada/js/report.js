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
Sign in form
**********************************************************************/
$('#pbr-button').click(function () {
        var error = false;
        var pbr_battery_code = $('input#pbr_battery_code').val().trim();
        var pbr_start_date = $('input#pbr_start_date').val().trim();
        var pbr_end_date = $('input#pbr_end_date').val().trim();

        if (pbr_battery_code == "" || pbr_battery_code == " ") {
            $('#err-pbr_battery_code').show(500);
            $('#err-pbr_battery_code').delay(2000);
            $('#err-pbr_battery_code').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

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

        if (error === false) {
            const user_id = document.getElementById('user-id').getAttribute('data-user-id');
            const reportSelect = document.getElementById('reportSelect');
            const selectedOption = reportSelect.options[reportSelect.selectedIndex];

            var dataString = $('#pbr-form').serialize(); // Collect data from form
            const reportUrl = selectedOption.getAttribute('data-url');
            if (reportUrl) {
                const URL = reportUrl + "?user_id=" + user_id + "&" + dataString;
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

        };

        return false;
});