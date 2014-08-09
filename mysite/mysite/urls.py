from django.conf.urls import patterns, include, url

from django.contrib import admin
#admin.autodiscover()     url(r'^basicsite/tracks/(?P<track>\d{4})', 'basicsite.views.tracks'),


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'basicsite.views.login'),
    url(r'^basicsite/login', 'basicsite.views.login'),
    url(r'^basicsite/thanks', 'basicsite.views.thanks'),
    url(r'^basicsite/tasks', 'basicsite.views.tasks'),
    url(r'^basicsite/timeline', 'basicsite.views.timeline'),
    url(r'^basicsite/submitcommenttask', 'basicsite.views.submitcommenttask'),
    url(r'^basicsite/submitcommenttrack', 'basicsite.views.submitcommenttrack'),
    url(r'^basicsite/changetask', 'basicsite.views.changetask'),
    url(r'^basicsite/createtask', 'basicsite.views.createtask'),
    url(r'^basicsite/submittask', 'basicsite.views.submittask'),
    url(r'^basicsite/createtrack', 'basicsite.views.createtrack'),
    url(r'^basicsite/tools', 'basicsite.views.tools'),
    url(r'^basicsite/uploadtool', 'basicsite.views.uploadtool'),
    url(r'^basicsite/receivetool', 'basicsite.views.receivetool'),
    url(r'^basicsite/downloadtool/([0-9])/$', 'basicsite.views.downloadtool'),
)
