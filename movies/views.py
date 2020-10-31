from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model # why this instead of settings.AUTH_USER_MODEL ?
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.http import Http404
from django.db.models import Max, Min, Avg

from .models import (Movie, GameRound, Trophy, UserProfile, UserMovieDetail, UserRoundDetail, TrophyProfileDetail)
from .forms import AddMovieForm, UserMovieDetailForm

# Note: using get_user_model and settings.AUTH_USER_MODEL are unneccessary in this project, as you are
# using the default django admin User model. You can rewrite the models and views to simply access User
# and import it as done above.

class IndexPageView(ListView):
    queryset = Movie.objects.order_by('-date_watched')
    template_name = 'movies/index.html'
    context_object_name = 'movies'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        date_today = timezone.now()

        # if there isn't a current round, the current_round name will have a value of None, which can be checked
        # against conditionally in the template
        # (make sure that calling .last() on an empty Queryset actually does return None...)
        current_round = GameRound.objects.filter(active_round__exact=True).last() # use last() in case there is more than one (though there shouldn't be)

        current_round_pairs = []

        if current_round:
            current_round_participants = current_round.participants.all()   # note the.all() on the connection !
        
            for p in current_round_participants:
                profile = UserProfile.objects.get(user=p)
                current_round_pairs.append((p, profile))

        # this will leave current_round_pairs empty, which is fine
        else:
            pass


        context['current_round'] = current_round
        context['current_round_pairs'] = current_round_pairs
        context['date_today'] = date_today

        return context

class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'movies/settings.html'

    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        movies = Movie.objects.order_by('-date_watched')
        members = User.objects.all()
        profiles = UserProfile.objects.all()
        game_rounds = GameRound.objects.order_by('-round_number')  # display high to low (recent at top)

        # you will eventually need to sort movies by their game_round attribute,
        # so you can display movies by round.

        context['game_rounds'] = game_rounds
        context['movies'] = movies
        context['members'] = members
        context['member_profiles'] = profiles

        return context


# I couldn't make this a DetailView, because that requires a pk argument to be captured by the URL, and 
# this view is called from base.html, and afaik I have no ability to pass an argument such as a pk in base.html,
# because I have no view for rendering it; the Results link in the navbar would need an <int:pk> in the url, which
# I can certainly add to the URL, but how do I -pass- an argument to that URL from the base.html template ? it has
# no access to results objects, and I have no view to provide it with that context...
class ResultsView(TemplateView):
    """
    When Round is in progress, this is used to display who has and has not submitted their details for each movie.
    When Round is complete, this is used to display the results of the round.

    """
    template_name = 'movies/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # make sure a current round exists, and grab it.
        if GameRound.objects.filter(active_round=True).exists():
            current_round = GameRound.objects.filter(active_round=True).last()
        else:
            current_round = None

        # a round object exists that has active_round = True
        if current_round:
            # flag used by template
            active_round_exists = True

            current_round_movies = current_round.movies_from_round.all()  # uses reverse manager defined in Movie model
            current_round_participants = current_round.participants.all() # get User objects related to current GameRound

            if not current_round.round_completed:

                round_concluded = False
                user_round_details = None  # we only need this if round has ended / results updated    

                total_details_for_round = (current_round_participants.count() * current_round_movies.count())
                details_received = 0

                round_progress_status = {}

                for movie in current_round_movies:

                    round_progress_status[movie.name] = {
                        'submitted':[], 
                        'incomplete': [],
                    }
                    
                    for participant in current_round_participants:

                        if UserMovieDetail.objects.filter(movie=movie, user=participant).exists():
                            round_progress_status[movie.name]['submitted'].append(participant)
                            details_received += 1

                        else:
                            round_progress_status[movie.name]['incomplete'].append(participant)


                number_needed_details = (total_details_for_round - details_received)

                if number_needed_details == 0:
                    ready_to_conclude = True
                else:
                    ready_to_conclude = False

            else:
                # the active round has already been completed; template will display results, not progress.
                round_concluded = True

                # collect the UserRoundDetail objects for current round
                user_round_details = UserRoundDetail.objects.filter(game_round=current_round)

                # we already have the GameRound object stored in current_round

                # have to set this due to context; better way to do this to avoid repetition with other branch ??
                # you could just add to the context within the branches, but then the template had a changing
                # context, which I don't like...

                number_needed_details = None
                details_received = None
                ready_to_conclude = False # it feels weird to set this to False here; the reality is that the variable
                                          # is only meaningful if round_concluded = False; here, round_concluded is True
                                          # and this variable is no longer meaningfully at all, but is being set simply
                                          # because the context expects it. but it seems decepetive to say False to
                                          # 'ready_to_conclude', and the meaning could be misinterpreted; so think about
                                          # else to package these flags / status checks that would be clearer.


        else:
            active_round_exists = False
            round_concluded = False
            round_progress_status = None
            ready_to_conclude = False
            user_round_details = None
            current_round_movies = None
            current_round_participants = None
            number_needed_details = None
            details_received = None


        # you still need to collect the old rounds, package them in context, print links to them
        # in results template; all links will go to old_rounds.html and display old round results.

        # weed through these and see what is / isn't actually getting used; I think round_movies is useless...
        context['active_round_exists'] = active_round_exists
        context['round_concluded'] = round_concluded
        context['current_round'] = current_round
        context['user_round_details'] = user_round_details
        context['round_progress_dict'] = round_progress_status
        context['ready_to_conclude'] = ready_to_conclude

        context['round_movies'] = current_round_movies
        context['round_participants'] = current_round_participants

        context['number_needed_details'] = number_needed_details
        context['details_received'] = details_received


        return context


# the way this is designed right now, this isn't really an UpdateView -- you aren't updating the GameRound object in here....
# this is more of a staging area for calculating and presenting the scoring results, from which you'd then trigger the actual
# update views...
# the trick is, since it's only creating a new data object (point_queue) and not modifying db contents, you need a way to 
# pass that data object to the views that actually do the updating
class ConcludeRoundView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = GameRound
    template_name = 'movies/conclude_round.html'
    context_object_name = 'game_round'
    # success_url = ...         ???   this isn't really being used as an UpdateView, so this seems irrelevant

    # this has to be defined, because this is an UpdateView, even though we don't use a form
    fields = []

    login_url = 'login'

    # used by UserPassesTestMixin; verify user has admin prvileges (required to conclude round)
    def test_func(self):
        user = self.request.user
        return user.userprofile.is_mmg_admin   # returns True if userprofile object has is_mmg_admin True


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # grab all the participants of the round
        round_participants = self.object.participants.all()

        # grab all the UserRoundDetail objects for each participant
        # user_round_details = []
        # for user in round_participants:
        #     urd_object = UserRoundDetail.objects.get(user=user, game_round=self.object)
        #     user_round_details.append(urd_object)

        # faster approach to above...
        user_round_details = UserRoundDetail.objects.filter(game_round=self.object)


        # grab all the movies in the round
        round_movies = self.object.movies_from_round.all()   # verify if this actually gets used anywhere!


        # this will store points per participant, as calculated by function calls
        point_queue = {}

        for participant in round_participants:

            # add the participant to the point_queue, establish nested dicts for point storage
            point_queue[participant.username] = {
                'points_by_guess': [],
                'points_by_movie_known': [],
                'points_by_movie_unseen': [],
                'points_by_movie_liked': [],
                'points_by_movie_disliked': [],
            }

            # TO-DO: ALL THE BELOW LOGIC + THE FUNCTIONS CALLED THEREIN MUST BE UPDATED TO ACCOUNT FOR THE
            # NEW FORMAT OF point_queue -- IT HAS THREE KEYS WITH THREE LISTS, SUBDIVIDING MOVIE POINTS
            # INTO THE TWO DIFFERNET TYPES, KNOWN AND UNSEEN; update all logic to follow this format.

            points_by_guess = self.calculate_guess_points(participant)
            point_queue[participant.username]['points_by_guess'].extend(points_by_guess)


            points_by_movie_known, points_by_movie_unseen, points_by_movie_liked, points_by_movie_disliked = self.calculate_movie_points(participant)

            point_queue[participant.username]['points_by_movie_known'].extend(points_by_movie_known)
            point_queue[participant.username]['points_by_movie_unseen'].extend(points_by_movie_unseen)
            point_queue[participant.username]['points_by_movie_liked'].extend(points_by_movie_liked)
            point_queue[participant.username]['points_by_movie_disliked'].extend(points_by_movie_disliked)


        # Note: the dict returned by this function has sorted the key-value pairs (participant, points) in order
        # from high (winner) to low. This will be userful later when using this dict to update the actual database
        # records.
        # IMPORTANT NOTE: we can't simply assign ranking from 1 - finish for the results in here, becuase there may
        # be duplicate scores, and we have to delve deeper to figure out who 'wins' in such a case, and then 
        # further sort from there, pushing ranks down as we go....
        total_points_by_participant = self.total_points_dict_builder(point_queue)

        # we won't use key=dict.get or itemgetter to retrieve winning key, because that wouldn't account for ties;
        # determine the highest score in the dictionary
        gold_winning_score = max(total_points_by_participant.values())

        # doing some janky python work so we can extract 2nd and 3rd highest scores without errors
        # if round_participants.count() >= 3:
        #     all_unique_scores = sorted(set(list(total_points_by_participant.values())), reverse=True)

        # retrieve all keys that had that score
        gold_winning_names = [name for name, value in total_points_by_participant.items() if value == gold_winning_score]

        # get the actual object of the winner(s) and store them in a list:
        gold_winners = []

        # note the we are retreiving actual user objects right here, and then using them throughout, up until we store data from 
        # them in request.session, which cannot hold class objects...
        for name in gold_winning_names:
            gold_winner_object = User.objects.get(username__icontains=name)
            gold_winners.append(gold_winner_object)

        # 'gold winners' here means multiple people had the same max score; until ranked by other criteria, they are all
        # 'gold'....

        # if there is a tie, determine single winner by average movie rating;
        # figure out how to refactor this as a query using aggregate Max; this feels like a very long route that could
        # be refactored to simply be a single query with aggregate....???
        # "of this set of user objects, return me the one whose movie choice has the highest average rating"
        # it's a deep search, becuase it goes User > Movie choice > UserMoveDetail objects > rating field average
        # you could combine the aggregate Avg with the order_by function, and then extract the first() from those results...

        if len(gold_winners) > 1:   # can we do .count instead on the list we created, since it contains records?
            gold_winner_tuples = []
            for winner in gold_winners:
                # thing to verify here is: can we use *both* a standard lookup + a deeper lookup together in the same get()...
                winner_movie = winner.related_movies.get(game_round=self.object, usermoviedetail__is_user_movie=True)
                average_rating = winner_movie.average_rating
                gold_winner_tuples.append((winner, average_rating))

            # how to assign to an arbitrary number of winners when we don't know how many tied?
            gold_winner, silver_winner, bronze_winner = self.return_winners_from_tie(gold_winner_tuples)

        else:
            gold_winner = gold_winners[0]
            silver_winner = None
            bronze_winner = None       # we need these values so we can check against them later to determine full ranking


        if silver_winner:
            silver_winner_name = silver_winner.username
        else:
            silver_winner_name = ''         # will be checked against for determining rest of ranking order
        if bronze_winner:
            bronze_winner_name = bronze_winner.username
        else:
            bronze_winner_name = ''

        # note that silver and bronze as named above are NOT the users with 2nd and 3rd highest point totals !! rather, they
        # are users, if applicable, who TIED with the first place winner but received 2nd or 3rd place based on fallback crtiteria,
        # which is avg rating of their movie choice.

        # we need one, clean dataset of users and final ranking + total point, average movie rating (per user movie choice) that
        # we can display results from; but remember, we are just in 'preliminary' land here, the db hasn't been udpated yet, this is
        # all python session data.... final display MUST be from updated db records, NOT from session data (it won't even be available
        # for most users!)

        # PROBLEM: if only session data contains FULL ranking, but final results are printed from URD objects, won't you have
        # to do all the sorting / ranking logic all over again when parsing the URD objects? isn't that messy / inefficient, 
        # since you are doing so much sorting / ranking on the session data ?
        # ANSWER: we need to create that 'complete results' data, and then meaningfully apply it so we can easily
        # show the results of a completed round at any time; this might mean additional db tables or some tinkering with
        # existing ones.

        # remember that the key in point_queue is just a string of the p's name, NOT the p object itself. change this?

        self.request.session['gold_winner_name'] = gold_winner.username
        self.request.session['silver_winner_name'] = silver_winner_name
        self.request.session['bronze_winner_name'] = bronze_winner_name
        self.request.session['point_queue'] = point_queue
        self.request.session['total_points_by_participant'] = total_points_by_participant

        context['gold_winner_object'] = gold_winner
        context['silver_winner_object'] = silver_winner
        context['bronze_winner_object'] = bronze_winner
        context['round_participants'] = round_participants      # sort these by rank; thing is, this view is 'prelim' results...
        context['user_round_details'] = user_round_details
        context['round_movies'] = round_movies                  # do we actually need this? is it used?
        context['point_queue'] = point_queue

        return context


    def return_winners_from_tie(self, tuple_list):
        
        winning_tuples = sorted(tuple_list, key=lambda x : x[1], reverse=True)
        
        # return tuples for gold and silver, bronze will be assigned None
        if len(winning_tuple) == 2:
            return winning_tuple[0], winning_tuple[1], None

        # return tuples for gold, silver and bronze
        elif len(winning_tuple) > 2:
            return winning_tuple[0], winning_tuple[1], winning_tuple[2]



    def total_points_dict_builder(self, point_queue):
        
        total_point_dict = {}

        for participant, results in point_queue.items():
            total_points_for_p = (len(results['points_by_guess']) + len(results['points_by_movie_known']) + 
                len(results['points_by_movie_unseen']) + len(results['points_by_movie_liked']) + 
                len(results['points_by_movie_disliked']))

            total_point_dict[participant] = total_points_for_p

        # sort the dictionary so key-val pair with highest value is first (descending). this requires rebuilding the 
        # sorted list of tuples returned by sorted() into a new dictionary, using a dictionary comprehension:

        final_dict = {k: v for k, v in sorted(total_point_dict.items(), key=lambda x: x[1], reverse=True)}

        return final_dict



    def calculate_guess_points(self, participant):

        points_by_guess = []

        round_movies = self.object.movies_from_round.all()

        participant_umds = [movie.usermoviedetail_set.get(user=participant) for movie in round_movies]


        for umd in participant_umds:
            user_that_chose_movie = UserMovieDetail.objects.get(movie=umd.movie, is_user_movie=True).user

            if umd.user_guess == user_that_chose_movie:   # can't compare against username, because in some cases value will be None (user record for movie they chose)
                point_dict = {
                    'point_value': 1,
                    'point_string': '+1  Correctly guessed that {} chose {}'.format(umd.user_guess.username, umd.movie.name)
                }

                points_by_guess.append(point_dict)

        return points_by_guess



    def calculate_movie_points(self, participant):

        points_by_movie_known = []
        points_by_movie_unseen = []
        points_by_movie_liked = []
        points_by_movie_disliked = []

        # get the movie object that is this participant's movie choice
        participant_movie = self.object.movies_from_round.get(usermoviedetail__user=participant, usermoviedetail__is_user_movie=True)

        # get all the UMD objects for the particular movie selected above
        umd_objects = UserMovieDetail.objects.filter(movie=participant_movie)

        for umd in umd_objects:
            if not umd.seen_previously:
                point_dict_one = {
                    'point_value': 1,
                    'point_string': '+1  {} had not previously seen {}.'.format(umd.user.username, umd.movie.name)
                }

                points_by_movie_unseen.append(point_dict_one)

            if umd.heard_of:
                point_dict_two = {
                    'point_value': 1,
                    'point_string': '+1  {} had heard of {}'.format(umd.user.username, umd.movie.name)
                }

                points_by_movie_known.append(point_dict_two)


            if umd.star_rating == 1:
                point_dict_three = {
                    'point_value': 1,
                    'point_string': '+1 {} gave {} the worst possible rating, 1 star.'.format(umd.user.username, umd.movie.name)

                }

                points_by_movie_disliked.append(point_dict_three)

            if umd.star_rating > 3:
                point_dict_four = {
                    'point_value': 1,
                    'point_string': '+1 {} rated {} higher than 3 stars.'.format(umd.user.username, umd.movie.name)
                }

                points_by_movie_liked.append(point_dict_four)


        return points_by_movie_known, points_by_movie_unseen, points_by_movie_liked, points_by_movie_disliked


# view for updating each UserRoundDetail object
class CommitUserRoundView(LoginRequiredMixin, UpdateView):
    model = UserRoundDetail
    template_name = 'movies/commit_user_round.html'
    context_object_name = 'urd_object'

    fields = ['correct_guess_points', 'known_movie_points', 'unseen_movie_points', 'liked_movie_points', 'disliked_movie_points', 'finalized_by_admin']

    login_url = 'login'

    # note that you could use get_initial or get_object here
    # def get_object(self):
    #     obj = super().get_object()
    #     # modify obj as needed here
    #     obj.save(commit=False)  # we don't want anything committed until form_valid is called to submit & save object
    #                             # question: could we skip saving altogether here? would it still display?


    # per my research, it also seems you can override get_form_kwargs for the same result; get_form_kwargs appears
    # to use the data in get_initial, so it's accomplishing the same task, just a little later in the overall 
    # process

    # only need this one OR get_object; not both. note that this approach doesn't include any save() call, so it might
    # be overall cleaner / preferable, since we don't want to save until form_valid is called.
    def get_initial(self):
        initial = super().get_initial()

        # access sesssions data for the dictionary of round results
        point_queue = self.request.session['point_queue']
        total_points_by_participant = self.request.session['total_points_by_participant']
        winner_name = self.request.session['winner_name']

        this_user = self.object.user

        initial['correct_guess_points'] = len(point_queue[this_user.username]['points_by_guess'])
        initial['known_movie_points'] = len(point_queue[this_user.username]['points_by_movie_known'])
        initial['unseen_movie_points'] = len(point_queue[this_user.username]['points_by_movie_unseen'])
        initial['liked_movie_points'] = len(point_queue[this_user.username]['points_by_movie_liked'])
        initial['disliked_movie_points'] = len(point_queue[this_user.username]['points_by_movie_disliked'])

        return initial


    def form_valid(self, form):
        """Update the UserProfile object with the data saved in UserRoundObject"""

        # we will update the related UserProfile object with all the scoring values obtained for this round
        # UserProfile tracks global progress, not per-round.

        this_user = self.object.user
        user_profile = this_user.userprofile    # one-to-one connection, reverse access syntax

        user_profile.total_correct_guess_points += form.instance.correct_guess_points
        user_profile.total_known_movie_points += form.instance.known_movie_points
        user_profile.total_unseen_movie_points += form.instance.unseen_movie_points
        user_profile.total_liked_movie_points += form.instance.liked_movie_points
        user_profile.total_disliked_movie_points += form.instance.disliked_movie_points

        if form.instance.winner_bool:
            user_profile.rounds_won += 1

        return super().form_valid(form)   # call to super() saves the form


    def get_success_url(self):
        return reverse('movies:conclude_round', kwargs={'pk': self.object.game_round.pk})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        point_queue = self.request.session['point_queue']
        total_points_by_participant = self.request.session['total_points_by_participant']

        this_user_name = self.object.user.username # huge previous bug: you did self.request.user here, which is NOT the user you want
        this_user_total_points = total_points_by_participant[this_user_name]  # this is just an int value

        user_point_results = point_queue[this_user_name]

        user_points_by_guess = user_point_results['points_by_guess'] # this is a list of point dicts

        # I need to build a new dict to contain all the non-by-guess resuts, so I can loop through it
        # in the tempalte without also dispaying the guess points; I'm only doing this because I couldn't
        # find a way, in the template, to loop through the user_point_results while skipping the guess results
        # (I want to display them separately):
        user_points_by_movie = {}
        user_points_by_movie['points_by_movie_known'] = user_point_results['points_by_movie_known']
        user_points_by_movie['points_by_movie_unseen'] = user_point_results['points_by_movie_unseen']
        user_points_by_movie['points_by_movie_liked'] = user_point_results['points_by_movie_liked']
        user_points_by_movie['points_by_movie_disliked'] = user_point_results['points_by_movie_disliked']

        context['user_points_by_guess'] = user_points_by_guess   # list of point dicts
        context['user_points_by_movie'] = user_points_by_movie   # dict, key= point type, value=list of point dicts
        context['point_total'] = this_user_total_points          # single int value
        context['point_total_movies_only'] = (this_user_total_points - len(user_points_by_guess)) # single int value

        return context


def build_complete_rankings(point_queue):
    """builds and returns a definitive, final ranking data structure based on points and avg movie ratings per user"""

    # this may render some of the logic in ConclueRoundView redundant / irrelevant; no prob, that view is HUGE anyway...

    # you should build the complete unraked data structure first, including User > point total for round > avg movie rating,
    # THEN perform the ranking on that datastructure based on the values it already contains.
    # this is better than 'grabbing values as needed' for avg movie rating, etc, becuase that gets really messy
    # this way, 1. you know exactly how many total participants there are, and thereby what the ranking number range
    # will be; 2. you already have the fallback values to compare, no need to reach out for them; it's a fixed, finite
    # structure that can just be evaluated as-is, and sorted accordingly, updating rank numbers as necessary, rather than
    # a messy, constantly branching structure that may or may not do queries to access data based on previous conditions, etc.
    # no need for that!
    # one question: include a 'final_rank' value in the dictionary, or just SORT to determine ranking, e.g. the sorting
    # of the p's in the list IS the ranking, so no need to track a number...or easier to track the numbers, since you can
    # enforce uniqueness on them and update them as needed, rather than pushing things around in the list?
    # wait...remember that dictionaries are UNORDERED so you may need to do some sorting with lambda and then 'rebuild'
    # back into dictionary form with dictionary comprehensions....

    # definitely need to answer: rank is a stored value that we modify vs. rank is implicit from ordering
    


# view for updating the overall GameRound object  -- can you merge this into the existing EditRound view ? seems
# weird to have two UpdateViews that work on the same object... can you 

class CommitGameRoundView(LoginRequiredMixin, UpdateView):
    model = GameRound
    template_name = 'movies/commit_game_round.html'
    context_object_name = 'game_round'
    #success_url = reverse_lazy('movies:conclude_round', kwargs={'pk': self.object.pk})

    fields = ['date_finished', 'winner', 'participants', 'round_completed']

    login_url = 'login'


    def get_initial(self):
        initial = super().get_initial()

        winner_name = self.request.session['winner_name']

        winner = User.objects.get(username__icontains=winner_name)

        initial['winner'] = winner

        return initial


    def form_valid(self, form):
        """do I have any tasks to perform in here ??"""
        return super().form_valid(form)


    def get_success_url(self):
        return reverse('movies:conclude_round', kwargs={'pk': self.object.pk})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_round_details = UserRoundDetail.objects.filter(game_round=self.object)

        if ((UserRoundDetail.objects.filter(game_round=self.object, finalized_by_admin=False).count()) > 0 ):
            all_data_reviewed = False
        else:
            all_data_reviewed = True

        # can you think of a cleaner way to do this? all we want to do is set value to False if any ONE
        # object in the user_round_details list has all_data_reviewed = False
        # all_data_reviewed = True
        # for urd in user_round_details:
        #     if urd.finalized_by_admin == False:
        #         all_data_reviewed = False
        #     else:
        #         pass

        # BIG QUESTION: do you want to update the GameRound object based on values in request.session,
        # or, since all the URD objects have been updated by this point, based on data in the actual URD database
        # records? using request.session is more consistent with the 'preliminary / middle man' approach used
        # above in CommitUserRoundView, but maybe that's not neccessary here, since we KNOW that this view cannot
        # be run until all the URDs have been successfully updated?

        context['user_round_details'] = user_round_details
        context['all_data_reviewed'] = all_data_reviewed

        return context






class OldRoundsView(ListView):
    queryset = GameRound.objects.filter(active_round=False)
    template_name = 'movies/old_rounds.html'
    context_object_name = 'game_rounds'



class MovieDetail(LoginRequiredMixin, DetailView):
    model = Movie
    template_name = 'movies/movie.html'
    context_object_name = 'movie'
    query_pk_and_slug = True

    login_url = 'login' # only used by LoginRequiredMixin, if unauthorized access attempted


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # this is fairly redundant, you could just use self.object whenever you need to access the movie object...
        movie = self.object

        # put exception handling here, or use GetObjectOr404...
        user_profile = UserProfile.objects.get(user=user)

        if UserMovieDetail.objects.filter(user=user, movie=movie).exists():
            user_movie_details = UserMovieDetail.objects.get(user=user, movie=movie)
        else:
            user_movie_details = None
            # user_movie_details = UserMovieDetail(user=user, movie=movie)
            # user_movie_details.save()

        # we simply build the form we want here, and pass it in the context; this works, even though this CBV is a 
        # DetailView, not an edit view. When the form is processed, a different view will be called, process_details.
        form = UserMovieDetailForm(current_user=self.request.user)
        #form.fields['user_guess'].queryset = User.objects.filter(related_game_rounds=self.object.game_round) # this works! note: this is equivalent to movie.game_round

        results_ready = False

        game_round = movie.game_round

        # it's also worth noting that some of this stuff can be accessed in the template, through the base objects
        # in the context; check for redundancy...

        context['game_round'] = game_round
        context['user_profile'] = user_profile
        context['user_movie_details'] = user_movie_details
        context['form'] = form
        context['results_ready'] = results_ready

        return context

@login_required
def process_details(request, movie_pk):
    """This is when the UMD is being created for the first time, as opposied to modifying existing record"""
    if request.method == 'POST':

        # verify that this usage of select_related is working as desired 
        movie = Movie.objects.select_related('game_round').get(pk=movie_pk)

        # game_round is cached by select_related above, so this line does not perform a query on the db itself:
        game_round = movie.game_round    # connects to a single specific game_round instance

        # this doesn't really 'need' the current_user argument, as that is only used for how the form is displayed,
        # and this function is only a POST request, after the data is submitted; but, since the form constructor
        # is being called, and the __init__ method of the form includes an assigment using the current_user value,
        # you need to provide it here simply because its expected.
        form = UserMovieDetailForm(data=request.POST, current_user=request.user) 

        if form.is_valid():
            umd_object = form.save(commit=False)
            umd_object.user = request.user
            umd_object.movie = movie
            umd_object.save()

            # this behavior is baffling, and seems to contradict the django docs (which say redirect() can
            # take a kwargs argument)...
            #return redirect('movies:movie', kwargs={'pk': movie.pk, 'slug': movie.slug}) # doesn't work! 
            #return redirect('movies:movie', pk=movie.pk, slug=movie.slug)  # this works, though...
            return redirect(movie)  # this works, using get_absolute_url of movie object

            # short version of Q: why can I pass the kwargs dict to reverse() successfully (like I do
            # numerous times in NoirDB views for the UMD) but not to redirect() ?


@login_required
def update_details(request, umd_pk):
    """update details of an existing record"""
    umd_object = UserMovieDetail.objects.select_related('movie').get(pk=umd_pk)

    # we want the movie object so we can redirect to it when finished (see below); alternatively, we could
    # pass the url plus required values-to-be-captured  to redirect instead.
    movie = umd_object.movie

    if umd_object.user != request.user:
        raise Http404

    if request.method != 'POST':
        # initial GET request
        # adding current_user keyword argument to match behavior of get_form_kwargs method of CBV version of this;
        # this is used in the ModelForm to exclude the user, see: UserMovieDetailForm
        # note: you also have to pass this to the From in the Movie detail view!
        form = UserMovieDetailForm(instance=umd_object, current_user=request.user) # create the form, using data from existing object
        # filter users so only users that are participating in current round are displayed in guess choice:
        #form.fields['user_guess'].queryset = User.objects.filter(related_game_rounds=movie.game_round) # works!

    else:
        # POST request
        form = UserMovieDetailForm(instance=umd_object, data=request.POST, current_user=request.user)  # UserMovieDetailForm(request.POST, instance=umd_object) is also OK
        if form.is_valid():
            form.save()

            return redirect(movie)

    context = {'form': form, 'object': umd_object }
    return render(request, 'movies/update_details.html', context)


# the current big Q: how to get the modification of the form.fields performed in the function above to work inside
# the CBV below....what method do I override to put it there? it -must- go in the GET portion of the CVB's functionality...

class UpdateDetailsView(LoginRequiredMixin, UpdateView):
    model = UserMovieDetail
    template_name = 'movies/update_details.html'
    form_class = UserMovieDetailForm

    login_url = 'login' # used by LoginRequiredMixin


    # using this to attach the user to the kwargs received by the form, so the form has access to the current
    # user, which we will use to exclude the user from the user_guess queryset
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'current_user': self.request.user})
        return kwargs


    def get_success_url(self):
        return reverse('movies:movie', kwargs={'pk': self.object.movie.pk, 'slug': self.object.movie.slug })

    # UpdateView takes care of passing the to-be-updated object instance to the ModelForm constructor
    # you'd only need to do that if you were writing this as a non-CBV function.


class MembersView(ListView):
    #model = get_user_model()
    # I want to order by total points, but that is a property so I can't; which means we need
    # a static, non-property value that holds the total points, and is computed by a method in
    # the UserProfile model, and that method gets called.... when? here? somewhere else?
    queryset = User.objects.order_by('userprofile__total_correct_guess_points')
    template_name = 'movies/members.html'
    context_object_name = 'members'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        game_rounds = GameRound.objects.order_by('-date_started')
        current_round = game_rounds.filter(active_round=True).last()  # current round will be None if there are no rounds

        user_profile_pairs = []
        current_round_pairs = []

        # get the profile for each user, store user and their profile as a tuple in master list
        if context['members']:
            for member in context['members']:
                profile = UserProfile.objects.get(user=member)
                user_profile_pairs.append((member, profile))

        # retrieve Users through the paticipants attribute of GameRound object (M2M)
        if current_round:
            current_round_participants = current_round.participants.all()   # note the.all() on the connection !

        # TEST THESE OUT, THEY AREN'T CURRRENTLY USED, BUT I WANT TO CONFIRM HOW TO FILTER DOWN THE
        # DESIRED OBJECTS IN THE QUERYSET USING THE FOLLOWING APPROACHES...
        # alternately, retrieve Users by filtering the queryset of all members, which is already in our context

        # note that you have now defined UserRoundDetail, the intermediary table between User and Round, which
        # should make the format of these queries more obvious....

        #crp2 = context['members'].filter(gameround__round_number=current_round.round_number)

        # could you just shorten it by providing the game round object itself?
        #crp3 = context['members'].filter(gameround=current_round)

            for p in current_round_participants:
                profile = UserProfile.objects.get(user=p)
                current_round_pairs.append((p, profile))


        context['current_round'] = current_round
        context['user_profile_pairs'] = user_profile_pairs
        context['current_round_pairs'] = current_round_pairs

        return context


# an old question: how to access the (already grabbed) queryset while inside get_context_data method? I know
# you did this before...

class AddMovieView(LoginRequiredMixin, CreateView):
    model = Movie
    template_name = 'movies/add_movie.html'
    context_object_name = 'movie'
    success_url = reverse_lazy('movies:index')   # this should later be udpated to go to new movie page itself

    form_class = AddMovieForm

    login_url = 'login' # only used by LoginRequiredMixin, if unauthorized access attempted

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # this is checked against by the add_movie page, to tell user they must add an active Round
        # before they can add a movie.
        if GameRound.objects.filter(active_round=True).exists():
            active_round_exists = True
        else:
            active_round_exists = False

        context['active_round_exists'] = active_round_exists

        return context


class CreateRoundView(LoginRequiredMixin, CreateView):
    model = GameRound
    template_name = 'movies/create_round.html'
    success_url = reverse_lazy('movies:settings')
    context_object_name = 'game_round'
    fields = ['round_number', 'active_round', 'round_completed', 'date_started', 'participants']

    login_url = 'login'

# the method below  is a good example of breaking up the normal flow of a form_valid method; we want to modify
# the object AFTER it is saved, but before the redirect. That's why the format of this is different
# than the other 'standard' form_valid methods used. Another good example is in the NoirDB User registration
# view. There are two possible approaches as documented on SO thread: 
# "Django CreateView: How to perform action upon save";
  
    # no longer doing this, for now; round number is simply entered on creation form.
    # def form_valid(self, form):

    #     self.object = form.save() # manually create the object instance so we can then modify it
    #     self.object.round_number = self.object.compute_round_number()
    #     return redirect(self.get_success_url())


class EditRoundView(LoginRequiredMixin, UpdateView):
    model = GameRound
    template_name = 'movies/edit_round.html'
    success_url = reverse_lazy('movies:settings')
    context_object_name = 'game_round'
    fields = ['round_number', 'active_round', 'round_completed', 'date_started', 'participants', 'date_finished']

    login_url = 'login'


class TrophiesView(ListView):
    model = Trophy
    template_name = 'movies/trophies.html'
    context_object_name = 'trophies'



