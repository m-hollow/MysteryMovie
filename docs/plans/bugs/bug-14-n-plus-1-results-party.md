# BUG-14: N+1 Query in Results Party View

## Severity: Medium

## Location
`movies/views.py` ~lines 386–422

## Problem
```python
for round_user in round_users:
    users_index[round_user.user_id] = round_user.user.username  # Extra query per user
```
Each iteration triggers a lazy load of the related `User` object.

## Fix Plan

### Step 1: Add select_related to queryset
```python
round_users = UserRoundDetail.objects.filter(
    game_round=current_round
).select_related('user')
```

### Step 2: Also check for similar patterns
- Search for `.user.username` patterns after queryset loops
- Add `select_related` or `prefetch_related` where needed
- Check `ResultsView`, `OldRoundView`, `MembersView` for similar issues

## Risk
Very low — `select_related` is additive and doesn't change behavior.
