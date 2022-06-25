from django.contrib import admin

from .models import Answer, Question, QuestionAnswer

admin.site.register([Answer, Question, QuestionAnswer])
