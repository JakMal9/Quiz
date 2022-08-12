import datetime
import json
from dataclasses import dataclass

from django.db.models import QuerySet
from django.http import Http404, HttpRequest
from questions.forms import AnswerForm
from questions.models import QuestionAnswer


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


def get_question_answer(request: HttpRequest, question_id: int) -> QuestionAnswer:
    try:
        if request.POST:
            form = AnswerForm(request.POST)
        else:
            data = json.loads(request.body)
            form = AnswerForm(data)
        if not form.is_valid():
            raise Http404()
        answer_id = form.data["answer"]
        question_answer = QuestionAnswer.objects.get(
            question__pk=question_id, answer__pk=answer_id
        )
        return question_answer
    except (QuestionAnswer.DoesNotExist, KeyError, ValueError):
        raise Http404()
