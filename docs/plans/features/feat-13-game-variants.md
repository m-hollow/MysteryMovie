# FEAT-13: Game Variants

## Summary
Alternative round formats to keep the game fresh.

## Proposed Variants

### Blind Round
- Players don't know who else is participating
- Guesses are harder — no process of elimination
- Implementation: Hide participant list from non-admin views during active round

### Theme Round
- Admin sets a theme: "Horror", "80s", "Foreign Language", etc.
- All movies must match the theme
- Add `theme` field to GameRound
- Display theme prominently on round page

### Director's Cut
- All movies by a single director
- Admin picks the director
- Special scoring: bonus points for obscure picks

### Team Mode
- Players split into teams of 2
- Team submits one movie together
- Points earned by team, not individual
- Requires: Team model, team assignment UI

## Model Changes
```python
# Add to GameRound
variant = models.CharField(
    max_length=20,
    choices=[
        ('standard', 'Standard'),
        ('blind', 'Blind'),
        ('theme', 'Theme'),
        ('directors', "Director's Cut"),
        ('team', 'Team'),
    ],
    default='standard'
)
theme_description = models.CharField(max_length=200, blank=True)
```

### Steps
1. Add variant field to GameRound
2. Implement Blind Round (hide participants — simplest variant)
3. Implement Theme Round (add theme display)
4. Consider Team Mode as a future phase (most complex)
5. Update CreateRoundView to allow variant selection

## Effort: Varies (Blind: low, Theme: low, Team: high)
