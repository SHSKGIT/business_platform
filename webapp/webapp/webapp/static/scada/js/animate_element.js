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

//Animate contact form
jQuery('.ai-form').bind('inview', function (event, visible) {
    if (visible == true) {
        jQuery('.ai-form').addClass("animated bounceIn");
    } else {
        jQuery('.ai-form').removeClass("animated bounceIn");
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