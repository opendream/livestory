$(document).ready(function () {
    $('.messages .close').click(function () {
        $(this).parent('.alert').slideUp('fast');
    })
})