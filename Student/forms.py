from django import forms
from CarrierApp.models import Student


class Stud_profileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'full_name', 'dob', 'gender', 'district', 'place', 
            'phone', 'email', 'sslc_percentage', 'stream_12th', 
            'twelfth_percentage', 'interest_keywords'
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name"}),
            "dob": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "district": forms.Select(attrs={"class": "form-control"}),
            "place": forms.TextInput(attrs={"class": "form-control", "placeholder": "City/Town"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "sslc_percentage": forms.NumberInput(attrs={"class": "form-control", "placeholder": "SSLC %", "step": "0.1"}),
            "stream_12th": forms.Select(attrs={"class": "form-control"}),
            "twelfth_percentage": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Plus Two %", "step": "0.1"}),
        }
        




# forms.py


class CareerPreferenceForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    education = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    specialization = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    skills = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 
                                                         'placeholder': 'Enter comma-separated skills, e.g. Python, SQL, Communication'}))
    score = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '100'}))