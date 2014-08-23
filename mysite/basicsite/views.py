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
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
import zipfile
import StringIO

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
        request.session['user'] = user
        request.session['password'] = password
        
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
    request.session['currenttoolpage'] = '/basicsite/tools/'
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
                specificfamily = ToolFamily(toolfamilyname=familyname, datecreated=pub_date, description=request.POST['familydescription'], category=request.POST['purposes'])
                specificfamily.save()
        else:
            specificfamily = ToolFamily.objects.get(id=request.POST['family'])
        newtf = ToolFile(
            tf = request.FILES['fileform'],
            versionlog = request.FILES['versionform'],
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
    
# Defines the form for the upload tool page
class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    fileform  = forms.FileField(label='Tool File:')
    versionform = forms.FileField(label='Version Log:')
    description = forms.CharField( widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}) )
    purposes = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1', 'Collection',), ('2', 'Check-Processing',), ('3', 'Labeling',)))
    versionnumber = forms.FloatField(widget=forms.NumberInput)
    family = forms.ChoiceField(widget=forms.RadioSelect)
    familydescription = forms.ChoiceField( widget=forms.Textarea(attrs={'cols': 40, 'rows': 2}))
    newfamily = forms.CharField(max_length=50)
    
    def __init__(self, families, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.fields['family'] = forms.ChoiceField(choices=[ (o.id, o.toolfamilyname) for o in ToolFamily.objects.all()])

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
    request.session['currenttoolpage'] = '/basicsite/toolcategories/collection/'
    tools = ToolFile.objects.order_by('-versionnumber')
    try:
        families = ToolFamily.objects.all()
        containsArr = []
        relatedtools = []
        for family in families:
            ranhere='yes'
            if family.category == '1':
                for tool in tools:
                    toolfamid = tool.family_id 
                    famid = family.id
                    if tool.family_id == family.id:
                        if not tool.family_id in containsArr:
                            relatedtools.append(tool)
                            containsArr.append(tool.family_id)
    except:
        relatedtools = []       
    alltools = []
    for tool in tools:
        if tool.purpose=='1':
            alltools.append(tool)
    return render_to_response(SPECIFICTOOLPAGETEMPLATE, { 'alltools' : alltools, 'pagetitle' : 'Collection Tools', 'relatedtools':relatedtools}, context_instance=RequestContext(request))

# Loads page with just the tools for the Checking/Processing category
def checkprocesssection(request):
    request.session['currenttoolpage'] = '/basicsite/toolcategories/checkprocess/'
    tools = ToolFile.objects.order_by('-versionnumber')
    try:
        families = ToolFamily.objects.all()
        containsArr = []
        relatedtools = []
        for family in families:
            ranhere='yes'
            if family.category == '2':
                for tool in tools:
                    toolfamid = tool.family_id 
                    famid = family.id
                    if tool.family_id == family.id:
                        if not tool.family_id in containsArr:
                            relatedtools.append(tool)
                            containsArr.append(tool.family_id)
    except:
        relatedtools = []       
    alltools = []
    for tool in tools:
        if tool.purpose=='2':
            alltools.append(tool)
    return render_to_response(SPECIFICTOOLPAGETEMPLATE, { 'alltools' : alltools, 'pagetitle' : 'Checking & Processing Tools', 'relatedtools':relatedtools}, context_instance=RequestContext(request))

# Loads page with just the tools for the Labeling category
def labelsection(request):
    request.session['currenttoolpage'] = '/basicsite/toolcategories/labeling/'
    tools = ToolFile.objects.order_by('-versionnumber')
    try:
        families = ToolFamily.objects.all()
        containsArr = []
        relatedtools = []
        for family in families:
            ranhere='yes'
            if family.category == '3':
                for tool in tools:
                    toolfamid = tool.family_id 
                    famid = family.id
                    if tool.family_id == family.id:
                        if not tool.family_id in containsArr:
                            relatedtools.append(tool)
                            containsArr.append(tool.family_id)
    except:
        relatedtools = []       
    alltools = []
    for tool in tools:
        if tool.purpose=='3':
            alltools.append(tool)
    return render_to_response(SPECIFICTOOLPAGETEMPLATE, { 'alltools' : alltools, 'pagetitle' : 'Labeling Tools', 'relatedtools':relatedtools}, context_instance=RequestContext(request))

class UploadVideoForm(forms.Form):
    upload_multiple = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1', 'One Giant Zip For Mankind',), ('2', 'One Video Per Zip',),))
    videotitle = forms.CharField(max_length=50)
    collection = forms.ChoiceField(widget=forms.RadioSelect)
    checkprocess = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}))
    
    def __init__(self, *args, **kwargs):
        super(UploadVideoForm, self).__init__(*args, **kwargs)
        alltools = ToolFile.objects.order_by('-versionnumber')
        collectiontools = []
        checkprocesstools = []
        for tool in alltools:
            if tool.purpose == '1':
                collectiontools.append(tool)
            if tool.purpose == '2':
                checkprocesstools.append(tool)
        self.fields['collection'] = forms.ChoiceField(widget=forms.RadioSelect, choices=[ (o.id, o.tooltitle + ' ->   v' + str(o.versionnumber) ) for o in collectiontools])
        self.fields['checkprocess'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), choices=[ (o.id, o.tooltitle + ' ->    v' + str(o.versionnumber) ) for o in checkprocesstools])
        
def uploadvideopage(request):
    uploadform = UploadVideoForm()
    return render_to_response(UPLOADVIDEOPAGETEMPLATE, { 'uploadform':uploadform }, context_instance=RequestContext(request))

def handleuploadrequest(request):
    fileList = request.FILES.getlist('files')
    uploadeventtitle = request.POST['videotitle']
    pathtouploadeventfolder = CURRENTLOCATION + '/videos/' + uploadeventtitle
    os.mkdir(pathtouploadeventfolder)
    u = User.objects.get(user_name=request.session['user'])
    ev = Event(name=uploadeventtitle, description=request.POST['description'],event_date=timezone.now(), uploader_id=u.id)
    ev.save()
    if request.POST['upload_multiple'] == '2':
        for file in fileList:
            videoname = request.POST['videotitle']
            withproperpath = pathtouploadeventfolder + '/' + file.name
            fd = open(withproperpath, 'wb+')  # or 'wb+' for binary file
            for chunk in file.chunks():
                fd.write(chunk)
            fd.close()
            
            selectedcheckprocesslist = ''
            for toolid in request.POST.getlist('checkprocess'):
                selectedcheckprocesslist = str(toolid)  + ',' + selectedcheckprocesslist

            selectedcollect = ToolFile.objects.get(id=request.POST['collection'])

            cleanedvideoname = file.name.replace('.zip', '')

            v = Video(video_number=int(cleanedvideoname), uploaded_date=timezone.now(), collectiontool=selectedcollect, checkprocesstool = selectedcheckprocesslist, event=ev)
            v.save()
        allvideos = Video.objects.all()
        filenames = []
        pathtouploadeventfolder = CURRENTLOCATION + '/videos/' + ev.name
        for video in allvideos:
            if video.event_id == ev.id:
                withproperpath = pathtouploadeventfolder + '/' + str(video.video_number) + '.zip'
                filenames.append(withproperpath)

        zip_filename = pathtouploadeventfolder + '/' + ev.name + '.zip'
        zf = zipfile.ZipFile(zip_filename, 'w')
        for fpath in filenames:
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(ev.name, fname)
            zf.write(fpath, zip_path)
        zf.close()
    return redirect('/basicsite/uploadvideo/')
    
    
def specificfamilypage(request, familyid):
    conv_id = int(familyid)
    everytool = ToolFile.objects.order_by('-versionnumber')
    alltools = []
    for tool in everytool:
        if tool.family_id == conv_id:
            toolfamily = ToolFamily.objects.get(id=conv_id)
            familyname = toolfamily.toolfamilyname
            alltools.append(tool)
    return render_to_response(SPECIFICFAMILYPAGETEMPLATE, {'alltools':alltools, 'familyname':familyname}, context_instance=RequestContext(request))

def deletetool(request, toolid):
    tool = ToolFile.objects.get(id=toolid)
    tool.delete()    
    alltools = ToolFile.objects.order_by('-versionnumber')
    return redirect(request.session['currenttoolpage'])

# Delete files from filesystem when the corresponding object in the database is removed
@receiver(models.signals.post_delete, sender=ToolFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.tf:
        if os.path.isfile(instance.tf.path):
            os.remove(instance.tf.path)
            
def viewversionlog(request, familyid):
    conv_id = int(familyid)
    everytool = ToolFile.objects.order_by('-versionnumber')
    latestTool = ToolFile()
    foundlatest = 'no'
    versionlog = ''
    for tool in everytool:
        if foundlatest == 'no':
            if tool.family_id == conv_id:
                foundlatest = 'yes'
                latestTool = tool
                versionlogfilename = latestTool.versionlog
                versionlog = versionlogfilename.file.read()
              #  versionlog = versionlogfile.read()
    return render_to_response(VIEWVERSIONLOGPAGETEMPLATE, {'latestTool':latestTool, 'versionlog':versionlog}, context_instance=RequestContext(request))
    
def videos(request):
    allvideos = Video.objects.all()
    allevents = Event.objects.order_by("-event_date")
    finalListMajor = []
    for event in allevents:
        finalListMinor = []
        for video in allvideos:
            if video.event_id == event.id:
                sorted = video.checkprocesstool.split(",")
                checkprocessminor = []
                intermediary = []
                for toolid in sorted:
                    if toolid != '':
                        tool = ToolFile.objects.get(id=toolid)
                        checkprocessminor.append(tool)
                intermediary.append(video)
                intermediary.append(checkprocessminor)
                finalListMinor.append(intermediary)
        intermediarymajor = []
        intermediarymajor.append(event)
        intermediarymajor.append(finalListMinor)
        finalListMajor.append(intermediarymajor)
    return render_to_response(VIDEOSPAGETEMPLATE, {'allvideos':allvideos, 'finalListMajor':finalListMajor}, context_instance=RequestContext(request))

def videofilterpage(request):
    return render_to_response(VIDEOFILTERPAGETEMPLATE, {}, context_instance=RequestContext(request))

def videoassigntotaskpage(request):
    return render_to_response(VIDEOASSIGNTOTASKPAGETEMPLATE, {}, context_instance=RequestContext(request))

def videotasks(request):
    return render_to_response(VIDEOTASKSPAGETEMPLATE, {}, context_instance=RequestContext(request))
    
def downloadvideo(request, videonumber, event_id):
    video = Video.objects.get(video_number=videonumber,event_id=event_id)
    event = Event.objects.get(id=video.event_id)
    pathtovideo = CURRENTLOCATION + '/videos/' + event.name + '/' + str(video.video_number) + '.zip'
    video_handle = open(pathtovideo, 'rb')
    response = HttpResponse(video_handle, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + str(video.video_number)
    return response
    
def downloadevent(request, event_id):
    allvideos = Video.objects.all()
    event_id = int(event_id)
    ev = Event.objects.get(id=event_id)
    pathtouploadeventfolder = CURRENTLOCATION + 'videos/' + ev.name
    zip_filename = pathtouploadeventfolder + '/' + ev.name + '.zip'
    event_handle = open(zip_filename, 'rb')
    response = HttpResponse(event_handle, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + ev.name + '.zip'
    return response

def addtoevent(request, event_id):
    event_id = int(event_id)
    ev = Event.objects.get(id=event_id)
    form = AddToEventForm()
    return render_to_response(ADDTOEVENTPAGETEMPLATE, {'form':form, 'event':ev}, context_instance=RequestContext(request))

class AddToEventForm(forms.Form):
    upload_multiple = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1', 'One Giant Zip For Mankind',), ('2', 'One Video Per Zip',),))
    collection = forms.ChoiceField(widget=forms.RadioSelect)
    checkprocess = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())
    
    def __init__(self, *args, **kwargs):
        super(AddToEventForm, self).__init__(*args, **kwargs)
        alltools = ToolFile.objects.order_by('-versionnumber')
        collectiontools = []
        checkprocesstools = []
        for tool in alltools:
            if tool.purpose == '1':
                collectiontools.append(tool)
            if tool.purpose == '2':
                checkprocesstools.append(tool)
        self.fields['collection'] = forms.ChoiceField(widget=forms.RadioSelect, choices=[ (o.id, o.tooltitle + ' ->   v' + str(o.versionnumber) ) for o in collectiontools])
        self.fields['checkprocess'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), choices=[ (o.id, o.tooltitle + ' ->    v' + str(o.versionnumber) ) for o in checkprocesstools])
        
def handleaddtoevent(request, event_id):
    event_id = int(event_id)
    fileList = request.FILES.getlist('files')
    u = User.objects.get(user_name=request.session['user'])
    ev = Event.objects.get(id=event_id)
    pathtouploadeventfolder = CURRENTLOCATION + 'videos/' + ev.name
    if request.POST['upload_multiple'] == '2':
        for file in fileList:
            withproperpath = pathtouploadeventfolder + '/' + file.name
            fd = open(withproperpath, 'wb+')
            for chunk in file.chunks():
                fd.write(chunk)
            fd.close()
            
            selectedcheckprocesslist = ''
            for toolid in request.POST.getlist('checkprocess'):
                selectedcheckprocesslist = str(toolid)  + ',' + selectedcheckprocesslist

            selectedcollect = ToolFile.objects.get(id=request.POST['collection'])

            cleanedvideoname = file.name.replace('.zip', '')

            v = Video(video_number=int(cleanedvideoname), uploaded_date=timezone.now(), collectiontool=selectedcollect, checkprocesstool = selectedcheckprocesslist, event=ev)
            v.save()
        allvideos = Video.objects.all()
        filenames = []
        pathtouploadeventfolder = CURRENTLOCATION + '/videos/' + ev.name
        for video in allvideos:
            if video.event_id == ev.id:
                withproperpath = pathtouploadeventfolder + '/' + str(video.video_number) + '.zip'
                filenames.append(withproperpath)
        zip_filename = pathtouploadeventfolder + '/' + ev.name + '.zip'
        os.remove(zip_filename)
        zf = zipfile.ZipFile(zip_filename, 'w')
        for fpath in filenames:
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(ev.name, fname)
            zf.write(fpath, zip_path)
        zf.close()
    
    return redirect('/basicsite/videos/')