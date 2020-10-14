from django.urls import path
from .views import IndexPageView, MovieDetail, MemberDetail, AddMovieView, TrophiesView

app_name = 'movies'
urlpatterns = [
    # Home Page
    path('', IndexPageView.as_view(), name='index'),
    path('movie/<int:pk>-<str:slug>/', MovieDetail.as_view(), name='movie'),
    path('member/<int:pk>-<str:slug>/', MemberDetail.as_view(), name='member'),
    path('add_movie/', AddMovieView.as_view(), name='add_movie'),
    path('trophies/', TrophiesView.as_view(), name='trophies'),
]

