
window.SURVEY_URL = 'https://www.surveymonkey.com/r/XM7JZQ7';
window.tookSurvey = localStorage.surveyUrl === window.SURVEY_URL
window.dataLayer = window.dataLayer || [];

// Open external links in a new tab
$(document).ready(function () {
    checkPrivacyBannerStatus();
    $('a[href^="http://"], a[href^="https://"]').not('a[class*=internal]').attr('target', '_blank');

    if(!window.tookSurvey) {
        $('#survey-link').attr('href', window.SURVEY_URL);
    }
});


$(window).scroll(function() {
    let offset = $(window).scrollTop();
    let winHeight = $(window).height();
    let docHeight = $(document).height();
    let height = docHeight - winHeight;

    //console.log(`${offset} ${docHeight} ${height}`)

    // Only show the survey dialog if the user scrolls to >50% of the page
    if(localStorage.bannerClosed && !window.tookSurvey && offset > height * 0.5) {
        $("#survey-iframe").on('load', function() {
            $('#dlg-survey').css('display', 'block');
        });
        $("#survey-iframe").attr('src', window.SURVEY_URL);
        $("#dlg-survey-close").on("click", closeSurvey);
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

function checkPrivacyBannerStatus() {
    if (!localStorage.bannerClosed) {
        $('.privacy-banner').show();
        $('.privacy-banner-accept').click(function() {
            $('.privacy-banner').hide()
            localStorage.bannerClosed = 'true';
            initialiseGoogleAnalytics();
        });
        
    } else {
        initialiseGoogleAnalytics();
    }
}

function closeSurvey() {
    window.tookSurvey = true;
    localStorage.surveyUrl = window.SURVEY_URL
    $('#dlg-survey').css('display', 'none');
}
