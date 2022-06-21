from django.contrib import admin

from .models import Answer, Question, QuestionsAnswers

admin.site.register([Answer, Question, QuestionsAnswers])
