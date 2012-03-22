from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('blog.views',
    url(r'create/$', 'blog_create', name='blog_create'),
    url(r'manage/$', 'blog_manage', name='blog_manage'),
    url(r'manage/published/$', 'blog_manage_published', name='blog_manage_published'),
    url(r'manage/draft/$', 'blog_manage_draft', name='blog_manage_draft'),
    url(r'manage/trash/$', 'blog_manage_trash', name='blog_manage_trash'),
    url(r'manage/bulk/$', 'blog_manage_bulk', name='blog_manage_bulk'),
    url(r'(?P<blog_id>\d+)/$', 'blog_view', name='blog_view'),
    url(r'(?P<blog_id>\d+)/view/$', 'blog_view', name='blog_view'),
    url(r'(?P<blog_id>\d+)/edit/$', 'blog_edit', name='blog_edit'),
    url(r'(?P<blog_id>\d+)/love/$', 'blog_love', name='blog_love'),
    url(r'(?P<blog_id>\d+)/unlove/$', 'blog_unlove', name='blog_unlove'),
    url(r'(?P<blog_id>\d+)/trash/$', 'blog_trash', name='blog_trash'),
    url(r'(?P<blog_id>\d+)/restore/$', 'blog_restore', name='blog_restore'),
    url(r'all/$', 'blog_all', name='blog_all'),
)
