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
    

    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserRoundDetail', verbose_name='Participating Members', 
        related_name='related_game_rounds')


    def __str__(self):
        return 'Round {}'.format(self.round_number)


    def save(self, *args, **kwargs):
        """ do stuff here as needed"""
        super().save(*args, **kwargs)


# WIP, may discard this idea entirely...
# class GlobalRank(models.Model):

#     title = models.CharField(max_length=200)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     last_updated = models.DateTimeField()

#     # example records for current global ranks, calculated across all rounds:

#     # user who chose overall highest rated movies
#     # user who chose overall lowest rated movies
#     # user who has made most correct guesses matching users to their movies
#     # user who has made the least correct guesses
#     # user who has won the most rounds


class RoundRank(models.Model):
    rank_int = models.PositiveSmallIntegerField(default=0, unique=True)
    rank_string = models.CharField(max_length=100, unique=True)


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

    total_points = models.PositiveSmallIntegerField(default=0, null=True)
    
    rank = models.ForeignKey(RoundRank, on_delete=models.CASCADE, null=True)

    # the average rating of the movie that the participant chose for this round
    movie_average_rating = models.DecimalField(default=0.0, null=True, max_digits=2, decimal_places=1)

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

    game_round = models.ForeignKey(GameRound, default="", on_delete=models.CASCADE, related_name='movies_from_round')

    # NOTE: THIS FIELD CURRENTLY NOT BEING USED, AND NEVER ACTUALLY GETS ASSIGNED TO !!! (it was put here for quick-n-dirty access)
    chosen_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
        related_name='chosen_movie', null=True, blank=True, verbose_name="Chosen By User")

    watched = models.BooleanField(choices=bool_choices, default=False, verbose_name="Watched Yet?")

    date_watched = models.DateField(default=date.today, null=True, verbose_name = "Date Watched")

    # NOTE! Order of 'through fields' in the tuple is CRITICAL: the first one MUST be the one that refers to
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
        average_dict = self.usermoviedetail_set.aggregate(avg_rating=Avg('star_rating'))  # note: quotes required on named field!!
        return round(average_dict['avg_rating'], 1) # round the average to one decimal place


    class Meta:
        ordering = ['date_watched']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        kwargs = {
            'pk': str(self.id),
            'slug': self.slug
        }

        # round still in progress, movie page is the active, form-loading version
        if not self.game_round.round_completed:
            return reverse('movies:movie', kwargs=kwargs)
        # round is complete; call a different movie pag, one without the form / no modifications
        else:
            return reverse('movies:old_movie', kwargs=kwargs)


    def save(self, *args, **kwargs):
        value_for_slug = self.name
        self.slug = slugify(value_for_slug, allow_unicode=True)
        super().save(*args, **kwargs)


# NOT an intermediary table;  connected via OneToOne to the default User model
class UserProfile(models.Model):
    # you MUST review / learn what it means to set primary_key = True on this, and why you would want to...
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)

    BOOL_CHOICES = ((True, 'Yes'), (False, 'Nope'))

    # overall points for the User -- includes ALL game rounds they participated in
    # NOTE: in the current build, these are not being used or displayed.
    # if you want to use them, you'll have to figure out where to implement an update
    # to them in a bug-free manner
    total_correct_guess_points = models.PositiveSmallIntegerField(default=0, null=True)
    total_known_movie_points = models.PositiveSmallIntegerField(default=0, null=True)
    total_unseen_movie_points = models.PositiveSmallIntegerField(default=0, null=True)
    total_liked_movie_points = models.PositiveSmallIntegerField(default=0, null=True)
    total_disliked_movie_points= models.PositiveSmallIntegerField(default=0, null=True)

    total_trophy_points = models.PositiveSmallIntegerField(default=0, null=True)

    # does this user have MMG admin priviledges (distinct from django admin, mind you!)
    is_mmg_admin = models.BooleanField(choices=BOOL_CHOICES, default=False)

    total_trophies = models.ManyToManyField(Trophy, through='TrophyProfileDetail', related_name='related_profiles')

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

    def update_all_data():
        """A method that scans through all users in all game rounds and updates their profile attributes with 'all-time' values"""
        pass

        # updating the total... fields above will simply mean looping through UserRoundDetail objects and extracting values as necessary.
        # remember, a given class / Model doesn't necessarily (and perhaps shouldn't) need to access another model through a Table-level connection,
        # you should go through the related models as defined in the fields of this class. related models are already filtered, in the sense that you
        # are only accessing models instances connected to this model instance.
        # so, to get the relevant URDs inside this class, you'd acccess this classes' user field.
        # but wait, is there some reason we can't just do a table-level query on URD itself, passing the user as an argument? so we get actual URDs returned?
        # going through user gets as user objects, not URDs -- it's probably still possible to access URDs through the user (user has a reverse connection to urd,
        # so we can get there with a reverse manager) but is that really 'better' than just calling the Table itself? 

        # NOTE OF POSSIBLE EXCEPTION TO ABOVE: model Managers are meant to work on a table-level, so it's possible that in a manager you'd define
        # table-level queries / extractions that don't relate to the instance-related objects. 

        # get a queryset of all UserRoundDetail objects for the user of this userprofile:
        user_urds = self.user.userrounddetail_set.all()

        # alternatively, do this from a Table-level query. is the above preferable because it 
        # gathers the desired objects through the related object? or is accessing through the
        # table like this ok to do? I know it's totally OK to do in a view, but this is a Model method...
        # so that's my big Q: inside a Model method (as opposed to a view)  is it ok to to do Table-level
        # query? Note that in the model Managers section of the django docs, they say Table-level queries
        # are handled by Managers and record-level queries are handled by methods; does that suggest
        # the above is the 'correct' approach? 

        user_urds = UserRoundDetail.objects.filter(user=self.user)

        # even if technically Managers are "for" Table-level queries, is the above still perhaps fine to do?
        # because frankly it's a clearer syntax than the through-related query above...

        # next step: loop through urds to retrieve values, keep a running total in a dictionary,
        # then update this object instance (UserProfile) with the results in the dict, and save it.


# the methods to calculate a given UserProfile's all-time points would be record-level (that is, per-user instance), so they are methods on the Class;
# the methods to return a group of UsersProfiles ranked by their attributes are Table-Level, sorting and returning a queryset of records, so those methods
# should be custom Manager methods or additional Managers -- in both cases, the Class manager handles the behavior at the Table level.



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
        return '{} tropy awarded to {}'.format(self.trophy.name, self.profile.user)



class PointsEarned(models.Model):
    """A simple point Table so we can display strings about how points were earned, rather than just using ints"""

    user_round_ob = models.ForeignKey(UserRoundDetail, on_delete=models.CASCADE, related_name='points_earned') # think of a point objects relationship to URD as equivalent to
                                                                                 # an Entry -> Topic or Article --> Magazine / Publisher

    point_int = models.PositiveSmallIntegerField()
    point_type = models.CharField(max_length=100, null=True, verbose_name='Type of Point Earned')
    point_string = models.CharField(max_length=300, verbose_name='How Point Was Earned')

    def __str__(self):
        return self.point_string




