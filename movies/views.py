from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .models import (Movie, Trophy, UserProfile, UserMovieDetail, TrophyProfileDetail)
from .forms import AddMovieForm


class IndexPageView(ListView):
    queryset = Movie.objects.order_by('date_watched')
    template_name = 'movies/index.html'
    context_object_name = 'movies'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        date_today = timezone.now()

        context['date_today'] = date_today

        return context



class MovieDetail(DetailView):
    model = Movie
    template_name = 'movies/movie.html'
    context_object_name = 'movie'
    query_pk_and_slug = True



class MemberDetail(DetailView):
    pass



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


    




