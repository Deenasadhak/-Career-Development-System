from django import forms
from CarrierApp.models import Question,Answer


class QuestionForm(forms.ModelForm):
    class Meta:
        model=Question
        fields='__all__'

class AnswerForm(forms.ModelForm):
    class Meta:
        model=Answer
        fields='__all__' 
        widgets={
            "question":forms.Select(attrs={"class":"form-select"}),
            
            
        }      