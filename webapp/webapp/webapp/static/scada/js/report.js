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