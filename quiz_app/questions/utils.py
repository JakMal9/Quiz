import datetime
from dataclasses import dataclass

from django.db.models import QuerySet


@dataclass
class UserStats:
    total_number: int = 0
    correct: int = 0
    incorrect: int = 0
    correct_percent: int = 0
    incorrect_percent: int = 0

    def calculate_percentage(self):
        if self.total_number == 0:
            return
        self.correct_percent = round(self.correct * 100 / self.total_number)
        self.incorrect_percent = round(self.incorrect * 100 / self.total_number)


def convert_range_to_datetime(
    start_date: datetime.date, end_date: datetime.date
) -> tuple[datetime.datetime, datetime.datetime]:
    return (
        datetime.datetime.combine(start_date, datetime.time.min),
        datetime.datetime.combine(end_date, datetime.time.max),
    )


def get_users_stats(answers: QuerySet) -> UserStats:
    total_answers = answers.count()
    if not total_answers:
        return UserStats()
    stats = UserStats(
        total_number=total_answers,
        correct=answers.are_correct(),
        incorrect=answers.are_incorrect(),
    )
    stats.calculate_percentage()
    return stats
