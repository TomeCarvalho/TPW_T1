from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_protect
from .forms import SignUpForm


# Create your views here.
def index(request):
    params = {"logged": request.user.is_authenticated}
    return render(request, 'layout.html', params)


@csrf_protect
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(index)
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
