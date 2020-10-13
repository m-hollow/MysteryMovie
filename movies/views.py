from django.shortcuts import render, redirect

from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from .models import (Movie, Trophy, UserProfile, UserMovieDetail, TrophyProfileDetail)

class IndexPageView(TemplateView):
    template_name = 'movies/index.html'



