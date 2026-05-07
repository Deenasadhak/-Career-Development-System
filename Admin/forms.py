from django import forms
from CarrierApp.models import Question, Answer

class QuestionWithChoicesForm(forms.ModelForm):
    option_a = forms.CharField(max_length=500, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Option A"}))
    option_b = forms.CharField(max_length=500, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Option B"}))
    option_c = forms.CharField(max_length=500, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Option C"}))
    option_d = forms.CharField(max_length=500, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Option D"}))
    
    CORRECT_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    correct_option = forms.ChoiceField(choices=CORRECT_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = Question
        fields = ['question', 'category', 'marks']
        widgets = {
            "question": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter question text here..."}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "marks": forms.NumberInput(attrs={"class": "form-control"}),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = '__all__'
        widgets={
            "question": forms.Select(attrs={"class":"form-select"}),
        }