# FEAT-14: Yearly Recap & Awards

## Summary
Automated year-end summary celebrating the year's highlights and member achievements.

## Content

### Automatically Generated
- **Best Movie of the Year** — highest average rating
- **Worst Movie** — lowest average rating
- **Best Guesser** — highest guess accuracy
- **Most Points** — cumulative points across all rounds that year
- **Most Improved** — biggest rank improvement from first to last round
- **Most Rounds Won** — win count for the year
- **Most Controversial** — widest rating spread

### Voted Awards (Optional)
- Members vote on custom categories: "Funniest Movie", "Best Twist", "Most Forgettable"
- Voting period: last week of December
- Results revealed at New Year

## Implementation

### View
- `/recap/<year>/` — year recap page
- Compute all stats from existing data filtered by year

### Template
- Single-page scrollable layout
- Section for each award with movie poster, stats, winner
- Shareable (public URL option)

### Steps
1. Create `RecapView` with year filter
2. Compute all stats from GameRound/UserRoundDetail/UserMovieDetail filtered by date
3. Create visually rich `recap.html` template
4. Add navigation: "Year in Review" link (appears in December/January)
5. (Optional) Add voting model and voting UI for custom awards

## Effort: Medium (1 day for auto-generated, 2 days with voting)
