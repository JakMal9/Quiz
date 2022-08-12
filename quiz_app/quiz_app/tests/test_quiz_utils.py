import pytest
from django.contrib.auth.models import User
from questions.models import QuestionAnswer, UserAnswer
from quizzes.models import Quiz
from quizzes.utils import get_quiz_and_question, get_remaining_quiz_questions


@pytest.mark.django_db
def test_get_quiz_and_question(small_quiz: Quiz) -> None:
    first_question = small_quiz.questions.first()
    current_quiz, current_question = get_quiz_and_question(
        small_quiz.pk, first_question.pk
    )
    assert current_quiz == small_quiz
    assert current_question == first_question


@pytest.mark.django_db
def test_get_remaining_quiz_questions_first_question(
    small_quiz: Quiz, registered_user: User
) -> None:
    first_question = small_quiz.questions.first()
    questions_left = get_remaining_quiz_questions(
        registered_user, small_quiz, first_question.pk
    )
    assert len(questions_left) == small_quiz.questions.count() - 1
    assert first_question.pk not in questions_left


@pytest.mark.django_db
def test_get_remaining_quiz_questions_last_question(
    small_quiz: Quiz, registered_user: User
) -> None:
    quiz_questions = [question.pk for question in small_quiz.questions.all()]
    for question in quiz_questions[:-1]:
        question_answer = QuestionAnswer.objects.filter(question=question).first()
        UserAnswer.objects.create(
            author=registered_user, quiz=small_quiz, question_answer=question_answer
        )
    questions_left = get_remaining_quiz_questions(
        registered_user, small_quiz, quiz_questions[-1]
    )
    assert len(questions_left) == 0
