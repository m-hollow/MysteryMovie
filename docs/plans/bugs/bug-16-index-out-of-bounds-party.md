# BUG-16: Index Out of Bounds in Results Party

## Severity: Medium

## Location
`movies/views.py` ~line 454

## Problem
```python
context['current_film_index'] = round_films[PartyState.objects.last().idx-1].id
```
No bounds checking:
- If `idx` > `len(round_films)`, raises `IndexError`
- If `round_films` is empty, raises `IndexError`
- If no `PartyState` records exist, `.last()` returns `None` and `.idx` raises `AttributeError`

## Fix Plan

### Step 1: Add bounds checking
```python
party_state = PartyState.objects.last()
if party_state and round_films:
    idx = min(party_state.idx - 1, len(round_films) - 1)
    idx = max(idx, 0)
    context['current_film_index'] = round_films[idx].id
else:
    context['current_film_index'] = None
```

### Step 2: Handle None in template
Ensure the template handles `current_film_index` being `None` gracefully.

## Risk
Very low — defensive bounds checking.
