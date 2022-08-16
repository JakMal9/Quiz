import datetime
from typing import Generator
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth.models import User
from questions.models import Answer, Question, QuestionAnswer, UserAnswer
from quizzes.models import Quiz


@pytest.mark.django_db
def test_user_create():
    User.objects.create_user("john", "johndoe@test.com", "StrongPassword")
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_create_new_question_with_answers(
    question: dict[str, str], answers: list[dict]
) -> None:
    new_question = Question.objects.create(**question)
    for answer in answers:
        content = answer["content"]
        new_question.answers.create(
            content=content, through_defaults={"correct": content == "Cinderella"}
        )
    assert Question.objects.count() == 1
    assert Answer.objects.count() == QuestionAnswer.objects.count() == 4
    question_db = Question.objects.first()
    assert question_db.answers.count() == 4
    correct_answer = question_db.answers.filter(questionanswer__correct=True)
    assert len(correct_answer) == 1
    assert correct_answer[0].content == "Cinderella"


@pytest.mark.django_db
def test_create_user_answer(
    question_with_answers: QuestionAnswer,
    registered_user: User,
    fake_now: datetime.datetime,
    patch_datetime_now: Generator,
) -> None:
    question_answer = QuestionAnswer.objects.first()
    user = User.objects.first()
    UserAnswer.objects.create(author=user, question_answer=question_answer)
    user_answer = UserAnswer.objects.first()
    assert user_answer.author == user
    assert user_answer.question_answer == question_answer
    assert user_answer.answered_at == fake_now


@pytest.mark.django_db
def test_create_user_answer_different_dates(
    question_with_answers: QuestionAnswer,
    registered_user: User,
) -> None:
    question_answer = QuestionAnswer.objects.first()
    user = User.objects.first()
    quiz = Quiz.objects.create()
    quiz.questions.add(question_answer.question)
    UserAnswer.objects.create(author=user, question_answer=question_answer, quiz=quiz)
    past_date = datetime.datetime.now() - datetime.timedelta(days=7)
    with patch("django.utils.timezone.now", Mock(return_value=past_date)):
        UserAnswer.objects.create(author=user, question_answer=question_answer)
    date_range = UserAnswer.objects.datetimes("answered_at", "day")
    assert date_range.count() == 2
    assert UserAnswer.objects.filter(quiz=quiz).count() == 1


@pytest.mark.django_db
def test_create_user_answer_queryset_methods(
    question_with_answers: QuestionAnswer,
    registered_user: User,
) -> None:
    question_answers = QuestionAnswer.objects.all()
    user = User.objects.first()
    for question_answer in question_answers:
        UserAnswer.objects.create(author=user, question_answer=question_answer)
    assert UserAnswer.objects.are_correct() == 1
    assert UserAnswer.objects.are_incorrect() == 3


@pytest.mark.django_db
def test_create_quiz(question_with_answers: QuestionAnswer) -> None:
    question = Question.objects.first()
    new_quiz = Quiz.objects.create()
    new_quiz.questions.add(question)
    quizzes = Quiz.objects.all()
    assert quizzes.count() == 1
    assert quizzes.first().questions.first() == question
