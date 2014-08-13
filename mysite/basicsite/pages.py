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
currentLocation = os.getcwd().replace("\\","/")  + "/basicsite/"
LoginPageTemplate = currentLocation + 'templates/loginpage.html'
TaskPageTemplate = currentLocation + 'templates/tasks.html'
ThanksPageTemplate = currentLocation + 'templates/thanks.html'
CreateTaskPageTemplate = currentLocation + 'templates/createtask.html'
CreateTrackPageTemplate = currentLocation + 'templates/createtrack.html'
ToolPageTemplate = currentLocation + 'templates/tools.html'
UploadToolPageTemplate = currentLocation + 'templates/uploadtool.html'
SpecificToolPageTemplate = currentLocation + 'templates/specifictoolpage.html'
