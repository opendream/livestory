from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('blog.views',
    url(r'create/$', 'blog_create', name='blog_create'),
    url(r'(?P<blog_id>\d+)/$', 'blog_view', name='blog_view'),
    url(r'(?P<blog_id>\d+)/view/$', 'blog_view', name='blog_view'),
    url(r'(?P<blog_id>\d+)/edit/$', 'blog_edit', name='blog_edit'),
)