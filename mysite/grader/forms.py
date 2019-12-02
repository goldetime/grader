from django import forms

from .models import Problem
from .models import Testcase

class ProblemForm(forms.ModelForm):
    time_limit = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Хугацааны хязгаарлалт'}
        ),
        help_text='Секунд'
    )

    mem_limit = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Санах ойн хязгаарлалт'}
        ),
        help_text='Mib'
    )
    
    class Meta:
        model = Problem
        fields = ('pid', 'time_limit', 'mem_limit')

class TestcaseForm(forms.ModelForm):
    class Meta:
        model = Testcase
        fields = ('input', 'output')
