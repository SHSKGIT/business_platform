'use strict';

/*
 * A Design by Jerry Wang Studio
 * Author: Jerry Wang
 */
 jQuery(document).ready(function ($) {

    var lastId,
    topMenu = $("#top-navigation"),
    topMenuHeight = topMenu.outerHeight(),
        // All list items
        menuItems = topMenu.find("a"),
        // Anchors corresponding to menu items
        scrollItems = menuItems.map(function () {
            var href = $(this).attr("href");
            if(href.indexOf("#") === 0){
                var item = $($(this).attr("href"));
                if (item.length) {
                    return item;
                }
            }
        });

    //Get width of container
    var containerWidth = $('.section .container').width();
    //Resize animated triangle
    $(".triangle").css({
        "border-left": containerWidth / 2 + 'px outset transparent',
        "border-right": containerWidth / 2 + 'px outset transparent'
    });
    $(window).resize(function () {
        containerWidth = $('.container').width();
        $(".triangle").css({
            "border-left": containerWidth / 2 + 'px outset transparent',
            "border-right": containerWidth / 2 + 'px outset transparent'
        });
    });


    //Initialize header slider.
    $('#da-slider').cslider();

    //Initial mixitup, used for animated filtering portgolio.
    $('#portfolio-grid').mixitup({
        'onMixStart': function (config) {
            $('div.toggleDiv').hide();
        }
    });

    //Initial Out clients slider in client section
    $('#clint-slider').bxSlider({
        pager: false,
        minSlides: 1,
        maxSlides: 5,
        moveSlides: 2,
        slideWidth: 210,
        slideMargin: 25,
        prevSelector: $('#client-prev'),
        nextSelector: $('#client-next'),
        prevText: '<i class="icon-left-open"></i>',
        nextText: '<i class="icon-right-open"></i>'
    });


    $('input, textarea').placeholder();

    // Bind to scroll
    $(window).scroll(function () {

        //Display or hide scroll to top button 
        if ($(this).scrollTop() > 100) {
            $('.scrollup').fadeIn();
        } else {
            $('.scrollup').fadeOut();
        }

        if ($(this).scrollTop() > 130) {
            $('.navbar').addClass('navbar-fixed-top animated fadeInDown');
        } else {
            $('.navbar').removeClass('navbar-fixed-top animated fadeInDown');
        }

        // Get container scroll position
        var fromTop = $(this).scrollTop() + topMenuHeight + 10;

        // Get id of current scroll item
        var cur = scrollItems.map(function () {
            if ($(this).offset().top < fromTop)
                return this;
        });

        // Get the id of the current element
        cur = cur[cur.length - 1];
        var id = cur && cur.length ? cur[0].id : "";

        if (lastId !== id) {
            lastId = id;
            // Set/remove active class
            menuItems
            .parent().removeClass("active")
            .end().filter("[href=#" + id + "]").parent().addClass("active");
        }
    });

    /*
    Function for scroliing to top
    ************************************/
    $('.scrollup').click(function () {
        $("html, body").animate({
            scrollTop: 0
        }, 600);
        return false;
    });


    $(window).load(function () {
        function filterPath(string) {
            return string.replace(/^\//, '').replace(/(index|default).[a-zA-Z]{3,4}$/, '').replace(/\/$/, '');
        }
        $('a[href*=#]').each(function () {
            if (filterPath(location.pathname) == filterPath(this.pathname) && location.hostname == this.hostname && this.hash.replace(/#/, '')) {
                var $targetId = $(this.hash),
                $targetAnchor = $('[name=' + this.hash.slice(1) + ']');
                var $target = $targetId.length ? $targetId : $targetAnchor.length ? $targetAnchor : false;

                if ($target) {

                    $(this).click(function () {

                        //Hack collapse top navigation after clicking
                        topMenu.parent().attr('style', 'height:0px').removeClass('in'); //Close navigation
                        $('.navbar .btn-navbar').addClass('collapsed');

                        var targetOffset = $target.offset().top - 63;
                        $('html, body').animate({
                            scrollTop: targetOffset
                        }, 800);
                        return false;
                    });
                }
            }
        });
});

    /*
    Send newsletter
    **********************************************************************/
    $('#subscribe').click(function () {
        var error = false;
        var first_name = $('input#nlfirstname').val().trim();
        var last_name = $('input#nllastname').val().trim();
        var company = $('input#nlcompany').val().trim();
        var phone = $('input#nlphone').val().trim();
        var email = $('input#nlmail').val().trim().toLowerCase(); // get the value of the input field

        var error = false;
        if (first_name == "" || first_name == " ") {
            $('#err-nlfirstname').show(500);
            $('#err-nlfirstname').delay(2000);
            $('#err-nlfirstname').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        if (last_name == "" || last_name == " ") {
            $('#err-nllastname').show(500);
            $('#err-nllastname').delay(2000);
            $('#err-nllastname').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        if (company == "" || company == " ") {
            $('#err-nlcompany').show(500);
            $('#err-nlcompany').delay(2000);
            $('#err-nlcompany').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        const phoneCompare = /^(\+1\s?)?(\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}$/;
        if (phone == "" || phone == " " || !phoneCompare.test(phone)) {
            $('#err-nlphone').show(500);
            $('#err-nlphone').delay(2000);
            $('#err-nlphone').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        const emailCompare = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/; // Syntax to compare against input
        if (email == "" || email == " " || !emailCompare.test(email)) {
            $('#err-nlmail').show(500);
            $('#err-nlmail').delay(2000);
            $('#err-nlmail').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        if (error === false) {
            var dataString = $('#subscribe-form').serialize(); // Collect data from form
            $.ajax({
                type: 'POST',
                url: $('#subscribe-form').attr('action'),
                data: dataString,
                timeout: 60000,  // EC2 containers responds slow, so set 60s
                error: function (request, error) {
                    alert("An error occurred");
                },
                success: function (response) {
                    if (response.success) {
                        $('#success-subscribe').show();
                        $('#success-subscribe').html('<strong>Well done, ' + response.name + '!</strong> You have successfully subscribed to our newsletter.');
                        $('#nlfirstname').val('');
                        $('#nllastname').val('');
                        $('#nlcompany').val('');
                        $('#nlphone').val('');
                        $('#nlmail').val('');
                    } else {
                        alert("An error occurred");
                    }
                }
            });
        }

        return false;
    });

/*
Sign in form
**********************************************************************/
$('#sign-in-button').click(function () {
        var error = false;
        var user_name = $('input#username').val().trim();
        var password = $('input#password').val().trim();

        var error = false;
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

        if (error === false) {
            var dataString = $('#sign-in-form').serialize(); // Collect data from form
            $.ajax({
                type: 'POST',
                url: $('#sign-in-form').attr('action'),
                data: dataString,
                timeout: 60000,  // EC2 containers responds slow, so set 60s
                error: function (request, error) {
                    alert("An error occurred");
                },
                success: function (response) {
                    if (response.success) {
                        $('#username').val('');
                        $('#password').val('');
                        window.location.href = $('#sign-in-form').attr('action');
                    } else {
                        $('#err-sign-in').html(response.sign_in_form_invalid_error);
                        $('#err-sign-in').show(500);
                        $('#err-sign-in').delay(2000);
                        $('#err-sign-in').animate({
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
/*
click sign up link
**********************************************************************/
$("#sign-up-link").click(function (event) {
    event.preventDefault(); // Prevents the default action of the link
    window.open(
        $(this).attr('href'),
        "SignUpWindow",
        "width=600,height=550,left=100,top=100"
    );
});
/*
contact form
**********************************************************************/
$("#send-mail").click(function () {

        var name = $('input#name').val().trim(); // get the value of the input field
        var error = false;
        if (name == "" || name == " ") {
            $('#err-name').show(500);
            $('#err-name').delay(2000);
            $('#err-name').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
            });
            error = true; // change the error state to true
        }

        var emailCompare = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/; // Syntax to compare against input
        var email = $('input#email').val().trim().toLowerCase(); // get the value of the input field
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
            var dataString = $('#contact-form').serialize(); // Collect data from form
            $.ajax({
                type: "POST",
                url: $('#contact-form').attr('action'),
                data: dataString,
                timeout: 60000,  // EC2 containers responds slow, so set 60s
                error: function (request, error) {
                    alert("An error occurred");
                },
                success: function (response) {
//                    response = $.parseJSON(response);
                    if (response.success) {
                        $('#successSend').show();
                        $('#successSend').html('<strong>Well done, ' + response.name + '!</strong> Your message has been sent. We will contact you soon.');
                        $("#name").val('');
                        $("#email").val('');
                        $("#comment").val('');
                    } else {
                        $('#error-subscribe').show();
                    }
                    const textarea = document.getElementById('comment');
                    const counter = document.querySelector('.char-counter');
                    const maxLength = textarea.getAttribute('maxlength');
                    counter.textContent = `0 / ${maxLength}`; // Reset counter
                }
            });
            return false;
        }

        return false; // stops request
    });



    //Function for show or hide portfolio desctiption.
    $.fn.showHide = function (options) {
        var defaults = {
            speed: 1000,
            easing: '',
            changeText: 0,
            showText: 'Show',
            hideText: 'Hide'
        };
        var options = $.extend(defaults, options);
        $(this).click(function () {
            $('.toggleDiv').slideUp(options.speed, options.easing);
            var toggleClick = $(this);
            var toggleDiv = $(this).attr('rel');
            $(toggleDiv).slideToggle(options.speed, options.easing, function () {
                if (options.changeText == 1) {
                    $(toggleDiv).is(":visible") ? toggleClick.text(options.hideText) : toggleClick.text(options.showText);
                }
            });
            return false;
        });
    };

    //Initial Show/Hide portfolio element.
    $('div.toggleDiv').hide();
    $('.show_hide').showHide({
        speed: 500,
        changeText: 0,
        showText: 'View',
        hideText: 'Close'
    });

    /************************
    Animate elements
    *************************/
    
    //Animate thumbnails 
    jQuery('.thumbnail').one('inview', function (event, visible) {
        if (visible == true) {
            jQuery(this).addClass("animated fadeInDown");
        } else {
            jQuery(this).removeClass("animated fadeInDown");
        }
    });

    //Animate triangles
    jQuery('.triangle').bind('inview', function (event, visible) {
        if (visible == true) {
            jQuery(this).addClass("animated fadeInDown");
        } else {
            jQuery(this).removeClass("animated fadeInDown");
        }
    });
    
    //animate first team member
    jQuery('#first-person').bind('inview', function (event, visible) {
        if (visible == true) {
            jQuery('#first-person').addClass("animated pulse");
        } else {
            jQuery('#first-person').removeClass("animated pulse");
        }
    });
    
    //animate sectond team member
    jQuery('#second-person').bind('inview', function (event, visible) {
        if (visible == true) {
            jQuery('#second-person').addClass("animated pulse");
        } else {
            jQuery('#second-person').removeClass("animated pulse");
        }
    });

    //animate thrid team member
    jQuery('#third-person').bind('inview', function (event, visible) {
        if (visible == true) {
            jQuery('#third-person').addClass("animated pulse");
        } else {
            jQuery('#third-person').removeClass("animated pulse");
        }
    });
    
    //Animate price columns
    jQuery('.price-column, .testimonial').bind('inview', function (event, visible) {
        if (visible == true) {
            jQuery(this).addClass("animated fadeInDown");
        } else {
            jQuery(this).removeClass("animated fadeInDown");
        }
    });
    
    //Animate contact form
    jQuery('.contact-form').bind('inview', function (event, visible) {
        if (visible == true) {
            jQuery('.contact-form').addClass("animated bounceIn");
        } else {
            jQuery('.contact-form').removeClass("animated bounceIn");
        }
    });

    //Animate sign in form
    jQuery('.sign-in-form').bind('inview', function (event, visible) {
        if (visible == true) {
            jQuery('.sign-in-form').addClass("animated bounceIn");
        } else {
            jQuery('.sign-in-form').removeClass("animated bounceIn");
        }
    });

    //Animate skill bars
    jQuery('.skills > li > span').one('inview', function (event, visible) {
        if (visible == true) {
            jQuery(this).each(function () {
                jQuery(this).animate({
                    width: jQuery(this).attr('data-width')
                }, 3000);
            });
        }
    });
});

//Initialize google map for contact setion with your location.
function initializeMap() {

    var lat = '51.049999'; //Set your latitude.
    var lon = '-114.066666'; //Set your longitude.

    var centerLon = lon - 0.0105;

    var myOptions = {
        scrollwheel: true,
        draggable: true,
        disableDefaultUI: false,
        center: new google.maps.LatLng(lat, centerLon),
        zoom: 15,
        mapTypeId: google.maps.MapTypeId.HYBRID
    };

    //Bind map to element with id map-canvas
    var map = new google.maps.Map(document.getElementById('map-canvas'), myOptions);
    var marker = new google.maps.Marker({
        map: map,
        position: new google.maps.LatLng(lat, lon),

    });

    var infowindow = new google.maps.InfoWindow({
        content: "We are here!"
    });

    google.maps.event.addListener(marker, 'click', function () {
        infowindow.open(map, marker);
    });

    infowindow.open(map, marker);
}

// for any textarea max length dynamic update
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('comment');
    const counter = document.querySelector('.char-counter');
    const maxLength = textarea.getAttribute('maxlength');

    // Update counter as the user types
    textarea.addEventListener('input', function() {
        const currentLength = textarea.value.length;
        counter.textContent = `${currentLength} / ${maxLength}`;
    });
});

// social network not available alert when click the button
var notAvailableLinks = document.querySelectorAll('.not-available-link');
// Loop through each element and add an event listener
notAvailableLinks.forEach(function(link) {
    link.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent the link from navigating
        setTimeout(function() {
            $('#err-social-icon-message').show(500);
            $('#err-social-icon-message').delay(2000);
            $('#err-social-icon-message').animate({
                height: 'toggle'
            }, 500, function () {
                // Animation complete.
                });
        });
    });
});

