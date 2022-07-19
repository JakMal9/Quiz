from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in")
        return redirect("questions_list")
    form = AuthenticationForm()
    if request.POST:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Successfully logged in")
                return redirect("questions_list")
    context = {"form": form}
    return render(request, "login.html", context)


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect("login")
