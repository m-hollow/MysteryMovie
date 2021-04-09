from django.urls import path
from django.views.generic.base import RedirectView

from .views import (IndexPageView, MovieDetail, OldMovieDetail, MembersView, AddMovieView,
    process_details, update_details, UpdateDetailsView, TrophiesView, ResultsView, OldRoundView, 
    ConcludeRoundView, CommitUserRoundView, CommitGameRoundView, CreateRoundView, EditRoundView, 
    SettingsView, UserResultsView, update_points, UserProfileView, OverviewView)

app_name = 'movies'
urlpatterns = [
    # Home Page
    #path('', RedirectView.as_view(url='/users/login/')), # base url redirects to default auth login at users/login/
    path('', IndexPageView.as_view(), name='index'),
    path('movie/<int:pk>-<str:slug>/', MovieDetail.as_view(), name='movie'),
    path('old_movie/<int:pk><str:slug>/', OldMovieDetail.as_view(), name='old_movie'), # distinguish between a movie in current round & previous round
    path('members/', MembersView.as_view(), name='members'),
    path('add_movie/', AddMovieView.as_view(), name='add_movie'),

    path('overview/', OverviewView.as_view(), name='overview'),
    # note that this view does not render a page; the relevant form is rendered by the 'movie' view,
    # and then THIS view is called as a POST request when the form is submitted:
    path('add_details/<int:movie_pk>/', process_details, name='add_details'),

    # this one, on the other hand, renders its own page, update_details.html
    #path('update_details/<int:pk>/', UpdateDetailsView.as_view(), name='update_details'),

    path('update_details/<int:umd_pk>/', update_details, name='update_details'),

    path('trophies/', TrophiesView.as_view(), name='trophies'),
    path('create_round/',CreateRoundView.as_view(), name='create_round'),
    path('edit_round/<int:pk>/', EditRoundView.as_view(), name='edit_round'),
    path('conclude_round/<int:pk>/', ConcludeRoundView.as_view(), name='conclude_round'),
    path('commit_user_round/<int:pk>/', CommitUserRoundView.as_view(), name='commit_user_round'),
    path('commit_game_round/<int:pk>/', CommitGameRoundView.as_view(), name='commit_game_round'),
    path('results/', ResultsView.as_view(), name='results'),
    path('old_round_results/<int:pk>/', OldRoundView.as_view(), name='old_round_results'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('settings/update_points/', update_points, name='update_points'),
    path('user_results/<int:pk>/', UserResultsView.as_view(), name='user_results'),
    path('user_profile/<int:pk>/', UserProfileView.as_view(), name='user_profile'),
]




