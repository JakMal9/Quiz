from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.questions_list, name="questions_list"),
    path("user/answers/", views.user_answers, name="user_answers"),
    path("<int:question_id>/", views.question_details, name="question_details"),
    path("<int:question_id>/answer/", views.correct_answer, name="correct_answer"),
    path(
        "<int:question_id>/answer/check",
        TemplateView.as_view(template_name="answer.html"),
    ),
]
