from django.db import models


class Quiz(models.Model):
    questions = models.ManyToManyField("questions.Question")
