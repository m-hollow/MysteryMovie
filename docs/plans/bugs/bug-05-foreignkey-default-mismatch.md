# BUG-05: ForeignKey Default Value Mismatch on Movie.game_round

## Severity: High

## Location
`movies/models.py` ~line 169

## Problem
`game_round = models.ForeignKey(GameRound, default="", on_delete=models.CASCADE, ...)` — an empty string is not a valid value for a ForeignKey. Django expects either `None` (if nullable) or a valid PK. This will cause `ValueError` or `IntegrityError` when creating a Movie without explicitly passing `game_round`.

## Fix Plan

### Step 1: Determine if game_round should be optional
- Check all places Movies are created (AddMovieView, any admin forms)
- If game_round is always provided explicitly, remove the default entirely
- If it should be optional, use `null=True, blank=True, default=None`

### Step 2: Update the model field
Most likely fix:
```python
game_round = models.ForeignKey(GameRound, on_delete=models.CASCADE, related_name='movies_from_round')
```
(Remove `default=""` entirely — the form requires it anyway.)

### Step 3: Create and run migration
```bash
python3 manage.py makemigrations movies
python3 manage.py migrate
```

### Step 4: Test
- Create a movie through AddMovieView
- Verify it saves correctly with the game_round FK

## Risk
Low if default is simply removed. Medium if changing to nullable (requires checking all queries that assume non-null).
