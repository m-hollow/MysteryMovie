# FEAT-12: Movie Poster Card Layout

## Summary
Replace text-only movie listings with visual card grid showing poster thumbnails.

## Design
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  [POSTER]   │  │  [POSTER]   │  │  [POSTER]   │
│             │  │             │  │             │
│  Movie Name │  │  Movie Name │  │  Movie Name │
│  (2024)     │  │  (2023)     │  │  (2022)     │
│  ★★★★☆     │  │  ★★★☆☆     │  │  ★★★★★     │
│  Chosen by: │  │  Chosen by: │  │  Chosen by: │
│  Player X   │  │  Player Y   │  │  Player Z   │
└─────────────┘  └─────────────┘  └─────────────┘
```

### CSS Grid Layout
```css
.movie-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1.5rem;
}
```

### Card Component
```html
<div class="movie-card">
    <img src="{{ movie.poster_url }}" alt="{{ movie.name }}" class="movie-poster">
    <div class="movie-info">
        <h3>{{ movie.name }}</h3>
        <span class="year">{{ movie.year }}</span>
        <div class="rating">{{ movie.average_rating|stars }}</div>
    </div>
</div>
```

### Fallback
- If no poster image: show a styled placeholder with movie title
- Use existing `/media/movie/{id}.jpg` files from EditRoundImagesView uploads

### Steps
1. Create card component CSS
2. Create `_movie_card.html` partial template
3. Update `index.html` to use card grid
4. Update `overview.html` with toggle: list view / grid view
5. Add lazy loading for poster images

## Effort: Low (half day)
