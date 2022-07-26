import datetime
from typing import Generator, Union

import pytest
from django.contrib.messages import get_messages
from django.test import Client
from questions.models import Answer, Question, QuestionAnswer, UserAnswer


@pytest.mark.django_db
def test_questions_list_view(
    authenticated_client: Client, question_with_answers: None
) -> None:
    question_db = Question.objects.first()
    res = authenticated_client.get("/questions/")
    assert res.status_code == 200
    assert question_db.content in res.content.decode("utf-8")


@pytest.mark.django_db
def test_question_details_view(
    authenticated_client: Client, question_with_answers: None
) -> None:
    question_db = Question.objects.first()
    res = authenticated_client.get(f"/questions/{question_db.pk}/")
    assert res.status_code == 200
    assert question_db.content in res.content.decode("utf-8")
    for answer in question_db.answers.all():
        assert answer.content in res.content.decode("utf-8")


@pytest.mark.django_db
def test_question_details_view_index_out_of_range(
    authenticated_client: Client, question_with_answers: None
) -> None:
    question_last_id = Question.objects.last().pk
    res = authenticated_client.get(f"/questions/{question_last_id + 1}/")
    assert res.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_type", ["multipart/form-data; boundary=BoUnDaRyStRiNg", "application/json"]
)
def test_answer_view(
    authenticated_client: Client,
    question_with_answers: None,
    content_type: str,
    fake_now: datetime.datetime,
    patch_datetime_now: Generator,
) -> None:
    questionanswers_db = QuestionAnswer.objects.all()
    user_id = authenticated_client.session["_auth_user_id"]
    content_type_header: dict = (
        {"content_type": content_type} if "json" in content_type else {}
    )
    for qa in questionanswers_db:
        payload = {"answer": qa.answer.pk}
        res = authenticated_client.post(
            f"/questions/{qa.question.pk}/answer/",
            payload,
            **content_type_header,
        )
        assert res.status_code == 200

        # Check if answer was save down for logged in user
        user_answer = UserAnswer.objects.get(question_answer=qa, author__pk=user_id)
        assert user_answer.answered_at == fake_now

        if content_type_header:
            assert res.json()["correct"] == qa.correct
        else:
            expected_msg = (
                "Success! Your answer is correct!" if qa.correct else "Try again"
            )
            assert expected_msg in res.content.decode("utf-8")

    # Check whether all answers were save down logged in user
    assert (
        UserAnswer.objects.filter(author__pk=user_id).count()
        == questionanswers_db.count()
    )


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_answer_view_method_not_allowed(
    authenticated_client: Client, method: str
) -> None:
    res = getattr(authenticated_client, method)("/questions/1/answer/")
    assert res.status_code == 405


@pytest.mark.django_db
def test_answer_view_index_out_of_range(
    authenticated_client: Client, question_with_answers: None
) -> None:
    last_question_id = Question.objects.last().pk
    last_answer_id = Answer.objects.last().pk
    out_of_range_q_id = last_question_id + 1
    out_of_range_a_id = last_answer_id + 1
    res = authenticated_client.post(
        f"/questions/{out_of_range_q_id}/answer/", {"answer": last_answer_id}
    )
    assert res.status_code == 404
    res = authenticated_client.post(
        f"/questions/{last_question_id}/answer/", {"answer": out_of_range_a_id}
    )
    assert res.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize("answer", ["should not be string", 6.6, ""])
@pytest.mark.parametrize(
    "content_type", ["multipart/form-data; boundary=BoUnDaRyStRiNg", "application/json"]
)
def test_answer_view_incorrect_payload(
    authenticated_client: Client,
    question_with_answers: None,
    answer: Union[str, float],
    content_type: str,
) -> None:
    qa_db = QuestionAnswer.objects.first()
    content_type_header: dict = (
        {"content_type": content_type} if "json" in content_type else {}
    )
    payload = {"answer": answer}
    res = authenticated_client.post(
        f"/questions/{qa_db.question.pk}/answer/", payload, **content_type_header
    )
    assert res.status_code == 302
    assert res.url == f"/questions/{qa_db.question.pk}/"


@pytest.mark.django_db
@pytest.mark.parametrize("route", ["/questions/", "/questions/{pk}/"])
def test_question_routes_unauthorized(
    client: Client, question_with_answers: None, route: str
) -> None:
    if "pk" in route:
        question_id = Question.objects.first().pk
        route = route.format(pk=question_id)
    res = client.get(route)
    assert res.status_code == 302
    assert "/auth/login/" in res.url


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_type", ["multipart/form-data; boundary=BoUnDaRyStRiNg", "application/json"]
)
def test_answer_view_unauthorized(
    client: Client, question_with_answers: None, content_type: str
) -> None:
    questionanswers_db = QuestionAnswer.objects.all()
    content_type_header: dict = (
        {"content_type": content_type} if "json" in content_type else {}
    )
    for qa in questionanswers_db:
        payload = {"answer": qa.answer.pk}
        res = client.post(
            f"/questions/{qa.question.pk}/answer/",
            payload,
            **content_type_header,
        )
        assert res.status_code == 302
        assert "/auth/login/" in res.url


@pytest.mark.django_db
def test_user_answers_empty(
    authenticated_client: Client, question_with_answers: None
) -> None:
    res = authenticated_client.get("/questions/user/answers/")
    assert res.status_code == 302
    assert "/questions/" in res.url
    assert (
        get_messages(res.wsgi_request)._queued_messages[0].__dict__["message"]
        == "Try to answer some questions first"
    )


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_user_answers_view_method_not_allowed(
    authenticated_client: Client, method: str
) -> None:
    res = getattr(authenticated_client, method)("/questions/user/answers/")
    assert res.status_code == 405


@pytest.mark.django_db
def test_user_answers_view_unauthorized(client: Client, user_answers: None) -> None:
    res = client.get("/questions/user/answers/")
    assert res.status_code == 302
    assert "/auth/login/" in res.url


@pytest.mark.django_db
def test_user_answers_view_correct(
    authenticated_client: Client, user_answers: None
) -> None:
    res = authenticated_client.get("/questions/user/answers/")
    assert res.status_code == 200
    user_answers_db = UserAnswer.objects.all()
    for answer in user_answers_db:
        assert answer.author.username in res.content.decode("utf-8")
        assert answer.question_answer.question.content in res.content.decode("utf-8")
        assert answer.question_answer.answer.content in res.content.decode("utf-8")
        assert str(answer.question_answer.correct) in res.content.decode("utf-8")
