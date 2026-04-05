# FEAT-07: Custom Scoring Rules

## Summary
Admin-configurable point values, seasonal rulesets, and optional handicap system.

## Design

### Configurable Point Values
Currently hardcoded in `get_point_values()`:
```python
{"liked_point_value": 2, "guess_point_value": 2, ...}
```

Move to a model:
```python
class ScoringConfig(models.Model):
    name = models.CharField(max_length=100)
    guess_points = models.PositiveSmallIntegerField(default=2)
    liked_points = models.PositiveSmallIntegerField(default=2)
    disliked_points = models.PositiveSmallIntegerField(default=2)
    unseen_points = models.PositiveSmallIntegerField(default=1)
    known_points = models.PositiveSmallIntegerField(default=1)
    is_default = models.BooleanField(default=False)
```

### Per-Round Override
Add FK to GameRound:
```python
scoring_config = models.ForeignKey(ScoringConfig, null=True, on_delete=models.SET_NULL)
```
If null, use default config.

### Handicap (Optional)
```python
class UserHandicap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game_round = models.ForeignKey(GameRound, on_delete=models.CASCADE)
    multiplier = models.DecimalField(default=1.0)  # 1.5 = 50% bonus
```

### Steps
1. Create ScoringConfig model
2. Migrate and seed with default values
3. Update point calculation to read from config
4. Add config management to admin settings page
5. (Optional) Add handicap model and integrate with scoring

## Effort: Medium (1 day)
