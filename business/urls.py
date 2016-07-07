from django.conf.urls import patterns, include, url

urlpatterns = patterns('business.views',
    url(r'(?P<cc>\w+)/$', 'urltest'),
    #url(r'(?P<cc>\w+)/main/', 'urltest'),    #right
    #url(r'(\W{1,10})/$', 'urltest'),
    #url(r'(\w+)/$', 'urltest'),
)