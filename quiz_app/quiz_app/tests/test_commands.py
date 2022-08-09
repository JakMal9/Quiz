from io import StringIO
from typing import Optional

import pytest
from django.core.management import call_command
from questions.models import Answer, Question, QuestionAnswer


@pytest.mark.django_db
@pytest.mark.parametrize(
    "num_of_questions,command", [(10, None), (20, "-q"), (20, "--questions")]
)
def test_populate_database(num_of_questions: int, command: Optional[str]) -> None:
    out = StringIO()
    if num_of_questions == 10:
        call_command("populate_database", stdout=out)
    else:
        call_command("populate_database", f"{command}={num_of_questions}", stdout=out)
    questions = Question.objects.all()
    answers = Answer.objects.all()
    questions_with_answers = QuestionAnswer.objects.all()
    output = out.getvalue()
    assert len(questions) == num_of_questions
    assert len(answers) == num_of_questions * 4
    assert len(questions_with_answers) == num_of_questions * 4
    assert questions_with_answers.filter(correct=True).count() == num_of_questions
    assert questions[0].answers.count() == 4
    assert f"Creating {num_of_questions} questions with answers" in output
