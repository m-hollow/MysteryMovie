# FEAT-02: Streaming Availability Links

## Summary
Show where each movie is currently streaming using a streaming availability API.

## Design

### API Options
- **Streaming Availability API** (RapidAPI) — covers Netflix, Hulu, Disney+, Prime, etc.
- **JustWatch** (unofficial API or web scraping)
- **TMDB Watch Providers** — free with TMDB API key

### Display
Add a "Where to Watch" section on movie detail pages:
- Icons for each streaming service with direct links
- Cache results (streaming availability changes slowly — cache for 24 hours)

### Implementation Steps
1. Choose API and get credentials
2. Create `movies/services/streaming.py` client
3. Add caching layer (Django cache framework or model field)
4. Add "Where to Watch" partial template
5. Include in `movie.html` and `old_movie.html`
6. Handle movies not found gracefully

## Dependencies
- Requires FEAT-01 (IMDb ID) for reliable lookup, or use title+year matching

## Effort: Low-Medium (half day, once API is chosen)
