from django import forms
from .models import Assignment, Course, ExamRoutine, Event, FeeDue, CustomUser, Submission
from django.utils import timezone
from datetime import date

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('file',)

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'subject', 'due_date', 'semester', 'file')
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

        def clean_due_date(self):
            due_date = self.cleaned_data.get('due_date')
            if due_date and due_date < date.today():
                raise forms.ValidationError("Due date cannot be in the past.")
            return due_date

class SemesterSelectionForm(forms.Form):
    semester = forms.IntegerField(min_value=1, max_value=8, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Semester (1-8)'}))
    section = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Section'}))

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        # fields = ('name', 'faculty', 'available_seats')
        fields = ['name', 'description', 'duration', 'location', 'available_seats']
        
class ExamRoutineForm(forms.ModelForm):
    class Meta:
        model = ExamRoutine
        fields = ('semester', 'title', 'start_date', 'end_date', 'details', 'file')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Semester (1-8)'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Routine Title'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter Description'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].required = True
        self.fields['end_date'].required = True
        self.fields['title'].required = True
        self.fields['semester'].required = True
        self.fields['file'].required = True

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("End date cannot be before start date.")
        return cleaned_data


class NotificationForm(forms.Form):
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)
    RECIPIENT_CHOICES = [
        ('specific', 'Specific Users'),
        ('specific_semester', 'Specific Semester'),
        ('all_students', 'All Students'),
        ('all_students_teachers', 'All Students & Teachers'),
    ]
    recipient_type = forms.ChoiceField(choices=RECIPIENT_CHOICES, widget=forms.RadioSelect, initial='specific')
    recipients = forms.ModelMultipleChoiceField(queryset=CustomUser.objects.filter(role='student'),
                                  widget=forms.CheckboxSelectMultiple, required=False)
    semester = forms.IntegerField(min_value=1, max_value=8, required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Semester (1-8)'}))

class UpdateSeatsForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all())
    available_seats = forms.IntegerField(min_value=0)

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'description', 'date', 'type')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class FeeDueForm(forms.ModelForm):
    class Meta:
        model = FeeDue
        fields = ('student', 'amount', 'due_date')
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < date.today():
            raise forms.ValidationError("Due date cannot be in the past.")
        return due_date