from django.conf.urls import patterns, include, url

urlpatterns = patterns('manage.views',
    (r'^$', 'manage'),
    (r'^login/$', 'login'),
    (r'^company/$', 'manage_company'),
    (r'^log/$', 'manage_log'),
    )