# BUG-19: Python Sorting Instead of Database Ordering

## Severity: Low

## Location
`movies/views.py` ~line 133

## Problem
```python
queryset = sorted(Movie.objects.all(), key=lambda x: x.average_rating, reverse=True)
```
This:
1. Loads ALL movies into memory
2. Calls `average_rating` property on each (which runs an aggregate DB query)
3. Sorts in Python — O(n log n) with n DB queries

## Fix Plan

### Step 1: Use database-level annotation and ordering
```python
from django.db.models import Avg

queryset = Movie.objects.annotate(
    avg_rating=Avg('usermoviedetail__star_rating')
).order_by('-avg_rating')
```

### Step 2: Update template references
If the template uses `movie.average_rating`, it can now use `movie.avg_rating` (the annotated field), avoiding the property's extra query.

### Step 3: Apply same pattern to other sorted views
Check if `MembersView` or other views do similar Python-level sorting.

## Risk
Low — annotate/order_by is the standard Django pattern. Verify results match the property calculation.
