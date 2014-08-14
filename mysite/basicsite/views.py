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
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django import forms
from models import *
from django.utils import timezone
from django.http import HttpResponse
from django.template import RequestContext
from constants import *

# Landing page to let user login or create new account
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
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
            return redirect('/basicsite/tools/')
            
        username = request.POST.get('username')
        password = request.POST.get('password')
    else:
        form = LoginForm()
    # Renders and displays the login page, passing LoginForm
    return render(request, LOGINPAGETEMPLATE, {'form': form,})

# Processes and returns the /tasks/ page based on the cookies. Page is defaulted to first task, first track.
def tasks(request):
    formarea = ReplyBox()
    allcomments = Comment.objects.all()
    tasks = Task.objects.all()
    tracks = Track.objects.all()
    
    # determine the current task based off of cookies, otherwise defaults to first task
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
    
    # determine the current track based off of cookies, otherwise defaults to first track
    try:
        currenttrack = request.session['currenttrack']
        currenttrack = Track.objects.get(id=currenttrackid)
        ctrack = currenttrack.id
    except:
        currenttrack = tracks[0]
        request.session['currenttrack'] = currenttrack.id;
        ctrack = currenttrack.id
    
    # Filter out comments by task and track
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
    
    # display the tasks page with the passed objects
    return render(request,TASKPAGETEMPLATE, {'formarea': formarea, 
        'allcomments' : allcomments, 
        'commentstask' : commentstask, 
        'commentstrack' : commentstrack, 
        'tracksfortask' : tracksfortask, 
        'alltasks' : tasks, 
        'currenttask' : currenttask, 
        'currenttrack' : currenttrack, 
        'whichmethod' : whichmethod,
        'ctask' : ctask })
    
# Defines the Login Form data for validation
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField()
    
# this is a debug page to test state of cookies
def thanks(request):
    user = request.session['user']
    password = request.session['password']
    if request.method == 'POST':
        taskName = request.POST['taskname']
        selectedNames = request.POST.getlist('usernamelist')
    return render(request,THANKSPAGETEMPLATE, {"username" : user, "password" : password, 'taskName' : taskName, 'selectedNames' : selectedNames });
    
# Form for the comment submission, one correlates to task, two to track
class ReplyBox(forms.Form):
    comment1 = forms.CharField( widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}) )
    comment2 = forms.CharField( widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}) )

# Creates a comment object and then relates it to the task
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
        return redirect('/basicsite/tasks/')
    return render(request,THANKSPAGETEMPLATE)
    
# Creates a comment object and then relates it to the task
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
    return render(request, THANKSPAGETEMPLATE)
    
# reloads the /tasks/ page with the task defined by cookie
def changetask(request):
    if request.method == 'POST':
        request.session['currenttask'] = request.POST['tasks']
        return redirect('/basicsite/tasks/')
    return render(request, THANKSPAGETEMPLATE)
    
# form class for creating task, nameEntry refers a user that can be assigned to task
class CreateTaskBox(forms.Form):
    taskname = forms.CharField(max_length=100)
    nameEntry = forms.BooleanField()
    
# form class for creating track, nameEntry refers a user that can be assigned to track
class CreateTrackBox(forms.Form):
    trackname = forms.CharField(max_length=100)
    nameEntry = forms.BooleanField()
    
# loads the create task page
def createtask(request):
    allusers = User.objects.all()
    form = CreateTaskBox()
    return render(request,CREATETASKPAGETEMPLATE, {'form' : form, 'allusers' : allusers })

# creates the task based off of the passed form data (attaches to cookies by name of fields in class)
def submittask(request):
    if request.method == 'POST':
        taskName = request.POST['taskname']
        selectedNames = request.POST.getlist('usernamelist')
        pub_date=timezone.now()
        tk = Task(task_title = taskName, started_date=pub_date)
        tk.save()
    # involve selected users to task
    for id in selectedNames:
        u = User.objects.get(id=id)
        tkroster = TaskRoster(user_identifier_id = u.id, task_identifier_id = tk.id, task_role = 'labeler')
        tkroster.save()
    return redirect('/basicsite/tasks/') # Redirect after POST

# loads the create track page
def createtrack(request):
    allusers = User.objects.all()
    form = CreateTrackBox()
    currenttask = request.session['currenttask']
    ctkrostercount = TaskRoster.objects.all()
    ctkroster=[]
    # only members in task can be assigned to track
    for tkobj in ctkrostercount:
        tkobjid = tkobj.id
        if tkobj.task_identifier_id==int(currenttask):
            isamatch = 'yes'
            ctkroster.append(tkobj)
    ctkrosterclean = []
    for tkrstrobj in ctkroster:
        userToAppend = User.objects.get(id=tkrstrobj.user_identifier_id)
        ctkrosterclean.append(userToAppend)
    return render(request, CREATETRACKPAGETEMPLATE, {'form' : form, 'allusers' : allusers, 'ctkrosterclean' : ctkrosterclean })

# creates the task based off of the passed form data (attaches to cookies by name of fields in class)
def submittrack(request):
    if request.method == 'POST':
        trackName = request.POST['trackname']
        selectedNames = request.POST.getlist('usernamelist')
        pub_date=timezone.now()
        tc = Track(track_title = trackName, started_date=pub_date)
        tc.save()
    # involve selected users to task
    for id in selectedNames:
        u = User.objects.get(id=id)
        tkroster = TaskRoster(user_identifier_id = u.id, task_identifier_id = tk.id, task_role = 'labeler')
        tkroster.save()
    return redirect('/basicsite/tasks/') # Redirect after POST    
    
# Load all tools, descending by version number, then display tools page
def tools(request):
    alltools = ToolFile.objects.order_by('-versionnumber')
    return render(request, TOOLPAGETEMPLATE, {'alltools':alltools})

# Loads the upload tool page
def uploadtool(request):
    families = ToolFamily.objects.all()
    form = UploadFileForm(families)
    return render(request, UPLOADTOOLPAGETEMPLATE, {'form':form, 'families':families})

# Handles the upload request, then redirects to the tools page
def receivetool(request):
    # Handle file upload
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        uploaddate=timezone.now()
        originalfilename = str(request.FILES['fileform'])
        originalfilename.replace("tools/", "");
        if request.POST['newfamily'] != '':
            familyname = request.POST['newfamily']
            try:
                # test to see if already exists
                specificfamily = ToolFamily.objects.get(toolfamilyname=familyname)
            except ToolFamily.DoesNotExist:
                # does not exist, create new family
                pub_date=timezone.now()
                specificfamily = ToolFamily(toolfamilyname=familyname, datecreated=pub_date, description=request.POST['familydescription'])
                specificfamily.save()
        else:
            specificfamily = ToolFamily.objects.get(id=request.POST['family'])
        newtf = ToolFile(
            tf = request.FILES['fileform'], 
            tooltitle = request.POST['title'], 
            toolfilename = originalfilename, 
            uploaded = uploaddate,
            description = request.POST['description'],
            purpose = request.POST['purposes'],
            versionnumber = request.POST['versionnumber'],
            family = specificfamily
            )
        newtf.save()
    else:
        form = DocumentForm()
    return redirect('/basicsite/tools/')

# Handles a download request on the tool pages
# This function creates an HTTPResponse with an attachment property set in the header fields so that the client browser knows its a download.
def downloadtool(request, toolfileid):
    conv = int(toolfileid)
    toolfile = ToolFile.objects.get(id=conv)
    if "jpg" in str(toolfile.tf):
        response = HttpResponse(toolfile, content_type='image/jpeg')
        response['Contntent-Disposition'] = 'attachment; filename=' + toolfile.toolfilename
    elif "zip" in str(toolfile.tf):
        response = HttpResponse(toolfile.tf, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=' + toolfile.toolfilename
    return response

# Loads page with just the tools for the Collection category
def collectionsection(request):
    tools = ToolFile.objects.order_by('-versionnumber')
    alltools = []
    for tool in tools:
        if tool.purpose=='1':
            alltools.append(tool)
    return render_to_response(SPECIFICTOOLPAGETEMPLATE, { 'alltools' : alltools, 'pagetitle' : 'Collection Tools'}, context_instance=RequestContext(request))

# Loads page with just the tools for the Checking/Processing category
def checkprocesssection(request):
    tools = ToolFile.objects.order_by('-versionnumber')
    alltools = []
    for tool in tools:
        if tool.purpose=='2':
            alltools.append(tool)
    return render_to_response(SPECIFICTOOLPAGETEMPLATE, { 'alltools' : alltools, 'pagetitle' : 'Checking & Processing Tools'}, context_instance=RequestContext(request))

# Loads page with just the tools for the Labeling category
def labelsection(request):
    tools = ToolFile.objects.order_by('-versionnumber')
    alltools = []
    for tool in tools:
        if tool.purpose=='3':
            alltools.append(tool)
    return render_to_response(SPECIFICTOOLPAGETEMPLATE, { 'alltools' : alltools, 'pagetitle' : 'Labeling Tools'}, context_instance=RequestContext(request))

# Defines the form for the upload tool page
class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    fileform  = forms.FileField(label='Tool File:')
    description = forms.CharField( widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}) )
    purposes = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1', 'Collection',), ('2', 'Check-Processing',), ('3', 'Labeling',)))
    versionnumber = forms.DecimalField(widget=forms.NumberInput)
    family = forms.ChoiceField(widget=forms.RadioSelect)
    familydescription = forms.ChoiceField( widget=forms.Textarea(attrs={'cols': 40, 'rows': 2}))
    newfamily = forms.CharField(max_length=50)
    
    def __init__(self, families, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.fields['family'] = forms.ChoiceField(choices=[ (o.id, o.toolfamilyname) for o in ToolFamily.objects.all()])
        
        
def uploadvideopage(request):
    
    return render_to_response(UPLOADVIDEOPAGETEMPLATE, {}, context_instance=RequestContext(request))

