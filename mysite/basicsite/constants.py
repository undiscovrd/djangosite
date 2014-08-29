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
# This page details the page templates for use in the views.py
# Author: Michael Zuccarino
# Date: 8.12.2014
############################################################
import os.path

# File Path used to reference the templates
CURRENTLOCATION = os.getcwd().replace("\\","/")  + "/basicsite/"
LOGINPAGETEMPLATE = CURRENTLOCATION + 'templates/loginpage.html'
TASKPAGETEMPLATE = CURRENTLOCATION + 'templates/tasks.html'
THANKSPAGETEMPLATE = CURRENTLOCATION + 'templates/thanks.html'
CREATETASKPAGETEMPLATE = CURRENTLOCATION + 'templates/createtask.html'
CREATETRACKPAGETEMPLATE = CURRENTLOCATION + 'templates/createtrack.html'
TOOLPAGETEMPLATE = CURRENTLOCATION + 'templates/tools.html'
UPLOADTOOLPAGETEMPLATE = CURRENTLOCATION + 'templates/uploadtool.html'
SPECIFICTOOLPAGETEMPLATE = CURRENTLOCATION + 'templates/specifictoolpage.html'
UPLOADVIDEOPAGETEMPLATE = CURRENTLOCATION + 'templates/uploadvideodevelopmentpage.html'
SPECIFICFAMILYPAGETEMPLATE = CURRENTLOCATION + 'templates/specificfamilypage.html'
VIEWVERSIONLOGPAGETEMPLATE = CURRENTLOCATION + 'templates/viewversionlogpage.html'
VIDEOSPAGETEMPLATE = CURRENTLOCATION + 'templates/videospage.html'
VIDEOFILTERPAGETEMPLATE = CURRENTLOCATION + 'templates/videofilterpage.html'
VIDEOASSIGNTOTASKPAGETEMPLATE = CURRENTLOCATION + 'templates/videoassigntotaskpage.html'
VIDEOTASKSPAGETEMPLATE = CURRENTLOCATION + 'templates/videotasks.html'
ADDTOEVENTPAGETEMPLATE = CURRENTLOCATION + 'templates/addtoevent.html'
SPECIFICEVENTPAGETEMPLATE = CURRENTLOCATION + 'templates/specificeventpage.html'
HOMEPAGETEMPLATE = CURRENTLOCATION + 'templates/homepage.html'
ALLPIPELINESPAGETEMPLATE = CURRENTLOCATION + 'templates/pipeline.html'
PIPELINEFILTERPAGETEMPLATE = CURRENTLOCATION + 'templates/pipelinefilterpage.html'
MYPIPELINESPAGETEMPLATE = CURRENTLOCATION + 'templates/mypipelinespage.html'
CONSTRUCTPIPELINEPAGETEMPLATE = CURRENTLOCATION + 'templates/constructpipelinepage.html'
SPECIFICPIPELINEPAGETEMPLATE = CURRENTLOCATION + 'templates/specificpipeline.html'
SPECIFICTRACKPAGETEMPLATE = CURRENTLOCATION + 'templates/specifictrackpage.html'
SEARCHSTATUSPAGETEMPLATE = CURRENTLOCATION + 'templates/searchstatuspage.html'
SEARCHUSERPAGETEMPLATE = CURRENTLOCATION + 'templates/searchuserpage.html'
SEARCHVIDEOPAGETEMPLATE = CURRENTLOCATION + 'templates/searchvideopage.html'
SEARCHTOOLPAGETEMPLATE = CURRENTLOCATION + 'templates/searchtoolpage.html'