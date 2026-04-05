# FEAT-06: Achievement/Badge System

## Summary
Persistent achievements beyond per-round trophies — unlock conditions based on cumulative history.

## Proposed Achievements

### Round-Based
- **Perfect Round** — All guesses correct in a single round
- **Sweep** — Won with the highest score in every category
- **Comeback Kid** — Won after placing last in previous round

### Cumulative
- **Veteran** — Played 10/25/50 rounds (bronze/silver/gold)
- **Sharpshooter** — 75%+ guess accuracy across 5+ rounds
- **Crowd Pleaser** — Average movie rating > 4 stars across 5+ movies
- **Deep Hurter** — Chosen movie rated 1 star by 3+ people
- **The Enigma** — Nobody correctly guessed your movie 3 times

### Special
- **Founding Member** — Played in Round 1
- **Iron Streak** — Played in X consecutive rounds without missing one

## Model Design
```python
class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # CSS class or emoji
    tier = models.CharField(choices=[('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold')])

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    date_earned = models.DateTimeField(auto_now_add=True)
    round_earned = models.ForeignKey(GameRound, null=True, on_delete=models.SET_NULL)
```

### Steps
1. Create models and migration
2. Create achievement checker service (`movies/services/achievements.py`)
3. Hook checker into `CommitGameRoundView` (check after round completes)
4. Add achievements section to `UserProfileView`
5. Add achievements page listing all possible achievements
6. Show notification when achievement earned

## Effort: Medium-High (1-2 days)
