from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model # why this instead of settings.AUTH_USER_MODEL ?
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.urls import reverse, reverse_lazy
from django.utils import timezone

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


# I couldn't make this a DetailView, because that requires a pk argument to be capture by the URL, and 
# this view is called from base.html, and afaik I have no ability to pass an argument such as a pk in base.html,
# because I have no view for rendering it; the Results link in the navbar would need an <int:pk> in the url, which
# I can certainly add to the URL, but how do I -pass- an argument to that URL from the base.html template ? it has
# no access to results objects, and I have no view to provide it with that context...
class ResultsView(ListView):
    model = GameRound
    template_name = 'movies/results.html'
    context_object_name = 'game_rounds'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # the context has already been built by the 'get_queryset' method (in parent), and the
        # queryset is stored as 'game_rounds' per context_object_name attribute above.
        
        # this is a HUGE and kinda ungainly if block; is there a better way to organize the logic contained below?

        if context['game_rounds'].filter(active_round=True).exists():
            current_round = context['game_rounds'].filter(active_round=True).last()

        # would the template be able to loop through current_round.
            current_round_movies = current_round.movies_from_round.all()  # uses reverse manager defined in Movie model

            current_round_participants = current_round.participants.all() # get User objects related to current GameRound

            # get UserProfile, UserMovieDetail, UserRoundDetail for each participant user:
            
            round_results = []
            missing_details = []   # should this be a dict instead? think it through...
            
            # IMPORTANT TO-DO:
            # this would be a great place to look into use select_related and prefetch_related to cut down on db hits!
            # I see all kinds of places in here where 'related' objects are being directly accessed after the original
            # relation has already been loaded...you want to 'pre-load' all those additional related objects.

            for participant in current_round_participants.all():
                participant_package = {
                    'user': participant,
                    'profile': participant.userprofile,    # note that it's 'userprofile', the lower case of the other end of the One-to-One
                    'user_round_details': participant.userrounddetail_set.get(game_round=current_round),
                    'user_movie_details_list': [],
                } 
                
                for movie in current_round_movies:
                    
                    if movie.usermoviedetail_set.filter(user=participant).exists():  # exists() only works with filter(), not get() !!!
                        user_movie_details = movie.usermoviedetail_set.get(user=participant)
                        participant_package['user_movie_details_list'].append(user_movie_details)
                    else:
                        # this is the case in which the User has not yet submitted details for the given movie
                        # should you pass the actual objects in here, or just the relevant names?
                        missing_details.append((participant.username, movie.name ))

                round_results.append(participant_package)


            # generally I don't like this approach of the template having different context items depending on
            # conditional paths; I think it should always reliably have the same set of objects, and if some aren't
            # available, they are still listed in the context, but with value None. thus I've moved it to after the
            # conditional check, and the else block handles setting missing values accordingly.
            # context['missing_details'] = missing_details
            # context['current_round_movies'] = current_round_movies

        else:
            missing_details = None
            current_round_movies = None
            current_round = None
            round_results = None


        # note: for 1 round, there is 6 movies, which means you'll have 6 UserMovieDetail objects per user,
        # but only ONE UserRoundDetail object per user.

        context['missing_details'] = missing_details
        context['current_round_movies'] = current_round_movies
        context['current_round'] = current_round 
        context['round_results_by_participant'] = round_results # round_results is a list of dictionaries.


        return context


# a helper function called by the Results view to compute points from round



class MovieDetail(LoginRequiredMixin, DetailView):
    model = Movie
    template_name = 'movies/movie.html'
    context_object_name = 'movie'
    query_pk_and_slug = True

    login_url = 'login' # only used by LoginRequiredMixin, if unauthorized access attempted


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        movie = self.object

        # put exception handling here, or use GetObjectOr404...
        user_profile = UserProfile.objects.get(user=user)

        if UserMovieDetail.objects.filter(user=user, movie=movie).exists():
            user_movie_details = UserMovieDetail.objects.get(user=user, movie=movie)
        else:
            user_movie_details = None
            # user_movie_details = UserMovieDetail(user=user, movie=movie)
            # user_movie_details.save()

        form = UserMovieDetailForm()

        results_ready = False       # idea: create a 'Rounds' table in the db. 
                                    # you need a 'state' variable called results_ready that 
                                    # applies to the -entire round-. 
                                    # then, on an admin level, you have a button to flip that
                                    # value to True, and then results will appear across the
                                    # entire site.


        # add the current game round to the context, so you can check if it's been completed or not,
        # and display the results if so. Note: this will replace 'results ready' below.
        # you can retreive the round through the Movie object, that's a direct connection

        game_round = movie.game_round   # this retrieves the object, right? it's an FK field, many-to-one, so there
                                        # is only one possible GameRound record to retrieve here; still make sure this
                                        # assignment is actually assigning the game round object!


        # it's also worth noting that some of this stuff can be accessed in the template, through the base objects
        # in the context; e.g. since this template has Movie object by default, you could access gameround in the template
        # using movie.game_round -- so there's no real need to package it individually here, it's probably not efficient.
        # I think the point of accessing things here in the view is if you need to do something more complicated with
        # them, but if it's just to access it, store it in a name, and pass it in the context -- it's probably redundant.

        context['game_round'] = game_round
        context['user_profile'] = user_profile
        context['user_movie_details'] = user_movie_details
        context['form'] = form
        context['results_ready'] = results_ready

        return context

@login_required
def process_details(request, movie_pk):
    
    if request.method == 'POST':

        movie = Movie.objects.get(pk=movie_pk)

        form = UserMovieDetailForm(data=request.POST)

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


class UpdateDetailsView(LoginRequiredMixin, UpdateView):
    model = UserMovieDetail
    template_name = 'movies/update_details.html'
    form_class = UserMovieDetailForm

    login_url = 'login' # used by LoginRequiredMixin

    # why reverse instead of redirect()? because the CVB is handling the redirect itself. this method simply 
    # supplies the URL that the CBV will redirect to. when you write a non-CBV function based view, you use redirect;
    # the CBV is probably taking the value returned by get_success_url and calling HTTPResponseRedirect on it (I say
    # that rather than redirect() becuase redirect() includes a reverse, which would be redundant here since get_success_url
    # is handling the reverse part....

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
# "Django CreateView: How to perform action upon save"
  
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


    
# TO DO
# you need an admin page that only you and john will use, on which you can:
# add movies
# add rounds
# edit rounds
# add trophies
# edit trophies
# I don't want a link up top, though



