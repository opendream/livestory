from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('account.views',
    url(r'invite/$', 'account_invite', name='account_invite'),
    #url(r'login/$', 'account_login', name='account_login'),
    url(r'activate/(?P<key>\w+)/$', 'account_activate', name='account_activate'),
    url(r'profile/edit/$', 'account_profile_edit', name='account_profile_edit')
)