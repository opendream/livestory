from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('ajax.views',
    url(r'account/image/upload/$', 'ajax_account_image_upload', name='ajax_account_image_upload'),
    url(r'account/image/delete/$', 'ajax_account_image_delete', name='ajax_account_image_delete'),
    url(r'blog/image/upload/$', 'ajax_blog_image_upload', name='ajax_blog_image_upload'),
    url(r'blog/image/delete/$', 'ajax_blog_image_delete', name='ajax_blog_image_delete'),
)