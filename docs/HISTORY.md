# MysteryMovie Project History

A timeline of the Mystery Movie Club application from initial creation to present day.

## Overview

- **Project Duration**: October 2020 – April 2025 (4.5 years)
- **Total Commits**: ~74
- **Production URL**: www.clubprotean.com
- **Contributors**: m-hollow (primary developer), John C. Worsley, Corwin Light-Williams

---

## Phase 1: Project Foundation (October 12–28, 2020)

The project was created as a Django web application for a movie club game where members submit mystery movies, guess who chose each film, rate them, and earn points.

- Initial commit with Django project scaffolding (`mmg` project, `movies` and `users` apps)
- Core models established: `GameRound`, `Movie`, `UserMovieDetail`, `UserRoundDetail`, `UserProfile`
- Basic views and templates built for the round-based game flow
- Environment configuration via `.env` file with `django-environ`
- MySQL database backend chosen from the start

## Phase 2: Core Feature Development (October 28 – November 7, 2020)

Rapid development of the scoring and game mechanics:

- Point scoring system implemented (guess points, liked/disliked, seen/unseen, known)
- Ranking system with `RoundRank` model (1st through 10th place)
- Round conclusion workflow: `ConcludeRoundView` → `CommitUserRoundView` → `CommitGameRoundView`
- Results display pages for active and archived rounds
- Trophy system for special achievements
- `PointsEarned` model for detailed point tracking
- `AllTimeScore` model for snapshot rankings
- `requirements.txt` and dependency management

## Phase 3: Deployment & Settings Split (November 7, 2020 – February 2021)

Prepared the application for production deployment:

- Settings module split into `development.py` and `production.py`
- Production configured for PythonAnywhere hosting (`mholloway$movie_club` MySQL database)
- `www.clubprotean.com` set as allowed host
- WSGI configuration finalized
- Pre-deployment cleanup and optimization

## Phase 4: Frontend & UI Expansion (February – June 2021)

Major frontend feature push:

- **Members View** — Rankings page showing all-time leaderboards by category
- **User Profile Page** — Individual stats, movie history, all-time scores
- **Overview Page** — All movies across all rounds with sorting (by round, name, user, rating)
- Front-end sorting with jQuery UI integration
- Bug fixes for: sorting behavior, overview round count, total points calculation, average rating computation
- `average_rating` property bug fix (June 8, 2021) — last commit before a long hiatus

## Phase 5: UI Polish (March 2023)

After a nearly two-year gap (the app was in active production use during this time):

- Overview page styling improvements: alignment, table formatting, margins
- Added "Unseen" and "Known" flags to Member Rankings display

## Phase 6: Infrastructure & Maintenance (May – August 2023)

- **PR #1** — First merged pull request: added initial `README.md` and missing `wheel` requirement
- **PR #3** — MySQL UTF-8 4-byte character support upgrade
- Round 20 data handling ("omit round 20 from memory for Safety Reasons" — on separate branch `remove-round20`)
- `.gitignore` and registration handling updates
- Fixed participant count display on index page
- Contributor **Corwin Light-Williams** made first contributions

## Phase 7: Results Party Feature (November 2024 – April 2025)

The largest development effort in the project's history, spanning 8+ PRs over 5 months. Contributor **John C. Worsley** joined the project.

### PR #4–5 (November 2024)
- New `PartyState` and `PartyGoers` models for real-time synchronized viewing
- Complete Results Party UI: interactive stepped reveal of round results
- AJAX polling endpoints for party state synchronization
- Overhauled `views.py` with 634+ new lines for party logic
- New `resultsparty.html` template with JavaScript state machine

### PR #6 (December 25, 2024)
- Admin ability to upload movie cover art images to `MEDIA_ROOT`
- `EditRoundImagesView` for managing movie poster files

### PR #7 (December 28–29, 2024)
- Sanity-check validation in round conclusion
- Prevents 500 errors when users haven't completed all their votes

### PR #8 (February 2025)
- Minor bug fixes across the application

### PR #9 (April 4, 2025)
- User profile picture support (generic format, not WebP-only)
- Emoji support on profile pages
- Image view of user's movie choices on profile

### PR #10–11 (April 4, 2025)
- Final merge of `resultsparty` branch into `main`
- Fixed media path issues for user profile pictures
- "Fixed last path issue in user profile pic (i hope)" — most recent commit

---

## Branch History

| Branch | Purpose | Status |
|--------|---------|--------|
| `main` | Production branch | Active |
| `resultsparty` | Results Party feature development | Merged (PRs #4–11) |
| `mysql-utf8-4byte` | MySQL encoding upgrade | Merged (PR #3) |
| `remove-round20` | Round 20 data handling | Unmerged, preserved |

## Contributor Summary

| Contributor | Period | Focus |
|-------------|--------|-------|
| m-hollow (Michael Arthur Holloway) | Oct 2020 – present | Primary developer, all features |
| Corwin Light-Williams | 2023 | Infrastructure, README, requirements |
| John C. Worsley | Nov 2024 – present | Results Party feature, profile pics |

## Key Milestones

1. **October 12, 2020** — First commit
2. **November 7, 2020** — First production deployment to clubprotean.com
3. **June 8, 2021** — Last commit before 2-year maintenance period
4. **May 13, 2023** — First merged pull request (#1)
5. **November 15, 2024** — Results Party feature begins
6. **April 4, 2025** — Latest activity (PR #11 merged)
