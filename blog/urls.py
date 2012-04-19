from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('blog.views',
    url(r'create/$', 'blog_create', name='blog_create'),
    url(r'create/from/email/$', 'blog_create_by_email', name='blog_create_by_email'),
    
    url(r'manage/$', 'blog_manage', name='blog_manage'),
    url(r'manage/published/$', 'blog_manage_published', name='blog_manage_published'),
    url(r'manage/draft/$', 'blog_manage_draft', name='blog_manage_draft'),
    url(r'manage/trash/$', 'blog_manage_trash', name='blog_manage_trash'),
    url(r'manage/bulk/$', 'blog_manage_bulk', name='blog_manage_bulk'),
    url(r'(?P<blog_id>\d+)/$', 'blog_view', name='blog_view'),
    url(r'(?P<blog_id>\d+)/view/$', 'blog_view'),
    url(r'(?P<blog_id>\d+)/edit/$', 'blog_edit', name='blog_edit'),
    url(r'(?P<blog_id>\d+)/love/$', 'blog_love', name='blog_love'),
    url(r'(?P<blog_id>\d+)/unlove/$', 'blog_unlove', name='blog_unlove'),
    url(r'(?P<blog_id>\d+)/trash/$', 'blog_trash', name='blog_trash'),
    url(r'(?P<blog_id>\d+)/restore/$', 'blog_restore', name='blog_restore'),
    url(r'(?P<blog_id>\d+)/download/$', 'blog_download', name='blog_download'),
    url(r'all/$', 'blog_all', name='blog_all'),
    url(r'mood/(?P<mood>\w+)/$', 'blog_mood', name='blog_mood'),
    url(r'category/(?P<category>[0-9A-Za-z,-]+)/$', 'blog_category', name='blog_category'),
    url(r'place/$', 'blog_place', name='blog_place'),
    url(r'place/choose/$', 'blog_place_empty', name='blog_place_empty'),
    url(r'tags/$', 'blog_tags', name='blog_tags'),
    url(r'search/$', 'blog_search', name='blog_search'),

)
