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