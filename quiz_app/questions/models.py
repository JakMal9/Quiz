from django.conf import settings
from django.db import models
from quizzes.models import Quiz


class Answer(models.Model):
    content = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.content


class Question(models.Model):
    content = models.TextField(unique=True)
    answers = models.ManyToManyField(Answer, through="QuestionAnswer")

    def __str__(self):
        return self.content


class QuestionAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question} - {self.answer}, correct: {self.correct}"


class UserAnswerQuerySet(models.QuerySet):
    def are_correct(self):
        return self.filter(question_answer__correct=True).count()

    def are_incorrect(self):
        return self.filter(question_answer__correct=False).count()


class UserAnswer(models.Model):
    answered_at = models.DateTimeField(auto_now_add=True)
    question_answer = models.ForeignKey(QuestionAnswer, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    objects = UserAnswerQuerySet.as_manager()
