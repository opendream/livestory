from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('account.views',
    url(r'invite/$', 'account_invite', name='account_invite'),
    url(r'login/$', 'account_login', name='account_login'),

)