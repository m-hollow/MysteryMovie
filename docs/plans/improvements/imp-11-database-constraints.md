# IMP-11: Add Database Constraints for Business Rules

## Current State
Business rules are enforced only in application code:
- Only one active round (no DB constraint)
- One chooser per movie (no DB constraint)
- Valid point ranges (no DB constraint)

## Proposed Constraints

### GameRound: One active round
```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=['active_round'],
            condition=models.Q(active_round=True),
            name='unique_active_round'
        )
    ]
```

### UserMovieDetail: One chooser per movie
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

### UserMovieDetail: Valid star rating
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(star_rating__gte=1, star_rating__lte=5),
            name='valid_star_rating'
        )
    ]
```

## Steps
1. Audit existing data for constraint violations
2. Fix any violations found
3. Add constraints to models
4. Create and run migrations
5. Test that violations are properly rejected

## Effort: Medium (half day)
