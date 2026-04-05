# FEAT-04: Round Analytics & Heatmaps

## Summary
Per-round insights: guess heatmaps, controversial movies, and guess confidence calibration.

## Proposed Analytics

### Guess Heatmap
- Matrix showing "who guessed who" for each movie
- Rows = guessers, columns = actual choosers
- Color-coded: green = correct, red = incorrect
- Shows patterns: "Everyone always guesses Player X for horror movies"

### Controversy Index
- Movies with the widest rating spread (std deviation of ratings)
- "Most controversial" — some loved it, some hated it
- "Consensus" — everyone agreed on the rating

### Guess Difficulty
- Per movie: what percentage of players guessed correctly
- "Hardest to guess" and "Most obvious" rankings

## Implementation

### Computation
All data already exists in `UserMovieDetail`:
```python
# Guess heatmap
for umd in UserMovieDetail.objects.filter(movie__game_round=round):
    actual_chooser = umd.movie.chosen_by
    guessed = umd.user_guess
    matrix[umd.user][actual_chooser] = (guessed == actual_chooser)
```

### Display
- Use HTML table with color-coded cells for heatmap
- Or use a lightweight JS library (e.g., D3.js heatmap)
- Add as a section on `results.html` and `old_round_results.html`

### Steps
1. Create analytics computation functions
2. Add heatmap partial template
3. Integrate into results views
4. Add controversy and difficulty stats

## Effort: Medium (1 day)
