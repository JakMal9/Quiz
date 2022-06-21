from django.urls import path

from . import views

urlpatterns = [
    path("", views.questions_list, name="questions_list"),
    path("<int:question_id>/", views.question_details, name="question_details"),
    path("<int:question_id>/answer/", views.correct_answer, name="correct_answer"),
]
