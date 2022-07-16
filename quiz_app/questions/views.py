import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import AnswerForm
from .models import Question, QuestionAnswer, UserAnswer


@login_required(login_url="/auth/login/")
def questions_list(request: HttpRequest) -> HttpResponse:
    questions = Question.objects.all()
    return render(request, "./questions.html", {"questions": questions})


@login_required(login_url="/auth/login/")
def question_details(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "question.html", {"question": question})


@require_POST
@login_required(login_url="/auth/login/")
def correct_answer(request: HttpRequest, question_id: int) -> HttpResponse:
    """We could have data submitted either by AJAX or html form."""
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


@require_GET
@login_required(login_url="/auth/login/")
def user_answers(request: HttpRequest) -> HttpResponse:
    answers = UserAnswer.objects.filter(author=request.user)
    if answers.count() == 0:
        messages.success(request, "Try to answer some questions first")
        return redirect("questions_list")
    return render(
        request,
        "user_answers.html",
        {"username": answers[0].author.username, "user_answers": answers},
    )
