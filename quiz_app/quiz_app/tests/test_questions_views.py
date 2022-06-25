import pytest

from questions.models import Question, QuestionAnswer


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
