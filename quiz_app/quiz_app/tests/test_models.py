import pytest
from django.contrib.auth.models import User

from questions.models import Answer, Question, QuestionsAnswers


@pytest.mark.django_db
def test_user_create():
    User.objects.create_user("john", "johndoe@test.com", "StrongPassword")
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_create_new_question_with_answers(question, answers):
    new_question = Question.objects.create(**question)
    for answer in answers:
        content = answer["content"]
        new_question.answers.create(
            content=content, through_defaults={"correct": content == "Cinderella"}
        )
    assert Question.objects.count() == 1
    assert Answer.objects.count() == QuestionsAnswers.objects.count() == 4
    question = Question.objects.first()
    assert question.answers.count() == 4
    correct_answer = question.answers.filter(questionsanswers__correct=True)
    assert len(correct_answer) == 1
    assert correct_answer[0].content == "Cinderella"
