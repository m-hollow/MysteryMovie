# BUG-08: KeyError in Results Party When chosen_by_id is None

## Severity: High

## Location
`movies/views.py` ~line 414

## Problem
```python
'chosen_by_name': users_index[round_film.chosen_by_id]
```
If `chosen_by_id` is `None` (movie has no assigned chooser yet), this raises `KeyError` because `None` is not in `users_index`.

## Fix Plan

### Step 1: Use dict.get() with a default
```python
'chosen_by_name': users_index.get(round_film.chosen_by_id, 'Unknown')
```

### Step 2: Consider if this state should be prevented
- Should movies always have a `chosen_by` before the round concludes?
- If so, add validation in `ConcludeRoundView` to reject rounds with unassigned movies

### Step 3: Test
- Verify Results Party works when all movies have a chooser
- Verify graceful handling when a movie has no chooser

## Risk
Very low — single line change with `.get()`.
