/*
reset password form
**********************************************************************/
$('#reset-password-button').click(function () {
        var error = false;
        var user_name = $('input#username').val().trim();
        var password = $('input#password').val().trim();
        var email = $('input#email').val().trim();

        if (user_name == "" || user_name == " ") {
            $('#err-username').show(500);
            $('#err-username').delay(2000);
            $('#err-username').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        if (password == "" || password == " ") {
            $('#err-password').show(500);
            $('#err-password').delay(2000);
            $('#err-password').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        const emailCompare = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/; // Syntax to compare against input
        if (email == "" || email == " " || !emailCompare.test(email)) {
            $('#err-email').show(500);
            $('#err-email').delay(2000);
            $('#err-email').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        if (error === false) {
            var dataString = $('#reset-password-form').serialize(); // Collect data from form
            $.ajax({
                type: 'POST',
                url: $('#reset-password-form').attr('action'),
                data: dataString,
                timeout: 60000,  // EC2 containers responds slow, so set 60s
                error: function (request, error) {
                    alert("An error occurred");
                },
                success: function (response) {
                    if (response.success) {
                        alert("You have successfully reset password. This window will close.");
                        window.close();
                    } else {
                        // no matching user, failed to reset
//                        alert("An error occurred");
                        $('#err-reset-password').html(response.reset_password_form_invalid_error);
                        $('#err-reset-password').show(500);
                        $('#err-reset-password').delay(2000);
                        $('#err-reset-password').animate({
                            height: 'toggle'
                        }, 500, function () {
                            // Animation complete.
                        });
                    }
                }
            });
        };

        return false;
});
