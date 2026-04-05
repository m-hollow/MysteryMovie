# IMP-05: Add select_related/prefetch_related to All Views

## Current State
Views iterate over querysets and access ForeignKey/M2M relations without optimization, causing N+1 queries.

## Known Problem Spots
1. **ResultsPartyView** (~line 386): `round_user.user.username` in loop
2. **ResultsView** (~line 210): Nested loop checking UserMovieDetail for each movie × participant
3. **OverviewView** (~line 133): `movie.average_rating` property in sort lambda
4. **MovieDetail**: Accessing `umd.user`, `umd.movie` in loops
5. **MembersView**: Accessing `profile.user` in loops

## Fix Pattern
For ForeignKey access in loops:
```python
# Before
for detail in UserRoundDetail.objects.filter(game_round=round):
    print(detail.user.username)  # Extra query per iteration

# After
for detail in UserRoundDetail.objects.filter(game_round=round).select_related('user'):
    print(detail.user.username)  # No extra queries
```

For M2M access:
```python
queryset = UserRoundDetail.objects.filter(...).prefetch_related('trophies_won')
```

## Steps
1. Install `django-debug-toolbar` query panel (already in requirements)
2. Navigate each major view in development mode
3. Identify all N+1 patterns from the toolbar
4. Add `select_related` / `prefetch_related` to each queryset
5. Verify query count reduction in toolbar

## Effort: Low-Medium (half day)
