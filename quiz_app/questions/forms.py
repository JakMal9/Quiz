from django import forms


class AnswerForm(forms.Form):
    answer = forms.IntegerField()
