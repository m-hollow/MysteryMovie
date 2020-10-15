from django import forms

from .models import Movie, UserMovieDetail

class AddMovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['name', 'year', 'date_watched']
        widgets = {
            'watched': forms.RadioSelect,
        }

class UserMovieDetailForm(forms.ModelForm):
    class Meta:
        model = UserMovieDetail
        fields = ['is_user_movie', 'seen_previously', 'heard_of', 'user_guess', 'star_rating', 'comments']
        widgets = {
            'is_user_movie': forms.RadioSelect,
            'seen_previously': forms.RadioSelect,
            'heard_of': forms.RadioSelect,
            'comments': forms.Textarea(attrs={'rows': 1}),
        }


