# BUG-04: Bare except Clauses Hide Real Errors

## Severity: Critical

## Location
`movies/views.py` ~lines 495, 530

## Problem
Bare `except:` clauses catch everything — including SystemExit, KeyboardInterrupt, and MemoryError. The caught exceptions are handled with only `print("INSERT uid")`, completely hiding the real error.

## Fix Plan

### Step 1: Identify what exceptions are expected
- These are in the PartyState/PartyGoers AJAX handlers
- The expected exception is likely `PartyGoers.DoesNotExist` (user not yet registered)
- May also encounter `IntegrityError` on duplicate insert

### Step 2: Replace with specific exception handling
```python
try:
    pg = PartyGoers.objects.get(uid=uid)
    pg.last_ping = timezone.now()
    pg.save()
except PartyGoers.DoesNotExist:
    PartyGoers.objects.create(uid=uid, last_ping=timezone.now())
```
Or use `get_or_create()` / `update_or_create()` to avoid try/except entirely.

### Step 3: Add logging
- Replace `print()` with `logger.warning()` or `logger.info()` as appropriate

## Risk
Low — straightforward refactor. Use `update_or_create()` for the cleanest fix.
