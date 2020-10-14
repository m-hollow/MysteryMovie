from django import forms

from .models import Movie

class AddMovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['name', 'year', 'date_watched']
        widgets = {
            'watched': forms.RadioSelect,
        }
