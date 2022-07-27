import pytest
from questions.models import UserAnswer
from questions.utils import get_users_stats


@pytest.mark.django_db
def test_get_user_stats(user_answers: UserAnswer) -> None:
    answers = UserAnswer.objects.all()
    stats = get_users_stats(answers=answers)
    assert stats.total_number == 4
    assert stats.correct == 1
    assert stats.incorrect == 3
    assert stats.correct_percent == 25
    assert stats.incorrect_percent == 75
