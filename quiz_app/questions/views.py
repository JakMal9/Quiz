import json

from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AnswerForm
from .models import Question, QuestionAnswer


@login_required(login_url="/auth/login/")
def questions_list(request):
    questions = Question.objects.all()
    return render(request, "./questions.html", {"questions": questions})


@login_required(login_url="/auth/login/")
def question_details(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "question.html", {"question": question})


@require_POST
@login_required(login_url="/auth/login/")
def correct_answer(request, question_id):
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
    if request.POST:
        return render(request, "answer.html", {"question_id": question_id, **res})
    return JsonResponse(res)
