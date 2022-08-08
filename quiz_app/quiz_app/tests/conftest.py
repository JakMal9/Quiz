import datetime
from typing import Generator
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth.models import User
from django.test import Client
from questions.models import Question, QuestionAnswer, UserAnswer


@pytest.fixture
def question() -> dict[str, str]:
    return {
        "content": "Which Disney character famously leaves a glass slipper behind at a royal ball?"
    }


@pytest.fixture
def answers() -> list[dict]:
    return [
        {"content": "Pocahontas"},
        {"content": "Sleeping Beauty"},
        {
            "content": "Cinderella",
        },
        {"content": "Elsa"},
    ]


@pytest.fixture
@pytest.mark.django_db
def question_with_answers(question: dict[str, str], answers: list[dict]) -> None:
    new_question = Question.objects.create(**question)
    for answer in answers:
        content = answer["content"]
        new_question.answers.create(
            content=content, through_defaults={"correct": content == "Cinderella"}
        )


@pytest.fixture
@pytest.mark.django_db
def registered_user(django_user_model: User) -> User:
    user = django_user_model.objects.create_user(username="test", password="test")
    return user


@pytest.fixture
def authenticated_client(client: Client, registered_user: User) -> Client:
    client.force_login(registered_user)
    return client


@pytest.fixture
def fake_now() -> datetime.datetime:
    return datetime.datetime(2022, 7, 10, 11, 0, 0, tzinfo=datetime.timezone.utc)


@pytest.fixture
def patch_datetime_now(fake_now) -> Generator:
    with patch("django.utils.timezone.now", Mock(return_value=fake_now)):
        yield


@pytest.fixture
@pytest.mark.django_db
def user_answers(question_with_answers: None, registered_user: User) -> None:
    question_answers = QuestionAnswer.objects.all()
    for question_answer in question_answers:
        UserAnswer.objects.create(
            question_answer=question_answer, author=registered_user
        )
