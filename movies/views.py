from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model # why this instead of settings.AUTH_USER_MODEL ?
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .models import (Movie, Trophy, UserProfile, UserMovieDetail, TrophyProfileDetail)
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

        context['user_profile'] = user_profile
        context['user_movie_details'] = user_movie_details
        context['form'] = form

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


class MembersView(ListView):
    model = get_user_model()
    template_name = 'movies/members.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

    #     user_profiles =  

    #     # package user and profiles into tuples, just like you did for actors and roles
    #     # loop through the tuples in the template

    #     return context


# an old question: how to access the (already grabbed) queryset while inside get_context_data method? I know
# you did this before...

class AddMovieView(LoginRequiredMixin, CreateView):
    model = Movie
    template_name = 'movies/add_movie.html'
    context_object_name = 'movie'
    success_url = reverse_lazy('movies:index')   # this should later be udpated to go to new movie page itself

    form_class = AddMovieForm

    login_url = 'login' # only used by LoginRequiredMixin, if unauthorized access attempted



class TrophiesView(ListView):
    model = Trophy
    template_name = 'movies/trophies.html'
    context_object_name = 'trophies'


    




