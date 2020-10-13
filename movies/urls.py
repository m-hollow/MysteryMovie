from django.urls import path
from .views import IndexPageView

app_name = 'movies'
urlpatterns = [
    # Home Page
    path('', IndexPageView.as_view(), name='index'),

]