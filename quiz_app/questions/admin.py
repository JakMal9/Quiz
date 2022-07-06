from django.contrib import admin

from .models import Answer, Question, QuestionAnswer


class AnswerInline(admin.TabularInline):
    model = Answer


class QuestionAnswerInline(admin.TabularInline):
    model = QuestionAnswer
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    inlines = (QuestionAnswerInline,)


admin.site.register(
    Answer,
)
admin.site.register(Question, QuestionAdmin)
