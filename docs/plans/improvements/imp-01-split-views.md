# IMP-01: Split Monolithic views.py Into Modules

## Current State
`movies/views.py` is 2000+ lines containing 20+ view classes and functions covering all application logic.

## Proposed Structure
```
movies/views/
├── __init__.py           # Re-exports all views for URL compatibility
├── game.py               # IndexPageView, AddMovieView, MovieDetail, OldMovieDetail
├── rounds.py             # CreateRoundView, EditRoundView, EditRoundImagesView
├── scoring.py            # ConcludeRoundView, CommitUserRoundView, CommitGameRoundView
├── results.py            # ResultsView, OldRoundView, UserResultsView
├── party.py              # ResultsPartyView, party state/increment endpoints
├── members.py            # MembersView, TrophiesView
├── profiles.py           # UserProfileView, OverviewView
├── settings.py           # SettingsView, update_points
└── helpers.py            # ShallWeParty, get_point_values, shared utilities
```

## Steps
1. Create `movies/views/` directory
2. Move each logical group of views to its own module
3. Create `__init__.py` that imports and re-exports everything
4. Verify all URL patterns still resolve (no import changes needed in urls.py if __init__.py re-exports)
5. Run all URL patterns manually to verify nothing broke

## Risks
- Import paths in URL conf may need updating if __init__.py re-export is insufficient
- Shared helper functions need to be in a common module to avoid circular imports
- IDE references may break temporarily

## Effort: Medium (half day)
