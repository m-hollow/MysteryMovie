# FEAT-01: Movie Database Integration (IMDb/OMDB)

## Summary
Auto-populate movie metadata (poster, director, cast, genre, runtime) from OMDB API when adding a movie.

## Design

### API Choice: OMDB API
- Free tier: 1,000 requests/day (more than enough)
- Returns: title, year, rated, genre, director, actors, plot, poster URL, IMDb rating
- Simple REST API with JSON responses

### Model Changes
Add fields to `Movie`:
```python
imdb_id = models.CharField(max_length=20, blank=True)
director = models.CharField(max_length=200, blank=True)
genre = models.CharField(max_length=200, blank=True)
runtime_minutes = models.PositiveIntegerField(null=True, blank=True)
plot_summary = models.TextField(blank=True)
poster_url = models.URLField(blank=True)
imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
```

### User Flow
1. User types movie name in AddMovieForm
2. AJAX autocomplete queries OMDB API
3. User selects correct match from results
4. Fields auto-populate (user can still edit year, etc.)
5. Poster image auto-downloaded to media/movie/

### Implementation Steps
1. Get OMDB API key (free at omdbapi.com)
2. Store API key in `.env`
3. Create `movies/services/omdb.py` client
4. Add model fields + migration
5. Add AJAX search endpoint
6. Update AddMovieForm with autocomplete
7. Auto-download poster on movie creation

## Effort: Medium (1-2 days)
