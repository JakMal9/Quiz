from django.db import models


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
