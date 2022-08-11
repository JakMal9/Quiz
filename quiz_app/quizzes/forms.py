from django import forms
from django.core.exceptions import ValidationError
from questions.models import Question


class StartQuizForm(forms.Form):
    num_of_questions = forms.IntegerField(label="Number of questions")

    def clean_num_of_questions(self):
        data = self.cleaned_data["num_of_questions"]
        questions_in_db = Question.objects.count()
        if data > questions_in_db:
            raise ValidationError(
                ("Not enough questions in db. Max number of questions: %(value)s"),
                params={"value": questions_in_db},
            )
        return data
