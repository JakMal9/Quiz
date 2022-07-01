import pytest

from questions.models import Question


@pytest.fixture
def question() -> dict[str]:
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
def question_with_answers(question, answers):
    new_question = Question.objects.create(**question)
    for answer in answers:
        content = answer["content"]
        new_question.answers.create(
            content=content, through_defaults={"correct": content == "Cinderella"}
        )
