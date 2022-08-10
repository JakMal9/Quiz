import pytest

from django.test import Client
from questions.models import Question
from quizzes.models import Quiz

@pytest.mark.django_db
def test_start_quiz_view_correct(authenticated_client: Client, multiple_questions: None) -> None:
    res_get = authenticated_client.get("/quizzes/")
    assert res_get.status_code == 200
    res_post = authenticated_client.post("/quizzes/", {"num_of_questions": 10})
    quizzes = Quiz.objects.all()
    assert quizzes.count() == 1
    questions = quizzes.first().questions.all()
    assert questions.count() == 10
    assert res_post.status_code == 302
    assert res_post.url == f"/quizzes/{quizzes.first().pk}/question/{questions.first().pk}/"


@pytest.mark.parametrize("method", ["put", "patch", "delete"])
def test_start_quiz_view_method_not_allowed(
    authenticated_client: Client, method: str
) -> None:
    res = getattr(authenticated_client, method)("/quizzes/")
    assert res.status_code == 405


@pytest.mark.django_db
def test_start_quiz_view_too_many_questions(authenticated_client: Client, multiple_questions: None) -> None:
    questions_count = Question.objects.all().count()
    res = authenticated_client.post("/quizzes/", {"num_of_questions": questions_count + 10})
    assert res.status_code == 200
    assert f"Not enough questions in db. Max number of questions: {questions_count}" in res.content.decode('utf-8')
