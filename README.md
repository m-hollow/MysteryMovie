# Mystery Movie Club

A Django web application for running a movie guessing game. Members submit mystery movies, watch them together, then guess who chose each film, rate them, and earn points across multiple rounds. The player with the most points wins each round.

**Production**: [www.clubprotean.com](http://www.clubprotean.com)

## How the Game Works

1. **Admin creates a round** and adds participants
2. **Each player secretly submits a movie** for the group to watch
3. **The group watches all movies** over time
4. **Players submit details for each movie**: whether they'd seen it before, heard of it, their rating (1–5 stars), who they think chose it, and comments
5. **Admin concludes the round** — points are calculated and rankings determined
6. **Results Party** — an interactive synchronized reveal of the results

### Point System

| Category | Points | Condition |
|----------|--------|-----------|
| Correct Guess | 2 | Correctly guessed who chose a movie |
| Liked Movie | 2 | Someone rated your movie > 3 stars |
| Disliked Movie | 2 | Someone rated your movie 1 star ("Deep Hurting") |
| Unseen Movie | 1 | Someone hadn't seen your movie before |
| Known Movie | 1 | Someone had heard of your movie |

### Trophies

Special awards given each round: Deepest Hurting (lowest rated), Light On Hurting (highest rated), A True Mystery (most unknown), The Wiseman (all correct guesses), The Seer (seen all movies).

## Tech Stack

- **Backend**: Django 3.1.2 (Python 3)
- **Database**: MySQL (mysqlclient)
- **Frontend**: Django templates, Bootstrap 4, jQuery UI
- **Forms**: django-crispy-forms, django-bootstrap4
- **Environment**: django-environ for `.env` configuration
- **Hosting**: PythonAnywhere (production)

## Project Structure

```
MysteryMovie/
├── mmg/                    # Django project configuration
│   ├── settings/
│   │   ├── development.py  # Local dev settings (DEBUG=True)
│   │   └── production.py   # Production settings (clubprotean.com)
│   ├── urls.py             # Root URL routing
│   └── wsgi.py             # WSGI entry point
├── movies/                 # Main app — game logic, models, views
│   ├── models.py           # GameRound, Movie, UserProfile, scoring models
│   ├── views.py            # All view classes and functions
│   ├── forms.py            # AddMovieForm, UserMovieDetailForm
│   ├── signals.py          # Auto-create UserProfile on User creation
│   ├── utility_functions.py # Date helpers, seed data functions
│   ├── templates/movies/   # 20+ HTML templates
│   └── migrations/         # 15 database migrations
├── users/                  # Authentication app
│   ├── views.py            # RegisterView (with auto-login)
│   └── templates/registration/  # login.html, register.html
├── manage.py
└── requirements.txt
```

## Key Models

- **GameRound** — A round of the game with participants, dates, and a winner
- **Movie** — A film entry with name, year, who chose it, and watch date
- **UserProfile** — One-to-one extension of Django User with all-time stats and admin flag
- **UserRoundDetail** — Per-user scoring for a specific round (points, rank, trophies)
- **UserMovieDetail** — A user's interaction with a movie (rating, guess, seen/heard flags)
- **Trophy** — Achievement awards with point values
- **PointsEarned** — Detailed point breakdown records
- **PartyState / PartyGoers** — Real-time state for the Results Party feature

## Required Software

- Python 3
- MySQL server
- libmysqlclient ([download](https://dev.mysql.com/downloads/c-api/))
- (Optional) Python 3 `venv`

## Setup & Installation

### 1. Clone and create virtual environment

```bash
git clone <repo-url>
cd MysteryMovie
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Set up MySQL database

```sql
sudo mysql

CREATE DATABASE mmg_1;
CREATE USER 'mmg_user_a'@'localhost' IDENTIFIED BY 'mmg_password';
GRANT CREATE, ALTER, INSERT, UPDATE, DELETE, SELECT, REFERENCES, INDEX
  ON mmg_1.* TO 'mmg_user_a'@'localhost';
```

### 4. Configure environment

Create a `.env` file in the project root:

```env
SECRET_KEY=<generate with: python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'>
DEBUG=True
DB_NAME=mmg_1
DB_USER=mmg_user_a
DB_PASSWORD=mmg_password
```

### 5. Run migrations

```bash
python3 manage.py migrate --settings=mmg.settings.development
```

### 6. Create a superuser

```bash
python3 manage.py createsuperuser --settings=mmg.settings.development
```

### 7. Seed initial data

From the Django shell (`python3 manage.py shell --settings=mmg.settings.development`):

```python
from movies.utility_functions import create_ranks, add_trophies
create_ranks()    # Creates RoundRank entries (1st–10th)
add_trophies()    # Creates default Trophy entries
```

### 8. Run the development server

```bash
python3 manage.py runserver --settings=mmg.settings.development
```

Visit `http://localhost:8000/` — you'll be redirected to the login page.

## Admin Workflow

The game admin (users with `UserProfile.is_mmg_admin = True`) manages rounds through:

1. **Settings page** (`/settings/`) — Overview of all rounds, movies, and members
2. **Create Round** (`/create_round/`) — Start a new game round
3. **Edit Round** (`/edit_round/<id>/`) — Modify round details and participants
4. **Edit Round Images** (`/edit_round_images/<id>/`) — Upload movie poster art
5. **Conclude Round** (`/conclude_round/<id>/`) — Calculate all points and rankings
6. **Commit User Round** (`/commit_user_round/<id>/`) — Finalize individual user scores
7. **Commit Game Round** (`/commit_game_round/<id>/`) — Mark round as complete, update all-time stats

## URL Reference

| Path | Purpose |
|------|---------|
| `/` | Current round home page |
| `/movie/<id>-<slug>/` | Movie detail (active round) |
| `/old_movie/<id><slug>/` | Movie detail (completed round) |
| `/members/` | Member rankings |
| `/overview/<sort_by>/` | All movies overview (sortable) |
| `/results/` | Current round results |
| `/resultsparty/` | Interactive results party |
| `/trophies/` | Trophy listings |
| `/user_profile/<id>/` | User profile with all-time stats |
| `/settings/` | Admin settings panel |
| `/admin/` | Django admin interface |

## Media Files

- **Movie posters**: `/media/movie/<movie_id>.jpg`
- **User profile pictures**: `/media/user/<user_id>`
- Fallback images served from `/static/img/movie/` if media files don't exist

## Contributing

The project uses a PR-based workflow with feature branches merged into `main`. See [HISTORY.md](docs/HISTORY.md) for the full development timeline.

## Related Documentation

- [HISTORY.md](docs/HISTORY.md) — Full project history and timeline
- [BUGS.md](docs/BUGS.md) — Known bugs listed by severity
- [FUTURE_IMPROVEMENTS.md](docs/FUTURE_IMPROVEMENTS.md) — Technical improvements and refactoring ideas
- [FEATURE_IDEAS.md](docs/FEATURE_IDEAS.md) — Ideas for new features
- [docs/plans/](docs/plans/) — Detailed plan files for bugs, improvements, and features
