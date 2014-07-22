# Create your views here.
from django.shortcuts import render
#from django.template import RequestContext

import os.path


# Path to basicsite
currentLocation = os.getcwd().replace("\\","/")  + "/basicsite/"

def index(request):
    return render(request,currentLocation + 'templates/loginpage.html')
	
def tasks(request):
    return render(request,currentLocation + 'templates/tasks.html')
	
def timeline(request):
    return render(request,currentLocation + 'templates/timeline.html')