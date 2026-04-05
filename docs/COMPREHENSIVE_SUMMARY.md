# Mystery Movie Club — Comprehensive Project Summary

A complete analysis of the Mystery Movie Club codebase covering project history, current state, bugs, improvement opportunities, and feature ideas.

**Generated**: April 4, 2026
**Codebase**: MysteryMovie (Django 3.1.2 / Python 3 / MySQL)
**Production**: www.clubprotean.com

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [History at a Glance](#history-at-a-glance)
3. [Architecture & Tech Stack](#architecture--tech-stack)
4. [Bug Summary](#bug-summary)
5. [Improvement Summary](#improvement-summary)
6. [Feature Ideas Summary](#feature-ideas-summary)
7. [Recommended Action Plan](#recommended-action-plan)
8. [Document Index](#document-index)

---

## Project Overview

Mystery Movie Club is a Django web application for running a movie guessing game. Members secretly submit movies, watch them together, then guess who chose each film, rate them on a 1–5 "Deep Hurting" scale, and earn points. The player with the most points wins each round. A recently added "Results Party" feature provides a synchronized interactive reveal of round results.

### How the Game Works

1. Admin creates a round and adds participants
2. Each player secretly submits a movie
3. The group watches all movies over time
4. Players submit their ratings, guesses, and comments for each movie
5. Admin concludes the round — points are calculated automatically
6. Results are revealed via the interactive Results Party

### Point System

| Category | Points | Condition |
|----------|--------|-----------|
| Correct Guess | 2 | Correctly guessed who chose a movie |
| Liked Movie | 2 | Someone rated your movie > 3 stars |
| Disliked Movie | 2 | Someone rated your movie 1 star |
| Unseen Movie | 1 | Someone hadn't seen your movie before |
| Known Movie | 1 | Someone had heard of your movie |

---

## History at a Glance

| Phase | Period | Key Events |
|-------|--------|------------|
| Foundation | Oct 2020 | Django project created, core models, basic views |
| Core Features | Oct–Nov 2020 | Scoring system, rankings, trophies, round workflow |
| Deployment | Nov 2020 – Feb 2021 | Production deployment to PythonAnywhere (clubprotean.com) |
| Frontend Expansion | Feb–Jun 2021 | Members page, user profiles, overview sorting, bug fixes |
| Maintenance | Jun 2021 – Mar 2023 | ~2 year gap — app in active use but no development |
| UI Polish | Mar 2023 | Overview styling, member ranking improvements |
| Infrastructure | May–Aug 2023 | First PR, MySQL UTF-8 upgrade, README added |
| Results Party | Nov 2024 – Apr 2025 | Major feature: 8+ PRs, party state, cover art, profile pics |

**Contributors**: m-hollow (primary, 57 commits), John C. Worsley (13 commits, Results Party era), Corwin Light-Williams (4 commits, infrastructure)

**Total Commits**: ~74 across 4.5 years

See [HISTORY.md](HISTORY.md) for the full timeline.

---

## Architecture & Tech Stack

```
MysteryMovie/
├── mmg/                    # Django project config
│   └── settings/           # development.py / production.py
├── movies/                 # Main app (2000+ line views.py, 2000+ line models.py)
│   ├── models.py           # 12 models: GameRound, Movie, UserProfile, scoring, party
│   ├── views.py            # 20+ views: game, admin, results, party, profiles
│   ├── forms.py            # AddMovieForm, UserMovieDetailForm
│   ├── signals.py          # Auto-create UserProfile on User creation
│   ├── templates/movies/   # 20 HTML templates
│   └── migrations/         # 15 migrations
├── users/                  # Auth app (registration + Django auth)
└── requirements.txt        # Django 3.1.2, Bootstrap4, crispy-forms, mysqlclient
```

### Key Models

| Model | Purpose |
|-------|---------|
| GameRound | A round of the game with participants, dates, winner |
| Movie | Film entry with name, year, chooser, watch date |
| UserProfile | OneToOne with User — all-time stats, admin flag |
| UserRoundDetail | Per-user scoring for a round (points, rank, trophies) |
| UserMovieDetail | User's rating, guess, and flags for a movie |
| Trophy | Achievement awards with point values |
| PointsEarned | Detailed point breakdown records |
| PartyState / PartyGoers | Real-time Results Party state tracking |

### Admin Workflow

`Create Round` → `Add Movies` → `Users Submit Details` → `Conclude Round` → `Commit User Scores` → `Commit Game Round` → `Results Party`

---

## Bug Summary

**21 bugs identified** through static code analysis. See [BUGS.md](BUGS.md) for full details with file locations and line numbers.

### Critical (4)

| ID | Bug | Impact |
|----|-----|--------|
| BUG-01 | Unreachable code in `CommitUserRoundView.form_valid()` | User scores may never persist to database |
| BUG-02 | Unsafe profile picture upload — no type/size validation | Arbitrary file upload, resource leak |
| BUG-03 | Unsafe movie image upload — same issues as BUG-02 | Arbitrary file writes via admin |
| BUG-04 | Bare `except:` clauses hide all errors | Database failures silently ignored |

### High (5)

| ID | Bug | Impact |
|----|-----|--------|
| BUG-05 | ForeignKey `default=""` on Movie.game_round | Database error on Movie creation |
| BUG-06 | `__icontains` username lookup matches multiple users | Crashes or wrong user during round conclusion |
| BUG-07 | Undefined variable `idx` in PartyState creation | NameError when creating first party state |
| BUG-08 | KeyError when `chosen_by_id` is None | Results Party crashes on unassigned movies |
| BUG-09 | Date fields default to today inappropriately | Misleading dates on new rounds/movies |

### Medium (8)

| ID | Bug | Impact |
|----|-----|--------|
| BUG-10 | No constraint preventing multiple active rounds | UI shows wrong round data |
| BUG-11 | Missing CSRF protection on AJAX endpoints | Security vulnerability |
| BUG-12 | View methods missing `self` parameter | Fragile code that works by accident |
| BUG-13 | Hardcoded `success_url` to round 30 | Wrong redirect after image upload |
| BUG-14 | N+1 query in Results Party view | Slow page loads with many participants |
| BUG-15 | Production missing security headers | Cookies over HTTP, no HSTS |
| BUG-16 | Index out of bounds in Results Party | Crash if party index exceeds film count |
| BUG-17 | `manage.py` settings module ambiguous | May load wrong settings |

### Low (4)

| ID | Bug | Impact |
|----|-----|--------|
| BUG-18 | `print()` statements in production | Log clutter, no structured logging |
| BUG-19 | Python sorting instead of DB ordering | O(n) queries for movie sort |
| BUG-20 | Potential MultipleObjectsReturned on movie chooser | Crash if data has duplicates |
| BUG-21 | Commented-out code blocks throughout | Readability burden |

---

## Improvement Summary

**12 technical improvements** identified. See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for full details.

### High Priority

| ID | Improvement | Rationale |
|----|-------------|-----------|
| IMP-04 | Add test suite (zero coverage currently) | Foundation for safe changes |
| IMP-10 | Upgrade Django 3.1 → 5.2 LTS | Security patches, EOL since 2022 |
| IMP-08 | Security middleware configuration | HTTPS, secure cookies, HSTS |

### Medium Priority

| ID | Improvement | Rationale |
|----|-------------|-----------|
| IMP-01 | Split 2000-line views.py into modules | Maintainability |
| IMP-02 | Extract point calculation to service layer | Testability, reusability |
| IMP-05 | Add select_related/prefetch_related everywhere | Performance |
| IMP-07 | Replace print() with Django logging | Observability |

### Lower Priority

| ID | Improvement | Rationale |
|----|-------------|-----------|
| IMP-03 | Replace session-based state with DB transactions | Data reliability |
| IMP-06 | Database annotations instead of property queries | Performance |
| IMP-09 | Add CI/CD pipeline (GitHub Actions) | Automated quality |
| IMP-11 | Add database constraints for business rules | Data integrity |
| IMP-12 | Clean up dead/unused code | Code hygiene |

---

## Feature Ideas Summary

**16 feature ideas** proposed. See [FEATURE_IDEAS.md](FEATURE_IDEAS.md) for full details.

### Quick Wins (Low Effort, High Satisfaction)

| ID | Feature | Effort |
|----|---------|--------|
| FEAT-11 | Dark mode | Half day |
| FEAT-12 | Movie poster card layout | Half day |
| FEAT-05 | Historical greatest hits page | Half day |

### High Impact

| ID | Feature | Effort |
|----|---------|--------|
| FEAT-01 | OMDB API integration (auto-populate movie data) | 1-2 days |
| FEAT-08 | Email notification system | 1 day |
| FEAT-10 | Mobile-optimized interface | 1-2 days |

### Engagement & Gamification

| ID | Feature | Effort |
|----|---------|--------|
| FEAT-03 | Advanced statistics dashboard | 1-2 days |
| FEAT-06 | Achievement/badge system | 1-2 days |
| FEAT-09 | Comments & discussion threads | 1 day |
| FEAT-04 | Round analytics & heatmaps | 1 day |

### Fun Additions

| ID | Feature | Effort |
|----|---------|--------|
| FEAT-07 | Custom scoring rules | 1 day |
| FEAT-13 | Game variants (blind, theme, team) | Varies |
| FEAT-14 | Yearly recap & awards | 1-2 days |

### Platform & Integration

| ID | Feature | Effort |
|----|---------|--------|
| FEAT-16 | REST API (Django REST Framework) | 1-2 days |
| FEAT-15 | Slack/Discord bot | Half day – 3 days |
| FEAT-02 | Streaming availability links | Half day |

---

## Recommended Action Plan

### Phase 1: Stabilize (Fix Critical Bugs)

Address the 4 critical and 5 high-severity bugs. These affect data integrity and basic functionality.

1. **BUG-01** — Fix unreachable code in CommitUserRoundView (scoring may be broken)
2. **BUG-02 + BUG-03** — Add file upload validation (security)
3. **BUG-04** — Replace bare except clauses
4. **BUG-05** — Fix ForeignKey default
5. **BUG-06** — Replace `__icontains` with exact username match
6. **BUG-07** — Define `idx` variable for PartyState
7. **BUG-08** — Use `.get()` for chosen_by_id lookup

### Phase 2: Fortify (Security & Testing)

Establish the foundations for safe ongoing development.

1. **IMP-10** — Upgrade Django to a supported LTS version
2. **IMP-08** — Add security headers to production
3. **IMP-04** — Write initial test suite (focus on scoring logic)
4. **BUG-15** — Production security headers

### Phase 3: Refactor (Code Quality)

Make the codebase maintainable for continued development.

1. **IMP-01** — Split views.py into modules
2. **IMP-02** — Extract scoring into service layer
3. **IMP-07** — Implement proper logging
4. **IMP-05** — Optimize database queries
5. **BUG-18** — Remove print statements (part of IMP-07)

### Phase 4: Enhance (Features)

Build on the stable, tested, maintainable codebase.

1. **FEAT-11** — Dark mode (quick win)
2. **FEAT-12** — Poster card layout (quick win)
3. **FEAT-01** — OMDB integration (high impact)
4. **FEAT-03** — Statistics dashboard (engagement)
5. **FEAT-08** — Notifications (engagement)

---

## Document Index

### Root Documents

| File | Description |
|------|-------------|
| [README.md](README.md) | Project overview, setup guide, URL reference |
| [HISTORY.md](HISTORY.md) | Full development timeline (Oct 2020 – Apr 2025) |
| [BUGS.md](BUGS.md) | 21 bugs by severity with file locations |
| [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) | 12 technical improvements with priority matrix |
| [FEATURE_IDEAS.md](FEATURE_IDEAS.md) | 16 feature ideas with priority suggestions |
| [COMPREHENSIVE_SUMMARY.md](COMPREHENSIVE_SUMMARY.md) | This document |

### Bug Plans (21 files in `docs/plans/bugs/`)

| File | Bug |
|------|-----|
| [bug-01-commit-user-round-unreachable-code.md](docs/plans/bugs/bug-01-commit-user-round-unreachable-code.md) | Critical: Unreachable code in form_valid |
| [bug-02-unsafe-profile-pic-upload.md](docs/plans/bugs/bug-02-unsafe-profile-pic-upload.md) | Critical: No upload validation |
| [bug-03-unsafe-movie-image-upload.md](docs/plans/bugs/bug-03-unsafe-movie-image-upload.md) | Critical: No upload validation |
| [bug-04-bare-except-clauses.md](docs/plans/bugs/bug-04-bare-except-clauses.md) | Critical: Exceptions swallowed |
| [bug-05-foreignkey-default-mismatch.md](docs/plans/bugs/bug-05-foreignkey-default-mismatch.md) | High: Invalid FK default |
| [bug-06-unsafe-username-icontains.md](docs/plans/bugs/bug-06-unsafe-username-icontains.md) | High: Wrong user match |
| [bug-07-undefined-idx-partystate.md](docs/plans/bugs/bug-07-undefined-idx-partystate.md) | High: NameError crash |
| [bug-08-keyerror-chosen-by-none.md](docs/plans/bugs/bug-08-keyerror-chosen-by-none.md) | High: KeyError crash |
| [bug-09-stale-date-defaults.md](docs/plans/bugs/bug-09-stale-date-defaults.md) | High: Wrong default dates |
| [bug-10-multiple-active-rounds.md](docs/plans/bugs/bug-10-multiple-active-rounds.md) | Medium: No unique constraint |
| [bug-11-missing-csrf-ajax.md](docs/plans/bugs/bug-11-missing-csrf-ajax.md) | Medium: CSRF vulnerability |
| [bug-12-missing-self-parameter.md](docs/plans/bugs/bug-12-missing-self-parameter.md) | Medium: Fragile view binding |
| [bug-13-hardcoded-success-url.md](docs/plans/bugs/bug-13-hardcoded-success-url.md) | Medium: Wrong redirect |
| [bug-14-n-plus-1-results-party.md](docs/plans/bugs/bug-14-n-plus-1-results-party.md) | Medium: N+1 queries |
| [bug-15-missing-security-headers.md](docs/plans/bugs/bug-15-missing-security-headers.md) | Medium: No HTTPS enforcement |
| [bug-16-index-out-of-bounds-party.md](docs/plans/bugs/bug-16-index-out-of-bounds-party.md) | Medium: IndexError |
| [bug-17-manage-py-settings.md](docs/plans/bugs/bug-17-manage-py-settings.md) | Medium: Ambiguous settings |
| [bug-18-print-statements.md](docs/plans/bugs/bug-18-print-statements.md) | Low: No logging |
| [bug-19-python-sorting.md](docs/plans/bugs/bug-19-python-sorting.md) | Low: Slow sorting |
| [bug-20-multiple-movie-choosers.md](docs/plans/bugs/bug-20-multiple-movie-choosers.md) | Low: Missing constraint |
| [bug-21-commented-out-code.md](docs/plans/bugs/bug-21-commented-out-code.md) | Low: Dead code |

### Improvement Plans (12 files in `docs/plans/improvements/`)

| File | Improvement |
|------|-------------|
| [imp-01-split-views.md](docs/plans/improvements/imp-01-split-views.md) | Split monolithic views.py |
| [imp-02-extract-point-calculation.md](docs/plans/improvements/imp-02-extract-point-calculation.md) | Scoring service layer |
| [imp-03-replace-session-state.md](docs/plans/improvements/imp-03-replace-session-state.md) | DB transactions over sessions |
| [imp-04-add-test-suite.md](docs/plans/improvements/imp-04-add-test-suite.md) | Test coverage from zero |
| [imp-05-optimize-queries.md](docs/plans/improvements/imp-05-optimize-queries.md) | select_related everywhere |
| [imp-06-database-annotations.md](docs/plans/improvements/imp-06-database-annotations.md) | Replace property aggregations |
| [imp-07-implement-logging.md](docs/plans/improvements/imp-07-implement-logging.md) | Django logging framework |
| [imp-08-security-hardening.md](docs/plans/improvements/imp-08-security-hardening.md) | Production security headers |
| [imp-09-add-ci-cd.md](docs/plans/improvements/imp-09-add-ci-cd.md) | GitHub Actions pipeline |
| [imp-10-upgrade-django.md](docs/plans/improvements/imp-10-upgrade-django.md) | Django 3.1 → 5.2 LTS |
| [imp-11-database-constraints.md](docs/plans/improvements/imp-11-database-constraints.md) | Business rule constraints |
| [imp-12-cleanup-dead-code.md](docs/plans/improvements/imp-12-cleanup-dead-code.md) | Remove unused code |

### Feature Plans (16 files in `docs/plans/features/`)

| File | Feature |
|------|---------|
| [feat-01-movie-database-integration.md](docs/plans/features/feat-01-movie-database-integration.md) | OMDB API auto-populate |
| [feat-02-streaming-availability.md](docs/plans/features/feat-02-streaming-availability.md) | Where to watch links |
| [feat-03-advanced-statistics.md](docs/plans/features/feat-03-advanced-statistics.md) | Per-user analytics dashboard |
| [feat-04-round-analytics.md](docs/plans/features/feat-04-round-analytics.md) | Guess heatmaps, controversy |
| [feat-05-historical-greatest-hits.md](docs/plans/features/feat-05-historical-greatest-hits.md) | All-time leaderboards |
| [feat-06-achievement-badges.md](docs/plans/features/feat-06-achievement-badges.md) | Persistent achievement system |
| [feat-07-custom-scoring.md](docs/plans/features/feat-07-custom-scoring.md) | Configurable point values |
| [feat-08-notifications.md](docs/plans/features/feat-08-notifications.md) | Email alerts for game events |
| [feat-09-comments-discussion.md](docs/plans/features/feat-09-comments-discussion.md) | Post-round discussion threads |
| [feat-10-mobile-optimization.md](docs/plans/features/feat-10-mobile-optimization.md) | Responsive mobile redesign |
| [feat-11-dark-mode.md](docs/plans/features/feat-11-dark-mode.md) | Dark/light theme toggle |
| [feat-12-poster-card-layout.md](docs/plans/features/feat-12-poster-card-layout.md) | Visual movie card grid |
| [feat-13-game-variants.md](docs/plans/features/feat-13-game-variants.md) | Blind, theme, team modes |
| [feat-14-yearly-recap.md](docs/plans/features/feat-14-yearly-recap.md) | Year-end summary & awards |
| [feat-15-chat-bot-integration.md](docs/plans/features/feat-15-chat-bot-integration.md) | Slack/Discord bot |
| [feat-16-rest-api.md](docs/plans/features/feat-16-rest-api.md) | Django REST Framework API |

---

## By the Numbers

| Category | Count |
|----------|-------|
| Bugs found | 21 |
| Improvements proposed | 12 |
| Feature ideas | 16 |
| Plan files created | 49 |
| Total documents | 55 |
| Project age | 4.5 years |
| Total commits | ~74 |
| Contributors | 3 |
| Django models | 12 |
| Views | 20+ |
| Templates | 20 |
| Test coverage | 0% |
