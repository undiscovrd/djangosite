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
# Models.py defines the classes that are used to create the database, and store data.
# Author: Michael Zuccarino
# Date: 8.12.2014
############################################################

from django.db import models
from django import forms

# User model contains a user's login credentials and rights.
class User(models.Model):
    user_name = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    rights = models.CharField(max_length=30)
	
class Pipeline(models.Model):
    pipeline_title = models.CharField(max_length=30)
    description = models.CharField(max_length=400)
    started_date = models.DateTimeField()
    target_date = models.DateTimeField()
    creator = models.ForeignKey(User)

# Just maintains a record of who is assigned to the pipelines through a User->pipeline relationship. Includes role in pipeline.
class PipelineRoster(models.Model):
    user_identifier = models.ForeignKey(User)
    pipeline_identifier = models.ForeignKey(Pipeline)
    pipeline_role = models.CharField(max_length=30)

class VideoFamily(models.Model):
    familyname = models.CharField(max_length=200)
    datecreated = models.DateTimeField()

# List of tool families for more specific tool tracking. (i.e.: Face Labeling, Wake Up Tagging, etc..)
class ToolFamily(models.Model):
    toolfamilyname = models.CharField(max_length=150)
    datecreated = models.DateTimeField()
    description = models.CharField(max_length=400)
    category = models.CharField(max_length=2)

# List of all tools. File Info held by 'tf' relation. Purpose relates to one of the three main categories: Collection, Check/Processing, Labeling.
class ToolFile(models.Model):
    tooltitle = models.CharField(max_length=50)
    tf = models.FileField(upload_to='tools')
    versionlog = models.FileField(upload_to='versionlogs')
    toolfilename = models.CharField(max_length=150)
    uploaded = models.DateTimeField()
    description = models.CharField(max_length=400)
    purpose = models.CharField(max_length=50)
    versionnumber = models.FloatField()
    family = models.ForeignKey(ToolFamily)
    
# Keeps track of all the upload events
class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=400)
    event_date = models.DateTimeField()
    uploader = models.ForeignKey(User)
    
# Maintains a list of videos, when they were uploaded, and where it is stored
class Video(models.Model): 
    video_number = models.IntegerField()
    uploaded_date = models.DateTimeField()
    collectiontool = models.ForeignKey(ToolFile)
    event = models.ForeignKey(Event)
    checkprocesstool = models.CharField(max_length=20)
    
# List of tracks, the status of it, and the video it is related to. Multiple tracks point to a single pipeline.
class Track(models.Model):
    pipeline_identifier = models.ForeignKey(Pipeline)
    video_identifier = models.ForeignKey(Video)
    status = models.CharField(max_length=50)
    started_date = models.DateTimeField()
    
class CommentTrack(models.Model):
    text = models.CharField(max_length=2000)
    author = models.ForeignKey(User)
    posted_date = models.DateTimeField()
    track = models.ForeignKey(Track)
    
class TrackFileEvent(models.Model):
    eventname = models.CharField(max_length=200)
    uploader = models.ForeignKey(User)
    track = models.ForeignKey(Track)
    description = models.CharField(max_length=500)
    uploaded_date = models.DateTimeField()
    toolsused = models.CharField(max_length=10)
    
class TrackFiles(models.Model):
    filename = models.CharField(max_length=200)
    trackfilevent = models.ForeignKey(TrackFileEvent)
    toolsused = models.CharField(max_length=10)