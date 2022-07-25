from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.QuestionsListView.as_view(), name="questions_list"),
    path(
        "<int:question_id>/",
        views.QuestionDetailView.as_view(),
        name="question_details",
    ),
    path(
        "<int:question_id>/answer/",
        views.VerifyAnswerView.as_view(),
        name="correct_answer",
    ),
    path(
        "<int:question_id>/answer/check",
        TemplateView.as_view(template_name="answer.html"),
    ),
]
