from django import forms


class AnswerForm(forms.Form):
    answer = forms.IntegerField()


class QuizStatsForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
