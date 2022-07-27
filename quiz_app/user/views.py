from typing import Any

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView


class UserLoginView(SuccessMessageMixin, LoginView):
    template_name: str = "login.html"
    next_page: str = reverse_lazy("questions_list")
    success_message: str = "Successfully logged in"


class UserLogoutView(LogoutView):
    http_method_names: list[str] = ["get"]
    success_message: str = "Successfully logged out"
    next_page: str = "/auth/login/"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            messages.success(request, self.success_message)
        return super().dispatch(request, *args, **kwargs)


class UserRegisterView(SuccessMessageMixin, CreateView):
    template_name: str = "register.html"
    success_url: str = "/auth/login/"
    success_message: str = "Successfully created new user"
    form_class = UserCreationForm
