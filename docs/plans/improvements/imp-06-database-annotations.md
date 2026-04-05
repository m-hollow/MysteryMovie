# IMP-06: Replace Property-Based Aggregation with Database Annotations

## Current State
`Movie.average_rating` is a Python property that runs `self.usermoviedetail_set.aggregate(Avg('star_rating'))` — a database query on every access. When displaying/sorting movie lists, this creates O(n) queries.

## Proposed Fix
Use Django ORM annotations in views instead of the property:
```python
movies = Movie.objects.filter(game_round=round).annotate(
    avg_rating=Avg('usermoviedetail__star_rating'),
    rating_count=Count('usermoviedetail__star_rating')
)
```

## Steps
1. Add annotation to `OverviewView.get_queryset()` for sorting
2. Add annotation to `ResultsView.get_context_data()` for display
3. Update templates to use `movie.avg_rating` (annotated field) instead of `movie.average_rating` (property)
4. Keep the `average_rating` property for backward compatibility in non-list contexts
5. Consider deprecating the property with a comment

## Affected Views
- `OverviewView` — sorting by rating
- `ResultsView` — displaying best/worst movies
- `OldRoundView` — displaying archived results
- `UserProfileView` — displaying user's movie stats

## Effort: Low (2-3 hours)
