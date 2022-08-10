from django.urls import path

from . import views
from questions.views import QuestionDetailView

urlpatterns = [
    path("", views.StartQuizView.as_view(), name="start_quiz"),
    path("<int:quiz_id>/question/<int:question_id>/", QuestionDetailView.as_view(), name="quiz_question")
]