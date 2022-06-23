import pytest

from questions.models import Question, QuestionsAnswers


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
def test_answer_view(client, question_with_answers):
    questionanswers_db = QuestionsAnswers.objects.all()
    for qa in questionanswers_db:
        payload = {"answer": qa.answer.pk}
        res = client.post(
            f"/questions/{qa.question.pk}/answer/",
            payload,
            content_type="application/json",
        )
        assert res.status_code == 200
        assert res.json()["correct"] == qa.correct
