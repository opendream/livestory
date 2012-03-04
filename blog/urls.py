from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('blog.views',
    url(r'create/$', 'blog_create', name='blog_create'),
    url(r'manage/$', 'blog_manage', name='blog_manage'),
    url(r'manage/bulk/$', 'blog_manage_bulk', name='blog_manage_bulk'),
    url(r'manage/set/private/$', 'blog_manage_set_private', name='blog_manage_set_private'),
    url(r'manage/set/public/$', 'blog_manage_set_public', name='blog_manage_set_public'),
    url(r'(?P<blog_id>\d+)/$', 'blog_view', name='blog_view'),
    url(r'(?P<blog_id>\d+)/view/$', 'blog_view', name='blog_view'),
    url(r'(?P<blog_id>\d+)/edit/$', 'blog_edit', name='blog_edit'),
    url(r'(?P<blog_id>\d+)/love/$', 'blog_love', name='blog_love'),
    url(r'(?P<blog_id>\d+)/unlove/$', 'blog_unlove', name='blog_unlove'),
)
