from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from datetime import date


class GameRound(models.Model):
    
    bool_choices = ((True, 'Yes'), (False, 'No'))

    # the method to set this is called by the CreateView that creats this object CreateRoundView
    round_number = models.PositiveSmallIntegerField(null=True)

    # Q: should you add unique=True to this field, so only one game round record can be the active round?
    # what happens if this unique rule is broken? 
    active_round = models.BooleanField(choices=bool_choices, default=False, verbose_name="Is this round currently active?")  # is this the 'active' round, now in progress.

    # round_completed is distinct from current_round = False, because you might add a round that hasn't started yet
    round_completed = models.BooleanField(choices=bool_choices, default=False, verbose_name="Round Already Completed")



    date_started = models.DateField(default=date.today, null=True, verbose_name="Round begins on")
    date_finished = models.DateField(default=date.today, null=True, verbose_name="Completed On")

    # should this instead be tracked in an intermediary table linking GameRound to User as M2M ?
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, verbose_name='Winner')
    
    # if you create an intermediary table for this connection, you could store 'winner' as an additional field
    # in that table, instead of having a winner field in  this model; this is directly comparable to your situation of
    # having the 'chosen by' field in movie, even though you are also tracking that info 'is_user_movie' in the
    # intermediary table of Movie and User, UserMovieDetail.
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='Participating Members', 
        related_name='rounds_from_user')

    def __str__(self):
        return 'Round {} - Active? {}'.format(self.round_number, self.current_round)

    # call this in the form_valid method of the view that creates rounds, if possible...
    def compute_round_number(self):
        if GameRound.objects.last().exists():
            # could /should you use an F expression here, instead of pulling value into memory to use it?
            previous_round = GameRound.objects.last()
            prev_round_num = previous_round.round_number

            return (prev_round_num + 1)

            # self.round_number = (prev_round_num + 1)
            # self.save()
        else:
            return 1


    def save(self, *args, **kwargs):
        """ do stuff here as needed"""
        super().save(*args, **kwargs)



class Movie(models.Model):
    name = models.CharField(max_length=150, verbose_name='Movie Title')
    year = models.PositiveIntegerField(null=True, verbose_name='Year Released')

    bool_choices = ((True, 'Yes'), (False, 'No'))

    game_round = models.ForeignKey(GameRound, null=True, on_delete=models.CASCADE)

    chosen_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
        related_name='chosen_movie', null=True, blank=True, verbose_name="Chosen By User")
    

    watched = models.BooleanField(choices=bool_choices, default=False, verbose_name="Watched Yet?")

    date_watched = models.DateField(default=date.today, null=True, verbose_name = "Date Watched")

    # we must define 'through_fields' below, because UMD has *two* FKs relating to User; to clear the ambiguity,
    # we specify the two FKs used specifically for the M2M relationship to THIS field.
    # (see 'user' and 'user_guess' fields in UMD model)
    # NOTE! Order of through fields in the tuple is CRITICAL: the first one MUST be the one that refers to
    # the model that defines the M2M connection, e.g. in this case, movie MUST be the first entry.
    # in other words, tuple format is (model_defined_on, targeted_model)

    # why is this here, specifically? think of it like this: 
    # you are saying "create a connection to User, and use an intermediary; BUT that intermediary
    # table itself linking this Movie model to the User table is going to have ANOTHER link to user, so
    # we need to specify exactly which fields in the intermediary table refer to THIS here connection, which
    # are the two fields forming the M2M connection: movie and user.
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserMovieDetail', 
        through_fields=('movie', 'user'), related_name='related_movies')

    slug = models.SlugField(
        default = '',
        editable = True,
        max_length = 150,
        )


    class Meta:
        ordering = ['date_watched']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        kwargs = {
            'pk': str(self.id),
            'slug': self.slug
        }
        return reverse('movies:movie', kwargs=kwargs)

    def save(self, *args, **kwargs):
        value_for_slug = self.name
        self.slug = slugify(value_for_slug, allow_unicode=True)
        super().save(*args, **kwargs)


class Trophy(models.Model):
    name = models.CharField(max_length=200)
    condition = models.CharField(max_length=1000)
    point_value = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name + " - " + self.condition



class UserProfile(models.Model):
    # you MUST review / learn what it means to set primary_key = True on this, and why you would want to...
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)

    BOOL_CHOICES = ((True, 'Yes'), (False, 'Nope'))

    correct_guess_points = models.PositiveSmallIntegerField(default=0, null=True)
    known_movie_points = models.PositiveSmallIntegerField(default=0, null=True)
    unseen_movie_points = models.PositiveSmallIntegerField(default=0, null=True)
    trophy_points = models.PositiveSmallIntegerField(default=0, null=True)

    # does this user have MMG admin priviledges (distinct from django admin, mind you!)
    is_mmg_admin = models.BooleanField(choices=BOOL_CHOICES, default=False)

    trophies = models.ManyToManyField(Trophy, through='TrophyProfileDetail', related_name='related_profiles')

    @property
    def total_points(self):
        return (self.correct_guess_points + self.known_movie_points + self.unseen_movie_points + self.trophy_points)

    def update_points(self):
        pass
     
    # don't forget to add the 'signal' code that creates a profile when a user is created, there is no profile for
    # admin right now!!

class UserMovieDetail(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    BOOL_CHOICES = ((True, 'Yes'), (False, 'Nope'))

    is_user_movie = models.BooleanField(choices=BOOL_CHOICES, default=False, verbose_name="Is this your movie?")
    seen_previously = models.BooleanField(choices=BOOL_CHOICES, default=False, verbose_name="Had you seen this movie previously?")
    heard_of = models.BooleanField(choices=BOOL_CHOICES, default=False, verbose_name="Had you heard of this movie before?")

    # user guesses who chose the movie
    user_guess = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name='related_via_guess',
        verbose_name="Who do you think chose this?  (Leave blank if it's your movie)")

    rating_choices = [
        (1, 'It destroyed me... One Star'),
        (2, 'New dimensions of suffering... Two Stars'),
        (3, "Damage sustained, but I'll recover... Three Stars"),
        (4, 'Surprisingly light on hurting... Four Stars'),
        (5, "It didn't hurt at all!... Five Stars"),
    ]

    star_rating = models.PositiveSmallIntegerField(choices=rating_choices, default=3, verbose_name='Deep Hurting Level')

    comments = models.TextField(default='', blank=True, max_length=1000) # if left blank, default value of empty string is used; no Null in table.

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










