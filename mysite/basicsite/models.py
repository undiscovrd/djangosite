from django.db import models

# Create your models here.
class User(models.Model):
    user_name = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    rights = models.CharField(max_length=30)
	
class Task(models.Model):
    task_title = models.CharField(max_length=30)
    started_date = models.DateTimeField()
	
class TaskRoster(models.Model):
    user_identifier = models.ForeignKey(User)
    task_identifier = models.ForeignKey(Task)
    task_role = models.CharField(max_length=30)
	
class Video(models.Model):
    video_number = models.IntegerField()
    uploaded_date = models.DateTimeField()
    location = models.CharField(max_length=200)

#this guy will have his own identifier, so track->video->task
class Track(models.Model):
    task_identifier = models.ForeignKey(Task)
    video_identifier = models.ForeignKey(Video)
    status = models.CharField(max_length=50)
	
class Comment(models.Model):
    user_identifier = models.ForeignKey(User)
    date_commented = models.DateTimeField()
    comment_text = models.CharField(max_length=400)
	
class CommentTask(models.Model):
    comment_identifier = models.ForeignKey(Comment)
    task_identifier = models.ForeignKey(Task)

class CommentTrack(models.Model):
    comment_identifier = models.ForeignKey(Comment)
    track_identifier = models.ForeignKey(Track)
    comment_text = models.CharField(max_length=400)