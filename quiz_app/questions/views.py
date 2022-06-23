import json

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Answer, Question, QuestionsAnswers


def questions_list(request):
    questions = Question.objects.all()
    return render(request, "./questions.html", {"questions": questions})


def question_details(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "question.html", {"question": question})


@require_POST
def correct_answer(request, question_id):
    try:
        data = json.loads(request.body)
        answer_id = data["answer"]
        question_answers = QuestionsAnswers.objects.get(
            question__pk=question_id, answer__pk=answer_id
        )
    except (KeyError, QuestionsAnswers.DoesNotExist, ValueError):
        raise Http404()
    return JsonResponse({"correct": question_answers.correct})
