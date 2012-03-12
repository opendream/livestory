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
        
    });
    

    

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