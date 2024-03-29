from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('ajax.views',
    url(r'account/image/upload/$', 'ajax_account_image_upload', name='ajax_account_image_upload'),
    url(r'account/(\d+)/image/upload/$', 'ajax_profile_image_upload', name='ajax_profile_image_upload'),
    url(r'account/image/delete/$', 'ajax_account_image_delete', name='ajax_account_image_delete'),
)