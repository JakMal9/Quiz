import datetime
from typing import Generator

import pytest
from django.contrib.auth.models import User
from questions.models import Answer, Question, QuestionAnswer, UserAnswer


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
