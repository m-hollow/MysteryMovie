# BUG-07: Undefined Variable `idx` in PartyState Creation

## Severity: High

## Location
`movies/views.py` ~line 818

## Problem
```python
if PartyState.objects.count() == 0:
    record = PartyState(idx=idx, next_time=timezone.now())
```
The variable `idx` is never defined in this scope. This causes a `NameError` when creating the first PartyState record.

## Fix Plan

### Step 1: Determine what idx should be
- `idx` tracks the current film index in the Results Party
- When creating initial state, it should be `0` or `1` (depending on 0-indexed vs 1-indexed)
- Check how `idx` is used in `ResultsPartyView` and `ResultsPartyStateIncrement`

### Step 2: Fix the initialization
```python
if PartyState.objects.count() == 0:
    record = PartyState(idx=0, next_time=timezone.now())
    record.save()
```

### Step 3: Test
- Delete all PartyState records
- Trigger the code path that creates initial state
- Verify Results Party loads correctly

## Risk
Low — simple fix. The tricky part is determining the correct initial value (0 or 1).
