import json
from turtle import pd

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .models import Question, QuestionAnswer


def questions_list(request):
    questions = Question.objects.all()
    return render(request, "./questions.html", {"questions": questions})


def question_details(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "question.html", {"question": question})


@require_POST
def correct_answer(request, question_id):
    """We could have data submitted either by AJAX or html form."""
    try:
        if request.POST:
            answer_id = request.POST["answer"]
        else:
            data = json.loads(request.body)
            answer_id = data["answer"]
        question_answers = QuestionAnswer.objects.get(
            question__pk=question_id, answer__pk=answer_id
        )
    except (QuestionAnswer.DoesNotExist, KeyError, ValueError):
        raise Http404()
    res = {"correct": question_answers.correct}
    if request.POST:
        return render(request, "answer.html", {"question_id": question_id, **res})
    return JsonResponse(res)
