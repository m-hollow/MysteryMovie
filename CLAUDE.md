# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mystery Movie Club ("MMG") — a Django web app for a movie guessing game. Players secretly submit movies, the group watches them, then players guess who chose each film and rate them. Points and trophies are awarded. Production site: clubprotean.com (hosted on PythonAnywhere).

## Development Commands

```bash
# All Django commands require the --settings flag
python3 manage.py runserver --settings=mmg.settings.development
python3 manage.py migrate --settings=mmg.settings.development
python3 manage.py makemigrations --settings=mmg.settings.development
python3 manage.py shell --settings=mmg.settings.development
python3 manage.py createsuperuser --settings=mmg.settings.development

# Install dependencies
pip3 install -r requirements.txt
```

There is no test suite, linter, or CI pipeline configured. The `movies/tests.py` and `users/tests.py` files exist but are empty.

## Environment Setup

Requires a `.env` file in the project root with: `SECRET_KEY`, `DEBUG`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. Database is MySQL. After first migration, seed data via the Django shell:

```python
from movies.utility_functions import create_ranks, add_trophies
create_ranks()    # RoundRank entries (1st-10th)
add_trophies()    # Default Trophy entries
```

## Architecture

### Settings Module

Settings are split into `mmg/settings/development.py` and `mmg/settings/production.py` (no shared base). Both add an extra `.parent` to `BASE_DIR` because the settings file is nested one level deeper than Django's default. The `__init__.py` is empty — Django doesn't auto-discover the right settings file; it must be specified via `--settings`.

### Two Django Apps

- **`movies/`** — All game logic. Contains all models, the bulk of views (20+ view classes/functions), forms, templates, URL routing, and scoring logic. This is where nearly all development happens.
- **`users/`** — Thin authentication wrapper. Uses Django's built-in auth URLs; registration is currently disabled (route commented out in `users/urls.py`).

### Key Model Relationships

The data model centers on a round-based game flow:

- `GameRound` has participants via M2M through `UserRoundDetail` (per-user scoring for that round)
- `Movie` belongs to a `GameRound`; has users via M2M through `UserMovieDetail` (ratings, guesses, comments)
- `UserProfile` is a OneToOne extension of Django's `User` (auto-created via signal in `movies/signals.py`), storing all-time cumulative stats
- `PointsEarned` records are children of `UserRoundDetail`, storing individual point descriptions
- `PartyState` / `PartyGoers` manage real-time state for the Results Party feature (polling-based sync)

### Active Round Pattern

Many views depend on `GameRound.objects.filter(active_round=True).last()` to find the current round. Only one round should have `active_round=True` at a time. Views check `round_completed` to determine whether to show active game pages or read-only results.

### Admin vs Django Admin

The app has its own admin concept (`UserProfile.is_mmg_admin`) separate from Django's `is_staff`/`is_superuser`. Views that perform admin functions (conclude round, commit scores, settings) check `is_mmg_admin` via `UserPassesTestMixin`. The round lifecycle is: Create Round -> Players submit movies/details -> Conclude Round -> Commit User Rounds -> Commit Game Round.

### Results Party

The Results Party (`resultsparty/`) is a synchronized reveal feature using polling. `PartyState` tracks a global index (which movie is being revealed), and `PartyGoers` tracks individual user heartbeats. The `ShallWeParty()` function in views.py gates access — if the active round is completed and the party index hasn't advanced past all films, users get redirected to the party page.

### Frontend

Django templates with Bootstrap 4, crispy-forms, and jQuery UI. The base template is `movies/templates/movies/base.html`. No JavaScript build system — scripts are inline or served from static files.

### Media Files

Movie posters: `media/movie/<movie_id>.jpg`. User profile pics: `media/user/<user_id>`. The `media/` directory is gitignored. Static fallback images exist for missing media.
