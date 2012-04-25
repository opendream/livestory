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
                $('input[type=hidden][name=image_file_name]', scope).val(data.result.name);
                $('.drop-area', scope).hide();
                setTimeout(function () {
                    $('.image-wrapper').show();
                }, 800);
                // Hide error message
                scope.siblings('.help-inline').hide()
            }
        }
        
        $('.fileupload', scope).fileupload(param);
        $('.image-delete', scope).click(function (e) {
            e.preventDefault();
            $('.drop-area', scope).show();
            $('.image-border', scope).show();
            $('.image-wrapper').hide();
            $('input[type=hidden][name=image_file_name]', scope).val('');

        });

        $('.fileupload', scope).bind('fileuploadstart', function () {
            var widget = $(this),
            progressElement = $('#fileupload-progress').show(),
            progressElementWrap = $('#fileupload-progress-wrapper').show(),
            interval = 500,
            total = 0,
            loaded = 0,
            loadedBefore = 0,
            progressTimer,
            drop = $('.drop-area').fadeOut(),
            
            progressHandler = function (e, data) {
                loaded = data.loaded;
                total = data.total;
            },
            stopHandler = function () {
                widget
                    .unbind('fileuploadprogressall', progressHandler)
                    .unbind('fileuploadstop', stopHandler);
                window.clearInterval(progressTimer);
                progressElement.fadeOut(function () {
                    //progressElement.html('');
                    progressElement.hide();
                    progressElementWrap.hide();
                    $('.image-border').hide();
                    
                    //drop.fadeIn();
                });
            },
            formatTime = function (seconds) {
                var date = new Date(seconds * 1000);
                return ('0' + date.getUTCHours()).slice(-2) + ':' +
                    ('0' + date.getUTCMinutes()).slice(-2) + ':' +
                    ('0' + date.getUTCSeconds()).slice(-2);
            },
            formatBytes = function (bytes) {
                if (bytes >= 1000000000) {
                    return (bytes / 1000000000).toFixed(2) + ' GB';
                }
                if (bytes >= 1000000) {
                    return (bytes / 1000000).toFixed(2) + ' MB';
                }
                if (bytes >= 1000) {
                    return (bytes / 1000).toFixed(2) + ' KB';
                }
                return bytes + ' B';
            },
            formatPercentage = function (floatValue) {
                return (floatValue * 100)+ '%';
            },
            updateProgressElement = function (loaded, total, bps) {
                progressElement.children('#fileupload-complete').css('width', formatPercentage(loaded / total));
            },
            intervalHandler = function () {
                var diff = loaded - loadedBefore;
                if (!diff) {
                    return;
                }
                loadedBefore = loaded;
                updateProgressElement(
                    loaded,
                    total,
                    diff * (1000 / interval)
                );
            };
            widget
                .bind('fileuploadprogressall', progressHandler)
                .bind('fileuploadstop', stopHandler);
            progressTimer = window.setInterval(intervalHandler, interval);
        });
    })
    
    $('.dropdown-toggle#notification-section').click(function(e) {
        var self = this;
        var url = '/notifications/';
        var params = {};
        var callback = function(result) {
            if (result.status == 200) {
                $(self).children('.notify').children('.value').html('0');
                // TODO. add class for zero notification
            }
        }
        $.get(url, params, callback);
    });
    /*
    $('.field-mood .mood-list input').change(function (e) {
        $('.field-mood .mood-list .mood-icon').removeClass('active');
        $(this).siblings('.mood-icon').addClass('active');
    });
    */
    $('.mood-list').click(function () {
        var icon = $('.mood-icon', this);
        if (!icon.hasClass('active')) {
            inp = $('input', this);
            $('.field-mood .mood-list .mood-icon').removeClass('active');
            icon.addClass('active');
            inp.click();
        }
    });


    
    // Filter =====================
    var default_current_filter = '#' + $('.filter-menu.default').attr('id');
    var current_filter = default_current_filter;
    var duration = 500;
    
    $('a.has-filter').click(function (e) {
        e.preventDefault();

        var href = $(this).attr('href');
        $('a.filter-close').attr('href', href);
        if (current_filter == href) {
            return false;
        }
        var obj = $(href);
        if (obj.hasClass('default')) {
            obj.addClass('dshow');
        }
        
        $('.filter-menu').hide();
        obj.show();
        
        setTimeout(function () {
            var height = obj.height();

            $('.filter-block-append').css('overflow', 'hidden');
            $('.filter-block-append').animate({'height': height}, {
                'queue': false, 
                'duration': duration
            });
        }, 100);
        
        current_filter = href;
    });
    $('a.filter-close').click(function (e) {
        e.preventDefault();
        var href = $(this).attr('href');
        var obj = $(href);

        if (obj.hasClass('dshow')) {
            obj.removeClass('dshow');
        }
        
        var height = obj.height();
        
        current_filter = default_current_filter;
        
        if (!$('.filter-menu.default.dshow').length) {
            current_filter = '';
        }
        
        var dshow = $('.filter-menu.dshow');
        if (dshow.length) {
            $('.filter-block-append').animate({'height': dshow.height()}, {'queue': false, 'duration': duration});
            $('.filter-menu').hide();
            dshow.show();
            $('a.filter-close').attr('href', '#' + dshow.attr('id'));
        }
        else {
            $('.filter-block-append').stop().animate({'height': 0}, {'queue': false, 'duration': duration});
        }

    });
    
    setTimeout(function () {
        var dshow = $('.filter-menu.dshow');
        if (dshow.length) {
            $('.filter-block-append').css('height', dshow.height() + 40);
        }
        else {
            $('.filter-block-append').css('height', 0);
        }
    }, 500);
    
    $('a.filter-close').attr('href', '#' + $('.filter-menu.dshow').attr('id'));

    // End Filter =====================
});