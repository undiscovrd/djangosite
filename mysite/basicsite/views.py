# Create your views here.
from django.shortcuts import render
from django.shortcuts import redirect
from django import forms
from models import User
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
            
            return redirect('/basicsite/tasks/') # Redirect after POST
            
        username = request.POST.get('username')
        password = request.POST.get('password')
    else:
        form = LoginForm() # An unbound form

    return render(request, currentLocation + 'templates/loginpage.html', {'form': form,})
	
def tasks(request):
    if request.method == 'POST': # If the form has been submitted...
        # ContactForm was defined in the previous section
        form = ReplyBox(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            user = form.cleaned_data['username']
            password = form.cleaned_data['password']
            request.session['user'] = user
            request.session['password'] = password
            
            return redirect('/basicsite/tasks/') # Redirect after POST
            
        username = request.POST.get('username')
        password = request.POST.get('password')
    else:
        form = ReplyBox() # An unbound form
    
    return render(request,currentLocation + 'templates/tasks.html', {'form': form,})
	
def timeline(request):
    return render(request,currentLocation + 'templates/timeline.html')
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField()
    
def thanks(request):
    user = request.session['user']
    password = request.session['password']
    
    u = User(user_name=user, password=password, rights="user")
    u.save()
    
    return render(request, currentLocation + 'templates/thanks.html', {"username" : user, "password" : password});
    
class ReplyBox(forms.Form):
    comment = forms.CharField( widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}) )