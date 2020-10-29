from django.urls import path
from .views import (IndexPageView, MovieDetail, MembersView, AddMovieView, 
    process_details, update_details, UpdateDetailsView, TrophiesView, ResultsView, OldRoundsView, ConcludeRoundView, CommitUserRoundView, CommitGameRoundView, CreateRoundView, EditRoundView, SettingsView)

app_name = 'movies'
urlpatterns = [
    # Home Page
    path('', IndexPageView.as_view(), name='index'),
    path('movie/<int:pk>-<str:slug>/', MovieDetail.as_view(), name='movie'),
    path('members/', MembersView.as_view(), name='members'),
    path('add_movie/', AddMovieView.as_view(), name='add_movie'),

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
    path('commit_game_round/<int:pk>/', CommitGameRoundView.as_view(), name='commit_game_round)'),
    path('results/', ResultsView.as_view(), name='results'),
    path('old_rounds/', OldRoundsView.as_view(), name='old_rounds'),
    path('settings/', SettingsView.as_view(), name='settings'),
]



