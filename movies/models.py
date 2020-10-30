from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import F, Max, Min, Avg
from datetime import date



class GameRound(models.Model):
    
    bool_choices = ((True, 'Yes'), (False, 'No'))

    # the method to set this is called by the CreateView that creats this object CreateRoundView
    round_number = models.PositiveSmallIntegerField()

    # Q: should you add unique=True to this field, so only one game round record can be the active round?
    # what happens if this unique rule is broken? 
    active_round = models.BooleanField(choices=bool_choices, default=False, verbose_name="Is this round currently active?")  # is this the 'active' round, now in progress.

    # round_completed is distinct from current_round = False, because you might add a round that hasn't started yet
    round_completed = models.BooleanField(choices=bool_choices, default=False, verbose_name="Round Already Completed?")

    date_started = models.DateField(default=date.today, null=True, verbose_name="Round Start Date")
    date_finished = models.DateField(default=date.today, null=True, blank=True, verbose_name="Round Finished Date")

    # QUESTION: what would unique=True on this field actually do / mean ?
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, verbose_name='Winner')
    
    # if you create an intermediary table for this connection, you could store 'winner' as an additional field
    # in that table, instead of having a winner field in  this model; this is directly comparable to your situation of
    # having the 'chosen by' field in movie, even though you are also tracking that info 'is_user_movie' in the
    # intermediary table of Movie and User, UserMovieDetail.
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserRoundDetail', verbose_name='Participating Members', 
        related_name='related_game_rounds')


    def __str__(self):
        return 'Round {}'.format(self.round_number)


    def save(self, *args, **kwargs):
        """ do stuff here as needed"""
        super().save(*args, **kwargs)


class Trophy(models.Model):
    name = models.CharField(max_length=200)
    condition = models.CharField(max_length=1000)
    point_value = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name + " - " + self.condition


#intermediary table of the 'participants' M2M field in GameRound above
class UserRoundDetail(models.Model):
    # M2M connections
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game_round = models.ForeignKey(GameRound, on_delete=models.CASCADE)

    # Extra fields
    winner_bool = models.BooleanField(default=False) # flip to True for record containing User who won the Round
    correct_guess_points = models.PositiveSmallIntegerField(default=0, null=True)
    known_movie_points = models.PositiveSmallIntegerField(default=0, null=True)
    unseen_movie_points = models.PositiveSmallIntegerField(default=0, null=True)
    liked_movie_points = models.PositiveSmallIntegerField(default=0, null=True)
    disliked_movie_points = models.PositiveSmallIntegerField(default=0, null=True)

    trophy_points = models.PositiveSmallIntegerField(default=0, null=True)

    trophies_won = models.ManyToManyField(Trophy, verbose_name='Trophies Won This Round', 
        related_name='related_user_round_details')

    finalized_by_admin = models.BooleanField(default=False)


    def __str__(self):
        return 'Round {} results for {}'.format(self.game_round.round_number, self.user.username)


class Movie(models.Model):
    name = models.CharField(max_length=150, verbose_name='Movie Title')
    year = models.PositiveIntegerField(null=True, verbose_name='Year Released')

    bool_choices = ((True, 'Yes'), (False, 'No'))

    # remove null=True here, every movie must be assigned to a round
    # IMPORTANT QUESTION; when I try to remove it and do makemigrations, even with an EMPTY database (e.g.
    # no Movie records exist, it still throws the 'set default' warning, wanting me to provide a default
    # for 'existing rows' -- but there are no existing rows!
    game_round = models.ForeignKey(GameRound, default="", on_delete=models.CASCADE, related_name='movies_from_round')

    # when is this getting set? are we using it at all? 
    chosen_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
        related_name='chosen_movie', null=True, blank=True, verbose_name="Chosen By User")

    watched = models.BooleanField(choices=bool_choices, default=False, verbose_name="Watched Yet?")

    date_watched = models.DateField(default=date.today, null=True, verbose_name = "Date Watched")

    # NOTE! Order of through fields in the tuple is CRITICAL: the first one MUST be the one that refers to
    # the model that defines the M2M connection, e.g. in this case, movie MUST be the first entry.
    # in other words, tuple format is (model_defined_on, targeted_model)

    # why are through_fields required here, specifically? think of it like this: 
    # you are saying "create a connection to User, and use an intermediary table; BUT that intermediary
    # table, which itself links Movie table to the User table, is going to have ANOTHER link to user, so
    # we need to specify exactly which fields in the intermediary table refer to THIS here connection, which
    # are the two fields forming the M2M connection: movie and user.
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserMovieDetail', 
        through_fields=('movie', 'user'), related_name='related_movies')

    slug = models.SlugField(
        default = '',
        editable = True,
        max_length = 150,
        )


    @property
    def average_rating(self):
        # aggregate returns a dict
        average_dict = self.usermoviedetail_set.aggregate(avg_rating=Avg(star_rating))
        return average_dict['avg_rating']


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


# NOT an intermediary table;  connected via OneToOne to the default User model
class UserProfile(models.Model):
    # you MUST review / learn what it means to set primary_key = True on this, and why you would want to...
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)

    BOOL_CHOICES = ((True, 'Yes'), (False, 'Nope'))

    # IMPORTANT: these points need to be tied to a specific Round, currently, they are just 'global'
    # you could still use these fields as a CUMULATIVE POINT TOTAL that sums all points from all rounds, which
    # is probalby worth tracking, but not neccessarily super useful...
    total_correct_guess_points = models.PositiveSmallIntegerField(default=0, null=True)
    total_known_movie_points = models.PositiveSmallIntegerField(default=0, null=True)
    total_unseen_movie_points = models.PositiveSmallIntegerField(default=0, null=True)
    total_liked_movie_points = models.PositiveSmallIntegerField(default=0, null=True)
    total_disliked_movie_points= models.PositiveSmallIntegerField(default=0, null=True)

    total_trophy_points = models.PositiveSmallIntegerField(default=0, null=True)

    # does this user have MMG admin priviledges (distinct from django admin, mind you!)
    is_mmg_admin = models.BooleanField(choices=BOOL_CHOICES, default=False)

    # same issue here, it's global, not per-Round
    total_trophies = models.ManyToManyField(Trophy, through='TrophyProfileDetail', related_name='related_profiles')

    # this could be 
    rounds_won = models.PositiveSmallIntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return 'Profile record for User {}'.format(self.user)

    @property
    def total_points(self):
        return (self.total_correct_guess_points + self.total_known_movie_points + self.total_unseen_movie_points + self.total_trophy_points)
    
    def calculate_trophy_points(self):
        total = 0
        if self.trophies:
            for trophy in self.trophies:
                total += trophy.point_value

        self.total_trophy_points = total


class UserMovieDetail(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    # I think this is unnecessary / redundant, as we can access the round object through the movie field above.
    # it seems in schema design there is a point where risk making spaghetti out of your tables...
    #game_round = models.ForeignKey(GameRound, on_delete=models.CASCADE, related_name = 'umd_from_round')

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
        return '{} tropy awarded to {}'.format(self.trophy.name, self.profile.user)










