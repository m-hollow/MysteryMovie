# FEAT-05: Historical Greatest Hits

## Summary
All-time leaderboards for movies: highest rated, most controversial, most mysterious, and compilation pages.

## Proposed Sections

### "Hall of Fame" Page
- **Highest Rated Ever** — Top 10 movies by average rating across all rounds
- **Most Hated** — Top 10 lowest rated ("Deep Hurting Hall of Shame")
- **Most Controversial** — Widest rating spread
- **True Mysteries** — Movies nobody had heard of
- **Best Guessed** — Movies everyone identified correctly
- **Most Surprising** — High rating + nobody had heard of it

### Implementation
All computable from existing data:
```python
# Highest rated
Movie.objects.annotate(avg=Avg('usermoviedetail__star_rating')).order_by('-avg')[:10]

# Most controversial (highest std deviation)
Movie.objects.annotate(
    avg=Avg('usermoviedetail__star_rating'),
    stddev=StdDev('usermoviedetail__star_rating')
).order_by('-stddev')[:10]
```

### Steps
1. Create `GreatestHitsView` with all queries
2. Create `greatest_hits.html` template
3. Add URL pattern and navigation link
4. Cache the page (data only changes when rounds complete)

## Effort: Low (half day)
