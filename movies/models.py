from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import F, Max, Min, Avg
from datetime import date
from django.db.models import Avg, Max, Min, Count, Q
from django.core.exceptions import ObjectDoesNotExist



class GameRound(models.Model):
    
    bool_choices = ((True, 'Yes'), (False, 'No'))

    # the method to set this is called by the CreateView that creats this object CreateRoundView
    round_number = models.PositiveSmallIntegerField()

    # Q: should you add unique=True to this field, so only one game round record can be the active round?
    # what happens if this unique rule is broken? 
    active_round = models.BooleanField(choices=bool_choices, default=False, verbose_name="Is this round currently active?")  # is this the 'active' round, now in progress.

    # a round can be complete and still  be the active round -- e.g. it's data is displayed on index and will be there until a new round is started
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


    def get_absolute_url(self):

        if self.round_completed == False:
            return reverse('movies:results')
        # round is complete; go to old_round_results display, not 'active' results page.
        elif self.round_completed == True:
            return reverse('movies:old_round_results', kwargs={'pk': str(self.pk)})


#NOTE: this is not currently used at all, and isn't really necessary; data is drawn from UserProfiles to show all-time scores.
class AllTimeScore(models.Model):
    """Stores current all-time ranks for specific areas, as tabulated every time a Round is concluded; e.g. 'best guesser', 'worst movie chooser'"""

    # each record is a "timestamp" of when the last calculation was run. A given record says: "at time of calculation on date X, here are the 
    # all-time-standings per specific rank-type"

    date_created = models.DateTimeField(auto_now_add=True)

    most_rounds_won = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="all_time_rounds", null=True)
    most_guess_points = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="all_time_guess")
    most_liked_points = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="all_time_liked")
    most_disliked_points = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="all_time_disliked")
    most_seen_points = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="all_time_seen")
    most_unseen_points = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="all_time_unseen")

    def __str__(self):
        return 'All-Time Results as tabulated on {}'.format(self.date_last_run)

    # with this approach of having 'hard coded' the rank fields, we can write methods that update those fields meaningfully

    # Question: given that a new record always represents the tabulation of results at that time, should the calculation code go into
    # the save method rather than an additional custom method? Answer: Yes, that is the design principle of this table: any update to scores
    # always represents A NEW RECORD IN THE TABLE. A method that updates the above fields for an existing record is pointless, we don't
    # need to ever update those unless something went wrong in calculations and we needed to override results; any given record of this table
    # will show the standings at the time that record was created. there is no "update" to an instance, we simply create a new record
    # instead.

    def save(self, *args, **kwargs):
        """add logic here"""
        
        # first, calculate all the #1 placehodlers for each field-rank at time of new record creation; use aggregates to do that?
        # you will simply compute that by looking at all UserProfile objects, then grabbing the relevant user.

        # then do self.most_rounds_won = result_here

        # I guess the only remaining question is, what calls the constructor of this class? the view? that's bad -- that would create
        # a record everytime the relevant page is rendered! It should be added as an Admin function in the admin page.

        super().save(*args, **kwargs)


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
        if average_dict['avg_rating']:
            return round(average_dict['avg_rating'], 1) # round the average to one decimal place
        else:
            return -1   # this is gaming things a bit; OverviewView sorts a queryset of movies and looks at average rating;
                        # movies in an incomplete round will return NoneType, which can't be rounded.

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


    def assign_user(self):
        """When a Round is completed, this method will be called on each Movie object in the Round to 
        update the chosen_by field to the appropriate user. Movie objects in non-completed rounds all
        have None assigned to the chosen_by field, by default"""
        if self.game_round.round_completed == False:
            print('This movie is part of a Round that has not been completed yet!\
             \nCannot assign a User to Movie until the round is completed')
            pass
        else:
            try:
                user_who_chose = self.users.get(usermoviedetail__is_user_movie=True)
            except ObjectDoesNotExist:
                pass # object wasn't found, so no assigment to this instance is made, just do nothing
            else:
                # assign the found user to this movie instance, and save it:
                self.chosen_by = user_who_chose
                self.save()

        # Q: if you wanted to do this with the less-generic Model.DoesNotExist exception (which wouldn't
        # require importing ObjectDoesNotExist up top), would you write:

        # try:
        #     user_who_chose = self.users.get(usermoviedetail__is_user_movie=True)
        # except Movie.DoesNotExist:
        #     pass

        # the issue here being: I'm explicitly naming the Movie model, which seems weird to do
        # here inside the definition of that Model itself. It's kinda Meta. it maybe doesn't even
        # work? or is it fine because it's inside a method and Movie will have been defined? self is
        # an instance of Movie, so self.DoesNotExist doesn't make sense -- the exception exists
        # on the class itself, Movie; instance.DoesNotExist probably wouldn't find it....



# NOT an intermediary table;  connected via OneToOne to the default User model
class UserProfile(models.Model):
    # you MUST review / learn what it means to set primary_key = True on this, and why you would want to...
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)

    BOOL_CHOICES = ((True, 'Yes'), (False, 'Nope'))

    # overall points for the User -- includes ALL game rounds they participated in
    # updated by a call to the method update_all_data, which should be run whenever a round is concluded
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

    def update_all_data(self):
        """A method that scans through all urd objects for a user (profile) instance and updates relevant total points fields"""

        # there's no problem running this method multiple times, it won't screw up point totals, as it will simply re-calculate
        # the values and (re)assign them to the relevant field; doing it over and over would just be pointless, but not destructive.
    
        # get all UserRoundDetail objects for user of this user profile instance:
        user_urds = self.user.userrounddetail_set.filter(game_round__round_completed=True)

        # Note on above: technically, filtering by completed round isn't necessary, because a urd record is only created for a round when the round
        # is completed. But the above query more 'accurately' reflects exactly what we want to retrieve. 

        # two approaches -- one, loop through objects and sum totals, e.g., pure python code based on values retrieved from db;
        # two, use database-level functions via django / sql:  aggregate and annotate as necessary using sum(), max(), etc.
        # or perhaps just use F() expressions to grab the data on the db level?

        # build a point dictionary, defaults to 0 for everything
        point_dict = {
            'all_time_rounds': 0,
            'all_time_guess': 0,
            'all_time_known': 0,
            'all_time_unseen': 0,
            'all_time_liked': 0,
            'all_time_disliked': 0,
        }

        # loop through all UserRoundDetail objects connected to this UserProfile instance, accumulate points from each into point_dict
        for urd in user_urds:
            point_dict['all_time_guess'] += urd.correct_guess_points
            point_dict['all_time_known'] += urd.known_movie_points
            point_dict['all_time_unseen'] += urd.unseen_movie_points
            point_dict['all_time_liked'] += urd.liked_movie_points
            point_dict['all_time_disliked'] += urd.disliked_movie_points

            if urd.winner_bool:
                point_dict['all_time_rounds'] += 1
            else:
                pass

        # update the fields of this UserProfile instance, based on data stored in point_dict
        self.rounds_won = point_dict['all_time_rounds']

        self.total_correct_guess_points = point_dict['all_time_guess']
        self.total_known_movie_points = point_dict['all_time_known']
        self.total_unseen_movie_points = point_dict['all_time_unseen']
        self.total_liked_movie_points = point_dict['all_time_liked']
        self.total_disliked_movie_points = point_dict['all_time_disliked']

        self.save()


    def get_absolute_url(self):
        return reverse('movies:user_profile', kwargs={'pk': str(self.pk)}) # note the pk field on UserProfile is 'user_id'




# note: the rounds_won field is currently updated by a view -- the conclude round view, I think. ultimately the update_all_data method
# should include it's own code to correctly compute how many rounds a given P has won. We shouldnt rely on some code stuck in a view 
# for keeping rounds_won tabulated....
# in short: add it in the method above so it gets updated with all the point totals, AND remove the code that sets it in the view,
# otherwise you could wind up with things being accumulated twice, etc....actually, I think as long as you do
# the update points AFTER the round conclusion, it will always calculate and overwrite the value to the correct value;
# but regardless, you should probably remove the rounds_won update in the view, it's redundant with point update method...












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




