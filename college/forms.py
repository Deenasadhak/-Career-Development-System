from django import forms
from core.models import College, Course, CollegeCourse

class CollegeProfileForm(forms.ModelForm):
    class Meta:
        model = College
        fields = ['name', 'district', 'college_type', 'address', 'website']
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "College name"}),
            "district": forms.TextInput(attrs={"class": "form-control", "placeholder": "District"}),
            "college_type": forms.TextInput(attrs={"class": "form-control", "placeholder": "College Type"}),
            "address": forms.Textarea(attrs={"class": "form-control", "placeholder": "Address", "rows": 3}),
            "website": forms.URLInput(attrs={"class": "form-control", "placeholder": "Website"}),
        }

class CollegeCourseForm(forms.ModelForm):
    class Meta:
        model = CollegeCourse
        fields = ['course', 'total_intake', 'cutoff_general', 'academic_year']
        widgets = {
            "course": forms.Select(attrs={"class": "form-select"}),
            "total_intake": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Total Seats"}),
            "cutoff_general": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Cutoff Mark (0-600)"}),
            "academic_year": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., 2024-2025"}),
        }

    def clean_cutoff_general(self):
        cutoff = self.cleaned_data.get('cutoff_general')
        if cutoff is not None and (cutoff < 0 or cutoff > 600):
            raise forms.ValidationError("Cutoff mark must be between 0 and 600.")
        return cutoff