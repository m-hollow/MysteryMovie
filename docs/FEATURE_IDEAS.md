# Feature Ideas

New functionality that would extend the Mystery Movie Club experience. Each idea has a detailed plan in [`plans/features/`](plans/features/).

---

## Content & Metadata

### FEAT-01: Movie Database Integration (IMDb/OMDB)
- **What**: Auto-populate movie details (poster, director, cast, genre, runtime, year) by searching IMDb or the OMDB API. Users add movies by title or IMDb URL instead of manual entry.
- **Why**: Reduces manual data entry, adds rich metadata, enables genre-based analytics.
- **Plan**: [docs/plans/features/feat-01-movie-database-integration.md](plans/features/feat-01-movie-database-integration.md)

### FEAT-02: Streaming Availability Links
- **What**: Show where each movie is currently streaming (Netflix, Hulu, etc.) using the JustWatch or Streaming Availability API.
- **Why**: Helps members find and watch movies more easily.
- **Plan**: [docs/plans/features/feat-02-streaming-availability.md](plans/features/feat-02-streaming-availability.md)

## Analytics & Statistics

### FEAT-03: Advanced Statistics Dashboard
- **What**: Per-user analytics: genre preferences, rating tendencies ("you rate 0.5 stars higher than the group"), head-to-head records, guess accuracy by opponent, win streaks.
- **Why**: Adds depth and engagement between rounds; members love comparing stats.
- **Plan**: [docs/plans/features/feat-03-advanced-statistics.md](plans/features/feat-03-advanced-statistics.md)

### FEAT-04: Round Analytics & Heatmaps
- **What**: Per-round insights: who guesses who correctly most often (heatmap), most controversial movies (widest rating spread), guess confidence calibration.
- **Why**: Makes results review more interesting and reveals group dynamics.
- **Plan**: [docs/plans/features/feat-04-round-analytics.md](plans/features/feat-04-round-analytics.md)

### FEAT-05: Historical Greatest Hits
- **What**: All-time leaderboards: highest rated movies ever, most controversial, most mysterious (hardest to guess), "greatest hits" compilations.
- **Why**: Celebrates the club's history and provides nostalgia value.
- **Plan**: [docs/plans/features/feat-05-historical-greatest-hits.md](plans/features/feat-05-historical-greatest-hits.md)

## Gamification

### FEAT-06: Achievement/Badge System
- **What**: Beyond trophies — persistent achievements: "Perfect Round" (all guesses correct), "Contrarian" (movie everyone disliked), "Trendsetter" (movie everyone loved), "Dark Horse" (movie nobody heard of), persistence badges (X rounds played).
- **Why**: Adds long-term engagement goals beyond round-by-round scoring.
- **Plan**: [docs/plans/features/feat-06-achievement-badges.md](plans/features/feat-06-achievement-badges.md)

### FEAT-07: Custom Scoring Rules
- **What**: Admin-configurable point values per category. Seasonal rulesets (e.g., "double guess points" month). Handicap system for experienced vs. new players.
- **Why**: Keeps the game fresh and allows balancing as the group evolves.
- **Plan**: [docs/plans/features/feat-07-custom-scoring.md](plans/features/feat-07-custom-scoring.md)

## Communication & Social

### FEAT-08: Notification System
- **What**: Email (or optional SMS) alerts: new round started, submission deadline approaching, round concluded, results published, profile comments.
- **Why**: Keeps members engaged and reduces admin nagging.
- **Plan**: [docs/plans/features/feat-08-notifications.md](plans/features/feat-08-notifications.md)

### FEAT-09: Comments & Discussion
- **What**: Post-round discussion threads on movies. Reactions (thumbs up, laughing, etc.) on comments. Optional per-movie discussion visible after all ratings submitted.
- **Why**: Captures the social aspect of watching and discussing movies together.
- **Plan**: [docs/plans/features/feat-09-comments-discussion.md](plans/features/feat-09-comments-discussion.md)

## User Experience

### FEAT-10: Mobile-Optimized Interface
- **What**: Responsive redesign for mobile: simplified forms, touch-friendly buttons, collapsible tables, card-based movie browsing with poster images.
- **Why**: Members likely submit ratings from their phones after watching movies.
- **Plan**: [docs/plans/features/feat-10-mobile-optimization.md](plans/features/feat-10-mobile-optimization.md)

### FEAT-11: Dark Mode
- **What**: User-selectable dark/light theme, stored as a preference. Automatic switching based on system preference.
- **Why**: Reduces eye strain for evening movie sessions; popular user expectation.
- **Plan**: [docs/plans/features/feat-11-dark-mode.md](plans/features/feat-11-dark-mode.md)

### FEAT-12: Movie Poster Card Layout
- **What**: Replace text-only movie listings with visual card grid showing poster images, title, year, and rating at a glance.
- **Why**: More engaging and visually appealing; leverages the poster upload feature from PR #6.
- **Plan**: [docs/plans/features/feat-12-poster-card-layout.md](plans/features/feat-12-poster-card-layout.md)

## Advanced Game Modes

### FEAT-13: Game Variants
- **What**: Alternative round formats: "Blind Round" (don't know who else is playing), "Theme Round" (all movies must match a theme), "Director's Cut" (one director), "Team Mode" (2v2v2).
- **Why**: Keeps the game fresh after many rounds; encourages creative movie choices.
- **Plan**: [docs/plans/features/feat-13-game-variants.md](plans/features/feat-13-game-variants.md)

### FEAT-14: Yearly Recap & Awards
- **What**: Automated year-end summary: best movies, worst movies, best guesser, most improved, "Oscar" categories voted on by members.
- **Why**: Celebrates the year's highlights and creates a fun annual tradition.
- **Plan**: [docs/plans/features/feat-14-yearly-recap.md](plans/features/feat-14-yearly-recap.md)

## Integration

### FEAT-15: Slack/Discord Bot
- **What**: Bot that announces new rounds, sends submission reminders, shares results highlights, and allows quick movie lookups from chat.
- **Why**: Meets members where they already communicate; reduces friction for engagement.
- **Plan**: [docs/plans/features/feat-15-chat-bot-integration.md](plans/features/feat-15-chat-bot-integration.md)

### FEAT-16: REST API
- **What**: Django REST Framework API for all read operations (rounds, movies, scores, profiles). Enables external tools, mobile apps, and third-party integrations.
- **Why**: Opens the platform for future development; enables a potential mobile app.
- **Plan**: [docs/plans/features/feat-16-rest-api.md](plans/features/feat-16-rest-api.md)

---

## Priority Suggestions

| Priority | Features | Rationale |
|----------|----------|-----------|
| **Quick Wins** | FEAT-11 (dark mode), FEAT-12 (poster cards) | Low effort, high user satisfaction |
| **High Impact** | FEAT-01 (OMDB), FEAT-08 (notifications), FEAT-10 (mobile) | Core UX improvements |
| **Engagement** | FEAT-03 (stats), FEAT-06 (achievements), FEAT-09 (comments) | Keeps members coming back |
| **Fun Additions** | FEAT-13 (game variants), FEAT-14 (yearly recap) | Freshness and tradition |
| **Platform** | FEAT-16 (REST API), FEAT-15 (bot) | Foundation for future growth |
