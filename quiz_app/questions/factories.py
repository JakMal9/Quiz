from factory import Faker, Iterator, LazyAttribute, RelatedFactory, SubFactory
from factory.django import DjangoModelFactory

from .models import Answer, Question, QuestionAnswer


class AnswerFactory(DjangoModelFactory):
    class Meta:
        model = Answer
        django_get_or_create = ("content",)

    content = Faker("text", max_nb_chars=20)


class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = Question
        exclude = ("sentence",)
        django_get_or_create = ("content",)

    sentence = Faker("sentence", nb_words=15)
    content = LazyAttribute(lambda obj: obj.sentence.replace(".", "?"))


class QuestionAnswerFactory(DjangoModelFactory):
    class Meta:
        model = QuestionAnswer

    correct = Iterator([False, True, False, False])
    question = SubFactory(QuestionFactory)
    answer = SubFactory(AnswerFactory)


class QuestionWithAnswersFactory(QuestionFactory):
    answer1 = RelatedFactory(
        QuestionAnswerFactory, factory_related_name="question", correct=False
    )
    answer2 = RelatedFactory(
        QuestionAnswerFactory, factory_related_name="question", correct=True
    )
    answer3 = RelatedFactory(
        QuestionAnswerFactory, factory_related_name="question", correct=False
    )
    answer4 = RelatedFactory(
        QuestionAnswerFactory, factory_related_name="question", correct=False
    )
