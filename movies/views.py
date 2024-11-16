from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model # why this instead of settings.AUTH_USER_MODEL ?
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.http import Http404, JsonResponse
from django.db.models import F, Max, Min, Avg, Count, Q
from datetime import date, datetime, timedelta

from .models import (Movie, GameRound, Trophy, UserProfile, UserMovieDetail, UserRoundDetail, TrophyProfileDetail, RoundRank, PointsEarned, PartyState, PartyGoers)
from .forms import AddMovieForm, UserMovieDetailForm

import json
import traceback

# Note: using get_user_model and settings.AUTH_USER_MODEL are unneccessary in this project, as you are
# using the default django admin User model. You can rewrite the models and views to simply access User
# and import it as done above.

# For debugging The Party
party_verbose = False

def ShallWeParty(kwargs, pk='movie'):
    idx = kwargs['pk'] if 'pk' in kwargs else None
    
    if not pk == 'movie':
        idx = None
    
    # find the game round object is that has active = True (only one will ever have this value)
    if GameRound.objects.filter(active_round=True).exists():
        current_round = GameRound.objects.filter(active_round=True).last()
        print("current_round.round_completed:" + str(current_round.round_completed))
        if current_round.round_completed and (idx is None or idx == current_round.id):
            # If the current active round is completed, but the party state is < the films involved, redirect to the Results Party for The Reveals.
            round_films = Movie.objects.filter(game_round_id=current_round)
            if PartyState.objects.count() == 0 or PartyState.objects.last().idx <= len(round_films):
                return True

    return False
    
class IndexPageView(LoginRequiredMixin, ListView):
    #queryset = Movie.objects.order_by('-date_watched') # we need get_querset override so we can grab round object...
    template_name = 'movies/index.html'
    context_object_name = 'movies'

    login_url = 'login'

    # this is a ListView because it shows all movies from current round; the self.object_list is the qs of movies
    # returned from this call
    # when you override get_queryset, you don't need to define model=Movie above
    def get_queryset(self):

        self.current_round = GameRound.objects.filter(active_round=True).last() # self so we can pass it to the context in get_context_data without needing to query for it again
        queryset = Movie.objects.filter(game_round=self.current_round).order_by('-date_watched')

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        date_today = timezone.now()

        context['current_round'] = self.current_round
        context['date_today'] = date_today
        if ShallWeParty(kwargs):
            context['the_party_is_on'] = True

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



class OverviewView(LoginRequiredMixin, ListView):
    def dispatch(self, request, *args, **kwargs):
        if ShallWeParty(kwargs):
            return redirect('/resultsparty/')
        
        # Otherwise dispatch as normal.
        return super().dispatch(request, *args, **kwargs)

    model = Movie
    template_name = 'movies/overview.html'
    context_object_name = 'movies'

    login_url = 'login'


    def get_queryset(self):

        if self.kwargs['sort_by'] == "round":
            queryset = Movie.objects.order_by('game_round__round_number')

        # not actually using this one in sort drop-down
        elif self.kwargs['sort_by'] == "movie":
            queryset = Movie.objects.order_by('name')

        elif self.kwargs['sort_by'] == "user":
            #queryset = Movie.objects.order_by('-chosen_by__username')
            queryset = Movie.objects.annotate(avg_rating=Avg('usermoviedetail__star_rating')).order_by('-chosen_by__username', '-avg_rating')

        elif self.kwargs['sort_by'] == "rating":
            queryset = sorted(Movie.objects.all(), key=lambda x: x.average_rating, reverse=True)

        return queryset



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_rounds = GameRound.objects.all()

        completed_rounds = all_rounds.filter(round_completed=True)

        context['rounds'] = all_rounds
        context['completed_rounds'] = completed_rounds

        return context



def get_point_values():
    return { 
        "liked_point_value":   2,
        "loathed_point_value": 2,
        "guess_point_value":   2,
        "unseen_point_value":  1, 
        "known_point_value":   1
    }

# this is not a DetailView becuase that requires a pk argument in the url, and this link appears in navbar on base.html,
# which I (currently) have no way to send vars to (for the url to capture).
class ResultsView(LoginRequiredMixin, TemplateView):
    """
    When Round is in progress, this is used to display who has and has not submitted their details for each movie.
    When Round is complete, this is used to display the results of the round.

    """
    template_name = 'movies/results.html'

    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        if ShallWeParty(kwargs):
            return redirect('/resultsparty/')
        
        # Otherwise dispatch as normal.
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # find the game round object is that has active = True (only one will ever have this value)
        if GameRound.objects.filter(active_round=True).exists():
            current_round = GameRound.objects.filter(active_round=True).last()
        else:
            current_round = None

        # a round object exists that has active_round = True
        if current_round:
            # flag used by template
            active_round_exists = True

            # look for places to use select_related / prefect_related in here...

            current_round_movies = current_round.movies_from_round.order_by('-date_watched')  # uses reverse manager defined in Movie model
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
                        'movie_object': movie,
                    }

                    for participant in current_round_participants:

                        if UserMovieDetail.objects.filter(movie=movie, user=participant).exists():
                            round_progress_status[movie.name]['submitted'].append(participant)
                            details_received += 1

                        else:
                            round_progress_status[movie.name]['incomplete'].append(participant)


                number_needed_details = (total_details_for_round - details_received)

                if number_needed_details == 0 and len(current_round_movies) != 0:  # added second condition because conclude_round link was showing up when there are no movies added!
                    ready_to_conclude = True
                else:
                    ready_to_conclude = False

            else:
                # the active round has already been completed; template will display results, not progress.
                round_concluded = True

                # collect the UserRoundDetail objects for current round
                # with the new fields on the URD model (total points, rank) we should be able to display the complete
                # results of the round. Do we need the UMD objects for any reason ?
                user_round_details = UserRoundDetail.objects.filter(game_round=current_round).order_by('rank') #interestingly, this works, but 'rank' is a RoundRank object...
                                                                                                               #which begs the question, what is this actually ordering by??


                # this is my workaround for getting the two movies with the lowest and highest average ratings
                # it should absolutely be possible to do this in a django query instead
                # the issue why I can't, currently:

                # 1. average_rating on the movie object is a @property, which can't be used in django queries;
                # if it wasn't a property, I'd just query the movies, do order_by('avg_rating') and grab .first() and .last()

                avg_ratings_list = [(movie.average_rating, movie) for movie in current_round_movies]

                sorted_avg_ratings_list = sorted(avg_ratings_list, key=lambda x: x[0]) # is lambda neccessary? wouldn't it sort by first item in tuple anyway?

                most_hated_movie = sorted_avg_ratings_list[0][1]
                most_enjoyed_movie = sorted_avg_ratings_list[-1][1]

                # need to package user objects with their chosen movie, to loop through to show who chose what

                # user_movie_pairs = []
                # for participant in current_round_participants:
                #     # alternate approach: Table-level query; yields identical results
                #     #p_movie = Movie.objects.get(game_round=current_round, usermoviedetail__user=participant, usermoviedetail__is_user_movie=True)
                #     p_movie = participant.related_movies.get(game_round=current_round, usermoviedetail__is_user_movie=True)

                #     user_movie_pairs.append((participant, p_movie))

                # alternate approach to above: loop through movies instead of participants to build user_movie_pairs; the movies have already been
                # sorted by date, so this will preserve the 'most recent at top' ordered display when printing user-movie pairs on the page

                user_movie_pairs = []
                for movie in current_round_movies:
                    p_who_chose = UserMovieDetail.objects.get(movie=movie, is_user_movie=True).user # .user is critical! get user, not umd object

                    user_movie_pairs.append((p_who_chose, movie))

                context['most_hated_score'] = sorted_avg_ratings_list[0][0]
                context['most_enjoyed_score'] = sorted_avg_ratings_list[-1][0]

                context['most_hated_movie'] = most_hated_movie
                context['most_enjoyed_movie'] = most_enjoyed_movie

                context['user_movie_pairs'] = user_movie_pairs

                number_needed_details = None
                details_received = None
                ready_to_conclude = False # don't misinterpret what this means: in this branch, the round has already concluded
                round_progress_status = None

        # this is simply the branch where there is no current round object (it's None), so we have nearly nothing to disply on the page
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


        # get previous game round objects, to provide links to view their results at bottom of main Results page
        previous_game_rounds = GameRound.objects.filter(active_round=False, round_completed=True).order_by('-round_number')

        # weed through these and see what is / isn't actually getting used; I think round_movies is useless...
        context['previous_game_rounds'] = previous_game_rounds

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

class ResultsPartyView(LoginRequiredMixin, TemplateView):
    """
    When Round is semi-complete (users, but not round), this is used to display the results of the round
    in a stepped/timed process.

    """
    template_name = 'movies/resultsparty.html'

    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # find the game round object is that has active = True (only one should ever have this value)
        current_active_round_idx = 0
        
        if GameRound.objects.filter(active_round=True).exists():
            round_idx = GameRound.objects.filter(active_round=True).last().round_number
            current_active_round_idx = round_idx

        # Allow override for history
        if 'pk' in kwargs:
            round_idx = kwargs['pk']

        if round_idx > 1:
            context['prev_round'] = round_idx - 1
        if round_idx < current_active_round_idx:
            context['next_round'] = round_idx + 1
            context['last_round'] = current_active_round_idx

        if GameRound.objects.filter(round_number=round_idx).exists():
            current_round = GameRound.objects.filter(round_number=round_idx).last()

            # Verify the round is semi-complete.
            all_finalized = True
            user_details = UserRoundDetail.objects.filter(game_round_id=current_round.id)
            for user_detail in user_details:
                if not user_detail.finalized_by_admin:
                    all_finalized = False
            
            if not all_finalized:
                context['current_round'] = current_round
                context["error"] = "Round " + str(current_round.id) + " is not presently ready to party."
                
                return context
        else:
            current_round = None
            context["error"] = "No active round to party with"
            return context

        context['current_round'] = current_round
        context['body_func'] = "Party()"
        
        users = []
        users_index = {}
        user_ratings = {}
        points_by_movie = {}
        guesses_by_movie = {}

        # get the round users
        round_users = UserRoundDetail.objects.filter(game_round_id=current_round)
        for round_user in round_users:
            if round_user.user_id == current_round.winner_id:
                context["winner_id"] = current_round.winner_id
                context["winner_name"] = round_user.user.username
            
            users.append({'user_id': round_user.user_id, 'username': round_user.user.username })
            user_ratings[round_user.user_id] = round_user.movie_average_rating
            users_index[round_user.user_id] = round_user.user.username
            user_points = PointsEarned.objects.filter(user_round_ob_id=round_user.id)
            points_by_movie[round_user.user_id] = { "liked": 0, "loathed": 0, "guesses": 0, "known": 0, "unseen": 0, "total": 0 }
            guesses_by_movie[round_user.user_id] = []
            for user_point in user_points:
                if user_point.point_type == "disliked":
                    points_by_movie[round_user.user_id]["loathed"] = points_by_movie[round_user.user_id]["loathed"] + user_point.point_int
                    points_by_movie[round_user.user_id]["total"] = points_by_movie[round_user.user_id]["total"] + user_point.point_int
                elif user_point.point_type != "guess":
                    points_by_movie[round_user.user_id][user_point.point_type] = points_by_movie[round_user.user_id][user_point.point_type] + user_point.point_int
                    points_by_movie[round_user.user_id]["total"] = points_by_movie[round_user.user_id]["total"] + user_point.point_int
        
        films = []
        all_guesses = {}
        round_films = Movie.objects.filter(game_round_id=current_round)
        idx = 1
        for round_film in round_films:
            print("chosen_by_id: " + str(round_film.chosen_by_id))
            
            films.append({'idx': idx, 'id': round_film.id, 'name': round_film.name, 'year': round_film.year, 'chosen_by_id': round_film.chosen_by_id, 'chosen_by_name': users_index[round_film.chosen_by_id], 'star_rating': user_ratings[round_film.chosen_by_id], 'stars_width': int(16 + (120 * (user_ratings[round_film.chosen_by_id] / 5))) })
            idx += 1

            # Set the winner film index
            if (round_film.chosen_by_id == current_round.winner_id):
                context["winner_film_id"] = round_film.id
            
            # guesses
            guesses = UserMovieDetail.objects.filter(movie_id=round_film.id).order_by('user_id')
            guesses_by_movie[round_film.chosen_by_id] = [] # index of correct user guesses by movie (actually indexed by the user who picked the movie)
            all_guesses[round_film.id] = []
            for guess in guesses:
                if guess.user_id and guess.user_guess_id:
                    all_guesses[round_film.id].append({ "user_id": guess.user_id, "user_guess_id": guess.user_guess_id, "username": users_index[guess.user_id], "guessed_username": users_index[guess.user_guess_id], "was_right": 1 if guess.user_guess_id == round_film.chosen_by_id else 0, "star_rating": guess.star_rating, "star_width": (8 + (60 * (guess.star_rating / 5.0))), "seen_previously": 1 if guess.seen_previously else 0, "heard_of": 1 if guess.heard_of else 0, "comments": guess.comments })
                    if guess.user_guess_id == round_film.chosen_by_id:
                        guesses_by_movie[round_film.chosen_by_id].append(guess.user_id)
                else:
                    all_guesses[round_film.id].append({ "user_id": guess.user_id, "user_guess_id": 0, "username": users_index[guess.user_id], "guessed_username": "-", "star_rating": guess.star_rating, "star_width": (8 + (60 * (guess.star_rating / 5.0))), "seen_previously": 1 if guess.seen_previously else 0, "heard_of": 1 if guess.heard_of else 0, "comments": guess.comments  })
        
        # Set current index
        if PartyState.objects.count() == 0 or PartyState.objects.last().idx == 0:
            # NOT STARTED
            context['current_index'] = 0
            context['current_film_index'] = 0;
            context['state'] = 'READY TO PARTY'
        elif PartyState.objects.last().idx > len(round_films):
            # COMPLETE
            context['current_index'] = len(round_films)
            context['current_film_index'] = context['winner_film_id']
            context['state'] = 'COMPLETE'
        else:
            # IN PROGRESS
            context['current_index'] = PartyState.objects.last().idx
            context['current_film_index'] = round_films[PartyState.objects.last().idx-1].id
            context['state'] = 'IN PROGRESS'
        
        # For Historical Parties.
        if round_idx < current_active_round_idx:
            context['state'] = 'COMPLETE'
            context['current_index'] = len(round_films)

        # Assign the top-level data
        context['round_start'] = current_round.date_started
        context['round_end'] = current_round.date_finished
        context['experiment_count'] = len(round_films)
        context['users'] = users
        context['users_json'] = users_index
        context['films'] = films
        context['all_guesses'] = all_guesses
        context['points_by_movie'] = points_by_movie
        context['guesses_by_movie'] = guesses_by_movie

        return context

class ResultsPartyStateIncrement(LoginRequiredMixin):
    """
    Backend for state incrementing.

    """
    def request(request, value):
        data = {}
        idx = value
        this_user_id = request.user.id
        
        mmg_user = UserProfile.objects.get(user_id=this_user_id)
        
        if mmg_user.is_mmg_admin:
            # Record this ping
            try:
                record = PartyGoers.objects.get(uid=this_user_id)
                if record:
                    print("UPDATE uid")
                    record.last_ping = timezone.now()
                    record.save()
            except:
                print("INSERT uid")
                record = PartyGoers(uid=this_user_id, last_ping=timezone.now())
                record.save()
            
            if PartyState.objects.count() == 0:
                print("INSERT idx")
                record = PartyState(idx=idx, next_time=timezone.now() + timedelta(0,2))
                record.save()
            else:
                print("UPDATE idx")
                record = PartyState.objects.last()
                record.idx = idx
                record.next_time = timezone.now() + timedelta(0,2)
                record.save()
            
            # If the index is past the last film that means we're done partying, 
            # so mark the round complete.
            
        return JsonResponse(data)
    
class ResultsPartyStateView(LoginRequiredMixin):
    """
    Backend for ajax querying.

    """
    def request(request):
        # Record this ping
        this_user_id = request.user.id
        try:
            record = PartyGoers.objects.get(uid=this_user_id)
            if record:
                #print("UPDATE uid")
                record.last_ping = timezone.now()
                record.save()
        except:
            #print("INSERT uid")
            record = PartyGoers(uid=this_user_id, last_ping=timezone.now())
            record.save()
        
        # Get each user's party state
        users = []
        partiers = PartyGoers.objects.filter()
        for partier in partiers:
            users.append({ "uid": partier.uid, "last_ping": partier.last_ping })
        
        # Get the overall party state
        server_time = timezone.now()
        
        idx = 0
        if PartyState.objects.count() == 0:
            next_time = server_time # if we aren't ready to advance, leave as current time
        else:
            idx = PartyState.objects.last().idx
            next_time = PartyState.objects.last().next_time
            if next_time < server_time:
                next_time = server_time
        
        delta = next_time - server_time
        
        if party_verbose:
            if delta.total_seconds() > 0:
                print("[{3}] [jcw] told user {0} to wait {1} to go to index {2}".format(this_user_id, delta.total_seconds(), idx, server_time))
        data = { "idx": idx, "server_time": server_time, "next_time": next_time, "users": users }

        return JsonResponse(data)
    
class UserResultsView(LoginRequiredMixin, DetailView):
    model = UserRoundDetail
    template_name = 'movies/user_results.html'
    context_object_name = 'user_round_details'

    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        game_round = self.object.game_round
        participant = self.object.user
        participant_movie = participant.related_movies.get(game_round=game_round, usermoviedetail__is_user_movie=True)
        movie_avg_rating = participant_movie.average_rating # this is a propery and can't (I think) be accessed by template

        # get all the point objects related to this URD object
        point_objects = self.object.points_earned.all()

        # retreive the point objects, sorting by type:
        point_values = get_point_values()
        
        guess_points = self.object.points_earned.filter(point_type='guess')
        unseen_points = self.object.points_earned.filter(point_type='unseen')
        known_points = self.object.points_earned.filter(point_type='known')
        liked_points = self.object.points_earned.filter(point_type='liked')
        disliked_points = self.object.points_earned.filter(point_type='disliked')

        movie_points_total = (unseen_points.count() * point_values["unseen_point_value"] + known_points.count() * point_values["known_point_value"] + liked_points.count() * point_values["liked_point_value"] + disliked_points.count() * point_values["loathed_point_value"])
        guess_points_total = (guess_points.count() * point_values["guess_point_value"])


        context['movie_points_total'] = movie_points_total
        context['guess_points_total'] = guess_points_total
        context['guess_points'] =  guess_points
        context['unseen_points'] = unseen_points
        context['known_points'] = known_points
        context['liked_points'] = liked_points
        context['disliked_points'] = disliked_points
        
        context['point_values'] = point_values

        context['round_length'] = game_round.participants.all().count()
        context['participant_movie'] = participant_movie
        context['movie_avg_rating'] = movie_avg_rating
        context['game_round'] = game_round
        return context


class UserProfileView(LoginRequiredMixin, DetailView):
    def dispatch(self, request, *args, **kwargs):
        if ShallWeParty(kwargs, 'users'):
            return redirect('/resultsparty/')
        
        # Otherwise dispatch as normal.
        return super().dispatch(request, *args, **kwargs)

    model = UserProfile
    template_name = 'movies/user_profile.html'
    context_object_name = 'user_profile'

    login_url = 'login'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get the user of this UserProfile instance
        user = self.object.user

        # get all movie objects for the user instance; MUST FILTER OUT NON-COMPLETED ROUND RESULTS!
        # (or they would display on the User Profile page, spoiling everything...!!!!)
        user_movies = Movie.objects.filter(usermoviedetail__user=user, usermoviedetail__is_user_movie=True).exclude(game_round__round_completed=False).order_by('-game_round__round_number')

        guess_points = int((self.object.total_correct_guess_points / 2))

        round_count = GameRound.objects.filter(round_completed=True).count()

        # bug found and fixed here: you did GameRound.objects.all(), which including counting current, incomplete round
        # participants; you only want to count total number of participants in -concluded- rounds!
        total_participants = GameRound.objects.exclude(round_completed=False).aggregate(summed=Count('participants')) # this returns a dict

        p_summed = total_participants['summed']

        guess_max = (p_summed - round_count)

        all_max = p_summed

        context['guess_points'] = guess_points
        context['user_movies'] = user_movies

        context['max_rounds'] = round_count
        context['max_guess'] = guess_max
        context['max_rest'] = all_max

        return context


# using UpdateView, but it's not, really; nothing gets updated in db until the Commit views are called.
class ConcludeRoundView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = GameRound
    template_name = 'movies/conclude_round.html'
    context_object_name = 'game_round'
    # success_url = ...         ???   this isn't really being used as an UpdateView, so this seems irrelevant

    # this has to be defined, because this is an UpdateView, even though we don't use a form
    fields = []

    login_url = 'login'

    # jcw: so we don't bounce to the success_url. perhaps NOT BEST PRACTICES?
    def form_valid(self, form):
        if not self.request.POST.getlist('lets'):
            context = self.get_context_data()
            return self.render_to_response(context)

        return super().form_valid(form)

    # used by UserPassesTestMixin; verify user has admin prvileges (required to conclude round)
    def test_func(self):
        user = self.request.user
        return user.userprofile.is_mmg_admin   # returns True if userprofile object has is_mmg_admin True


    def get_context_data(self, **kwargs):
        if party_verbose:
            print("[jcw] ConcludeRoundView.get_context_data(): {0}") # .format(traceback.format_stack()))
        context = super().get_context_data(**kwargs)
        
        # grab all the participants of the round
        round_participants = self.object.participants.all()

        # grab all the UserRoundDetail objects for each participant
        user_round_details = UserRoundDetail.objects.filter(game_round=self.object)

        # grab all the movies in the round
        round_movies = self.object.movies_from_round.all()   # verify if this actually gets used anywhere!

        # build a primary data structure for storing the rounds point results by participant, calculated by calling the calc methods:
        point_queue = {}

        # point calculating methods work on one participant at a time, so we loop through the participants, call each function, store the results
        for participant in round_participants:
            # add the participant to the point_queue, establish nested list values for point storage
            point_queue[participant.username] = {
                'points_by_guess': [],
                'points_by_movie_known': [],
                'points_by_movie_unseen': [],
                'points_by_movie_liked': [],
                'points_by_movie_disliked': [],
            }

            # call guess point calculating method, update point_queue with result
            points_by_guess = self.calculate_guess_points(participant)
            point_queue[participant.username]['points_by_guess'].extend(points_by_guess)

            # call movie point calculating method
            points_by_movie_known, points_by_movie_unseen, points_by_movie_liked, points_by_movie_disliked = self.calculate_movie_points(participant)

            # update the point_queue with results
            point_queue[participant.username]['points_by_movie_known'].extend(points_by_movie_known)
            point_queue[participant.username]['points_by_movie_unseen'].extend(points_by_movie_unseen)
            point_queue[participant.username]['points_by_movie_liked'].extend(points_by_movie_liked)
            point_queue[participant.username]['points_by_movie_disliked'].extend(points_by_movie_disliked)


        # get the ranked_results from the point_queue
        ranked_results = self.get_ranked_results(point_queue)  # this is a dictionary assignment

        # get the name of winner of the round -- this is so winner field of the GameRound object can be succesfully updated; it's somewhat
        # redundant overall, since the ranking itself will show the winner; this was done simply so GameRound has quick & dirty access
        # to the User who won the round

        winner_name = min(ranked_results, key=ranked_results.get) #  min, because the first val in list is rank, and rank 1 is winner

        # store the point_queue and ranked_results dictionaries in the session, to be used by both CommitUserRound and CommitGameRound views
        self.request.session['point_queue'] = point_queue
        self.request.session['ranked_results'] = ranked_results
        self.request.session['winner_name'] = winner_name

        context['user_round_details'] = user_round_details
        
        if party_verbose:
            print("[jcw] get_context_data() returning context: {0}".format(context))
            print("[jcw] get_context_data() returning point_queue: {0}".format(point_queue))
            print("[jcw] Calling static method to update... context.object: {0}".format(context['object'].id))
        
        if self.request.POST.getlist('conclude'):
            # Manually update every user if we've been requested to conclude the round.
            detail_objects = UserRoundDetail.objects.filter(game_round=context['object'].id)
            for detail_object in detail_objects:
                c = CommitUserRoundView()
                if party_verbose:
                    print("[jcw] *** detail_object *** {0} [id = {1}]".format(detail_object, detail_object.id))
                c.object = detail_object
                c.request = self.request
                c.update_user()
            
            # Manually conclude the round: taken from the now obsolete CommitGameRoundView.form_valid
            self.object.round_completed = True
            self.object.date_finished = date.today()
            winner = User.objects.get(username__icontains=winner_name)
            self.object.winner_id = winner.userprofile.user_id

            # grab movies related to this round and call their assign_movie method, so movies contain FK to user who chose them:
            round_movies = self.object.movies_from_round.all()

            for movie in round_movies:
                movie.assign_user()

            self.object.save()
            
            # Reset the party state
            if PartyState.objects.count() == 0:
                record = PartyState(idx=idx, next_time=timezone.now())
                record.save()
            else:
                record = PartyState.objects.last()
                record.idx = 0
                record.next_time = timezone.now()
                record.save()

            # do other stuff that can only be done after round has already been updated (saved) in database....

            # the following update_all_data calls must be made -after- form has been saved, or they won't include this round's URDs
            round_profiles = UserProfile.objects.filter(user__related_game_rounds=self.object) # get profiles of users in this round
            for p in round_profiles:
                p.update_all_data()

            # get urds to update movie avg (fix for Movie property side-effect); like all data calls above, MUST occur after
            # round has been saved (otherwise Movie average rating returns 0, becuase round_completed = False).
            # note: this will work for future submissions of game rounds, but won't work for already submitted rounds
            # where this code wasn't yet written; you'll need to manually updated those rounds, running same code below
            # in shell on server....
            urds = UserRoundDetail.objects.filter(game_round=self.object) # only get urds for current round

            # update the average rating field 
            for urd in urds:
                urd.update_average_rating()
            
            # Time to party.
            context['time_to_conclude'] = 0
        else:
            # Check if it is time to conclude or to party.
            incomplete_count = 0
            detail_objects = UserRoundDetail.objects.filter(game_round=context['object'].id)
            for detail_object in detail_objects:
                if party_verbose:
                    print("[jcw] *** detail_object *** {0} [id = {1}, finalized_by_admin = {2}]".format(detail_object, detail_object.id, detail_object.finalized_by_admin))
                if detail_object.finalized_by_admin == False:
                    incomplete_count += 1
            
            if incomplete_count > 0:
                context['time_to_conclude'] = 1
        
        return context

    # remember that participant is just a string name, not a User object; this is becuase request.session can't store django class objects, only
    # basic python data structures (at least, not without adding some elaborate serialization encoding and decoding)
    def get_ranked_results(self, point_queue):
        total_point_dict = {}
        
        items = point_queue.items()
        
        point_values = get_point_values()

        for participant, results in items:
            total_points_for_p = ((len(results['points_by_guess']) * point_values["guess_point_value"]) + 
                (len(results['points_by_movie_known']) * point_values["known_point_value"]) +
                (len(results['points_by_movie_unseen']) * point_values["unseen_point_value"]) + 
                (len(results['points_by_movie_liked']) * point_values["liked_point_value"]) +
                (len(results['points_by_movie_disliked']) * point_values["loathed_point_value"]))

            p_obj = User.objects.get(username__icontains=participant)
            p_movie = p_obj.related_movies.get(game_round=self.object, usermoviedetail__is_user_movie=True)
            avg_rating = p_movie.average_rating_incomplete # using the incomplete-allowed version here so we actually get a value to sort by for ties.
            if party_verbose:
                print("[jcw] avg_rating from average_rating_incomplete := {0}".format(avg_rating))

            total_point_dict[participant] = [total_points_for_p, avg_rating]

            if party_verbose:
                print("[jcw] total_points_for_p: %i, avg_rating: %f" % (total_points_for_p, avg_rating))

        # the dict created above has participant name as key, value is a list, first val in list is point total, second is avg movie score
        # now we sort the results of the dict we just built

        ranked_results = {k: v for k, v in sorted(total_point_dict.items(), reverse=True, key=lambda x : x[1])}

        # prepend an int value to each list, denoting the final rank value of that participant key
        r = 1
        for key, value in ranked_results.items():
            value.insert(0, r)  # at index 0, insert value of r, that is, using insert() to 'prepend' to list
            r += 1

        # final ranked_results dict contains: key - participant name, value - list with THREE items: rank, point total, avg rating of movie choice

        # just as a side-note, if you wanted to create a new dictionary that contained 'ranks' as keys with participant names as values,
        # just to have a simple package of 1: Jimmy, 2: Bimmy in a dict, you would do this:
        rank_only_dict = {rank: key for rank, key in enumerate(sorted(ranked_results, reverse=True, key=ranked_results.get), 1)}
        # note that this structure is different: 1. it does not use .items() 2. the key is the dict's .get method 3. rank, key are NOT key
        # value pairs from the dict! they are the enumerator index and the dict key -- because sorted returns dict keys by default.

        return ranked_results

    def calculate_guess_points(self, participant):

        point_values = get_point_values()

        points_by_guess = []

        round_movies = self.object.movies_from_round.all()

        participant_umds = [movie.usermoviedetail_set.get(user=participant) for movie in round_movies]


        for umd in participant_umds:
            user_that_chose_movie = UserMovieDetail.objects.get(movie=umd.movie, is_user_movie=True).user

            if umd.user_guess == user_that_chose_movie:   # can't compare against username, because in some cases value will be None (user record for movie they chose)
                point_dict = {
                    'point_value': point_values["guess_point_value"],
                    'point_string': 'Correctly guessed that {} chose {}'.format(umd.user_guess.username, umd.movie.name)
                }

                points_by_guess.append(point_dict)

        return points_by_guess


    def calculate_movie_points(self, participant):

        point_values = get_point_values()

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
                    'point_value': point_values['unseen_point_value'],
                    'point_string': '{} had not previously seen {}'.format(umd.user.username, umd.movie.name)
                }

                points_by_movie_unseen.append(point_dict_one)

            if umd.heard_of:
                point_dict_two = {
                    'point_value': point_values['known_point_value'],
                    'point_string': '{} had heard of {}'.format(umd.user.username, umd.movie.name)
                }

                points_by_movie_known.append(point_dict_two)


            if umd.star_rating == 1:
                point_dict_three = {
                    'point_value': point_values['loathed_point_value'],
                    'point_string': '{} gave {} the worst possible rating, 1 star.'.format(umd.user.username, umd.movie.name)

                }

                points_by_movie_disliked.append(point_dict_three)

            if umd.star_rating > 3:
                point_dict_four = {
                    'point_value': point_values['liked_point_value'],
                    'point_string': '{} rated {} higher than 3 stars.'.format(umd.user.username, umd.movie.name)
                }

                points_by_movie_liked.append(point_dict_four)


        return points_by_movie_known, points_by_movie_unseen, points_by_movie_liked, points_by_movie_disliked

# view for updating each UserRoundDetail object
class CommitUserRoundView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserRoundDetail
    template_name = 'movies/commit_user_round.html'
    context_object_name = 'urd_object'

    fields = ['correct_guess_points', 'known_movie_points', 'unseen_movie_points', 'liked_movie_points', 'disliked_movie_points', 'total_points', 'finalized_by_admin']

    login_url = 'login'
    # used by UserPassesTestMixin; verify user has admin prvileges (required to commit user round)
    def test_func(self):
        user = self.request.user
        return user.userprofile.is_mmg_admin   # returns True if userprofile object has is_mmg_admin True

    # note that you could use get_initial or get_object here
    # def get_object(self):
    #     obj = super().get_object()
    #     # modify obj as needed here
    #     obj.save(commit=False)  # we don't want anything committed until form_valid is called to submit & save object
    #                             # question: could we skip saving altogether here? would it still display?

    # per my research, it also seems you can override get_form_kwargs for the same result...

    def get_initial(self):
        """we want the form to display the current results, so we set initial data here"""
        initial = super().get_initial()

        # access sesssions data for the dictionary of round results
        point_queue = self.request.session['point_queue']
        ranked_results = self.request.session['ranked_results']

        this_user = self.object.user

        user_total_points = ranked_results[this_user.username][1]

        point_values = get_point_values()

        initial['correct_guess_points'] = (len(point_queue[this_user.username]['points_by_guess']) * point_values["guess_point_value"])
        initial['known_movie_points'] = (len(point_queue[this_user.username]['points_by_movie_known']) * point_values["known_point_value"])
        initial['unseen_movie_points'] = (len(point_queue[this_user.username]['points_by_movie_unseen']) * point_values["unseen_point_value"])
        initial['liked_movie_points'] = (len(point_queue[this_user.username]['points_by_movie_liked']) * point_values["liked_point_value"])
        initial['disliked_movie_points'] = (len(point_queue[this_user.username]['points_by_movie_disliked']) * point_values["loathed_point_value"])
        initial['total_points'] = user_total_points


        if party_verbose:
            print("[jcw] {0}".format(initial))

        return initial


    def update_user(self):
        """Update the UserProfile object with the data saved in UserRoundObject"""

        if party_verbose:
            print("[jcw] CommitUserRoundView.update_user: self: {0}".format(self))
            print("[jcw] CommitUserRoundView.update_user: self: {0}".format(type(self)))
            print("[jcw] CommitUserRoundView.update_user: self: {0}".format(self.__dict__))
        
        # we update the related UserProfile object with all the scoring values obtained for this round
        # UserProfile tracks global progress, not per-round.
        this_user = self.object.user
        this_user_name = this_user.username
        
        if party_verbose:
            print("[jcw] this_user: {0} this_user_name: {1}".format(this_user, this_user_name))

        user_rank = self.request.session['ranked_results'][this_user_name][0]  # first index of list is the rank int
        movie_avg = self.request.session['ranked_results'][this_user_name][2]  # third indexof list is their movie's avg rating
        if party_verbose:
            print("[jcw] user_rank: {0} movie_avg: {1}".format(user_rank, movie_avg))
    
        # get corresponding RoundRank object
        round_rank_object = RoundRank.objects.get(rank_int=user_rank) # there should be a 'task' to call the function that fills up the RoundRank table

        # assign the rank to the form's model (ForeignKey, rank is the 'one')
        # TEMP FORM form.instance.rank = round_rank_object
        # TEMP FORM form.instance.movie_average_rating = movie_avg  # this no longer works, because movie_avg will be 0

        # TEMP FORM if user_rank == 1:
            # TEMP FORM form.instance.winner_bool = True
            #user_profile.rounds_won += 1   # this logic has been moved to CommitGameRoundView's form_valid method

        # i'm removing the updates to total point fields in User Profile because 1. it's super buggy and 2. we don't even need / use them
        # update the related user profile, which stores global (all rounds) results
        # user_profile.total_correct_guess_points += form.instance.correct_guess_points
        # user_profile.total_known_movie_points += form.instance.known_movie_points
        # user_profile.total_unseen_movie_points += form.instance.unseen_movie_points
        # user_profile.total_liked_movie_points += form.instance.liked_movie_points
        # user_profile.total_disliked_movie_points += form.instance.disliked_movie_points

        #user_profile.save()

        # now we need to generate Point objects that will be related to this UserRoundDetail object, and store the relevant
        # string in their point_string field. These will be used to display detailed result data (the strings) later, in views
        # that have no access (naturally) to the session dict used in here.

        point_queue = self.request.session['point_queue']
        this_users_points = point_queue[this_user_name]


        # first, clear out (delete) any point object records that already exist for this user_round_object; otherwise
        # if an admin makes edits to the rounds point totals, then hits submit not for the first time, you will have a
        # duplicate set of point objects!
        if PointsEarned.objects.filter(user_round_ob=self.object).exists():
            PointsEarned.objects.filter(user_round_ob=self.object).all().delete()


        # think through how to do all of the below in *one* pass through the this_users_points dictionary; these five loops
        # are nearly identical -except- the distinction of point_type (stored by key) and the need to define that in the create() call;
        # we'd need a way to assign the key's value, e.g. 'points_by_movie_unseen' to the point_type field in the create call...

        # in case P has no points in the referenced list; empty list returns False
        if this_users_points['points_by_guess']:
            for point_dict in this_users_points['points_by_guess']:
                point_value = point_dict['point_value']
                point_string = point_dict['point_string']
                PointsEarned.objects.create(user_round_ob=self.object, point_int=point_value, point_type='guess', point_string=point_string)
        else:
            pass

        if this_users_points['points_by_movie_known']:
            for point_dict in this_users_points['points_by_movie_known']:         # using create() is just a convenience method that constructs the object and saves it all in one action
                point_value = point_dict['point_value']
                point_string = point_dict['point_string']
                PointsEarned.objects.create(user_round_ob=self.object, point_int=point_value, point_type='known', point_string=point_string)
        else:
            pass

        if this_users_points['points_by_movie_unseen']:
            for point_dict in this_users_points['points_by_movie_unseen']:
                point_value = point_dict['point_value']
                point_string = point_dict['point_string']
                PointsEarned.objects.create(user_round_ob=self.object, point_int=point_value, point_type='unseen', point_string=point_string)
        else:
            pass

        if this_users_points['points_by_movie_liked']:
            for point_dict in this_users_points['points_by_movie_liked']:
                point_value = point_dict['point_value']
                point_string = point_dict['point_string']
                PointsEarned.objects.create(user_round_ob=self.object, point_int=point_value, point_type='liked', point_string=point_string)
        else:
            pass

        if this_users_points['points_by_movie_disliked']:
            for point_dict in this_users_points['points_by_movie_disliked']:
                point_value = point_dict['point_value']
                point_string = point_dict['point_string']
                PointsEarned.objects.create(user_round_ob=self.object, point_int=point_value, point_type='disliked', point_string=point_string)
        else:
            pass
        
        # Update the record: get the values and apply them to the model object directly.
        initial = self.get_initial()
        
        if user_rank == 1:
            self.object.winner_bool = 1
        else:
            self.object.winner_bool = 0

        self.object.correct_guess_points  = initial['correct_guess_points']
        self.object.known_movie_points    = initial['known_movie_points']
        self.object.unseen_movie_points   = initial['unseen_movie_points']
        self.object.liked_movie_points    = initial['liked_movie_points']
        self.object.disliked_movie_points = initial['disliked_movie_points']
        self.object.total_points          = initial['total_points']

        self.object.rank_id               = round_rank_object
        self.object.movie_average_rating  = movie_avg 

        self.object.finalized_by_admin    = 1

        self.object.save()
        

    def form_valid(self, form):
        """Update the UserProfile object with the data saved in UserRoundObject"""

        if party_verbose:
            print("[jcw] CommitUserRoundView.form_valid: self: {0}".format(self))
            print("[jcw] CommitUserRoundView.form_valid: self: {0}".format(type(self)))
            print("[jcw] CommitUserRoundView.form_valid: self: {0}".format(self.object))
            print("[jcw] CommitUserRoundView.form_valid: self: {0}".format(type(self.object)))
            print("[jcw] CommitUserRoundView.form_valid: self: {0}".format(self.object.id))
            print("[jcw] CommitUserRoundView.form_valid: self: {0}".format(type(self.object.id)))
        # we update the related UserProfile object with all the scoring values obtained for this round
        # UserProfile tracks global progress, not per-round.
        this_user = self.object.user
        this_user_name = this_user.username
        #user_profile = this_user.userprofile    # one-to-one connection, reverse access syntax

        user_rank = self.request.session['ranked_results'][this_user_name][0]  # first index of list is the rank int
        movie_avg = self.request.session['ranked_results'][this_user_name][2]  # third indexof list is their movie's avg rating

        # get corresponding RoundRank object
        round_rank_object = RoundRank.objects.get(rank_int=user_rank) # there should be a 'task' to call the function that fills up the RoundRank table

        # assign the rank to the form's model (ForeignKey, rank is the 'one')
        form.instance.rank = round_rank_object
        form.instance.movie_average_rating = movie_avg  # this no longer works, because movie_avg will be 0

        if user_rank == 1:
            form.instance.winner_bool = True
            #user_profile.rounds_won += 1   # this logic has been moved to CommitGameRoundView's form_valid method

        # i'm removing the updates to total point fields in User Profile because 1. it's super buggy and 2. we don't even need / use them
        # update the related user profile, which stores global (all rounds) results
        # user_profile.total_correct_guess_points += form.instance.correct_guess_points
        # user_profile.total_known_movie_points += form.instance.known_movie_points
        # user_profile.total_unseen_movie_points += form.instance.unseen_movie_points
        # user_profile.total_liked_movie_points += form.instance.liked_movie_points
        # user_profile.total_disliked_movie_points += form.instance.disliked_movie_points

        #user_profile.save()

        # now we need to generate Point objects that will be related to this UserRoundDetail object, and store the relevant
        # string in their point_string field. These will be used to display detailed result data (the strings) later, in views
        # that have no access (naturally) to the session dict used in here.

        point_queue = self.request.session['point_queue']
        this_users_points = point_queue[this_user_name]


        # first, clear out (delete) any point object records that already exist for this user_round_object; otherwise
        # if an admin makes edits to the rounds point totals, then hits submit not for the first time, you will have a
        # duplicate set of point objects!
        if PointsEarned.objects.filter(user_round_ob=self.object).exists():
            PointsEarned.objects.filter(user_round_ob=self.object).all().delete()


        # think through how to do all of the below in *one* pass through the this_users_points dictionary; these five loops
        # are nearly identical -except- the distinction of point_type (stored by key) and the need to define that in the create() call;
        # we'd need a way to assign the key's value, e.g. 'points_by_movie_unseen' to the point_type field in the create call...

        # in case P has no points in the referenced list; empty list returns False
        if this_users_points['points_by_guess']:
            for point_dict in this_users_points['points_by_guess']:
                point_value = point_dict['point_value']
                point_string = point_dict['point_string']
                PointsEarned.objects.create(user_round_ob=self.object, point_int=point_value, point_type='guess', point_string=point_string)
        else:
            pass

        if this_users_points['points_by_movie_known']:
            for point_dict in this_users_points['points_by_movie_known']:         # using create() is just a convenience method that constructs the object and saves it all in one action
                point_value = point_dict['point_value']
                point_string = point_dict['point_string']
                PointsEarned.objects.create(user_round_ob=self.object, point_int=point_value, point_type='known', point_string=point_string)
        else:
            pass

        if this_users_points['points_by_movie_unseen']:
            for point_dict in this_users_points['points_by_movie_unseen']:
                point_value = point_dict['point_value']
                point_string = point_dict['point_string']
                PointsEarned.objects.create(user_round_ob=self.object, point_int=point_value, point_type='unseen', point_string=point_string)
        else:
            pass

        if this_users_points['points_by_movie_liked']:
            for point_dict in this_users_points['points_by_movie_liked']:
                point_value = point_dict['point_value']
                point_string = point_dict['point_string']
                PointsEarned.objects.create(user_round_ob=self.object, point_int=point_value, point_type='liked', point_string=point_string)
        else:
            pass

        if this_users_points['points_by_movie_disliked']:
            for point_dict in this_users_points['points_by_movie_disliked']:
                point_value = point_dict['point_value']
                point_string = point_dict['point_string']
                PointsEarned.objects.create(user_round_ob=self.object, point_int=point_value, point_type='disliked', point_string=point_string)
        else:
            pass

    def form_valid(self, form):
        return self.render_to_response(context)
        return super().form_valid(form) # call to super() saves the form, but not the user_profile we modify in the view


    def get_success_url(self):
        return reverse('movies:conclude_round', kwargs={'pk': self.object.game_round.pk})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        point_queue = self.request.session['point_queue']
        ranked_results = self.request.session['ranked_results']

        this_user_name = self.object.user.username # huge previous bug: you did self.request.user here, which is NOT the user you want
        this_user_total_points = ranked_results[this_user_name][1]  # this is just an int value, index 1 (point total) of the list value

        # can we remove the above total points variable, now that we are storing that data in the URD itself?
        # just print it from there, if you need it; then this method won't even need to access ranked_results at all...

        # extract this users points from the point_queue
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


class CommitGameRoundView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = GameRound
    template_name = 'movies/commit_game_round.html'
    context_object_name = 'game_round'
    #success_url = reverse_lazy('movies:conclude_round', kwargs={'pk': self.object.pk})

    fields = ['date_finished', 'winner', 'participants']

    login_url = 'login'
    # used by UserPassesTestMixin; verify user has admin prvileges (required to commit round)
    def test_func(self):
        user = self.request.user
        return user.userprofile.is_mmg_admin   # returns True if userprofile object has is_mmg_admin True


    def get_initial(self):
        initial = super().get_initial()

        winner_name = self.request.session['winner_name']

        winner = User.objects.get(username__icontains=winner_name)

        initial['winner'] = winner

        return initial

    # previous version of form_valid, does not make calls to UserProfile's update_all_data method, which means the admin
    # must manually hit the 'update all data' button on the Admin page after concluding a round to update UserProfile stats.
    def form_valid_old(self, form):
        # we have one additional task here: get the round winner and update their profile's rounds_won field
        # update: also calls assign_movie on movies related to this round.

        # I kept forgetting to input this manually on the form, so I'm making it automatic now:
        form.instance.round_completed = True    # we are committing the game round, so we set this to True automatically

        winner_name = self.request.session['winner_name']
        winner = User.objects.get(username__icontains=winner_name)
        winner_profile = winner.userprofile
        #update the profile to record the win
        winner_profile.rounds_won += 1
        winner_profile.save()

        round_movies = self.object.movies_from_round.all()

        for movie in round_movies:
            movie.assign_user()


        return super().form_valid(form)


    def form_valid(self, form):
        # we have one additional task here: get the round winner and update their profile's rounds_won field
        # update: added two more tasks: call update_all_data on user profiles, and assign_movie on movies.
        # this required changing the order of operations in this method, because the calls to the profile methods
        # must occur -after- the form / object has been saved (profile update data method only uses URD objects 
        # connected to a *completed* round; before the save, this round isn't completed!)

        # I kept forgetting to input this manually on the form, so I'm making it automatic now:
        form.instance.round_completed = True    # we are committing the game round, so we set this to True automatically
        form.instance.date_finished = date.today() # always forget to do this manually

        # this whole chunk is redundant now, because updating user profiles will update the profile.round_won field, which is
        # all this is doing -- you can therefore remove the next five lines of code (six including comment):
        winner_name = self.request.session['winner_name']
        winner = User.objects.get(username__icontains=winner_name)
        winner_profile = winner.userprofile
        #update the profile to record the win
        winner_profile.rounds_won += 1
        winner_profile.save()

        # grab movies related to this round and call their assign_movie method, so movies contain FK to user who chose them:
        round_movies = self.object.movies_from_round.all()

        for movie in round_movies:
            movie.assign_user()

        response = super().form_valid(form)     # call to super saves form and returns redirect object

        # do other stuff that can only be done after round has already been updated (saved) in database....

        # the following update_all_data calls must be made -after- form has been saved, or they won't include this round's URDs
        round_profiles = UserProfile.objects.filter(user__related_game_rounds=self.object) # get profiles of users in this round
        for p in round_profiles:
            p.update_all_data()


        # get urds to update movie avg (fix for Movie property side-effect); like all data calls above, MUST occur after
        # round has been saved (otherwise Movie average rating returns 0, becuase round_completed = False).
        # note: this will work for future submissions of game rounds, but won't work for already submitted rounds
        # where this code wasn't yet written; you'll need to manually updated those rounds, running same code below
        # in shell on server....
        urds = UserRoundDetail.objects.filter(game_round=self.object) # only get urds for current round

        # update the average rating field based on the 
        for urd in urds:
            urd.update_average_rating()


        return response     # the response is the redirect, so we return it

        # ALTERNATIVE APPROACH TO 'RE-ORDERING' THE BEHAVIOR OF THIS FORM_VALID METHOD:
        # do the work of the super() call manually: save the form, redirect to appropriate place. result is identical, and
        # no call to super() is needed:
        # form.save()
        # round_profiles = UserProfile.objects.filter(user__related_game_rounds=self.object)
        # for p in round_profiles:
        #     p.update_all_data()

        # return redirect(self.get_success_url)




    def get_success_url(self):
        return reverse('movies:conclude_round', kwargs={'pk': self.object.pk})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_round_details = UserRoundDetail.objects.filter(game_round=self.object)

        if ((UserRoundDetail.objects.filter(game_round=self.object, finalized_by_admin=False).count()) > 0 ):
            all_data_reviewed = False
        else:
            all_data_reviewed = True


        context['user_round_details'] = user_round_details
        context['all_data_reviewed'] = all_data_reviewed

        return context


class OldRoundView(LoginRequiredMixin, DetailView):
    model = GameRound
    template_name = 'movies/old_round_results.html'
    context_object_name = 'game_round'

    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        if ShallWeParty(kwargs):
            return redirect('/resultsparty/')
        
        # Otherwise dispatch as normal.
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #round_movies = self.object.movies_from_round.all()  # uses reverse manager defined in Movie model
        round_movies = self.object.movies_from_round.order_by('-date_watched') # uses reverse manager defined in Movie model
        #round_participants = self.object.participants.all() # not used now, since we loop through movies instead of participants to build user_movie_pairs


        user_round_details = UserRoundDetail.objects.filter(game_round=self.object).order_by('rank')

        avg_ratings_list = [(movie.average_rating, movie) for movie in round_movies]

        sorted_avg_ratings_list = sorted(avg_ratings_list, key=lambda x: x[0]) # is lambda neccessary? wouldn't it sort by first item in tuple anyway?

        most_hated_movie = sorted_avg_ratings_list[0][1]
        most_enjoyed_movie = sorted_avg_ratings_list[-1][1]

        # need to package user objects with their chosen movie, to loop through to show who chose what

        # user_movie_pairs = []
        # for participant in round_participants:

        #     p_movie = participant.related_movies.get(game_round=self.object, usermoviedetail__is_user_movie=True)

        #     user_movie_pairs.append((participant, p_movie))

        user_movie_pairs = []
        for movie in round_movies:
            p_who_chose = UserMovieDetail.objects.get(movie=movie, is_user_movie=True).user # .user is critical! get user, not umd object

            user_movie_pairs.append((p_who_chose, movie))


        context['user_round_details'] = user_round_details

        context['most_hated_score'] = sorted_avg_ratings_list[0][0]
        context['most_enjoyed_score'] = sorted_avg_ratings_list[-1][0]

        context['most_hated_movie'] = most_hated_movie
        context['most_enjoyed_movie'] = most_enjoyed_movie

        context['user_movie_pairs'] = user_movie_pairs


        return context


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
        user_profile = UserProfile.objects.get(user=user)  # you should probably just do user.userprofile, you have direct 1-to-1 access....

        if UserMovieDetail.objects.filter(user=user, movie=movie).exists():
            user_movie_details = UserMovieDetail.objects.get(user=user, movie=movie)
        else:
            user_movie_details = None

        # we simply build the form we want here, and pass it in the context; this works, even though this CBV is a
        # DetailView, not an edit view. When the form is processed, a different view will be called, process_details.
        form = UserMovieDetailForm(current_user=self.request.user)
        #form.fields['user_guess'].queryset = User.objects.filter(related_game_rounds=self.object.game_round) # this works! note: this is equivalent to movie.game_round

        results_ready = False

        game_round = movie.game_round

        # it's also worth noting that some of this stuff can be accessed in the template, through the base objects
        # in the context; check for redundancy...

        # movie object defines the M2M to users with field users - we can only access this after we KNOW all users have submitted details
        # (that's how is_user_movie gets updated) so this can only show if game_round is completed
        if game_round.round_completed:
            user_that_chose_movie = self.object.users.get(usermoviedetail__is_user_movie=True) # only one person marked True for *this specific movie*
            # same here for avg rating, only applies to a completed round:
            movie_average_rating = self.object.average_rating

            # get all UserMovieDetail objects for this movie so we can extract the Quotes and Ratings
            # use this version if you want to exclude the logged in user from results:
            #umds = UserMovieDetail.objects.filter(movie=self.object).exclude(user=user)
            umds = UserMovieDetail.objects.filter(movie=self.object)
            comments_for_movie = []
            ratings_for_movie = []

            guess_dicts = []
            non_guess_dicts = []

            for umd in umds:
                username = umd.user.username
                rating = umd.star_rating
                rating_dict = {'username': username, 'rating': rating}
                ratings_for_movie.append(rating_dict)

                guess_pair_dict = {}

                if umd.is_user_movie:
                    pass

                elif umd.user_guess == user_that_chose_movie:
                    guess_pair_dict['username'] = username
                    guess_pair_dict['guess'] = umd.user_guess
                    guess_pair_dict['result'] = 'Nailed It!'
                
                elif umd.user_guess != user_that_chose_movie and umd.user_guess != None:
                    guess_pair_dict['username'] = username
                    guess_pair_dict['guess'] = umd.user_guess
                    guess_pair_dict['result'] = 'Nope!'

                elif umd.user_guess == None:
                    non_guess_dict = {'username': username, 'guess': 'n/a', 'result': 'n/a'}
                    non_guess_dicts.append(non_guess_dict)

                if guess_pair_dict:    
                    guess_dicts.append(guess_pair_dict)
                # sort the guess_dicts by result so correct guess matches are listed first (this is just a dumb string-based
                # sort where Nailed It! evals as greater than Nope!)

                guess_dicts.sort(key=lambda x: x['result'])

                if umd.comments:
                    comment = umd.comments
                    comment_dict = {'username': username, 'comment': comment}
                    comments_for_movie.append(comment_dict)
                else:
                    pass

        else:
            user_that_chose_movie = None
            movie_average_rating = None
            comments_for_movie = None
            ratings_for_movie = None

            guess_dicts = None
            non_guess_dicts = None

            # Table-Level query to retreive same object above (user_that_chose_movie):
            #user_that_chose_movie = UserMovieDetail.objects.get(movie=uself.object, is_user_movie=True).user

        context['movie_comments'] = comments_for_movie
        context['movie_ratings'] = ratings_for_movie
        context['movie_avg_rating'] = movie_average_rating
        context['user_that_chose_movie'] = user_that_chose_movie
        context['game_round'] = game_round
        context['user_profile'] = user_profile
        context['user_movie_details'] = user_movie_details
        context['form'] = form
        context['results_ready'] = results_ready
        context['guess_dicts'] = guess_dicts
        context['non_guess_dicts'] = non_guess_dicts

        return context


class OldMovieDetail(LoginRequiredMixin, DetailView):
    """Unlike the MovieDetail view, this one has no form / form rendering, because this view is only called for a movie in -completed- round"""
    model = Movie
    template_name = 'movies/old_movie.html'
    context_object_name = 'movie'
    query_pk_and_slug = True

    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        if ShallWeParty(kwargs, 'old_movie'):
            return redirect('/resultsparty/')
        
        # Otherwise dispatch as normal.
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        user_profile = user.userprofile
        movie = self.object
        game_round = movie.game_round

        if UserMovieDetail.objects.filter(user=user, movie=movie).exists():
            user_movie_details = UserMovieDetail.objects.get(user=user, movie=movie)
        else:
            user_movie_details = None

        # technically this is unnecessary; this view is only called for movies in a completed round...
        if game_round.round_completed:
            user_that_chose_movie = self.object.users.get(usermoviedetail__is_user_movie=True)
            movie_average_rating = self.object.average_rating

            # get all UserMovieDetail objects for this movie so we can extract the Quotes
            # use this version if you want to exclude logged in user
            #umds = UserMovieDetail.objects.filter(movie=self.object).exclude(user=user) # could do a select_related on user here...
            umds = UserMovieDetail.objects.filter(movie=self.object)
            comments_for_movie = []
            ratings_for_movie = []

            guess_dicts = []
            non_guess_dicts = []

            for umd in umds:
                username = umd.user.username
                rating = umd.star_rating
                rating_dict = {'username': username, 'rating': rating}
                ratings_for_movie.append(rating_dict)

                guess_pair_dict = {}

                if umd.is_user_movie:
                    pass

                elif umd.user_guess == user_that_chose_movie:
                    guess_pair_dict['username'] = username
                    guess_pair_dict['guess'] = umd.user_guess
                    guess_pair_dict['result'] = 'Nailed It!'
                
                elif umd.user_guess != user_that_chose_movie and umd.user_guess != None:
                    guess_pair_dict['username'] = username
                    guess_pair_dict['guess'] = umd.user_guess
                    guess_pair_dict['result'] = 'Nope!'

                elif umd.user_guess == None:
                    non_guess_dict = {'username': username, 'guess': 'n/a', 'result': 'n/a'}
                    non_guess_dicts.append(non_guess_dict)

                if guess_pair_dict:    
                    guess_dicts.append(guess_pair_dict)
                # sort the guess_dicts by result so correct guess matches are listed first (this is just a dumb string-based
                # sort where Nailed It! evals as greater than Nope!)

                guess_dicts.sort(key=lambda x: x['result'])

                if umd.comments:
                    comment = umd.comments
                    comment_dict = {'username': username, 'comment': comment}
                    comments_for_movie.append(comment_dict)
                else:
                    pass
        else:
            user_that_chose_movie = None
            movie_average_rating = None
            comments_for_movie = None
            ratings_for_movie = None

            guess_dicts = None
            non_guess_dicts = None

        context['movie_comments'] = comments_for_movie
        context['movie_ratings'] = ratings_for_movie
        context['movie_avg_rating'] = movie_average_rating
        context['user_that_chose_movie'] = user_that_chose_movie
        context['game_round'] = game_round
        context['user_profile'] = user_profile
        context['user_movie_details'] = user_movie_details
        context['guess_dicts'] = guess_dicts
        context['non_guess_dicts'] = non_guess_dicts


        return context


@login_required
def process_details(request, movie_pk):
    """This is when the UMD is being created for the first time, as opposied to modifying existing record"""
    if request.method == 'POST':

        # verify that this usage of select_related is working as desired
        movie = Movie.objects.select_related('game_round').get(pk=movie_pk)

        # game_round is cached by select_related above, so this line does not perform a query on the db itself:
        game_round = movie.game_round    # connects to a single specific game_round instance

        # this doesn't really 'need' the current_user argument (in the sense that it's required, but won't be used),
        # as that is only used for how the form is displayed,
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
        # note: you also have to pass this to the Form in the Movie detail view!
        form = UserMovieDetailForm(instance=umd_object, current_user=request.user) # create the form, using data from existing object
        # filter users so only users that are participating in current round are displayed in guess choice:
        #form.fields['user_guess'].queryset = User.objects.filter(related_game_rounds=movie.game_round) # works!

    else:
        # POST request
        form = UserMovieDetailForm(instance=umd_object, data=request.POST, current_user=request.user)  # UserMovieDetailForm(request.POST, instance=umd_object) is also OK
        if form.is_valid():
            form.save()

            return redirect(movie) # this works because movie has a get_absolute_url method

    context = {'form': form, 'object': umd_object }
    return render(request, 'movies/update_details.html', context)


# utility function that is called by a 'fake form' (so it's a POST request) from admin page, to call the 
# update_all_data() model method on every existing instance of the UserProfile model.
def update_points(request):

    if not request.user.userprofile.is_mmg_admin:
        raise Http404

    # this view will never be called by a GET request
    if request.method == 'POST':

        for p in UserProfile.objects.all():
            p.update_all_data()               # model method updates the instance fields for all-time points

        return redirect('movies:members')


    if request.method != 'POST':
        raise Http404



# Q: how to get the modification of the form.fields performed in the functions up above (update_details) to work inside
# the CBV below....what method do I override to put it there? answer: use get_form() method
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


class MembersView(LoginRequiredMixin, ListView):
    def dispatch(self, request, *args, **kwargs):
        if ShallWeParty(kwargs):
            return redirect('/resultsparty/')
        
        # Otherwise dispatch as normal.
        return super().dispatch(request, *args, **kwargs)

    #queryset = User.objects.order_by('-userprofile__rounds_won').exclude(username__icontains='mmg_admin')
    queryset = UserProfile.objects.exclude(user__username__icontains='admin')
    template_name = 'movies/members.html'
    context_object_name = 'profiles'

    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profiles_by_round = self.queryset.order_by('-rounds_won')
        # annotate the profiles_by_guesses with actual # correct guesses, rather than use (x2) point total
        profiles_by_guesses = self.queryset.order_by('-total_correct_guess_points').annotate(correct_guesses=F('total_correct_guess_points') / 2)
        profiles_by_liked = self.queryset.order_by('-total_liked_movie_points')
        profiles_by_disliked = self.queryset.order_by('-total_disliked_movie_points')

        profiles_by_known = self.queryset.order_by('-total_known_movie_points')
        profiles_by_unseen = self.queryset.order_by('-total_unseen_movie_points')

        completed_game_rounds = GameRound.objects.filter(round_completed=True).order_by('-date_started')

        context['game_rounds'] = completed_game_rounds

        context['profiles_by_round'] = profiles_by_round
        context['profiles_by_guesses'] = profiles_by_guesses
        context['profiles_by_liked'] = profiles_by_liked
        context['profiles_by_disliked'] = profiles_by_disliked
        context['profiles_by_known'] = profiles_by_known
        context['profiles_by_unseen'] = profiles_by_unseen

        return context


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


class CreateRoundView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = GameRound
    template_name = 'movies/create_round.html'
    success_url = reverse_lazy('movies:settings')
    context_object_name = 'game_round'
    fields = ['round_number', 'round_completed', 'date_started', 'participants']

    login_url = 'login'
    # used by UserPassesTestMixin; verify user has admin prvileges (required to create round)
    def test_func(self):
        user = self.request.user
        return user.userprofile.is_mmg_admin   # returns True if userprofile object has is_mmg_admin True

    # we have an additional task to peform on the db related to the creation of this object, so override form_valid to do
    # the extra work:
    def form_valid(self, form):

        # if applicable, get the most recent GameRound object and 'de-activate' it
        if GameRound.objects.all().exists():
            previous_round = GameRound.objects.last() # current round we are creating in this view hasnt' been saved yet, so last item in list should be previously created round
            previous_round.active_round = False
            previous_round.save()

        # automatically set the new object to be the active round
        form.instance.active_round = True

        return super().form_valid(form) # newly created round is saved


class EditRoundView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = GameRound
    template_name = 'movies/edit_round.html'
    success_url = reverse_lazy('movies:settings')
    context_object_name = 'game_round'
    fields = ['round_number', 'active_round', 'round_completed', 'date_started', 'participants', 'date_finished']

    login_url = 'login'
    # used by UserPassesTestMixin; verify user has admin prvileges (required to edit a round)
    def test_func(self):
        user = self.request.user
        return user.userprofile.is_mmg_admin   # returns True if userprofile object has is_mmg_admin True


class TrophiesView(LoginRequiredMixin, ListView):
    model = Trophy
    template_name = 'movies/trophies.html'
    context_object_name = 'trophies'
    login_url = 'login'


