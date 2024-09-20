$('#monthly-report-button').click(function () {
    var user_id = document.getElementById('user-id').getAttribute('data-user-id');
    var URL = '/scada/pdf-report-1/?user_id=' + user_id;
    $.ajax({
        type: 'GET',
        url: URL,
        timeout: 60000,  // EC2 containers responds slow, so set 60s
        error: function (request, error) {
            alert("An error occurred");
        },
        success: function (response) {
            var newWindow = window.open(URL, '_blank');
            if (newWindow) {
                newWindow.focus();  // Ensure the new window is brought to the front
            } else {
                alert('Please allow pop-ups for this website');
            }
        }
    });
});

$('#general-report-button').click(function () {
    var user_id = document.getElementById('user-id').getAttribute('data-user-id');
    var URL = '/scada/pdf-report-2/?user_id=' + user_id;
    $.ajax({
        type: 'GET',
        url: URL,
        timeout: 60000,  // EC2 containers responds slow, so set 60s
        error: function (request, error) {
            alert("An error occurred");
        },
        success: function (response) {
            var newWindow = window.open(URL, '_blank');
            if (newWindow) {
                newWindow.focus();  // Ensure the new window is brought to the front
            } else {
                alert('Please allow pop-ups for this website');
            }
        }
    });
});
