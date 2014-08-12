from django.db import models
from django import forms

# User model contains a user's login credentials and rights.
class User(models.Model):
    user_name = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    rights = models.CharField(max_length=30)
	
# Task is the high level pipeline. Tracks are leaves of the task.
class Task(models.Model):
    task_title = models.CharField(max_length=30)
    started_date = models.DateTimeField()

# Just maintains a record of who is assigned to the tasks through a User->Task relationship. Includes role in task.
class TaskRoster(models.Model):
    user_identifier = models.ForeignKey(User)
    task_identifier = models.ForeignKey(Task)
    task_role = models.CharField(max_length=30)

# Maintains a list of videos, when they were uploaded, and where it is stored
class Video(models.Model):
    video_number = models.IntegerField()
    uploaded_date = models.DateTimeField()
    location = models.CharField(max_length=200)

# List of tracks, the status of it, and the video it is related to. Multiple tracks point to a single task.
class Track(models.Model):
    task_identifier = models.ForeignKey(Task)
    video_identifier = models.ForeignKey(Video)
    status = models.CharField(max_length=50)

# List of ALL comments across all tracks and tasks. They are accessed relationally by the identifier in the following classes.
class Comment(models.Model):
    user_identifier = models.ForeignKey(User)
    date_commented = models.DateTimeField()
    comment_text = models.CharField(max_length=400)
	
# List of identifiers that relate the comments made for tasks to the Comment table.
class CommentTask(models.Model):
    comment_identifier = models.ForeignKey(Comment)
    task_identifier = models.ForeignKey(Task)

# List of identifiers that relate the comments made for tracks to the Comment table.
class CommentTrack(models.Model):
    comment_identifier = models.ForeignKey(Comment)
    track_identifier = models.ForeignKey(Track)
    comment_text = models.CharField(max_length=400)

# List of tool families for more specific tool tracking. (i.e.: Face Labeling, Wake Up Tagging, etc..)
class ToolFamily(models.Model):
    toolfamilyname = models.CharField(max_length=150)
    datecreated = models.DateTimeField()
    description = models.CharField(max_length=400)

# List of all tools. File Info held by 'tf' relation. Purpose relates to one of the three main categories: Collection, Check/Processing, Labeling.
class ToolFile(models.Model):
    tooltitle = models.CharField(max_length=50)
    tf = models.FileField(upload_to='tools')
    toolfilename = models.CharField(max_length=150)
    uploaded = models.DateTimeField()
    description = models.CharField(max_length=400)
    purpose = models.CharField(max_length=50)
    versionnumber = models.DecimalField(max_digits=10, decimal_places=7)
    family = models.ForeignKey(ToolFamily)
    

    
    