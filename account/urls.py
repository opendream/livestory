from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('account.views',
    url(r'invite/$', 'account_invite', name='account_invite'),
    #url(r'login/$', 'account_login', name='account_login'),
    url(r'activate/(?P<key>\w+)/$', 'account_activate', name='account_activate'),
    url(r'profile/edit/$', 'account_profile_edit', name='account_profile_edit'),
    url(r'profile/create/$', 'account_profile_create', name='account_profile_create'),
    url(r'forgot/$', 'account_forgot', name='account_forgot'),

    url(r'users/manage/$', 'account_manage_users', name='account_manage_users'),
)