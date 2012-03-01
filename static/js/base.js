$(function () {
    $('.messages .close').click(function () {
        $(this).parent('.alert').slideUp('fast');
    });
    
    $('.dropdown-toggle').dropdown();

    
    $('.image-upload').each(function (i, item) {
        var scope = $(this);
        var upload_url = $('.upload_url', scope).val();
        var param = {
            dataType: 'json',
            url: upload_url,
            done: function (e, data) {
                $('div.image-append', scope).html('');
                $('div.image-append', scope).append($('<img/>').attr('src', data.result.thumbnail_url));
                $('.drop-area', scope).hide();
                $('.image-wrapper').show();
            }
        }
        
        $('.fileupload', scope).fileupload(param);
        $('.image-delete', scope).click(function (e) {
            e.preventDefault();
            $.getJSON($(this).attr('href'), function (resp) {
                if (resp.result == 'complete') {
                    $('.drop-area', scope).show();
                    $('.image-wrapper').hide();
                }
            });
        });
    })

    $('.dropdown-toggle').mouseenter(function(e) {
        var $toggle = $(this);
        var closeDropdown = function(e) {
            $toggle.parent().removeClass('open');
            $(this).unbind('mouseleave');
        }
        $toggle.parent().addClass('open');
        $toggle.siblings('.dropdown-menu').mouseleave(closeDropdown);
    });
});