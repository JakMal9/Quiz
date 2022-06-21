from django.shortcuts import get_object_or_404, render

from .models import Question, QuestionsAnswers


def questions_list(request):
    questions = Question.objects.all()
    return render(request, "./questions.html", {"questions": questions})


def question_details(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "question.html", {"question": question})


def correct_answer(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question_answers = QuestionsAnswers.objects.filter(
        question=question, correct=True
    ).first()
    return render(request, "answer.html", {"question_answers": question_answers})
