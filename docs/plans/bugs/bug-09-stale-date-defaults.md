# BUG-09: Date Fields Use Potentially Stale Defaults

## Severity: High

## Location
`movies/models.py` ~lines 26, 29, 176

## Problem
```python
date_started = models.DateField(default=date.today, null=True)
date_finished = models.DateField(default=date.today, null=True)  # GameRound
date_watched = models.DateField(default=date.today, null=True)   # Movie
```
While `default=date.today` (without parentheses) is technically correct — it passes the callable — the design is questionable:
- `date_finished` defaults to today even though the round hasn't finished yet
- `date_watched` defaults to today even for movies not yet watched
- Code comments acknowledge this is wrong but it was never fixed

## Fix Plan

### Step 1: Remove defaults for dates that shouldn't auto-populate
```python
date_started = models.DateField(null=True, blank=True)
date_finished = models.DateField(null=True, blank=True)
date_watched = models.DateField(null=True, blank=True)
```

### Step 2: Set dates explicitly in views
- `date_started`: Set when admin creates a round
- `date_finished`: Set when admin concludes a round
- `date_watched`: Set when admin marks a movie as watched

### Step 3: Update forms
- Ensure CreateRoundView and EditRoundView forms include date fields
- Add sensible defaults in form initial data if needed

### Step 4: Migration
```bash
python3 manage.py makemigrations movies
python3 manage.py migrate
```

## Risk
Medium — existing records may have incorrect dates. This changes form behavior so admin workflow needs testing.
