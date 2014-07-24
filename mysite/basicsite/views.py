# Create your views here.
from django.shortcuts import render
from django import forms
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
            user = form.cleaned_data['login']
            password = form.cleaned_data['password']
            
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = LoginForm() # An unbound form

    return render(request, index)
	
def tasks(request):
    return render(request,currentLocation + 'templates/tasks.html')
	
def timeline(request):
    return render(request,currentLocation + 'templates/timeline.html')
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField()