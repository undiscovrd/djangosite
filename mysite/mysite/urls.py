############################################################
#
# Aquifi Confidential
# Copyright (c) 2014 Aquifi, Inc., All Rights Reserved
#
# THE TERMS OF USE ARE SUBJECT TO THE PREVAILING LICENSING
# AGREEMENT. THIS FILE MAY NOT BE COPIED
# NOR DISTRIBUTED TO ANY OTHER PARTY.
#
############################################################
# This file handles the url requests to the server in the following standard:
#
#     example: localhost:8000/basicsite/page_name/
#    
# The url is referenced to a defined httpresponse in the views.py file.
#
# Author: Michael Zuccarino
# Date: 8.12.2014
############################################################

from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'basicsite.views.login'),
    url(r'^basicsite/login', 'basicsite.views.login'),
    url(r'^basicsite/thanks', 'basicsite.views.thanks'),
    url(r'^basicsite/tasks', 'basicsite.views.tasks'),
    url(r'^basicsite/submitcommenttask', 'basicsite.views.submitcommenttask'),
    url(r'^basicsite/submitcommenttrack', 'basicsite.views.submitcommenttrack'),
    url(r'^basicsite/changetask', 'basicsite.views.changetask'),
    url(r'^basicsite/createtask', 'basicsite.views.createtask'),
    url(r'^basicsite/submittask', 'basicsite.views.submittask'),
    url(r'^basicsite/submittrack', 'basicsite.views.submittrack'),
    url(r'^basicsite/createtrack', 'basicsite.views.createtrack'),
    url(r'^basicsite/tools', 'basicsite.views.tools'),
    url(r'^basicsite/uploadtool', 'basicsite.views.uploadtool'),
    url(r'^basicsite/receivetool', 'basicsite.views.receivetool'),
    url(r'^basicsite/downloadtool/([0-9])/$', 'basicsite.views.downloadtool'),
    url(r'^basicsite/toolcategories/collection', 'basicsite.views.collectionsection'),
    url(r'^basicsite/toolcategories/checkprocess', 'basicsite.views.checkprocesssection'),
    url(r'^basicsite/toolcategories/label', 'basicsite.views.labelsection'),
    url(r'^basicsite/uploadvideo', 'basicsite.views.uploadvideopage'),
    url(r'^basicsite/handleuploadrequest', 'basicsite.views.handleuploadrequest'),
)
