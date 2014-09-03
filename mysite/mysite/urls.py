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
    url(r'^basicsite/logwithuser', 'basicsite.views.logWithUser'),
    url(r'^basicsite/createnewuser', 'basicsite.views.createNewUser'),
    url(r'^basicsite/pipelines', 'basicsite.views.showAllPipelines'),
    url(r'^basicsite/constructpipeline', 'basicsite.views.constructPipeline'),
    url(r'^basicsite/pipelinecategories/filterpage', 'basicsite.views.showPipelineFilterPage'),
    url(r'^basicsite/pipelinecategories/mypipelines', 'basicsite.views.showMyPipelines'),
    url(r'^basicsite/submitpipeline', 'basicsite.views.submitPipeline'),
    url(r'^basicsite/specificpipeline/(\d+)/$', 'basicsite.views.showSpecificPipeline'),
    url(r'^basicsite/createtrack', 'basicsite.views.showCreateTrackPage'),
    url(r'^basicsite/addtracks', 'basicsite.views.createTrackResponse'),
    url(r'^basicsite/specifictrack/(\d+)/$', 'basicsite.views.showSpecificTrack'),
    url(r'^basicsite/posttrackcomment', 'basicsite.views.postTrackComment'),
    url(r'^basicsite/updatetrackstatus', 'basicsite.views.updateTrackStatus'),
    url(r'^basicsite/assigntopipeline', 'basicsite.views.assignUserToPipeline'),
    url(r'^basicsite/tooltopipeline', 'basicsite.views.addToolToPipeline'),
    url(r'^basicsite/postpipelinecomment', 'basicsite.views.postPipelineComment'),
    url(r'^basicsite/searchstatus', 'basicsite.views.searchByStatus'),
    url(r'^basicsite/searchuser', 'basicsite.views.searchByUser'),
    url(r'^basicsite/searchvideo', 'basicsite.views.searchForVideo'),
    url(r'^basicsite/searchtool', 'basicsite.views.searchByTool'),
    url(r'^basicsite/uploadrelatedfile', 'basicsite.views.uploadRelatedFile'),
    url(r'^basicsite/downloadrelatedevent/(\d+)/$', 'basicsite.views.downloadRelatedEventFiles'),
    url(r'^basicsite/downloadrelatedfile/(\d+)/$', 'basicsite.views.downloadSingleRelatedEventFile'),
    url(r'^basicsite/deletefilevent/(\d+)/$', 'basicsite.views.deleteAllFilesInEvent'),
    url(r'^basicsite/deleterelatedfile/(\d+)/$', 'basicsite.views.deleteSingleRelatedFile'),
    url(r'^basicsite/tools', 'basicsite.views.showAllTools'),
    url(r'^basicsite/uploadtool', 'basicsite.views.loadUploadToolPage'),
    url(r'^basicsite/receivetool', 'basicsite.views.uploadTool'),
    url(r'^basicsite/downloadtool/(\d+)/$', 'basicsite.views.downloadTool'),
    url(r'^basicsite/toolcategories/collection', 'basicsite.views.showCollectionTools'),
    url(r'^basicsite/toolcategories/checkprocess', 'basicsite.views.showCheckingProcessingTools'),
    url(r'^basicsite/toolcategories/label', 'basicsite.views.showLabelingTools'),
    url(r'^basicsite/uploadvideo', 'basicsite.views.showUploadVideoPage'),
    url(r'^basicsite/handleuploadrequest', 'basicsite.views.uploadVideos'),
    url(r'^basicsite/family/(\d+)/$', 'basicsite.views.showToolFamily'),
    url(r'^basicsite/family/versionlog/(\d+)/$', 'basicsite.views.viewFamilyVersionLog'),
    url(r'^basicsite/deletetool/(\d+)/$', 'basicsite.views.deleteTool'),
    url(r'^basicsite/videos', 'basicsite.views.showAllVideos'),
    url(r'^basicsite/videocategories/filterpage', 'basicsite.views.showAllEvents'),
    url(r'^basicsite/downloadvideo/(\d+)/(\d+)/$', 'basicsite.views.downloadVideo'),
    url(r'^basicsite/downloadevent/(\d+)/$', 'basicsite.views.downloadEvent'),
    url(r'^basicsite/addtoevent/(\d+)/$', 'basicsite.views.addVideoToEventPage'),
    url(r'^basicsite/handleaddtoevent/(\d+)/$', 'basicsite.views.uploadAddToVideo'),
    url(r'^basicsite/deletevideo/(\d+)/(\d+)/$', 'basicsite.views.deleteVideo'),
    url(r'^basicsite/specificevent/(\d+)/$', 'basicsite.views.showSpecificEvent'),
    url(r'^basicsite/home', 'basicsite.views.showHomePage'),
)
