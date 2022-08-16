from django.contrib.auth.models import User
from django.http import Http404
from questions.models import Question, UserAnswer

from .models import Quiz


def get_quiz_and_question(quiz_id: int, question_id: int) -> tuple[Quiz, Question]:
    try:
        quiz = Quiz.objects.get(pk=quiz_id)
        question = quiz.questions.get(pk=question_id)
    except (Quiz.DoesNotExist, Question.DoesNotExist):
        raise Http404()
    return quiz, question


def get_remaining_quiz_questions(user: User, quiz: Quiz, question_id: int) -> list:
    questions_to_exclude = [question_id]
    answered_questions = UserAnswer.objects.filter(author=user, quiz=quiz).values(
        "question_answer__question"
    )
    if answered_questions.exists():
        questions_to_exclude.extend(
            [question["question_answer__question"] for question in answered_questions]
        )
    return [
        question.pk
        for question in quiz.questions.exclude(pk__in=questions_to_exclude).all()
    ]
