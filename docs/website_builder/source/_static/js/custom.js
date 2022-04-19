
window.SURVEY_URL = 'https://www.surveymonkey.com/r/XM7JZQ7';
window.tookSurvey = localStorage.surveyUrl === window.SURVEY_URL
window.dataLayer = window.dataLayer || [];

// Open external links in a new tab
$(document).ready(function () {
    checkIfAcceptedCookies();
    $('a[href^="http://"], a[href^="https://"]').not('a[class*=internal]').attr('target', '_blank');
});


$(window).scroll(function() {
    let offset = $(window).scrollTop();
    let winHeight = $(window).height();
    let docHeight = $(document).height();
    let height = docHeight - winHeight;

    //console.log(`${offset} ${docHeight} ${height}`)

    // Only show the survey dialog if the user scrolls to >50% of the page
    if(localStorage.acceptedCookies && !window.tookSurvey && offset > height * 0.5) {
        if(!$('#dlg-survey').is(':visible')) {
            $('#dlg-survey').css('display', 'block');
            $("#dlg-survey-close").on("click", closeSurvey);
        }
    }
});


function gtag() {
    dataLayer.push(arguments);
}

function initialiseGoogleAnalytics() {
    console.log('Loading google analytics');
    gtag('js', new Date());
    gtag('config', gTrackingId, {'anonymize_ip': true});
}

function checkIfAcceptedCookies() {
    if (!localStorage.acceptedCookies) {
        $('.privacy-banner').show();
        $('.privacy-banner-accept').click(function() {
            $('.privacy-banner').hide()
            localStorage.acceptedCookies = 'true';
            onAcceptedCookies();
        });
        
    } else {
        onAcceptedCookies();
    }
}

function onAcceptedCookies() {
    initialiseGoogleAnalytics();
    $('#survey-link').attr('href', window.SURVEY_URL);
    checkIfSurveyCompleted();
}

function closeSurvey() {
    console.info('Took survey');
    window.tookSurvey = true;
    localStorage.surveyUrl = window.SURVEY_URL
    $('#dlg-survey').css('display', 'none');
}

function checkIfSurveyCompleted() {
    if(localStorage.surveyUrl === window.SURVEY_URL) {
        window.tookSurvey = true;
        $('#dlg-survey').css('display', 'none');
    } else {
        setTimeout(checkIfSurveyCompleted, 100);
    }

}
