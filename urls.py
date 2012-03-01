from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import settings

urlpatterns = patterns('',
    url(r'^$', 'blog.views.blog_home', name='blog_home'),
    url(r'^account/', include('account.urls')),
    url(r'^blog/', include('blog.urls')),
    url(r'^location/', include('location.urls')),
    url(r'^ajax/', include('ajax.urls')),
    
    url(r'^account/login/$', 'django.contrib.auth.views.login', name='account_login'),
    url(r'^account/logout/$', 'django.contrib.auth.views.logout', {'next_page':'/account/login/'}, name='account_logout'),
    
    url(r'^account/password_reset/$', 'django.contrib.auth.views.password_reset', name='account_password_reset'),
    url(r'^account/password_reset/done/$', 'django.contrib.auth.views.password_reset_done', name='account_password_reset_done'),
    url(r'^account/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'django.contrib.auth.views.password_reset_confirm', name='account_password_reset_confirm'),
    url(r'^account/reset/done/$', 'django.contrib.auth.views.password_reset_complete', name='account_password_reset_complete'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()