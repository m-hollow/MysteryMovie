# IMP-04: Add Test Suite

## Current State
Both `movies/tests.py` and `users/tests.py` are empty. Zero test coverage.

## Test Strategy

### Priority 1: Model Tests
- Point calculation correctness (scoring service once extracted)
- Model constraints and validation
- `UserProfile.update_all_data()` accuracy
- `Movie.average_rating` property
- Signal handlers (UserProfile auto-creation)

### Priority 2: View Tests
- Authentication required on all views
- Admin-only views reject non-admin users
- Round conclusion workflow (conclude → commit user → commit game)
- Form validation (AddMovieForm, UserMovieDetailForm)
- Results Party state transitions

### Priority 3: Integration Tests
- Full round lifecycle: create → add movies → submit details → conclude → commit
- Point totals match expected values for known test data
- User profile all-time stats update correctly

### Priority 4: Edge Cases
- Empty rounds (no movies, no participants)
- Movies with no ratings
- Users who haven't submitted all details
- Multiple active rounds (if constraint isn't added)

## Setup
```python
# movies/tests/__init__.py
# movies/tests/test_models.py
# movies/tests/test_views.py
# movies/tests/test_scoring.py
# movies/tests/test_integration.py
# movies/tests/factories.py  (test data factories)
```

Consider using `factory_boy` for test data generation.

## Effort: High (2-3 days for initial coverage, ongoing maintenance)
