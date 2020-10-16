from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model # why this instead of settings.AUTH_USER_MODEL ?
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .models import (Movie, GameRound, Trophy, UserProfile, UserMovieDetail, TrophyProfileDetail)
from .forms import AddMovieForm, UserMovieDetailForm


class IndexPageView(ListView):
    queryset = Movie.objects.order_by('-date_watched')
    template_name = 'movies/index.html'
    context_object_name = 'movies'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        date_today = timezone.now()

        context['date_today'] = date_today

        return context


class ResultsView(ListView):
    model = GameRound
    template_name = 'movies/results.html'
    context_object_name = 'game_rounds'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        current_round = context['game_rounds'].filter(active_round=True).last()

        movies = Movie.objects.filter()


        context['current_round'] = current_round

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
    model = get_user_model()
    template_name = 'movies/members.html'
    context_object_name = 'members'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_profile_pairs = []

        # get the profile for each user, store user and their profile as a tuple in master list
        for member in context['members']:
            profile = UserProfile.objects.get(user=member)
            user_profile_pairs.append((member, profile))

        context['user_profile_pairs'] = user_profile_pairs

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


class CreateRoundView(LoginRequiredMixin, CreateView):
    model = GameRound
    template_name = 'movies/create_round.html'
    success_url = reverse_lazy('movies:results')
    context_object_name = 'game_round'
    fields = ['active_round', 'round_completed', 'date_started', 'participants']

    login_url = 'login'

# the method below  is a good example of breaking up the normal flow of a form_valid method; we want to modify
# the object AFTER it is saved, but before the redirect. That's why the format of this is different
# than the other 'standard' form_valid methods used. Another good example is in the NoirDB User registration
# view. There are two possible approaches as documented on SO thread: 
# "Django CreateView: How to perform action upon save"
  
    def form_valid(self, form):

        self.object = form.save() # manually create the object instance so we can then modify it
        self.object.round_number = self.object.compute_round_number()
        return redirect(self.get_success_url())


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



