from django.contrib import admin

from .models import (Movie, GameRound, Trophy, UserProfile, UserMovieDetail, TrophyProfileDetail)

admin.site.register(Movie)
admin.site.register(GameRound)
admin.site.register(Trophy)
admin.site.register(UserProfile)
admin.site.register(UserMovieDetail)
admin.site.register(TrophyProfileDetail)



