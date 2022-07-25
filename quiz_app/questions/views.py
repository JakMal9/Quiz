import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import AnswerForm
from .models import Question, QuestionAnswer


class QuestionDetailView(LoginRequiredMixin, DetailView):
    http_method_names: list[str] = ["get"]
    model = Question
    pk_url_kwarg: str = "question_id"
    template_name: str = "single_question.html"
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
        if request.POST:
            return render(request, "answer.html", {"question_id": question_id, **res})
        return JsonResponse(res)
