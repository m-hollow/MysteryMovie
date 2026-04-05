# BUG-18: print() Statements Left in Production Code

## Severity: Low

## Location
`movies/views.py` — lines 39, 150, 155, 412, and others throughout

## Problem
Debug `print()` calls scattered through production code. No structured logging, no log levels, output goes to stdout and clutters server logs.

## Fix Plan

### Step 1: Set up Django logging
In settings, configure logging:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'movies': {'handlers': ['console'], 'level': 'INFO'},
    },
}
```

### Step 2: Replace print() with logger calls
```python
import logging
logger = logging.getLogger(__name__)

# Replace:
print("current_round.round_completed:" + str(current_round.round_completed))
# With:
logger.debug("current_round.round_completed: %s", current_round.round_completed)
```

### Step 3: Remove debug-only prints
Some prints are purely debugging artifacts and should be removed entirely rather than converted to log calls.

## Risk
Very low — no behavior change.
