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
    url(r'^basicsite/pipelines', 'basicsite.views.pipelines'),
    url(r'^basicsite/constructpipeline', 'basicsite.views.constructpipeline'),
    url(r'^basicsite/pipelinecategories/filterpage', 'basicsite.views.pipelinefilterpage'),
    url(r'^basicsite/pipelinecategories/mypipelines', 'basicsite.views.mypipelines'),
    url(r'^basicsite/submitpipeline', 'basicsite.views.submitpipeline'),
    url(r'^basicsite/specificpipeline/(\d+)/$', 'basicsite.views.specificpipeline'),
    url(r'^basicsite/createtrack', 'basicsite.views.createtrack'),
    url(r'^basicsite/addtracks', 'basicsite.views.addtracks'),
    url(r'^basicsite/specifictrack/(\d+)/$', 'basicsite.views.specifictrack'),
    url(r'^basicsite/posttrackcomment', 'basicsite.views.posttrackcomment'),
    url(r'^basicsite/updatetrackstatus', 'basicsite.views.updatetrackstatus'),
    url(r'^basicsite/assigntopipeline', 'basicsite.views.assigntopipeline'),
    url(r'^basicsite/postpipelinecomment', 'basicsite.views.postpipelinecomment'),
    url(r'^basicsite/searchstatus', 'basicsite.views.searchstatus'),
    url(r'^basicsite/searchuser', 'basicsite.views.searchuser'),
    url(r'^basicsite/searchvideo', 'basicsite.views.searchvideo'),
    url(r'^basicsite/searchtool', 'basicsite.views.searchtool'),
    url(r'^basicsite/uploadrelatedfile', 'basicsite.views.uploadrelatedfile'),
    url(r'^basicsite/downloadrelatedevent/(\d+)/$', 'basicsite.views.downloadrelatedevent'),
    url(r'^basicsite/downloadrelatedfile/(\d+)/$', 'basicsite.views.downloadrelatedfile'),
    url(r'^basicsite/deletefilevent/(\d+)/$', 'basicsite.views.deletefilevent'),
    url(r'^basicsite/deleterelatedfile/(\d+)/$', 'basicsite.views.deleterelatedfile'),
    url(r'^basicsite/tools', 'basicsite.views.tools'),
    url(r'^basicsite/uploadtool', 'basicsite.views.uploadtool'),
    url(r'^basicsite/receivetool', 'basicsite.views.receivetool'),
    url(r'^basicsite/downloadtool/(\d+)/$', 'basicsite.views.downloadtool'),
    url(r'^basicsite/toolcategories/collection', 'basicsite.views.collectionsection'),
    url(r'^basicsite/toolcategories/checkprocess', 'basicsite.views.checkprocesssection'),
    url(r'^basicsite/toolcategories/label', 'basicsite.views.labelsection'),
    url(r'^basicsite/uploadvideo', 'basicsite.views.uploadvideopage'),
    url(r'^basicsite/handleuploadrequest', 'basicsite.views.handleuploadrequest'),
    url(r'^basicsite/family/(\d+)/$', 'basicsite.views.specificfamilypage'),
    url(r'^basicsite/family/versionlog/(\d+)/$', 'basicsite.views.viewversionlog'),
    url(r'^basicsite/deletetool/(\d+)/$', 'basicsite.views.deletetool'),
    url(r'^basicsite/videos', 'basicsite.views.videos'),
    url(r'^basicsite/videocategories/filterpage', 'basicsite.views.videofilterpage'),
    url(r'^basicsite/videocategories/assigntotaskpage', 'basicsite.views.videoassigntotaskpage'),
    url(r'^basicsite/videocategories/tasks', 'basicsite.views.videotasks'),
    url(r'^basicsite/downloadvideo/(\d+)/(\d+)/$', 'basicsite.views.downloadvideo'),
    url(r'^basicsite/downloadevent/(\d+)/$', 'basicsite.views.downloadevent'),
    url(r'^basicsite/addtoevent/(\d+)/$', 'basicsite.views.addtoevent'),
    url(r'^basicsite/handleaddtoevent/(\d+)/$', 'basicsite.views.handleaddtoevent'),
    url(r'^basicsite/deletevideo/(\d+)/(\d+)/$', 'basicsite.views.deletevideo'),
    url(r'^basicsite/specificevent/(\d+)/$', 'basicsite.views.specificevent'),
    url(r'^basicsite/home/', 'basicsite.views.home'),
)
