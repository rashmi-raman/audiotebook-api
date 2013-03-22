from django.conf.urls import patterns, include, url
from django.conf.urls import *
from audiotebook_api.api import ReportingHistoryResource

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

reportinghistory_resource = ReportingHistoryResource()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
     #(r'^audiotebook_api/', include('audiotebook_api.urls')),
     (r'^api/', include(reportinghistory_resource.urls))
)
