# BUG-20: Potential MultipleObjectsReturned on UserMovieDetail

## Severity: Low

## Location
`movies/views.py` ~line 275

## Problem
```python
p_who_chose = UserMovieDetail.objects.get(movie=movie, is_user_movie=True).user
```
Assumes exactly one UserMovieDetail per movie has `is_user_movie=True`, but the model doesn't enforce this with a constraint. If two users are both flagged as the chooser, this raises `MultipleObjectsReturned`.

## Fix Plan

### Step 1: Add model-level enforcement
Consider a partial unique constraint:
```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=['movie'],
            condition=models.Q(is_user_movie=True),
            name='unique_movie_chooser'
        )
    ]
```

### Step 2: Use filter().first() as defensive fallback
```python
chooser_detail = UserMovieDetail.objects.filter(movie=movie, is_user_movie=True).first()
p_who_chose = chooser_detail.user if chooser_detail else None
```

### Step 3: Verify existing data
Check for duplicates:
```python
from django.db.models import Count
UserMovieDetail.objects.filter(is_user_movie=True).values('movie').annotate(c=Count('id')).filter(c__gt=1)
```

## Risk
Low — adding the constraint may fail if duplicates exist in production data. Check data first.
