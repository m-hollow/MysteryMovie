# IMP-07: Implement Proper Django Logging

## Current State
All debug output uses `print()`. No log levels, no structured output.

## Proposed Setup

### Settings Configuration
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'movies': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
    },
}
```

### Usage Pattern
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Round %s conclusion started", round.round_number)
logger.info("Points calculated for user %s: %d", user.username, total_points)
logger.warning("User %s has incomplete submissions", user.username)
logger.error("Failed to create PointsEarned: %s", str(e))
```

## Steps
1. Add LOGGING config to both development.py and production.py
2. Replace all `print()` calls with appropriate `logger.*()` calls
3. Remove the `party_verbose` flag — use log levels instead
4. Add logging to critical paths: round conclusion, point calculation, file uploads

## Effort: Low (2-3 hours)
