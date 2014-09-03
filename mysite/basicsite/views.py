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
# Views.py defines the functions and classes that construct the templates into rendered web pages
# Author: Michael Zuccarino
# Date: 9.2.2014
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
    try:
        userexists = request.session['userexists']
    except:
        userexists = 'notsubmitted'
    return render(request, LOGINPAGETEMPLATE, {'userexists':userexists})
    
def createNewUser(request):
    username = request.POST['username']
    email = request.POST['email']
    passw = request.POST['pwd']
    try:
        u = User.objects.get(user_name=username)
        request.session['userexists'] = 'yes'
        return redirect('/basicsite/login/')
    except:
        u = User(user_name=username,password=passw,rights='user')
        u.save()
        request.session['userexists'] = 'no'
        request.session['user'] = u.user_name
        return redirect('/basicsite/home/')

def logWithUser(request):
    username = request.POST['username']
    passw = request.POST['pwd']
    try:
        u = User.objects.get(user_name=username,password=passw)
        request.session['user'] = u.user_name
        request.session['userexists'] = 'oklogin'
        return redirect('/basicsite/home/')
    except:
        request.session['userexists'] = 'incorrectlogin'
        return redirect('/basicsite/login/')
        
    
# Defines the Login Form data for validation
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField()
    
# Load all tools, descending by version number, then display tools page
def showAllTools(request):
    alltools = ToolFile.objects.order_by('-versionnumber')
    request.session['currenttoolpage'] = '/basicsite/tools/'
    return render(request, TOOLPAGETEMPLATE, {'alltools':alltools})

# Loads the upload tool page
def loadUploadToolPage(request):
    families = ToolFamily.objects.all()
    form = UploadFileForm(families)
    return render(request, UPLOADTOOLPAGETEMPLATE, {'form':form, 'families':families})

# Handles the upload request, then redirects to the tools page
def uploadTool(request):
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
def downloadTool(request, toolfileid):
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
def showCollectionTools(request):
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
def showCheckingProcessingTools(request):
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
def showLabelingTools(request):
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

# Form that contains all the fields necessary for a video upload, (does not contain the multiple file upload)
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
        
# Returns the video event upload page
def showUploadVideoPage(request):
    uploadform = UploadVideoForm()
    return render_to_response(UPLOADVIDEOPAGETEMPLATE, { 'uploadform':uploadform }, context_instance=RequestContext(request))
    
# Receives the form post from the video upload page. Creates the video event, writes the uploaded files, then creates a zip containing all the video files
def uploadVideos(request):
    fileList = request.FILES.getlist('files')
    uploadeventtitle = request.POST['videotitle']
    pathtouploadeventfolder = CURRENTLOCATION + '/videos/' + uploadeventtitle
    os.mkdir(pathtouploadeventfolder)
    u = User.objects.get(user_name=request.session['user'])
    ev = Event(name=uploadeventtitle, description=request.POST['description'],event_date=timezone.now(), uploader_id=u.id)
    ev.save()
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
    
# Loads and returns tool family page based on what family id is passed in the url
def showToolFamily(request, familyid):
    conv_id = int(familyid)
    everytool = ToolFile.objects.order_by('-versionnumber')
    alltools = []
    for tool in everytool:
        if tool.family_id == conv_id:
            toolfamily = ToolFamily.objects.get(id=conv_id)
            familyname = toolfamily.toolfamilyname
            alltools.append(tool)
    return render_to_response(SPECIFICFAMILYPAGETEMPLATE, {'alltools':alltools, 'familyname':familyname}, context_instance=RequestContext(request))

# Delets tool object from database
def deleteTool(request, toolid):
    tool = ToolFile.objects.get(id=toolid)
    tool.delete()    
    alltools = ToolFile.objects.order_by('-versionnumber')
    return redirect(request.session['currenttoolpage'])

# Delete tool objects from filesystem when the corresponding object in the database is removed
@receiver(models.signals.post_delete, sender=ToolFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.tf:
        if os.path.isfile(instance.tf.path):
            os.remove(instance.tf.path)
            
# Loads and returns a page displaying the version log for the latest tool in the family identified by the number passed in the url
def viewFamilyVersionLog(request, familyid):
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
    return render_to_response(VIEWVERSIONLOGPAGETEMPLATE, {'latestTool':latestTool, 'versionlog':versionlog}, context_instance=RequestContext(request))
    
# Loads and a returns a page of every event and corresponding list of videos
def showAllVideos(request):
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
    now = timezone.now()
    return render_to_response(VIDEOSPAGETEMPLATE, {'allvideos':allvideos, 'finalListMajor':finalListMajor,'now':now}, context_instance=RequestContext(request))

# Loads a page that displays all video events in order of upload date descending
def showAllEvents(request):
    allevents = Event.objects.order_by('-event_date')
    return render_to_response(VIDEOFILTERPAGETEMPLATE, {'allevents':allevents}, context_instance=RequestContext(request))
    
# Returns a http response that lets the user download a single video
def downloadVideo(request, videonumber, event_id):
    video = Video.objects.get(video_number=videonumber,event_id=event_id)
    event = Event.objects.get(id=video.event_id)
    pathtovideo = CURRENTLOCATION + '/videos/' + event.name + '/' + str(video.video_number) + '.zip'
    video_handle = open(pathtovideo, 'rb')
    response = HttpResponse(video_handle, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + str(video.video_number)
    return response
    
# Returns an http response that lets the user download all the videos in an event
def downloadEvent(request, event_id):
    allvideos = Video.objects.all()
    event_id = int(event_id)
    ev = Event.objects.get(id=event_id)
    pathtouploadeventfolder = CURRENTLOCATION + 'videos/' + ev.name
    zip_filename = pathtouploadeventfolder + '/' + ev.name + '.zip'
    event_handle = open(zip_filename, 'rb')
    response = HttpResponse(event_handle, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + ev.name + '.zip'
    return response

# Adds a single video to a specific event
def addVideoToEventPage(request, event_id):
    event_id = int(event_id)
    ev = Event.objects.get(id=event_id)
    form = AddToEventForm()
    return render_to_response(ADDTOEVENTPAGETEMPLATE, {'form':form, 'event':ev}, context_instance=RequestContext(request))

# Form that contains tool fields for adding a video to event. Multiple file input handled separately.
class AddToEventForm(forms.Form):
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
        
# Receives the single video add to
def uploadAddToVideo(request, event_id):
    event_id = int(event_id)
    fileList = request.FILES.getlist('files')
    u = User.objects.get(user_name=request.session['user'])
    ev = Event.objects.get(id=event_id)
    pathtouploadeventfolder = CURRENTLOCATION + 'videos/' + ev.name
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
    
# Loads all the videos associated with a specific event
def showSpecificEvent(request, event_id):
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
    now = timezone.now()
    return render_to_response(SPECIFICEVENTPAGETEMPLATE, {'event':ev, 'eventvideos':eventvideos,'now':now}, context_instance=RequestContext(request))

# Home page
def showHomePage(request):
    u = request.session['user']
    user = User.objects.get(user_name=u)
    request.session['messageboard'] = 'closed'
    return render_to_response(HOMEPAGETEMPLATE, {'user':user}, context_instance=RequestContext(request))
    
# Returns a page with a list of all the pipelines created
def showAllPipelines(request):
    allpipelines = Pipeline.objects.all()
    now = timezone.now()
    request.session['messageboard'] = 'closed'
    return render_to_response(ALLPIPELINESPAGETEMPLATE, {'allpipelines':allpipelines, 'now':now}, context_instance=RequestContext(request))
    
# Loads the page to create a pipeline
def constructPipeline(request):
    form = ConstructPipelineForm()
    return render_to_response(CONSTRUCTPIPELINEPAGETEMPLATE, {'form':form}, context_instance=RequestContext(request))

# Create pipeline form    
class ConstructPipelineForm(forms.Form):
    title = forms.CharField(max_length=30)
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}))
    
# Returns a page that contains four different ways to filter everything related to a pipeline
def showPipelineFilterPage(request):
    alltracks = Track.objects.all()
    statuslist = []
    for track in alltracks:
        if track.status not in statuslist:
            statuslist.append(track.status)
    allusers  = User.objects.all()
    statusform = StatusForm()
    userform = UserForm()
    videoform = VideoForm()
    toolsform = ToolsForm()
    return render_to_response(PIPELINEFILTERPAGETEMPLATE, {'statuslist':statuslist,'statusform':statusform, 'allusers':allusers,'userform':userform,'videoform':videoform,'toolsform':toolsform}, context_instance=RequestContext(request))
    
# Form to filter through tasks by status
class StatusForm(forms.Form):
    statusfield = forms.CharField(max_length=30)
    
# Form to search for everything related to a user
class UserForm(forms.Form):
    userfield = forms.CharField(max_length=30)

# Form used to search for a video (needed: search for tasks related to video)
class VideoForm(forms.Form):
    videofield = forms.CharField(max_length=30)
    
# Form used to search all pipelines that use a certain tool
class ToolsForm(forms.Form):
    tools = forms.ChoiceField(widget=forms.RadioSelect)
    
    def __init__(self, *args, **kwargs):
        super(ToolsForm, self).__init__(*args, **kwargs)
        alltools = ToolFile.objects.order_by('-versionnumber')
        self.fields['tools'] = forms.ChoiceField(widget=forms.RadioSelect, choices=[ (o.id, o.tooltitle + ' ->   v' + str(o.versionnumber) ) for o in alltools])

# Searches for a returns all tasks that are of a status
def searchByStatus(request):
    allpipelines = Pipeline.objects.all()
    status2search = request.POST['statusfield']
    alltracks = Track.objects.all()
    trackswithstatus = []
    for pipeline in allpipelines:
        for track in alltracks:
            if track.pipeline_identifier.id == pipeline.id:
                if track.status in status2search:
                    trackswithstatus.append(track)
    finalListMajor = []
    for track in trackswithstatus:
        intermediary = []
        intermediary.append(track)
        v = Video.objects.get(id=track.video_identifier_id)
        intermediary.append(v)
        sorted = v.checkprocesstool.split(",")
        checkprocessminor = []
        for toolid in sorted:
            if toolid != '':
                tool = ToolFile.objects.get(id=toolid)
                checkprocessminor.append(tool)
        intermediary.append(checkprocessminor)
        finalListMajor.append(intermediary)
    now = timezone.now()
    return render_to_response(SEARCHSTATUSPAGETEMPLATE, {'trackswithstatus':trackswithstatus,'status2search':status2search,'finalListMajor':finalListMajor,'now':now}, context_instance=RequestContext(request))

# Searches and returns everything that is related to a user
def searchByUser(request):
    allroster = PipelineRoster.objects.all()
    try:
        u = User.objects.get(user_name=request.POST['userfield'])
        message = 'found'
    except:
        message = 'could not find this particular'
    if message != 'could not find this particular':
        resultingPipelines = []
        for person in allroster:
            tempPipelines = []
            if person.user_identifier.id == u.id:
                p = Pipeline.objects.get(id=person.pipeline_identifier.id)
                resultingPipelines.append(p)
        assignedPipelines = []
        for ap in reversed(resultingPipelines):
            assignedPipelines.append(ap)
        allevents = Event.objects.order_by('-event_date')
        userevents = []
        for event in allevents:
            if event.uploader.id == u.id:
                userevents.append(event)
        allTrackFileEvents = TrackFileEvent.objects.order_by('-uploaded_date')
        userfevents = []
        for filevent in allTrackFileEvents:
            if filevent.uploader.id == u.id:
                userfevents.append(filevent)
        alltrackfiles = TrackFiles.objects.all()
        relatedMajor = []
        for trackfilevent in userfevents:
            trackfiles = []
            for trackfile in alltrackfiles:
                if trackfile.trackfilevent.id == trackfilevent.id:
                    trackfiles.append(trackfile)
            minor = []
            minor.append(trackfilevent)
            minor.append(trackfiles)
            relatedMajor.append(minor)
    now = timezone.now()
    return render_to_response(SEARCHUSERPAGETEMPLATE, {'assignedPipelines':assignedPipelines,'userevents':userevents,'user':u,'now':now,'relatedMajor':relatedMajor}, context_instance=RequestContext(request))

# Searches for and returns the found video
def searchForVideo(request):
    allvideos = Video.objects.all()
    vnum = request.POST['videofield']
    foundvideo = Video()
    for video in allvideos:
        if video.video_number == int(vnum):
            foundvideo = video
            sorted = foundvideo.checkprocesstool.split(",")
            checkprocessminor = []
            for toolid in sorted:
                if toolid != '':
                    tool = ToolFile.objects.get(id=toolid)
                    checkprocessminor.append(tool)
            break
    ev = Event.objects.get(id=foundvideo.event.id)
    now = timezone.now()
    return render_to_response(SEARCHVIDEOPAGETEMPLATE, {'video':foundvideo,'event':ev,'checkprocessminor':checkprocessminor,'now':now}, context_instance=RequestContext(request))

# Searches for the pipelines and videos that are tied to this tool
def searchByTool(request):
    selectedTool = request.POST['tools']
    tool = ToolFile.objects.get(id=int(selectedTool))
    allvideos = Video.objects.order_by('-uploaded_date')
    videosWithTool = []
    for video in allvideos:
        if video.collectiontool.id == tool.id:
            videosWithTool.append(video)
        if selectedTool in video.checkprocesstool:
            videosWithTool.append(video)
    formattedList = []
    for video in videosWithTool:
        sorted = video.checkprocesstool.split(",")
        checkprocessminor = []
        intermediary = []
        for toolid in sorted:
            if toolid != '':
                tool = ToolFile.objects.get(id=toolid)
                checkprocessminor.append(tool)
        intermediary.append(video)
        intermediary.append(checkprocessminor)
        formattedList.append(intermediary)
    allptools= PipelineTools.objects.all()
    matchedtools = []
    for pipelinetool in allptools:
        if pipelinetool.tool_id == tool.id:
            matchedtools.append(pipelinetool)
    relatedpipes = []
    for mt in matchedtools:
        p = Pipeline.objects.get(id=mt.pipeline_id)
        relatedpipes.append(p)
    now = timezone.now()
    return render_to_response(SEARCHTOOLPAGETEMPLATE, {'now':now,'formattedList':formattedList,'relatedpipes':relatedpipes}, context_instance=RequestContext(request))
   
# Returns a list of pipelines the user created and a list that the user is assigned to
def showMyPipelines(request):
    currentuser = request.session['user']
    u = User.objects.get(user_name=currentuser)
    allroster = PipelineRoster.objects.all()
    finalList = []
    for person in allroster:
        intermediary = []
        if person.user_identifier.id == u.id:
            intermediary.append(person)
            p = Pipeline.objects.get(id=person.pipeline_identifier.id)
            intermediary.append(p)
            finalList.append(intermediary)
    allpipelines = Pipeline.objects.all()
    yourcreatedpipes=[]
    for pipe in allpipelines:
        if pipe.creator.id == u.id:
            yourcreatedpipes.append(pipe)
    now = timezone.now()
    request.session['messageboard'] = 'closed'
    return render_to_response(MYPIPELINESPAGETEMPLATE, {'finalList':finalList,'now':now,'yourcreatedpipes':yourcreatedpipes}, context_instance=RequestContext(request))
    
# Creates a new pipeline
def submitPipeline(request):
    title = request.POST['title']
    descript = request.POST['description']
    now = timezone.now()
    u = User.objects.get(user_name=request.session['user'])
    p = Pipeline(pipeline_title=title, description=descript, started_date=timezone.now(),target_date=now,creator=u)
    p.save()
    request.session['messageboard'] = 'closed'
    return redirect('/basicsite/specificpipeline/' + str(p.id) +'/')
    
# Returns a pipeline's specific page
def showSpecificPipeline(request, pipeline_id):
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
            sorted = v.checkprocesstool.split(",")
            checkprocessminor = []
            for toolid in sorted:
                if toolid != '':
                    tool = ToolFile.objects.get(id=toolid)
                    checkprocessminor.append(tool)
            intermediary.append(checkprocessminor)
            finalListMajor.append(intermediary)
    allroster = PipelineRoster.objects.all()
    roster = []
    for person in allroster:
        if person.pipeline_identifier.id == p.id:
            roster.append(person)
    allcomments = CommentPipeline.objects.all()
    comments = []
    for comment in allcomments:
        if comment.pipeline.id == p.id:
            comments.append(comment)
    allpipelinetools = PipelineTools.objects.all()
    labelingtools = []
    for atool in allpipelinetools:
        if atool.pipeline.id == p.id:
            labelingtools.append(atool)
    replybox = ReplyBox()
    p_id = int(p.id)
    form = AddToRosterForm(pipeline_id=p_id)
    pipelinetoolsform = PipelineToolsForm(pipeline_id=p_id)
    messageboard = request.session['messageboard']
    return render_to_response(SPECIFICPIPELINEPAGETEMPLATE, {'pipeline':p,'now':now,'tracks':tracks,'finalListMajor':finalListMajor,'roster':roster,'form':form,'comments':comments,'replybox':replybox,'messageboard':messageboard,'labelingtools':labelingtools,'pipelinetoolsform':pipelinetoolsform}, context_instance=RequestContext(request))
    
# Form to allow users to indicate another tool for use in a pipeline
class PipelineToolsForm(forms.Form):
    tools = forms.ChoiceField(widget=forms.RadioSelect)
    
    def __init__(self, *args, **kwargs):
        self.pipeline_id = kwargs.pop('pipeline_id')
        super(PipelineToolsForm, self).__init__(*args, **kwargs)
        alltools = ToolFile.objects.order_by('-versionnumber')
        allpipelinetools = PipelineTools.objects.all()
        unusedtools = []
        for atool in alltools:
            found = False
            for tool in allpipelinetools:
                if atool.purpose == '3':
                    if atool.id == tool.tool.id:
                        if tool.pipeline.id == int(self.pipeline_id):
                            found = True
            if not found:
                if atool.purpose == '3':
                    unusedtools.append(atool)
        self.fields['tools'] = forms.ChoiceField(widget=forms.RadioSelect, choices=[ (o.id, o.tooltitle + ' ->   v' + str(o.versionnumber) ) for o in unusedtools])
    
# Adds a tool for use within that pipeline
def addToolToPipeline(request):
    selectedTool = request.POST['tools']
    intTool = int(selectedTool)
    t = ToolFile.objects.get(id=intTool)
    currentpipeline = request.session['currentpipeline']
    currentpipeline = int(currentpipeline)
    p = Pipeline.objects.get(id=currentpipeline)
    pt = PipelineTools(tool=t, pipeline=p)
    pt.save()
    return redirect('/basicsite/specificpipeline/' + str(p.id) +'/')
    
# Loads a page which allows a user to select multiple videos to add to a track
def showCreateTrackPage(request):
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
    
# Handles the list of selected tracks to add to pipeline
def createTrackResponse(request):
    pipeline_id = int(request.session['currentpipeline'])
    p = Pipeline.objects.get(id=pipeline_id)
    now = timezone.now()
    stringlist = request.POST['selectedfields']
    list = stringlist.split(",")
    for video_id in list:
        v = Video.objects.get(id=int(video_id))
        tk = Track(pipeline_identifier_id=p.id,video_identifier_id=v.id,status='created',started_date=now)
        tk.save()
    return redirect('/basicsite/specificpipeline/' + str(request.session['currentpipeline']) +'/')
    
# General comment box for the message boards
class ReplyBox(forms.Form):
    commentbox = forms.CharField( widget=forms.Textarea(attrs={'cols': 90, 'rows': 5}) )
    
# Loads the page for a specific track
def showSpecificTrack(request, track_id):
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
    sorted = video.checkprocesstool.split(",")
    checkprocessminor = []
    for toolid in sorted:
        if toolid != '':
            tool = ToolFile.objects.get(id=toolid)
            checkprocessminor.append(tool)
    return render_to_response(SPECIFICTRACKPAGETEMPLATE, {'track':tk,'video':video,'now':now,'replybox':replybox,'comments':comments,'uploadform':uploadform,'relatedMajor':relatedMajor,'checkprocessminor':checkprocessminor}, context_instance=RequestContext(request))
    
# Handles a comment post in a track page
def postTrackComment(request):
    commenttext = request.POST['commentbox']
    if commenttext != '':
        username = request.session['user']
        user = User.objects.get(user_name=username)
        now = timezone.now()
        trackid = int(request.session['currenttrack'])
        trackobject = Track.objects.get(id=trackid)
        comment = CommentTrack(text=commenttext,author=user,posted_date=now,track_id=trackobject.id)
        comment.save()
    return redirect("/basicsite/specifictrack/" + request.session['currenttrack'] +"/")

# Form to allow for additional files to be attached to a track
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
        
# Handles the additional track file upload request
def uploadRelatedFile(request):
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
        
# Download all the files in an upload event on a track
def downloadRelatedEventFiles(request, relatedevent_id):
    relatedevent_id = int(relatedevent_id)
    trackfilevent = TrackFileEvent.objects.get(id=relatedevent_id)
    pathtouploadeventfolder = CURRENTLOCATION + 'relatedfiles/' + trackfilevent.eventname
    zip_filename = pathtouploadeventfolder + '/' + trackfilevent.eventname + '.zip'
    event_handle = open(zip_filename, 'rb')
    response = HttpResponse(event_handle, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + trackfilevent.eventname + '.zip'
    return response

# Download a single file in an upload event
def downloadSingleRelatedEventFile(request, relatedfile_id):
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
       
# Delete an entire upload event for a track
def deleteAllFilesInEvent(request, relatedevent_id):
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
        
# Delete a file for a track, and reform the event zip file
def deleteSingleRelatedFile(request, relatedfile_id):
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
        
# Updates the status of the track
def updateTrackStatus(request):
    currenttrack_id = int(request.session['currenttrack'])
    currenttrack = Track.objects.get(id=currenttrack_id)
    currenttrack.status = request.POST['newstatus']
    currenttrack.save()
    return redirect("/basicsite/specifictrack/" + request.session['currenttrack'] +"/")
        
# Form to handle adding more users to a specific pipeline
class AddToRosterForm(forms.Form):
    users = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())
    role = forms.CharField(max_length=30)
    
    def __init__(self, *args, **kwargs):
        self.pipeline_id = kwargs.pop('pipeline_id')
        super(AddToRosterForm, self).__init__(*args, **kwargs)
        allusers = User.objects.all()
        allroster = PipelineRoster.objects.all()
        relevantPersons = []
        for person in allroster:
            if person.pipeline_identifier.id == int(self.pipeline_id):
                relevantPersons.append(person)
        newArr=[]
        for user in allusers:
            found = False
            for person in relevantPersons: 
               if person.user_identifier.id == user.id:
                   found = True
                   #break
            if not found:
                newArr.append(user)
        self.fields['users'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=[ (o.id, o.user_name ) for o in newArr])
        
# Assign a user to the pipeline (response to the AddToRosterForm)
def assignUserToPipeline(request):
    selectedpeeps = request.POST.getlist('users')
    p_id = request.session['currentpipeline']
    p = Pipeline.objects.get(id=int(p_id))
    for user_id in selectedpeeps:
        u = User.objects.get(id=int(user_id))
        pr = PipelineRoster(user_identifier=u,pipeline_identifier=p,pipeline_role=request.POST['role'])
        pr.save()
    return redirect('/basicsite/specificpipeline/' + str(request.session['currentpipeline']) +'/')
        
# Handles a comment post to the Pipeline Message Board
def postPipelineComment(request):
    commenttext = request.POST['commentbox']
    if commenttext != '':
        username = request.session['user']
        user = User.objects.get(user_name=username)
        now = timezone.now()
        p_id = request.session['currentpipeline']
        p = Pipeline.objects.get(id=int(p_id))
        comment = CommentPipeline(text=commenttext,author=user,posted_date=now,pipeline=p)
        comment.save()
    request.session['messageboard'] = 'open'
    return redirect('/basicsite/specificpipeline/' + str(request.session['currentpipeline']) +'/')
        
# Deletes a video from a specific event, and reforms the event zip
def deleteVideo(request, video_id, event_id):
    video_id = int(video_id)
    event_id = int(event_id)
    ev = Event.objects.get(id=event_id)
    u = User.objects.get(user_name=request.session['user'])
    allvideos = Video.objects.all()
    videos = []
    for video in allvideos:
        if video.event.id == ev.id:
            if video.id == video_id:
                v = video
            else:
                videos.append(video)
    pathtouploadeventfolder = CURRENTLOCATION + 'videos/' + ev.name
    fileinfolder = pathtouploadeventfolder + '/' + str(v.video_number) + '.zip'
    os.remove(fileinfolder)
    v.delete()
    filenames = []
    for video in videos:
        if video.event.id == ev.id:
            filename = pathtouploadeventfolder + '/' + str(video.video_number) + '.zip'
            filenames.append(filename)
    zip_filename = pathtouploadeventfolder + '/' + ev.name + '.zip'
    try:
        os.remove(zip_filename)
        zf = zipfile.ZipFile(zip_filename, 'w')
    except:
        #do nothing
        zf = zipfile.ZipFile(zip_filename, 'w')
    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(ev.name, fname)
        zf.write(fpath, zip_path)
    zf.close()
    return redirect("/basicsite/videos/")
        