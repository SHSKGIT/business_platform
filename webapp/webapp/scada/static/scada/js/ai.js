/*
ai form
**********************************************************************/
$("#ai-button").click(function () {
    var error = false;
    var comment = $('textarea#comment').val().trim(); // get the value of the input field
    if (comment == "" || comment == " ") {
        $('#err-comment').show(500);
        $('#err-comment').delay(2000);
        $('#err-comment').animate({
            height: 'toggle'
        }, 500, function () {
            // Animation complete.
        });
        error = true; // change the error state to true
    }

    if (error == false) {
        var dataString = $('#ai-form').serialize(); // Collect data from form
        $.ajax({
            type: "POST",
            url: $('#ai-form').attr('action'),
            data: dataString,
            timeout: 60000,  // EC2 containers responds slow, so set 60s
            error: function (request, error) {
                alert("An error occurred");
            },
            success: function (response) {
//                    response = $.parseJSON(response);
                if (response.success) {
                    // Display the AI response in the box
                    $('#ai-response').show();
                    $('#ai-response').html(response.response_text);
                } else {
                    $('#error-comment').show();
                }
                const textarea = document.getElementById('comment');
                const counter = document.querySelector('.char-counter');
                const maxLength = textarea.getAttribute('maxlength');
                counter.textContent = `0 / ${maxLength}`; // Reset counter
            }
        });
    }
    return false; // stops request
});