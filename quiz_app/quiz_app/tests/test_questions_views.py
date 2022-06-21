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
    questionanswers_db = QuestionsAnswers.objects.filter(correct=True).first()
    res = client.get(f"/questions/{questionanswers_db.question.pk}/answer/")
    assert res.status_code == 200
    assert questionanswers_db.question.content in res.content.decode("utf-8")
    assert questionanswers_db.answer.content in res.content.decode("utf-8")
