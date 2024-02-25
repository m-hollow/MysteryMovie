from django.urls import path, include
from .views import RegisterView

urlpatterns = [
    # Include the default auth urls (login, logout, etc)
    path('', include('django.contrib.auth.urls')),
    # Registration needs to be manually defined
    # path('register/', RegisterView.as_view(), name='register'), # removed 2/25/24 !!
]
