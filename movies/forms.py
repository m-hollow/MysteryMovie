from django import forms

from .models import Movie, UserMovieDetail

# currently, this form isn't really necessary; you could have the CreateView aut-create the form, since you
# don't have any deviations from the default behavior in the form definition.
class AddMovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['name', 'year', 'game_round', 'date_watched']
        widgets = {
            'watched': forms.RadioSelect,  # no longer used in form, left this here for future udpates.
        }


# this form makes sense, as you are specifying widgets here (thereby modifying the default).
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


