""" 
Forms for songrank.
"""
from django import forms
from datetime import date
from songrank.models import SongComment, ChopperComment


class ReschedulePipelineForm(forms.Form):
    """ 
    Form to reschedule a pipeline.
    """
    new_due_date = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control'}))

class CommentForm(forms.Form):
    """ 
    Form for a comment.
    """
    comment = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control"}))
    
    def add_song_comment(self, song, member):
        """ 
        Adds a new song comment.
        """
        return SongComment.objects.create(
            comment=self.cleaned_data['comment'],
            song=song,
            member=member,
            date=date.today()
        )
    
    def add_chopper_comment(self, chopper, member):
        """ 
        Adds a new chopper comment.
        """
        return ChopperComment.objects.create(
            comment=self.cleaned_data['comment'],
            chopper=chopper,
            commenter=member,
            date=date.today()
        )

