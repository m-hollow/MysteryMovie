from django.contrib import admin

from .models import (Movie, GameRound, Trophy, UserProfile, UserMovieDetail, UserRoundDetail, TrophyProfileDetail, RoundRank, PointsEarned, AllTimeScore)

admin.site.register(GameRound)
admin.site.register(Movie)
admin.site.register(Trophy)
admin.site.register(UserProfile)
admin.site.register(UserMovieDetail)
admin.site.register(UserRoundDetail)
admin.site.register(TrophyProfileDetail)
admin.site.register(RoundRank)
admin.site.register(PointsEarned)
admin.site.register(AllTimeScore)


