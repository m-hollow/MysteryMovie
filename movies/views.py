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

    # note: I only included this method so there would be a way to 'back out' of the editing view; I added
    # a 'go back' link that returns to the movie page, but that meant I needed this method so I'd have all
    # the values necessary for building the appropriate url. I note this, just so you're aware that this 
    # get_context_data has literaly no part in the form-updating functionality of this UpdateView CBV.

    # actually, it turns out NONE of this is necessary after all, becuase in the template I can simply access
    # the id and slug of the movie object through the UserMovieDetail object that the template already has
    # access to!   object.movie.pk  object.movie.slug      note that I'm only using object here because I didn't
    # bother to rename the context object in the attributes of this CVB.

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

    #     movie_id = self.object.movie.pk
    #     movie_slug = self.object.movie.slug

    #     context['movie_id'] = movie_id
    #     context['movie_slug'] = movie_slug

    #     return context

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



class TrophiesView(ListView):
    model = Trophy
    template_name = 'movies/trophies.html'
    context_object_name = 'trophies'


    




