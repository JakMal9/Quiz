import pytest
from django.contrib.auth.models import User
from django.test import Client

from questions.models import Question


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
