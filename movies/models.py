from django.db import models
from django.conf import settings
from django.utils.text import slugify     # are you going to use this?


class Movie(models.Model):
    name = models.CharField(max_length=150)
    year = models.PositiveIntegerField(null=True)

    chosen_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chosen_movie')
    watched = models.BooleanField(default=True)
    date_watched = models.DateTimeField(null=True)

    # we must define 'through_fields' below, because UMD has *two* FKs relating to User; to clear the ambiguity,
    # we specify the two FKs used specifically for the M2M relationship to THIS field.
    # (see 'user' and 'user_guess' fields in UMD model)
    # NOTE! Order of through fields in the tuple is CRITICAL: the first one MUST be the one that refers to
    # the model that defines the M2M connection, e.g. in this case, movie MUST be the first entry.
    # in other words, tuple format is (model_defined_on, targeted_model) 
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserMovieDetail', 
        through_fields=('movie', 'user'), related_name='related_movies')

    class Meta:
        ordering = ['date_watched']

    def __str__(self):
        return self.name



class Trophy(models.Model):
    name = models.CharField(max_length=200)
    condition = models.CharField(max_length=1000)
    point_value = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name + " - " + self.condition



class UserProfile(models.Model):
    # you MUST review / learn what it means to set primary_key = True on this, and why you would want to...
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)

    correct_guess_points = models.PositiveSmallIntegerField(default=0, null=True)
    known_movie_points = models.PositiveSmallIntegerField(default=0, null=True)
    unseen_movie_points = models.PositiveSmallIntegerField(default=0, null=True)
    trophy_points = models.PositiveSmallIntegerField(default=0, null=True)

    trophies = models.ManyToManyField(Trophy, through='TrophyProfileDetail', related_name='related_profiles')

    @property
    def total_points(self):
        return (correct_guess_points + known_movie_points + unseen_movie_points + trophy_points)

    def update_points(self):
        pass
     
    

class UserMovieDetail(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    is_user_movie = models.BooleanField(default=False)
    seen_previously = models.BooleanField(default=False)
    heard_of = models.BooleanField(default=False)

    # user guesses who chose the movie
    user_guess = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='related_via_guess')

    rating_choices = [
        (1, 'The Absolute Worst...(One Star)'),
        (2, 'Very Bad...(Two Stars)'),
        (3, 'It was alright...(Three Stars)'),
        (4, 'It was quite good...(Four Stars)'),
        (5, 'Wow, it was amazing!...(Five STars)'),
    ]

    star_rating = models.PositiveSmallIntegerField(choices=rating_choices, default=3)

    comments = models.TextField(default='', max_length=1000)

    # cannot have two rows that list same user-movie pair
    class Meta: 
        constraints = [
            models.UniqueConstraint(fields=['user', 'movie'], name='unique_user_movie_pairs')
        ]

    def __str__(self):
        text = "{}'s details for {}".format(self.user.username, self.movie.name)
        return text



class TrophyProfileDetail(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    trophy = models.ForeignKey(Trophy, on_delete=models.CASCADE)

    date_awarded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} tropy awarded to {}'.format(self.trophy.name, self.profile.user)   # make sure accessing user returns a string in this context, it might return whole object!










