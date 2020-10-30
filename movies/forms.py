from django import forms
from django.contrib.auth.models import User

from .models import Movie, UserMovieDetail, GameRound

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # need this for grabbing the queryset assigned below
        current_round = GameRound.objects.filter(active_round=True).last()

        self.fields['user_guess'].queryset = User.objects.filter(related_game_rounds=current_round)


# class UserRoundDetailForm(forms.ModelForm):
#     class Meta:
#         model = UserRoundDetail
#         fields = []






# don't forget the .queryset part of the assignment!


# the overriden __init__ method above works successfully to filter the ModelChoiceField results
# to only show the Users that are participants (related to) the current GameRound.

# the other appraoch is to set form.fields in the GET portion of your views; I've left the code
# in for doing this, commented out. It's in MovieDetail (because that is the view that renders
# the blank form initially) and also in update_details (the form view to modify already submitted
# details). I have no figured out yet how to implement that behavior into the CBV UpdateView
# version of update_details, UpdateDetailsView, so it is currently not being used (but, since
# you currently are using this form-modification version of a solution, you could start using
# the CVB UpdateDetailsView again if you wanted to!). Hopefully someone answers my stack overflow
# question so I know which method to override to get this behavior working in a CBV generic
# editing view.

