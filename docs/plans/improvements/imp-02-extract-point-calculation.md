# IMP-02: Extract Point Calculation Into Service Layer

## Current State
Point calculation methods (`calculate_guess_points()`, `calculate_movie_points()`, `get_ranked_results()`) live as methods on `ConcludeRoundView`. They can only be called through the view's HTTP request cycle.

## Proposed Design
Create `movies/services/scoring.py`:
```python
class ScoringService:
    def __init__(self, game_round):
        self.game_round = game_round
        self.participants = UserRoundDetail.objects.filter(game_round=game_round)

    def calculate_guess_points(self, user_round_detail):
        """Calculate points for correct guesses."""
        ...

    def calculate_movie_points(self, user_round_detail):
        """Calculate points for movie ratings."""
        ...

    def get_ranked_results(self):
        """Rank all participants by total points."""
        ...

    def conclude_round(self):
        """Full round conclusion: calculate all points and rank."""
        ...
```

## Steps
1. Create `movies/services/` package with `__init__.py`
2. Extract scoring logic from ConcludeRoundView into ScoringService
3. Write unit tests for ScoringService (see IMP-04)
4. Update ConcludeRoundView to delegate to ScoringService
5. Update CommitUserRoundView and CommitGameRoundView similarly

## Benefits
- Testable without HTTP request context
- Reusable (e.g., from management commands, admin actions)
- Single source of truth for scoring rules

## Effort: Medium (1 day)
