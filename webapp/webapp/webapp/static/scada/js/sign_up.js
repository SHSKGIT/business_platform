/*
sign up form
**********************************************************************/
$('#sign-up-button').click(function () {
        var error = false;
        var user_name = $('input#username').val().trim();
        var password = $('input#password').val().trim();
        var confirm_password = $('input#confirm_password').val().trim();
        var first_name = $('input#first_name').val().trim();
        var last_name = $('input#last_name').val().trim();
        var company = $('input#company').val().trim();
        var phone = $('input#phone').val().trim();
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

        if (confirm_password == "" || confirm_password == " ") {
            $('#err-confirm_password').show(500);
            $('#err-confirm_password').delay(2000);
            $('#err-confirm_password').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        if (password != confirm_password) {
            $('#err-sign-up').html("Confirmed Password Doesn't Match Password.");
            $('#err-sign-up').show(500);
            $('#err-sign-up').delay(2000);
            $('#err-sign-up').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        if (first_name == "" || first_name == " ") {
            $('#err-first_name').show(500);
            $('#err-first_name').delay(2000);
            $('#err-first_name').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        if (last_name == "" || last_name == " ") {
            $('#err-last_name').show(500);
            $('#err-last_name').delay(2000);
            $('#err-last_name').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        if (company == "" || company == " ") {
            $('#err-company').show(500);
            $('#err-company').delay(2000);
            $('#err-company').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        const phoneCompare = /^(\+1\s?)?(\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}$/;
        if (phone == "" || phone == " " || !phoneCompare.test(phone)) {
            $('#err-phone').show(500);
            $('#err-phone').delay(2000);
            $('#err-phone').animate({
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
            var dataString = $('#sign-up-form').serialize(); // Collect data from form
            $.ajax({
                type: 'POST',
                url: $('#sign-up-form').attr('action'),
                data: dataString,
                timeout: 60000,  // EC2 containers responds slow, so set 60s
                error: function (request, error) {
                    alert("An error occurred");
                },
                success: function (response) {
                    if (response.success) {
                        alert("You have successfully signed up. This window will close.");
                        window.close();
                    } else {
//                        alert("An error occurred");
                        $('#err-sign-up').html(response.sign_up_form_invalid_error);
                        $('#err-sign-up').show(500);
                        $('#err-sign-up').delay(2000);
                        $('#err-sign-up').animate({
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
