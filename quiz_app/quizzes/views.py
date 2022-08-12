import random
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView, FormView, ListView
from questions.models import Question, UserAnswer
from questions.utils import get_question_answer, get_users_stats
from quizzes.utils import get_quiz_and_question, get_remaining_quiz_questions

from .forms import StartQuizForm
from .models import Quiz


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


class QuizQuestionDetailView(LoginRequiredMixin, DetailView):
    http_method_names: list[str] = ["get"]
    model = Question
    pk_url_kwarg: str = "question_id"
    template_name: str = "question.html"
    context_object_name: str = "question"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        current_quiz, current_question = get_quiz_and_question(
            self.kwargs["quiz_id"], self.kwargs["question_id"]
        )
        context = super().get_context_data(**kwargs)
        context["quiz_id"] = current_quiz.pk
        return context


class VerifyQuizAnswerView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        """We could have data submitted either by AJAX or html form."""
        current_quiz, current_question = get_quiz_and_question(
            self.kwargs["quiz_id"], self.kwargs["question_id"]
        )
        questions_left = get_remaining_quiz_questions(
            self.request.user, current_quiz, current_question.pk
        )
        question_answer = get_question_answer(request, current_question.pk)
        UserAnswer.objects.create(
            question_answer=question_answer, quiz=current_quiz, author=request.user
        )
        if len(questions_left) == 0:
            messages.success(
                request,
                "It was the last question. Check your stats and start a new quiz.",
            )
            return redirect("quiz_stats", quiz_id=current_quiz.pk)
        res = {
            "correct": question_answer.correct,
            "quiz_id": current_quiz.pk,
            "next_question": questions_left[0],
        }
        if request.POST:
            return render(
                request,
                "answer.html",
                {"question_id": current_question.pk, **res},
            )
        return JsonResponse(res)


class QuizStatsView(LoginRequiredMixin, ListView):
    http_method_names: list[str] = ["get"]
    model = UserAnswer
    template_name: str = "quiz_stats.html"
    context_object_name: str = "user_answers"

    def get_queryset(self):
        return self.model.objects.filter(
            author=self.request.user, quiz__pk=self.kwargs["quiz_id"]
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["user_stats"] = get_users_stats(self.object_list)
        return context

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        if not self.object_list:
            messages.warning(self.request, "Quiz doesn't exist")
            return redirect("start_quiz")
        return super().render_to_response(context, **response_kwargs)
