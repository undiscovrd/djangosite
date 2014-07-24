from django.conf.urls import patterns, include, url

from django.contrib import admin
from basicsite.views import index
#admin.autodiscover()     url(r'^basicsite/tracks/(?P<track>\d{4})', 'basicsite.views.tracks'),


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'basicsite.views.login'),
    url(r'^basicsite/login', 'basicsite.views.login'),
    url(r'^basicsite/thanks', 'basicsite.views.thanks'),
    url(r'^basicsite/tasks/(?P<task>\d{4})', 'basicsite.views.tasks'),
    url(r'^basicsite/timeline', 'basicsite.views.timeline'),
)
