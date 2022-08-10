import random

from django.forms import Form
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import StartQuizForm
from .models import Quiz
from questions.models import Question


class StartQuizView(LoginRequiredMixin, FormView):
    http_method_names: list[str] = ["get", "post"]
    template_name: str = "start_quiz.html"
    form_class: Form = StartQuizForm

    def get_initial(self) -> dict[str, int]:
        return {"num_of_questions": 10}

    def form_valid(self, form: Form):
        num_of_questions = form.cleaned_data["num_of_questions"]
        random_questions = random.sample(list(Question.objects.all()), num_of_questions)
        new_quiz = Quiz.objects.create()
        new_quiz.questions.set(random_questions)
        self.object = new_quiz
        return super().form_valid(form)

    def get_success_url(self) -> str:
        quiz_id = self.object.pk
        first_question_id = self.object.questions.first().pk
        return f"/quizzes/{quiz_id}/question/{first_question_id}/"

