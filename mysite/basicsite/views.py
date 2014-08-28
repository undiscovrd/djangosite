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
from django.forms import widgets
import shutil

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
            return redirect('/basicsite/home/')
            
        username = request.POST.get('username')
        password = request.POST.get('password')
        request.session['user'] = user
        request.session['password'] = password
        
    else:
        form = LoginForm()
    # Renders and displays the login page, passing LoginForm
    return render(request, LOGINPAGETEMPLATE, {'form': form,})
    
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
    allevents = Event.objects.order_by('-event_date')
    return render_to_response(VIDEOFILTERPAGETEMPLATE, {'allevents':allevents}, context_instance=RequestContext(request))

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
    
def specificevent(request, event_id):
    event_id = int(event_id)
    ev = Event.objects.get(id=event_id)
    allvideos = Video.objects.all()
    eventvideos = []
    for video in allvideos:
        if video.event_id == ev.id:
            sorted = video.checkprocesstool.split(",")
            checkprocessminor = []
            intermediary = []
            for toolid in sorted:
                if toolid != '':
                    tool = ToolFile.objects.get(id=toolid)
                    checkprocessminor.append(tool)
            intermediary.append(video)
            intermediary.append(checkprocessminor)
            eventvideos.append(intermediary)
    return render_to_response(SPECIFICEVENTPAGETEMPLATE, {'event':ev, 'eventvideos':eventvideos}, context_instance=RequestContext(request))
    
def home(request):
    u = request.session['user']
    user = User.objects.get(user_name=u)
    return render_to_response(HOMEPAGETEMPLATE, {'user':user}, context_instance=RequestContext(request))
    
def pipelines(request):
    allpipelines = Pipeline.objects.all()
    now = timezone.now()
    return render_to_response(ALLPIPELINESPAGETEMPLATE, {'allpipelines':allpipelines, 'now':now}, context_instance=RequestContext(request))
    
def constructpipeline(request):
    form = ConstructPipelineForm()
    return render_to_response(CONSTRUCTPIPELINEPAGETEMPLATE, {'form':form}, context_instance=RequestContext(request))
    
class ConstructPipelineForm(forms.Form):
    title = forms.CharField(max_length=30)
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}))
    
def pipelinefilterpage(request):
    return render_to_response(PIPELINEFILTERPAGETEMPLATE, {}, context_instance=RequestContext(request))
    
def mypipelines(request):
    return render_to_response(MYPIPELINESPAGETEMPLATE, {}, context_instance=RequestContext(request))
    
def submitpipeline(request):
    title = request.POST['title']
    descript = request.POST['description']
    now = timezone.now()
    u = User.objects.get(user_name=request.session['user'])
    p = Pipeline(pipeline_title=title, description=descript, started_date=timezone.now(),target_date=now,creator=u)
    p.save()
    
    return redirect('/basicsite/pipelines/')
    
def specificpipeline(request, pipeline_id):
    pipeline_id = int(pipeline_id)
    p = Pipeline.objects.get(id=pipeline_id)
    now = timezone.now()
    request.session['currentpipeline']=pipeline_id
    alltracks = Track.objects.all()
    finalListMajor = []
    tracks = []
    videos = []
    for track in alltracks:
        intermediary = []
        if track.pipeline_identifier_id == pipeline_id:
            intermediary.append(track)
            v = Video.objects.get(id=track.video_identifier_id)
            intermediary.append(v)
            finalListMajor.append(intermediary)
    return render_to_response(SPECIFICPIPELINEPAGETEMPLATE, {'pipeline':p,'now':now,'tracks':tracks,'finalListMajor':finalListMajor}, context_instance=RequestContext(request))
 
def createtrack(request):
    pipeline_id = int(request.session['currentpipeline'])
    p = Pipeline.objects.get(id=pipeline_id)
    now = timezone.now()
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
    return render_to_response(CREATETRACKPAGETEMPLATE, {'pipeline':p,'now':now,'finalListMajor':finalListMajor}, context_instance=RequestContext(request))
    
def addtracks(request):
    pipeline_id = int(request.session['currentpipeline'])
    p = Pipeline.objects.get(id=pipeline_id)
    now = timezone.now()
    stringlist = request.POST['selectedfields']
    list = stringlist.split(",")
    for video_id in list:
        v = Video.objects.get(id=int(video_id))
        tk = Track(pipeline_identifier_id=p.id,video_identifier_id=v.id,status='created',started_date=now)
        tk.save()
    
    return redirect('/basicsite/pipelines')
    
class ReplyBox(forms.Form):
    comment1 = forms.CharField( widget=forms.Textarea(attrs={'cols': 90, 'rows': 5}) )
    
def specifictrack(request, track_id):
    request.session['currenttrack'] = track_id
    trackid = int(track_id)
    tk = Track.objects.get(id=trackid)
    video = Video.objects.get(id=tk.video_identifier_id)
    now=timezone.now()
    replybox = ReplyBox()
    allcomments = CommentTrack.objects.all()
    comments = []
    for comment in allcomments:
        if comment.track_id == trackid:
            comments.append(comment)
    uploadform = UploadRelatedFilesEventForm()
    alltrackfilevents = TrackFileEvent.objects.all()
    alltrackfiles = TrackFiles.objects.all()
    trackfilevents = []
    relatedMajor = []
    for trackfilevent in alltrackfilevents:
        strg = trackfilevent.track.id
        if trackfilevent.track.id == trackid:
            trackfilevents.append(trackfilevent)
            trackfiles = []
            for trackfile in alltrackfiles:
                if trackfile.trackfilevent.id == trackfilevent.id:
                    trackfiles.append(trackfile)
            minor = []
            minor.append(trackfilevent)
            minor.append(trackfiles)
            relatedMajor.append(minor)
    return render_to_response(SPECIFICTRACKPAGETEMPLATE, {'track':tk,'video':video,'now':now,'replybox':replybox,'comments':comments,'uploadform':uploadform,'relatedMajor':relatedMajor}, context_instance=RequestContext(request))
    
def posttrackcomment(request):
    commenttext = request.POST['comment1']
    if commenttext != '':
        username = request.session['user']
        user = User.objects.get(user_name=username)
        now = timezone.now()
        trackid = int(request.session['currenttrack'])
        trackobject = Track.objects.get(id=trackid)
        comment = CommentTrack(text=commenttext,author=user,posted_date=now,track_id=trackobject.id)
        comment.save()
    return redirect("/basicsite/specifictrack/" + request.session['currenttrack'] +"/")

class UploadRelatedFilesEventForm(forms.Form):
    eventname = forms.CharField(max_length=200)
    collection = forms.ChoiceField(widget=forms.RadioSelect)
    checkprocess = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}))
    
    def __init__(self, *args, **kwargs):
        super(UploadRelatedFilesEventForm, self).__init__(*args, **kwargs)
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
        
def uploadrelatedfile(request):
    event_name = request.POST['eventname']
    descript = request.POST['description']
    fileList = request.FILES.getlist('selectedfiles')
    u = User.objects.get(user_name=request.session['user'])
    current_track = int(request.session['currenttrack'])
    
    now=timezone.now()
    
    selectedcheckprocesslist = ''
    for toolid in request.POST.getlist('checkprocess'):
        selectedcheckprocesslist = str(toolid)  + ',' + selectedcheckprocesslist
    try:
        selectedcollect = request.POST['collection']
        selectedtools = selectedcheckprocesslist + ',' + str(selectedcollect)
    except:
        selectedtools = ''
    
    currentrack = Track.objects.get(id=int(current_track))
    
    trackevent = TrackFileEvent(eventname=event_name,uploader=u,track=currentrack,description=descript,uploaded_date=now,toolsused=selectedtools)
    trackevent.save()
    pathtouploadeventfolder = CURRENTLOCATION + 'relatedfiles/' + event_name
    os.mkdir(pathtouploadeventfolder)
    filenames = []
    for file in fileList:
        withproperpath = pathtouploadeventfolder + '/' + file.name
        fd = open(withproperpath, 'wb+')
        for chunk in file.chunks():
            fd.write(chunk)
        fd.close()
        trackfile = TrackFiles(filename=file.name,trackfilevent=trackevent,toolsused=selectedtools)
        trackfile.save()
        withproperpath = pathtouploadeventfolder + '/' + str(file.name)
        filenames.append(withproperpath)    
    
    zip_filename = pathtouploadeventfolder + '/' + event_name + '.zip'
    try:
        os.remove(zip_filename)
        zf = zipfile.ZipFile(zip_filename, 'w')
    except:
        #do nothing
        zf = zipfile.ZipFile(zip_filename, 'w')
    
    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(event_name, fname)
        zf.write(fpath, zip_path)
    zf.close()
    
    return redirect("/basicsite/specifictrack/" + request.session['currenttrack'] +"/")
        
def downloadrelatedevent(request, relatedevent_id):
    relatedevent_id = int(relatedevent_id)
    trackfilevent = TrackFileEvent.objects.get(id=relatedevent_id)

    pathtouploadeventfolder = CURRENTLOCATION + 'relatedfiles/' + trackfilevent.eventname
    zip_filename = pathtouploadeventfolder + '/' + trackfilevent.eventname + '.zip'
    
    event_handle = open(zip_filename, 'rb')
    response = HttpResponse(event_handle, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + trackfilevent.eventname + '.zip'
    return response

def downloadrelatedfile(request, relatedfile_id):
    relatedfile_id = int(relatedfile_id)
    trackfile = TrackFiles.objects.get(id=relatedfile_id)
    trackfilevent_id = trackfile.trackfilevent.id
    trackfilevent = TrackFileEvent.objects.get(id=trackfilevent_id)
    
    pathtouploadeventfolder = CURRENTLOCATION + 'relatedfiles/' + trackfilevent.eventname
    zip_filename = pathtouploadeventfolder + '/' + trackfile.filename

    event_handle = open(zip_filename, 'rb')
    response = HttpResponse(event_handle)
    response['Content-Disposition'] = 'attachment; filename=' + trackfile.filename
    return response
       
def deletefilevent(request, relatedevent_id):
    relatedevent_id = int(relatedevent_id)
    trackfilevent = TrackFileEvent.objects.get(id=relatedevent_id)

    pathtouploadeventfolder = CURRENTLOCATION + 'relatedfiles/' + trackfilevent.eventname
    shutil.rmtree(pathtouploadeventfolder)
 
    alltrackfiles = TrackFiles.objects.all()
    for trackfile in alltrackfiles:
        if trackfile.trackfilevent.id == trackfilevent.id:
            trackfile.delete()
    
    trackfilevent.delete()
    
    return redirect("/basicsite/specifictrack/" + request.session['currenttrack'] +"/")
        
def deleterelatedfile(request, relatedfile_id):
    relatedfile_id = int(relatedfile_id)
    trackfile = TrackFiles.objects.get(id=relatedfile_id)
    trackfilevent_id = trackfile.trackfilevent.id
    trackfilevent = TrackFileEvent.objects.get(id=trackfilevent_id)
    
    pathtouploadeventfolder = CURRENTLOCATION + 'relatedfiles/' + trackfilevent.eventname
    fileinfolder = pathtouploadeventfolder + '/' + trackfile.filename
    os.remove(fileinfolder)
    
    trackfile.delete()
    
    alltrackfiles = TrackFiles.objects.all()
    filenames = []
    for trackfile in alltrackfiles:
        if trackfile.trackfilevent.id == trackfilevent.id:
            filename = pathtouploadeventfolder + '/' + trackfile.filename
            filenames.append(filename)
    
    zip_filename = pathtouploadeventfolder + '/' + trackfilevent.eventname + '.zip'
    try:
        os.remove(zip_filename)
        zf = zipfile.ZipFile(zip_filename, 'w')
    except:
        #do nothing
        zf = zipfile.ZipFile(zip_filename, 'w')
    
    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(trackfilevent.eventname, fname)
        zf.write(fpath, zip_path)
    zf.close()
        

    
    return redirect("/basicsite/specifictrack/" + request.session['currenttrack'] +"/")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        