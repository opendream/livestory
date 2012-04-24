from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('blog.views_ajax',
    url(r'blog/image/upload/$', 'ajax_blog_image_upload', name='ajax_blog_image_upload'),

)
