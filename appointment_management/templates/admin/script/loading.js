if (isLoading) {
    $(document).ajaxStart(function() {
        $('#fullscreen-spinner').addClass('d-none');
    });
} else {
    $(document).ajaxStart(function() {
        $('#fullscreen-spinner').removeClass('d-none');
    });
}