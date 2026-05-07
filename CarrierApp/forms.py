from django import forms
from CarrierApp.models import Login, Student

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'full_name', 'dob', 'gender', 'district', 'place', 
            'phone', 'email', 'sslc_percentage', 'stream_12th', 
            'twelfth_percentage', 'interest_keywords'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'interest_keywords': forms.TextInput(attrs={'placeholder': 'e.g. Coding, Healthcare, Business'}),
        }

class Registration(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=[('STUDENT', 'Student'), ('COLLEGE_ADMIN', 'College Admin')])

    class Meta:
        model = Login
        fields = ['name', 'username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


