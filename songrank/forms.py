""" 
Forms for songrank.
"""
from django import forms


class ReschedulePipelineForm(forms.Form):
    """ 
    Form to reschedule a pipeline.
    """
    new_due_date = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control'}))
