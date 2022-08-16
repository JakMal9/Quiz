from django.urls import path

from . import views

urlpatterns = [
    path("", views.StartQuizView.as_view(), name="start_quiz"),
    path(
        "<int:quiz_id>/question/<int:question_id>/answer/",
        views.VerifyQuizAnswerView.as_view(),
        name="quiz_answer",
    ),
    path(
        "<int:quiz_id>/question/<int:question_id>/",
        views.QuizQuestionDetailView.as_view(),
        name="quiz_question",
    ),
]
