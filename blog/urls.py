from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('blog.views',
    url(r'create/$', 'blog_create', name='blog_create'),
    url(r'manage/$', 'blog_manage', name='blog_manage'),
    url(r'manage/bulk/$', 'blog_manage_bulk', name='blog_manage_bulk'),
    url(r'(?P<blog_id>\d+)/$', 'blog_view', name='blog_view'),
    url(r'(?P<blog_id>\d+)/view/$', 'blog_view', name='blog_view'),
    url(r'(?P<blog_id>\d+)/edit/$', 'blog_edit', name='blog_edit'),
    url(r'(?P<blog_id>\d+)/love/$', 'blog_love', name='blog_love'),
    url(r'(?P<blog_id>\d+)/unlove/$', 'blog_unlove', name='blog_unlove'),
    url(r'all/$', 'blog_all', name='blog_all'),
    url(r'mood/(?P<mood>\w+)/$', 'blog_mood', name='blog_mood'),
    url(r'category/(?P<category>[0-9A-Za-z,-]+)/$', 'blog_category', name='blog_category'),
)
