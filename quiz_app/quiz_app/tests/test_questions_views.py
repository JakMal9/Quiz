import pytest

from questions.models import Answer, Question, QuestionAnswer


@pytest.mark.django_db
def test_questions_list_view(client, question_with_answers):
    question_db = Question.objects.first()
    res = client.get("/questions/")
    assert res.status_code == 200
    assert question_db.content in res.content.decode("utf-8")


@pytest.mark.django_db
def test_question_details_view(client, question_with_answers):
    question_db = Question.objects.first()
    res = client.get(f"/questions/{question_db.pk}/")
    assert res.status_code == 200
    assert question_db.content in res.content.decode("utf-8")
    for answer in question_db.answers.all():
        assert answer.content in res.content.decode("utf-8")


@pytest.mark.django_db
def test_question_details_view_index_out_of_range(client, question_with_answers):
    question_last_id = Question.objects.last().pk
    res = client.get(f"/questions/{question_last_id + 1}/")
    assert res.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_type", ["multipart/form-data; boundary=BoUnDaRyStRiNg", "application/json"]
)
def test_answer_view(client, question_with_answers, content_type):
    questionanswers_db = QuestionAnswer.objects.all()
    content_type = {"content_type": content_type} if "json" in content_type else {}
    for qa in questionanswers_db:
        payload = {"answer": qa.answer.pk}
        res = client.post(
            f"/questions/{qa.question.pk}/answer/",
            payload,
            **content_type,
        )
        assert res.status_code == 200
        if content_type:
            assert res.json()["correct"] == qa.correct
        else:
            expected_msg = (
                "Success! Your answer is correct!" if qa.correct else "Try again"
            )
            assert expected_msg in res.content.decode("utf-8")


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_answer_view_method_not_allowed(client, method):
    res = getattr(client, method)(f"/questions/1/answer/")
    assert res.status_code == 405


@pytest.mark.django_db
def test_answer_view_index_out_of_range(client, question_with_answers):
    last_question_id = Question.objects.last().pk
    last_answer_id = Answer.objects.last().pk
    out_of_range_q_id = last_question_id + 1
    out_of_range_a_id = last_answer_id + 1
    res = client.post(
        f"/questions/{out_of_range_q_id}/answer/", {"answer": last_answer_id}
    )
    assert res.status_code == 404
    res = client.post(
        f"/questions/{last_question_id}/answer/", {"answer": out_of_range_a_id}
    )
    assert res.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize("answer", ["should not be string", 6.6, ""])
@pytest.mark.parametrize(
    "content_type", ["multipart/form-data; boundary=BoUnDaRyStRiNg", "application/json"]
)
def test_answer_view_incorrect_payload(
    client, question_with_answers, answer, content_type
):
    qa_db = QuestionAnswer.objects.first()
    content_type = {"content_type": content_type} if "json" in content_type else {}
    payload = {"answer": answer}
    res = client.post(
        f"/questions/{qa_db.question.pk}/answer/", payload, **content_type
    )
    assert res.status_code == 302
    assert res.url == f"/questions/{qa_db.question.pk}/"
