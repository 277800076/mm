from django.conf.urls import patterns, include, url

urlpatterns = patterns('doc.views',
    (r'^$', 'document'),
    (r'^(\d{2})/$', 'document_list'),
    (r'^new/$', 'document_new'),
    (r'^edit/(\w{32})$', 'document_edit'),
    (r'^view/(\w{32})$', 'document_view'),
    (r'^delete/(\w{32})$', 'document_delete'),
    )