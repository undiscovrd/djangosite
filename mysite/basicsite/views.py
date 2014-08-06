# Create your views here.
from django.shortcuts import render
from django.shortcuts import redirect
from django import forms
from models import User
from models import Comment
from models import CommentTask
from models import CommentTrack
from models import Task
from models import Track
from django.utils import timezone
#from django.template import RequestContext

import os.path


# Path to basicsite
currentLocation = os.getcwd().replace("\\","/")  + "/basicsite/"

def index(request):
    return render(request,currentLocation + 'templates/loginpage.html')
    
def login(request):
    if request.method == 'POST': # If the form has been submitted...
        # ContactForm was defined in the previous section
        form = LoginForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            user = form.cleaned_data['username']
            password = form.cleaned_data['password']
            request.session['user'] = user
            request.session['password'] = password
            
            try:
                testuser = User.objects.get(user_name=user)
                if (testuser.user_name != user):
                    u = User(user_name=user, password=password, rights="user")
                    u.save()
            except:
                u = User(user_name=user, password=password, rights="user")
                u.save()
            return redirect('/basicsite/tasks/') # Redirect after POST
            
        username = request.POST.get('username')
        password = request.POST.get('password')
    else:
        form = LoginForm() # An unbound form

    return render(request, currentLocation + 'templates/loginpage.html', {'form': form,})

def tasks(request):
    formarea = ReplyBox()
    allcomments = Comment.objects.all()
    tasks = Task.objects.all()
    tracks = Track.objects.all()
    try:
        currenttaskid = request.session['currenttask']
        currenttask = Task.objects.get(id=currenttaskid)
        whichmethod = "went through try"
        ctask = currenttask.id
    except:
        currenttask = tasks[0]
        request.session['currenttask'] = currenttask.id;
        ctask = currenttask.id
        whichmethod = "went through except"
        
    try:
        currenttrack = request.session['currenttrack']
        currenttrack = Track.objects.get(id=currenttrackid)
        ctrack = currenttrack.id
    except:
        currenttrack = tracks[0]
        request.session['currenttrack'] = currenttrack.id;
        ctrack = currenttrack.id
    
    forloopcomtask = CommentTask.objects.all()
    commentstask = []
    for comtask in forloopcomtask:
        if (comtask.task_identifier_id == ctask):
            commentstask.append(comtask)
        
    forloopcomtrack = CommentTrack.objects.all()
    commentstrack = []
    for comtrack in forloopcomtrack:
        if (comtrack.track_identifier_id == ctrack):
            commentstrack.append(comtrack)
        
    tracksfortask = []
    for track in tracks:
        if (track.task_identifier_id == ctask):
            tracksfortask.append(track)
    
    return render(request,currentLocation + 'templates/tasks.html', {'formarea': formarea, 
        'allcomments' : allcomments, 
        'commentstask' : commentstask, 
        'commentstrack' : commentstrack, 
        'tracksfortask' : tracksfortask, 
        'alltasks' : tasks, 
        'currenttask' : currenttask, 
        'currenttrack' : currenttrack, 
        'whichmethod' : whichmethod,
        'ctask' : ctask })

def timeline(request):
    return render(request,currentLocation + 'templates/timeline.html')
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField()
    
def thanks(request):
    user = request.session['user']
    password = request.session['password']
    
    return render(request, currentLocation + 'templates/thanks.html', {"username" : user, "password" : password});
    
class ReplyBox(forms.Form):
    comment1 = forms.CharField( widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}) )
    comment2 = forms.CharField( widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}) )
    
def submitcommenttask(request):
    if request.method == 'POST': # If the form has been submitted...
        comment1 = request.POST['comment1']
        usercookie = request.session['user']
        u = User.objects.get(user_name=usercookie)
        pub_date=timezone.now()
        c = Comment(user_identifier=u, date_commented=pub_date, comment_text=comment1)
        c.save()
        tk_id = request.session['currenttask']
        ct = CommentTask(comment_identifier_id=c.id,task_identifier_id=tk_id)
        ct.save()

       # ct = CommeTask(comment_identifier=c,
        return redirect('/basicsite/tasks/') # Redirect after POST
    
    return render(request, currentLocation + 'templates/thanks.html')
    
def submitcommenttrack(request):
    if request.method == 'POST': # If the form has been submitted...
        comment2 = request.POST['comment2']
        usercookie = request.session['user']
        u = User.objects.get(user_name=usercookie)
        pub_date=timezone.now()
        c = Comment(user_identifier=u, date_commented=pub_date, comment_text=comment2)
        c.save()
        ta_id = request.session['currenttrack']
        ca = CommentTrack(comment_identifier_id=c.id,track_identifier_id=ta_id)
        ca.save()
        return redirect('/basicsite/tasks/') # Redirect after POST
    
    return render(request, currentLocation + 'templates/thanks.html')
    
def changetask(request):
    if request.method == 'POST':
        request.session['currenttask'] = request.POST['tasks']
        return redirect('/basicsite/tasks/')
    
    return render(request, currentLocation + 'templates/thanks.html')
    
class CreateTaskBox(forms.Form):
    taskname = forms.CharField(max_length=100)
    nameEntry = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())
    
    def __init__(self, allusers, *args, **kwargs):
        super(CreateTaskBox, self).__init__(*args, **kwargs)
        self.fields['nameEntry'] = forms.ChoiceField(choices=[ (user.id, user.user_name) for user in allusers])
    
def createtask(request):
    allusers = User.objects.all()
    
    form = CreateTaskBox(allusers)
    
    return render(request, currentLocation + 'templates/createtask.html', {'form' : form })
    
    
    
    
    
    
    
    
    
    
    
    
