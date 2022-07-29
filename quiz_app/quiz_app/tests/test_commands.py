from io import StringIO

import pytest
from django.core.management import call_command
from questions.models import Answer, Question, QuestionAnswer


@pytest.mark.django_db
def test_populate_database():
    out = StringIO()
    call_command("populate_database", stdout=out)
    questions = Question.objects.all()
    answers = Answer.objects.all()
    questions_with_answers = QuestionAnswer.objects.all()
    output = out.getvalue()
    assert len(questions) == 10
    assert len(answers) == 40
    assert len(questions_with_answers) == 40
    assert questions_with_answers.filter(correct=True).count() == 10
    assert questions[0].answers.count() == 4
    assert "Creating 10 questions with answers" in output
