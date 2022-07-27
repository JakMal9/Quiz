import json
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import AnswerForm, QuizStatsForm
from .models import Question, QuestionAnswer, UserAnswer
from .utils import convert_range_to_datetime, get_users_stats


class UserAnswersView(LoginRequiredMixin, ListView):
    http_method_names: list[str] = ["get", "post"]
    model = UserAnswer
    template_name: str = "user_answers.html"
    context_object_name: str = "user_answers"

    def post(self, request, *args, **kwargs):
        form = QuizStatsForm(request.POST)
        user_answers = self.get_queryset()
        self.object_list = user_answers
        if form.is_valid() and user_answers.exists():
            selected_range = convert_range_to_datetime(
                form.cleaned_data.get("start_date"), form.cleaned_data.get("end_date")
            )
            self.object_list = user_answers.filter(answered_at__range=selected_range)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        if not self.get_queryset().exists():
            return {}
        context = super().get_context_data(**kwargs)
        if kwargs.get("form"):
            context["form"] = kwargs.get("form")
        else:
            answers_date_range = self.object_list.datetimes("answered_at", "day")
            form = QuizStatsForm(
                initial={
                    "start_date": answers_date_range.first(),
                    "end_date": answers_date_range.last(),
                }
            )
            context["form"] = form
        context["username"] = self.request.user.username
        context["user_stats"] = get_users_stats(self.object_list)
        return context

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        user_answers = self.get_queryset()
        if not user_answers.exists():
            messages.success(self.request, "Try to answer some questions first")
            return redirect("questions_list")
        return super().render_to_response(context, **response_kwargs)


class QuestionDetailView(LoginRequiredMixin, DetailView):
    http_method_names: list[str] = ["get"]
    model = Question
    pk_url_kwarg: str = "question_id"
    template_name: str = "question.html"
    context_object_name: str = "question"


class QuestionsListView(LoginRequiredMixin, ListView):
    http_method_names: list[str] = ["get"]
    model = Question
    template_name: str = "questions.html"
    context_object_name: str = "questions"


class VerifyAnswerView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        """We could have data submitted either by AJAX or html form."""
        question_id = kwargs["question_id"]
        try:
            if request.POST:
                form = AnswerForm(request.POST)
            else:
                data = json.loads(request.body)
                form = AnswerForm(data)
            if not form.is_valid():
                return redirect("question_details", question_id)
            answer_id = form.data["answer"]
            question_answers = QuestionAnswer.objects.get(
                question__pk=question_id, answer__pk=answer_id
            )
        except (QuestionAnswer.DoesNotExist, KeyError, ValueError):
            raise Http404()
        res = {"correct": question_answers.correct}
        UserAnswer.objects.create(question_answer=question_answers, author=request.user)
        if request.POST:
            return render(request, "answer.html", {"question_id": question_id, **res})
        return JsonResponse(res)
