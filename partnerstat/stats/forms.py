from django import forms

from .models import THRESHOLD_CHOICES, STREAM_TYPE_CHOICES

class ViewsSearchForm(forms.Form):
    date_from = forms.DateField(label='From date')
    date_to = forms.DateField(label='To date')
    threshold = forms.ChoiceField(choices=THRESHOLD_CHOICES)
    stream_type = forms.ChoiceField(choices=STREAM_TYPE_CHOICES)