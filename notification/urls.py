from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('notification.views',
    url(r'^notifications_viewed/$', 'ajax_set_notifications_as_viewed', name='ajax_set_notifications_as_viewed'),
    url(r'^notifications/$', 'view_notifications', name='notification_view'),


)
