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
                $('input[type=hidden][name=image_path]', scope).val(data.result.filepath);
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
            var params = {
                'image_path': $('input[type=hidden][name=image_path]', scope).val()
            };
            var onSuccess = function (resp) {
                if (resp.result == 'complete') {
                    $('.drop-area', scope).show();
                    $('.image-border', scope).show();
                    $('.image-wrapper').hide();
                    $('input[type=hidden][name=image_path]', scope).val('');
                }
            }
            if ($(this).attr('href')) {
                $.getJSON($(this).attr('href'), params, onSuccess);
            } else {
                onSuccess({'result': 'complete'});
            }
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
                $(self).children('.notify').html('0');
                // TODO. add class for zero notification
            }
        }
        $.get(url, params, callback);
    });
    
    $('.field-mood .mood-list input').change(function (e) {
        $('.field-mood .mood-list .mood-icon').removeClass('active');
        $(this).siblings('.mood-icon').addClass('active');
    });
    


    
    // Filter =====================
    var default_current_filter = '#' + $('.filter-menu.default').attr('id');
    var current_filter = default_current_filter;
    var duration = 500;
    
    $('a.has-filter').click(function (e) {
        e.preventDefault();
        
        var href = $(this).attr('href');
        if (current_filter == href) {
            return false;
        }
        var obj = $(href);
        if (obj.hasClass('default')) {
            obj.addClass('dshow');
        }
        
        var height = obj.height();
        var oheight = height-$(current_filter).height();

        $('.blog-list').stop().animate({'margin-top': oheight}, {'queue': false, 'duration': duration});
        
        $('.filter-menu').stop().hide();
        current_filter = href;
        
        obj.stop().slideDown(duration, function () {
            $('.blog-list').css('margin-top', 0);
            $('.filter-block-append').css('height', height);
        });
    });
    $('a.filter-close').click(function (e) {
        e.preventDefault();
        var href = $(this).attr('href');
        var obj = $(href);
        

        
        if (obj.hasClass('dshow')) {
            obj.removeClass('dshow');
        }
        
        var height = obj.height();
        var oheight = $(current_filter).height() - height;
        
        current_filter = default_current_filter;
        
        if (!$('.filter-menu.default.dshow').length) {
            current_filter = '';
        }
        
        var dshow = $('.filter-menu.dshow');
        if (dshow.length) {
            $('.filter-block-append').animate({'height': dshow.height()}, {'queue': false, 'duration': duration});
            $('.blog-list').stop().animate({'margin-top': -oheight}, {'queue': false, 'duration': duration});
            
            //$('.filter-block-append').height(dshow.height());
            $('.filter-menu').css('position', 'absolute');
            dshow.show()
        }
        else {
            $('.blog-list').stop().animate({'margin-top': -height}, {'queue': false, 'duration': duration});
        }

        
        obj.stop().slideUp(duration, function () {
            $('.blog-list').css('margin-top', 0);
            if (!dshow.length) {
                $('.filter-block-append').css('height', 0);
            }
            $('.filter-menu').css('position', 'relative');
        });

    });
    
    setTimeout(function () {
        var dshow = $('.filter-menu.dshow');
        if (dshow.length) {
            $('.filter-block-append').css('height', dshow.height());
        }
        else {
            $('.filter-block-append').css('height', 0);
        }
    }, 500);

    // End Filter =====================
});