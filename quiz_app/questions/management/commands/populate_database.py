from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from questions.factories import QuestionWithAnswersFactory
from tqdm import tqdm


class Command(BaseCommand):

    help = "Populates database with dummy content."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-questions",
            type=int,
            default=10,
            help="Number of questions to be created.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        num_of_questions = options["questions"]
        self.stdout.write(
            self.style.SUCCESS(f"Creating {num_of_questions} questions with answers")
        )
        for _ in tqdm(range(num_of_questions)):
            QuestionWithAnswersFactory.create()
