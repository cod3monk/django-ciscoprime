from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ciscoprime.views.home', name='home'),
    url(r'^main/', include('main.urls')),

    url(r'^admin/', include(admin.site.urls)),
)