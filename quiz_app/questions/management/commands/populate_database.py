from typing import Any, Optional

from django.core.management.base import BaseCommand
from questions.factories import QuestionWithAnswersFactory
from tqdm import tqdm


class Command(BaseCommand):

    help = "Populates database with dummy content."

    def handle(self, *args: Any, **options: Any) -> None:

        self.stdout.write(self.style.SUCCESS("Creating 10 questions with answers"))
        for _ in tqdm(range(10)):
            QuestionWithAnswersFactory.create()
