# FEAT-03: Advanced Statistics Dashboard

## Summary
Per-user analytics showing rating tendencies, guess accuracy, head-to-head records, and trends over time.

## Proposed Stats

### Per-User
- **Average rating given** vs. group average ("you rate 0.5 stars higher")
- **Guess accuracy** — overall and by opponent
- **Win rate** — rounds won / rounds played
- **Point breakdown** — pie chart of point sources
- **Best/worst movie** — highest and lowest rated movies they chose
- **Win streak** — current and all-time longest

### Head-to-Head
- For any two players: guess accuracy against each other, rating correlation
- "You correctly guessed Player X's movies 80% of the time"

### Trends
- Rating average per round (line chart over time)
- Point total per round (bar chart)
- Ranking history (line chart)

## Implementation

### New View: `StatsView`
- `/stats/` — personal dashboard
- `/stats/<user_id>/` — view another player's stats

### Computation
- Calculate stats from existing `UserMovieDetail` and `UserRoundDetail` data
- No new models needed — compute on the fly or cache
- For charts: use Chart.js (client-side) or serve data via JSON endpoint

### Steps
1. Create stats computation functions in `movies/services/stats.py`
2. Create `stats.html` template with Chart.js integration
3. Add `StatsView` and URL pattern
4. Add navigation link in base.html
5. Add caching for expensive computations

## Effort: Medium-High (1-2 days)
